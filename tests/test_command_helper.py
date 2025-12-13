import pytest
import inspect
from unittest.mock import Mock

from dopy import command_utils as cu
from dopy import command_helper as ch
from dopy.command import COMMANDS, command
from dopy.exception import CommandNotFoundException


def test_complete_commands_and_get_command():
    # register a dummy function
    COMMANDS.pop("_c1", None)

    @command
    def _c1():
        """My doc line"""
        return None

    # complete_commands expects a CLI-like ctx with `params['args']`.
    ctx = type("Ctx", (), {"params": {"args": []}})()
    items = ch.complete_commands(ctx, "_c")
    assert any(name == "_c1" and "My doc line" in doc for name, doc in items)

    # get_command raises for unknown
    with pytest.raises(CommandNotFoundException):
        cu.get_command("no_such_cmd")

    # cleanup
    COMMANDS.pop("_c1", None)


class TestAllCommandsForHelp:
    """Test the all_commands_for_help function."""

    def test_returns_empty_list_when_no_commands_match(self):
        """Should return empty list when prefix doesn't match any commands."""
        COMMANDS.clear()
        result = ch.all_commands_for_help("nonexistent")
        assert result == []

    def test_returns_matching_commands_with_prefix(self):
        """Should return commands starting with the given prefix."""
        COMMANDS.clear()

        @command
        def test_cmd():
            pass

        @command
        def test_another():
            pass

        @command
        def hello():
            pass

        result = ch.all_commands_for_help("test")
        assert len(result) == 2
        names = [name for name, _ in result]
        assert "test_cmd" in names
        assert "test_another" in names
        assert "hello" not in names

        COMMANDS.clear()

    def test_extracts_first_line_of_docstring(self):
        """Should extract only the first line of docstring."""
        COMMANDS.clear()

        @command
        def multi_doc():
            """
            First line of doc.
            
            This is the second line.
            """
            pass

        result = ch.all_commands_for_help("multi")
        assert len(result) == 1
        assert result[0] == ("multi_doc", "First line of doc.")

        COMMANDS.clear()

    def test_handles_empty_docstring(self):
        """Should handle commands with no docstring."""
        COMMANDS.clear()

        @command
        def no_doc():
            pass

        result = ch.all_commands_for_help("no")
        assert len(result) == 1
        assert result[0] == ("no_doc", "")

        COMMANDS.clear()


class TestFormatParameterSignature:
    """Test the format_parameter_signature function."""

    def test_basic_parameter_formatting(self):
        """Should format a basic parameter correctly."""

        def sample_func(name: str):
            pass

        sig = inspect.signature(sample_func)
        param = list(sig.parameters.values())[0]
        name_part, desc_part = ch.format_parameter_signature(param)

        assert name_part == "name="
        assert "str" in desc_part

    def test_parameter_with_default_value(self):
        """Should format default values as 'Default='."""

        def sample_func(count: int = 5):
            pass

        sig = inspect.signature(sample_func)
        param = list(sig.parameters.values())[0]
        name_part, desc_part = ch.format_parameter_signature(param)

        assert name_part == "count="
        assert "Default=" in desc_part

    def test_parameter_without_annotation(self):
        """Should handle parameters without type annotation."""

        def sample_func(arg):
            pass

        sig = inspect.signature(sample_func)
        param = list(sig.parameters.values())[0]
        name_part, desc_part = ch.format_parameter_signature(param)

        assert name_part == "arg="


class TestDecodeParams:
    """Test the decode_params function."""

    def test_decodes_key_value_pairs(self):
        """Should decode 'key', '=', 'value' into 'key=value'."""
        result = ch.decode_params(["a", "=", "b", "c"])
        assert result == ["a=b", "c"]

    def test_handles_consecutive_pairs(self):
        """Should handle multiple consecutive key=value pairs."""
        result = ch.decode_params(["x", "=", "1", "y", "=", "2", "z"])
        assert result == ["x=1", "y=2", "z"]

    def test_handles_empty_list(self):
        """Should return empty list for empty input."""
        result = ch.decode_params([])
        assert result == []

    def test_handles_list_without_pairs(self):
        """Should return unmodified list when no pairs to decode."""
        result = ch.decode_params(["a", "b", "c"])
        assert result == ["a", "b", "c"]


