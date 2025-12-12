import importlib
from textwrap import dedent

from typer.testing import CliRunner


def test_app_invokes_registered_command(tmp_path, monkeypatch):
    # create a temporary project with a do.py that registers a command
    proj = tmp_path / "proj"
    proj.mkdir()
    proj.joinpath("do.py").write_text(dedent("""
from dopy import command

@command
def say():
    print('hello-e2e')
"""))

    # change to project dir and reload modules so they pick up the new do.py
    monkeypatch.chdir(proj)
    loader = importlib.import_module("dopy.command_loader")
    importlib.reload(loader)
    loader.load_commands()

    # reload app to ensure it's using latest commands
    app_mod = importlib.import_module("dopy.app")
    importlib.reload(app_mod)

    runner = CliRunner()
    result = runner.invoke(app_mod.app, ["say"])
    assert result.exit_code == 0
    assert "hello-e2e" in result.stdout
