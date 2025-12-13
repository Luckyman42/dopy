import typer
from typing import Annotated
from rich.console import Console
from dopy.command_loader import load_commands
from dopy.command_utils import parse_args, execute_command
from dopy.command_helper import complete_commands, print_help, print_commands_help

console = Console()
"""Console instance for interactions"""
app = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=False,
)
"""Typer application which is the main componenet"""

load_commands()


@app.command(context_settings={"allow_extra_args": True})
def main(
    ctx: typer.Context,
    args: Annotated[
        list[str] | None,
        typer.Argument(help="The commands.", autocompletion=complete_commands),
    ] = None,
    help: bool = typer.Option(
        False, "--help", "-h", help="Show this help message and exit."
    ),
):
    """DO: A simple task runner"""
    # If no commands provided, display custom help
    try:
        if not args:
            print_help(console)
            return

        commands = parse_args(args)

        if help:
            print_commands_help(commands, console)

        for fn, args, kwargs in commands:
            execute_command(fn, *args, **kwargs)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
