import importlib
from textwrap import dedent
import pytest
import importlib.util

def write_do(path, content: str):
    (path / "do.py").write_text(dedent(content))


def test_loader_prefers_cwd(tmp_path, monkeypatch):
    # prepare default DOPY_HOME with a do.py that registers from_default
    default_dir = tmp_path / "dopy_home"
    default_dir.mkdir()
    write_do(default_dir, """
from dopy import command

@command
def from_default():
    return 'from_default'
""")

    # prepare cwd with a do.py that registers from_default differently
    cwd = tmp_path / "proj"
    cwd.mkdir()
    write_do(cwd, """
from dopy import command

@command
def from_default():
    return 'from_cwd'
""")

    # monkeypatch DOPY_HOME and cwd
    loader = importlib.import_module("dopy.command_loader")
    monkeypatch.setattr(loader, "DOPY_HOME", str(default_dir))
    monkeypatch.chdir(cwd)

    # ensure COMMANDS cleared
    cmd = importlib.import_module("dopy.command")
    cmd.COMMANDS.pop("from_default", None)

    # load commands and ensure cwd override
    loader.load_commands()
    assert "from_default" in cmd.COMMANDS

    # executing the registered function should print value from cwd version
    assert "from_cwd" == cmd.COMMANDS["from_default"]()


def test_loader_no_files_does_not_raise(tmp_path, monkeypatch):
    loader = importlib.import_module("dopy.command_loader")
    # set DOPY_HOME to an empty non-existent path and cwd to an empty tmp dir
    monkeypatch.setattr(loader, "DOPY_HOME", str(tmp_path / "nope"))
    monkeypatch.chdir(tmp_path)
    # should not raise
    loader.load_commands()


def test_loader_exec_errors(tmp_path, monkeypatch):
    # create a do.py that raises during import
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "do.py").write_text("raise RuntimeError('boom')")

    loader = importlib.import_module("dopy.command_loader")
    monkeypatch.chdir(proj)

    with pytest.raises(RuntimeError):
        loader.load_commands()


def test_loader_handles_spec_none(tmp_path, monkeypatch):
    loader = importlib.import_module("dopy.command_loader")

    # monkeypatch spec_from_file_location to return None to hit that branch
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)

    # create a dummy do.py file so exists(path) is True
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "do.py").write_text("# empty")
    monkeypatch.chdir(proj)

    # call should return without raising
    loader.load_commands()
