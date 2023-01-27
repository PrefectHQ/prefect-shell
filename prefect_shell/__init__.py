from . import _version
from .commands import shell_run_command, ShellCommand  # noqa

__version__ = _version.get_versions()["version"]
