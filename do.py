from dopy import sh, command, echo
from textwrap import dedent
from functools import wraps

def uv(fun):
    """Decorator to mark a command as using 'uv'."""
    @wraps(fun)
    def wrapper(*args, **kwargs):
        return "uv run " + fun(*args, **kwargs)
    return wrapper

@sh
def build():
    """Build"""
    return "uv build"

@sh
@uv
def linter():
    """Run linter"""
    return "ruff check dopy"

@sh
@uv
def linter_fix():
    """Run linter"""
    return "ruff check dopy --fix"

@sh
@uv
def type_checker():
    """Run static type checker"""
    return "pyright "

@sh
@uv
def formatter():
    """Run formatter"""
    return "ruff format dopy"

@command
def lint_all(): 
    """Formatter + Linter + type_checker"""
    formatter()
    linter()
    type_checker()

@sh
@uv
def test(): 
    """Run tests"""
    return "pytest -q"

@sh
@uv
def coverage():
    """Run tests with coverage"""
    return "pytest --cov=dopy --cov-report=term-missing"

@sh
def install_dev_dependencies():
    """Install dependencies for developing the project"""
    return dedent("""pip install uv
	uv sync
	uv run pre-commit install""")
