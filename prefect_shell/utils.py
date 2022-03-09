"""Utils for interacting with shell commands"""

import logging
import os
import sys
import tempfile
from multiprocessing import get_logger
from typing import List, Optional, Union

from anyio import open_process
from anyio.streams.text import TextReceiveStream


async def shell_run_command(
    command: str,
    env: Optional[dict] = None,
    helper_command: Optional[str] = None,
    shell: str = "bash",
    return_all: bool = False,
    stream_level: int = logging.INFO,
    logger: Optional[logging.Logger] = None,
) -> Union[List, str]:
    """
    Runs arbitrary shell commands as a util.

    Args:
        command: Shell command to be executed; can also be
            provided post-initialization by calling this task instance.
        env: Dictionary of environment variables to use for
            the subprocess; can also be provided at runtime.
        helper_command: String representing a shell command, which
            will be executed prior to the `command` in the same process.
            Can be used to change directories, define helper functions, etc.
            for different commands in a flow.
        shell: Shell to run the command with; defaults to "bash".
        return_all: Whether this task should return all lines of stdout as a list,
            or just the last line as a string; defaults to `False`.
        stream_level: The logging level of the stream.
        logger: Can pass a desired logger; if not passed, will automatically
            get a logger from Prefect.

    Returns:
        If return all, returns all lines as a list; else the last line as a string.

    Example:
        Echo "hey it works".
        ```python
        from prefect_shell.utils import shell_run_command
        await shell_run_command("echo hey it works")
        ```
    """
    logger = logger or get_logger()

    current_env = os.environ.copy()
    current_env.update(env or {})

    with tempfile.NamedTemporaryFile(prefix="prefect-") as tmp:
        if helper_command:
            tmp.write(helper_command.encode())
            tmp.write(os.linesep.encode())
        tmp.write(command.encode())
        tmp.flush()

        shell_command = [shell, tmp.name]
        if sys.platform == "win32":
            shell_command = " ".join(shell_command)

        lines = []
        async with await open_process(shell_command, env=env) as process:
            async for text in TextReceiveStream(process.stdout):
                logger.log(level=stream_level, msg=text)
                lines.extend(text.rstrip().split("\n"))

            await process.wait()
            if process.returncode:
                stderr = "\n".join(
                    [text async for text in TextReceiveStream(process.stderr)]
                )
                logger.error(stderr)
                msg = f"Command failed with exit code {process.returncode}"
                raise RuntimeError(msg)

    return lines if return_all else lines[-1]
