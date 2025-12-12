import importlib


def test_command_and_echo_and_sh_register_and_run(capsys):
    # import module fresh
    cmd = importlib.import_module("dopy.command")

    # ensure clean state for test names
    cmd.COMMANDS.pop("_tmp_cmd", None)
    cmd.COMMANDS.pop("_tmp_echo", None)
    cmd.COMMANDS.pop("_tmp_sh", None)

    @cmd.command
    def _tmp_cmd():
        return "ok"

    assert "_tmp_cmd" in cmd.COMMANDS
    # command returns value
    assert cmd.COMMANDS["_tmp_cmd"]() == "ok"

    @cmd.echo
    def _tmp_echo():
        return "echoed"

    # echo prints to stdout
    cmd.COMMANDS["_tmp_echo"]()
    captured = capsys.readouterr()
    assert "echoed" in captured.out

    @cmd.sh
    def _tmp_sh():
        # simple shell that prints 'hi'
        return "echo hi"

    # sh decorator executes shell command via os.system
    # os.system returns exit code (0 for success)
    result = cmd.COMMANDS["_tmp_sh"]()
    assert result == "echo hi"  # command returns the shell command string

    # cleanup
    cmd.COMMANDS.pop("_tmp_cmd", None)
    cmd.COMMANDS.pop("_tmp_echo", None)
    cmd.COMMANDS.pop("_tmp_sh", None)
