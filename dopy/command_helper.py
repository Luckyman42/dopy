from typing import Any
from collections.abc import Callable
from dopy.command import COMMANDS
import inspect
from dopy.command_utils import parse_args


def all_commands_for_help(incomplete: str) -> list[tuple[str, str]]:
    """Return a list of (command_name, short_doc) for commands starting with
    the given `incomplete` prefix.

    The short doc is the first line of the command's docstring (or empty
    string if none is present).
    """
    items: list[tuple[str, str]] = []
    for name, func in COMMANDS.items():
        if not name.startswith(incomplete):
            continue
        doc = (func.__doc__ or "").strip().split("\n")[0]
        if not doc:
            doc = ""
        items.append((name, doc))
    return items


def format_parameter_signature(param: inspect.Parameter) -> tuple[str, str]:
    """Return a compact signature tuple for a parameter.

    Returns a tuple of the form ("name=", "<description>") where the
    description is derived from `str(param)` and normalised to show default
    values as `Default=...`.
    """
    desc = str(param)
    if desc.startswith(param.name):
        desc = desc[len(param.name) :].lstrip()
    desc = desc.replace(": ", "").replace("= ", "=").replace("=", "Default=")
    return (f"{param.name}=", desc)


def decode_params(previous_params: list[str]):
    """Decode a flattened list of args where `a = b` may have been split.

    Example: ["a", "=", "b", "c"] -> ["a=b", "c"].
    """
    previous_args = []
    i = 0
    while i < len(previous_params):
        if i + 1 < len(previous_params) and previous_params[i + 1] == "=":
            previous_args.append(previous_params[i] + "=" + previous_params[i + 2])
            i += 3
            continue
        previous_args.append(previous_params[i])
        i += 1
    return previous_args


def complete_commands(ctx, incomplete: str):
    """Provide completion candidates for the current command context.

    Given a `ctx` (containing a `commands` iterable) and the current
    `incomplete` token, return either matching command names + docs or
    parameter signature completions for the last command.
    """
    previous_params = decode_params(list(ctx.params["args"]))
    if not previous_params:
        return all_commands_for_help(incomplete)
    try:
        commands = parse_args(previous_params)
        if not commands:
            return all_commands_for_help(incomplete)
    except Exception:
        return all_commands_for_help(incomplete)
    last_command = commands[-1]
    sig = inspect.signature(last_command[0])
    params_missing: list[Any] = []
    for i, p in enumerate(sig.parameters.values()):
        if i < len(last_command[1]):
            continue
        if p.name in last_command[2]:
            continue
        params_missing.append(p)

    if (
        not params_missing
        or params_missing[0].kind == inspect.Parameter.VAR_POSITIONAL
        or params_missing[0].kind == inspect.Parameter.VAR_KEYWORD
    ):
        return all_commands_for_help(incomplete)
    return [format_parameter_signature(p) for p in params_missing]


def get_command_information(commands: Callable) -> tuple[str, str, dict[str, str]]:
    """Get the command signature, docstring, and parameter docs for a command."""
    sig = inspect.signature(commands)
    command_signature = f"{commands.__name__}{sig}"
    command_doc = commands.__doc__ or ""
    param_docs: dict[str, str] = {}
    for param in sig.parameters.values():
        _, desc = format_parameter_signature(param)
        param_docs[param.name] = desc
        # desc = (param.annotation.__doc__ or "").strip() if hasattr(param.annotation, "__doc__") else ""
    return command_signature, command_doc.strip(), param_docs


def print_help(console):
    """Display custom help message listing available commands."""
    console.print("[bold cyan]dopy[/bold cyan] - A simple task runner")
    console.print()
    console.print("[bold]Usage:[/bold]")
    console.print("\tdopy <command> [args...] (Repeat)")
    console.print("\tAdd ... param=value ... for defining command arguments by name.")
    console.print()
    console.print("[bold]Available commands:[/bold]")
    commands = all_commands_for_help("")
    if commands:
        for name, doc in commands:
            doc_str = f" - {doc}" if doc else ""
            console.print(f"\t{name}{doc_str}")
    else:
        console.print("  (No commands available)")
    console.print()


def print_command_help(commands, console):
    command_signature, command_doc, param_docs = get_command_information(commands)
    console.print(f"[bold cyan]{command_signature}[/bold cyan]")
    console.print()
    if command_doc:
        console.print(command_doc)
        console.print()
    if param_docs:
        console.print("[bold]Parameters:[/bold]")
        for name, doc in param_docs.items():
            doc_str = f": {doc}" if doc else ""
            console.print(f"\t{name}{doc_str}")
        console.print()


def print_commands_help(commands, console):
    print("----------------------")
    for command in set([cmd[0] for cmd in commands]):
        print_command_help(command, console)
        print("----------------------")
    return
