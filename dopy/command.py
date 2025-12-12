from typing import ParamSpec, TypeVar
from collections.abc import Callable
from functools import wraps
import os

P = ParamSpec("P")
R = TypeVar("R")

COMMANDS = {}


def _make_decorator(factory):
    """Return a decorator that registers wrapped functions into `COMMANDS`.

    `factory` is a callable that takes the original function and returns
    the wrapper to be used at runtime. This makes it easy to create new
    decorators that both wrap behavior and register the result.
    """

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
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


@dopy_command
def sh(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        command = func(*args, **kwargs)
        if os.system(command) > 0:
            raise RuntimeError(f"Shell command failed: {command}")
        return command

    return wrapper


@dopy_command
def echo(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        result = func(*args, **kwargs)
        print(result)
        return result

    return wrapper
