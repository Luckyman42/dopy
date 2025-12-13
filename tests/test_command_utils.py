import pathlib
import datetime

import pytest

from dopy import command_utils as cu
from dopy.command import COMMANDS, command
from dopy.exception import CommandNotFoundException, InvalidCommandArgumentsException


def test_convert_basic_types():
    assert cu._convert_value("123", int) == 123
    assert cu._convert_value("3.14", float) == pytest.approx(3.14)
    assert cu._convert_value("true", bool) is True
    assert cu._convert_value("False", bool) is False
    p = cu._convert_value("/tmp/x", pathlib.Path)
    assert isinstance(p, pathlib.Path)
    dt = cu._convert_value("2025-12-12", datetime.datetime)
    assert isinstance(dt, datetime.datetime)


def test_convert_list_and_set():
    l = cu._convert_value("a,b,c", list[str])
    assert l == ["a", "b", "c"]

    lnum = cu._convert_value("1,2,3", list[int])
    assert isinstance(lnum, list)
    assert lnum == [1, 2, 3]

    s = cu._convert_value("1,2,3", set[int])
    assert isinstance(s, set)
    assert s == {1, 2, 3}


def test_resolve_arguments_positional_overrides_kwargs():
    def f(name: str, num: int = 1):
        return None

    # positional provided for 'name', and kwargs include name and num
    pos_args, kw_args = cu.resolve_arguments(f, ["positional_name"], {"name": "kw_name", "num": "5"})
    assert pos_args == ["positional_name"]
    # name should not be in kw_args because it was provided positionally
    assert "name" not in kw_args
    assert kw_args.get("num") == 5


def test_parse_args_integration_and_registration():
    # create a temporary command and register it via decorator
    @command
    def testcmd(name: str, extra: list[str]|None = None):
        return None

    try:
        commands = cu.parse_args(["name=pami", "testcmd", "posval"]) 
        assert len(commands) == 1
        func, pos_args, kw_args = commands[0]
        assert func.__name__ == "testcmd"
        # positional 'posval' should be assigned to the first parameter (name)
        assert pos_args == ["posval"]
        # since name was provided positionally, kwargs should not include it
        assert "name" not in kw_args
    finally:
        # cleanup registration
        COMMANDS.pop("testcmd", None)


def test_execute_command_type_error_raises():
    def f(a):
        return a

    with pytest.raises(InvalidCommandArgumentsException):
        cu.execute_command(f)


def test_split_commands_error():
    # ensure no such command raises
    with pytest.raises(CommandNotFoundException):
        cu.split_commands(["not_a_cmd"]) 


def test_resolve_arguments_var_kw():
    def g(**kwargs):
        return None

    pos, kw = cu.resolve_arguments(g, [], {"a": "1", "b": "2"})
    assert pos == []
    assert kw == {"a": "1", "b": "2"}


def test_convert_value_fail_and_empty_list():
    # conversion fail should return original string
    assert cu._convert_value("notint", int) == "notint"
    # empty list string -> empty list
    assert cu._convert_value("", list[str]) == []
