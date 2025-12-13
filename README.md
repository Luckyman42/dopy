DoPy — Do Python! (task runner)
================================
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Overview
--------
DoPy is a small, Python-based task runner that lets you define project-specific or global tasks as Python functions in a `do.py` file. Tasks are registered with simple decorators and executed from a lightweight CLI. The tool is intended as a flexible alternative to Makefiles where full Python logic is helpful.

Key features
------------
- Define tasks as Python functions and register them using decorators (`@command`, `@sh`, `@echo`).
- Supports both project-local `do.py` and global defaults loaded from `DOPY_HOME` (default: `~/.dopy`). The project-local `do.py` always overrides global defaults when names conflict.
- Convenient `key=value` argument passing that is available to all tasks in the same run.
- Basic type conversion using Python annotations: `int`, `float`, `bool`, `pathlib.Path`, `datetime.datetime`.
- Support for `list[T]` and `set[T]` parameters: pass a single comma-separated string and it will be split and element-wise converted when possible.

Why use DoPy
------------
- Replace repeated Makefile fragments with reusable Python tasks.
- Keep shared, personal tasks in `DOPY_HOME` and project-specific tasks next to each project.
- Run arbitrary Python logic as part of your tasks (complex setup, dynamic inputs, custom validation).

Installation
------------
For development, install in editable mode from the repository root:

```bash
python3 -m pip install -e .
```

For usage, install the whl file via pip

> You avoid the only pipx installation because if you want to use it,
> you need to import the dopy module 

Basic usage
-----------
Create a `do.py` in the project root. Example:

```python
from dopy import command, sh, echo

@command
def hello(name: str):
    print(f"Hello {name}")

@echo
def hello_echo():
    return "Hello, World!"

@sh
def hello_sh():
    return "echo hello_from_sh"

```

Run tasks with the `dopy` CLI. `key=value` pairs are collected and provided to tasks in the run:

```bash
$ dopy hello_echo hello_sh
>Hello, World!
>hello_from_sh
$ dopy hello Pami
> Hello Pami
$ dopy name=pami hello  
> Hello Pami
$ dopy name=pami hello Lucky 
> Hello Lucky # positional argument 'Lucky' overrides name from kwargs for that positional parameter

$ dopy 
# print help for the available commands

$ dopy {command} --help
# print help for the {command}
```

Argument parsing and types
--------------------------
- All `key=value` pairs passed on the command line for a run are collected and available to every task executed in that run.
- If a task function has parameter annotations, DoPy attempts to convert string inputs to the annotated type. Supported conversions include:
  - `int`, `float`, `bool`
  - `pathlib.Path`
  - `datetime.datetime` (ISO format or common date/time patterns)
  - `list[T]` and `set[T]`: the CLI accepts a single comma-separated string (e.g. `"a,b,c"`) which is split and each element is converted to `T` where possible. If conversion of an element fails, the raw string is kept.

Important behavior
------------------
- If you provide a positional argument for a parameter, that positional value takes precedence and will not be replaced by a `key=value` of the same name (avoids duplicate argument errors).
- If a conversion fails, DoPy leaves the original string value — it will not raise an error during parsing.

Examples
--------
- Pass a list of tags to a task:

```bash
dopy tags "alpha,beta,gamma"
```

- Use a global default defined in `~/.dopy/do.py` (for example a standard `podman build` recipe) and override locally where necessary.

