import typer
from rich.console import Console
from dopy.command_loader import load_commands
from dopy.command_utils import parse_args, execute_command, complete_commands

console = Console()
"""Console instance for interactions"""
app = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=True,
)
"""Typer application which is the main componenet"""

load_commands()


@app.command(context_settings={"allow_extra_args": True})
def main(
    ctx: typer.Context,
    command_name: str = typer.Argument(None, autocompletion=complete_commands),
):
    """DO: A simple task runner"""
    params = ([command_name] + list(ctx.args)) if command_name else list(ctx.args)
    for fn, args, kwargs in parse_args(params):
        try:
            execute_command(fn, *args, **kwargs)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(code=1)