class TestGetCommandInformation:
    """Test the get_command_information function."""

    def test_returns_command_signature_and_docs(self):
        """Should return command name, signature, docstring, and param docs."""

        def sample_cmd(name: str, count: int = 1):
            """Sample command for testing.
            
            Longer description here.
            """
            pass

        sig, doc, params = ch.get_command_information(sample_cmd)

        assert "sample_cmd" in sig
        assert "name: str" in sig
        assert "count: int = 1" in sig
        assert "Sample command for testing." in doc
        assert "name" in params
        assert "count" in params

    def test_handles_command_without_docstring(self):
        """Should handle commands with no docstring."""

        def no_doc_cmd(x):
            pass

        sig, doc, params = ch.get_command_information(no_doc_cmd)

        assert "no_doc_cmd" in sig
        assert doc == ""
        assert "x" in params

    def test_includes_all_parameters(self):
        """Should extract all parameters from function signature."""

        def multi_param_cmd(a, b: str, c: int = 5):
            """Multi param command."""
            pass

        sig, doc, params = ch.get_command_information(multi_param_cmd)

        assert len(params) == 3
        assert "a" in params
        assert "b" in params
        assert "c" in params


class TestCompleteCommands:
    """Test the complete_commands function."""

    def test_returns_all_commands_when_no_previous_params(self):
        """Should return all matching commands when no previous params."""
        COMMANDS.clear()

        @command
        def hello():
            """Hello"""
            pass

        @command
        def help_cmd():
            """Help"""
            pass

        ctx = type("Ctx", (), {"params": {"args": []}})()
        result = ch.complete_commands(ctx, "h")

        names = [name for name, _ in result]
        assert "hello" in names

        COMMANDS.clear()

    def test_handles_malformed_command_args(self):
        """Should gracefully handle malformed command args."""
        ctx = type("Ctx", (), {"params": {"args": ["nonexistent_cmd"]}})()
        result = ch.complete_commands(ctx, "")

        # Should return command list on error instead of crashing
        assert isinstance(result, list)


class TestPrintHelp:
    """Test the print_help function."""

    def test_prints_help_message(self):
        """Should print formatted help message."""
        COMMANDS.clear()

        @command
        def test_cmd():
            """Test command"""
            pass

        mock_console = Mock()
        ch.print_help(mock_console)

        # Verify print was called multiple times
        assert mock_console.print.call_count > 0


class TestPrintCommandHelp:
    """Test the print_command_help function."""

    def test_prints_command_documentation(self):
        """Should print command signature, docstring, and parameters."""

        def sample_cmd(name: str, verbose: bool = False):
            """Sample command for testing.
            
            This is a longer description.
            """
            pass

        mock_console = Mock()
        ch.print_command_help(sample_cmd, mock_console)

        assert mock_console.print.call_count > 0

    def test_handles_command_without_params(self):
        """Should handle commands with no parameters."""

        def no_params_cmd():
            """Command without params."""
            pass

        mock_console = Mock()
        ch.print_command_help(no_params_cmd, mock_console)

        assert mock_console.print.call_count > 0


class TestPrintCommandsHelp:
    """Test the print_commands_help function."""

    def test_prints_help_for_multiple_commands(self):
        """Should print help for each unique command in the list."""
        COMMANDS.clear()

        @command
        def cmd1():
            """First command"""
            pass

        @command
        def cmd2():
            """Second command"""
            pass

        commands = [(cmd1, [], {}), (cmd2, [], {}), (cmd1, ["arg"], {})]
        mock_console = Mock()

        # Capture print output
        ch.print_commands_help(commands, mock_console)

        # Should print help for cmd1 and cmd2 (cmd1 appears twice but should print once)
        assert mock_console.print.call_count > 0

        COMMANDS.clear()
