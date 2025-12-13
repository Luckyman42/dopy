from typing import ParamSpec, TypeVar
from collections.abc import Callable
from functools import wraps
import os

P = ParamSpec("P")
R = TypeVar("R")

COMMANDS = {}


def _make_decorator(factory):
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        wrapper = factory(func)
        COMMANDS[func.__name__] = wrapper
        return wrapper

    return decorator


def dopy_command(factory):
    """Decorator to convert a factory function into a registered decorator.

    Usage:

    @dopy_command
    def sh_factory(func):
        def wrapper(...):
            ...
        return wrapper

    After decoration, `sh_factory` becomes a decorator named `sh_factory`.
    """
    return _make_decorator(factory)


@dopy_command
def command(func: Callable[P, R]) -> Callable[P, R]:
    """Basic command decorator that registers the function as a command."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


@dopy_command
def sh(func: Callable[P, str]) -> Callable[P, str]:
    """Execute the returned string as a shell command.

    The wrapped function should return a shell command string. The
    wrapper runs it via `os.system` and raises `RuntimeError` if the
    command exits with a non-zero status.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
        command: str = func(*args, **kwargs)
        if os.system(str(command)) > 0:
            raise RuntimeError(f"Shell command failed: {command}")
        return command

    return wrapper


@dopy_command
def echo(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator that prints the wrapped function's result to stdout.

    Useful for simple CLI helpers that should both display and return
    their result.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        result = func(*args, **kwargs)
        print(result)
        return result

    return wrapper
