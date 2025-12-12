from typing import Any
from collections.abc import Callable
from dopy.exception import CommandNotFoundException, InvalidCommandArgumentsException
from dopy.command import COMMANDS
import inspect
from typing import get_origin, get_args
import pathlib
import datetime


def complete_commands(incomplete: str):
    items = []
    for name, func in COMMANDS.items():
        if not name.startswith(incomplete):
            continue
        doc = (func.__doc__ or "").strip().split("\n")[0]
        if not doc:
            doc = ""
        completion_item = (name, doc)
        items.append(completion_item)
    return items


def get_command(name: str):
    comm = COMMANDS.get(name)
    if comm is None:
        raise CommandNotFoundException(f"Command '{name}' not found.")
    return comm


def execute_command(attr: Callable, *args, **kwargs) -> None:
    try:
        attr(*args, **kwargs)
    except TypeError as e:
        raise InvalidCommandArgumentsException(str(e))


def split_commands(args) -> list[tuple[str, list[str]]]:
    result = []
    current_cmd = None
    current_params: list[str] = []
    for arg in args:
        if arg in COMMANDS:
            if current_cmd:
                result.append((current_cmd, current_params))
            current_cmd = arg
            current_params = []
        elif current_cmd:
            current_params.append(arg)
        else:
            raise CommandNotFoundException(f"Command '{arg}' not found.")
    if current_cmd:
        result.append((current_cmd, current_params))
    return result


def _convert_value(value: str, annotation):
    if annotation is inspect._empty:
        return value
    # handle common builtins
    try:
        if annotation is bool:
            low = str(value).lower()
            if low in ("1", "true", "yes", "y", "on"):
                return True
            if low in ("0", "false", "no", "n", "off"):
                return False
            # fallback: raise to fallthrough
            raise ValueError()
        # pathlib.Path
        if annotation is pathlib.Path:
            return pathlib.Path(value)
        # datetime
        if annotation is datetime.datetime:
            # try common ISO formats
            try:
                return datetime.datetime.fromisoformat(value)
            except Exception:
                # fallback to parsing common formats
                from datetime import datetime as _dt

                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                    try:
                        return _dt.strptime(value, fmt)
                    except Exception:
                        continue
                # if all fail, fall through to generic conversion
        # list/set types (e.g. list[str], set[int], typing.List[str])
        origin = get_origin(annotation)
        if origin in (list, set):
            # split by comma into elements (empty string -> empty list)
            if value == "":
                elements = []
            else:
                elements = [s.strip() for s in value.split(",")]
            elem_type = None
            args = get_args(annotation)
            if args:
                elem_type = args[0]
            converted = []
            for el in elements:
                if elem_type:
                    try:
                        converted.append(_convert_value(el, elem_type))
                    except Exception:
                        converted.append(el)
                else:
                    converted.append(el)
            return set(converted) if origin is set else converted
        # For simple types like int, float, str
        return annotation(value)
    except Exception:
        # If conversion fails, return the original string
        return value


def resolve_arguments(
    fn: Callable, positional_args: list[str], passed_kwargs: dict[str, str]
):
    """Resolve positional and keyword arguments for `fn`, converting types
    based on annotations when available.

    `passed_kwargs` is a per-run dict parsed from `key=value` args.
    """
    sig = inspect.signature(fn)
    params = list(sig.parameters.values())

    # Convert positional args according to parameter annotations
    converted_pos = []
    for i, val in enumerate(positional_args):
        if i < len(params):
            ann = params[i].annotation
            converted_pos.append(_convert_value(val, ann))
        else:
            converted_pos.append(val)

    # If function accepts **kwargs, pass all passed_kwargs through (no annotation info)
    has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params)
    if has_var_kw:
        return converted_pos, dict(passed_kwargs)

    # Otherwise, map provided key-values into named parameters and convert types
    kw = {}
    # Determine which parameter names were already provided positionally
    positional_param_names = [p.name for p in params[: len(converted_pos)]]

    for name, p in sig.parameters.items():
        # Skip parameters already provided positionally
        if name in positional_param_names:
            continue
        if name in passed_kwargs:
            kw[name] = _convert_value(passed_kwargs[name], p.annotation)

    return converted_pos, kw


def parse_args(args: list[str]):
    commands: list[tuple[Callable, list[Any], dict[str, Any]]] = []
    params: list[str] = []
    local_kwargs: dict[str, str] = {}
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            local_kwargs[key] = value
        else:
            params.append(arg)

    functions = split_commands(params)
    for func_name, func_params in functions:
        func = get_command(func_name)
        pos_args, kw_args = resolve_arguments(func, func_params, local_kwargs)
        commands.append((func, pos_args, kw_args))
    return commands
