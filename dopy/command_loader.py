import os
import importlib.util
from dopy.config import DOPY_HOME


def _load_module_from_path(path: str, module_name: str) -> None:
    """Load a module from a file path without relying on sys.path ordering.

    This ensures we can load a default `do.py` and then the current working
    directory's `do.py`, letting the latter override any registered commands.
    """
    if not os.path.exists(path):
        return
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        # We intentionally swallow errors during loading so the CLI can still run
        # even if a user's `do.py` has issues; Typer will report runtime errors.
        pass


def load_commands() -> None:
    """Load `do.py` from the DOPY_HOME (default) and then from cwd.

    The cwd version is loaded second so its command registrations override
    the defaults (if they share names).
    """
    default_path = os.path.join(DOPY_HOME, "do.py")
    _load_module_from_path(default_path, "do_default")

    cwd_path = os.path.join(os.getcwd(), "do.py")
    _load_module_from_path(cwd_path, "do")
