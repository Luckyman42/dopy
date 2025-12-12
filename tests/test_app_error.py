import importlib
from textwrap import dedent
from typer.testing import CliRunner


def test_app_handles_command_exception(tmp_path, monkeypatch):
    proj = tmp_path / "proj"
    proj.mkdir()
    proj.joinpath("do.py").write_text(dedent("""
from dopy import command

@command
def fail():
    raise RuntimeError('oops')
"""))

    monkeypatch.chdir(proj)
    loader = importlib.import_module("dopy.command_loader")
    importlib.reload(loader)
    loader.load_commands()

    app_mod = importlib.import_module("dopy.app")
    importlib.reload(app_mod)

    runner = CliRunner()
    result = runner.invoke(app_mod.app, ["fail"])
    # Typer should exit with code 1
    assert result.exit_code == 1
    assert "Error:" in result.stdout
