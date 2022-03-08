import os
import tempfile
import logging
import sys
from subprocess import PIPE, STDOUT, Popen
from typing import Any, List, Union, Optional

from prefect import task
from prefect.logging import get_run_logger


@task
def shell_run_command(
    command: str = None,
    env: dict = None,
    helper_script: str = None,
    shell: str = "bash",
    return_all: bool = False,
    log_stderr: bool = False,
    stream_output: Union[bool, int, str] = False,
):
    """
    Task for running arbitrary shell commands.

    NOTE: This task combines stderr and stdout because reading from both
          streams without blocking is tricky.

    Args:
        command: shell command to be executed; can also be
            provided post-initialization by calling this task instance
        env (dict, optional): dictionary of environment variables to use for
            the subprocess; can also be provided at runtime
        helper_script (str, optional): a string representing a shell script, which
            will be executed prior to the `command` in the same process. Can be used to
            change directories, define helper functions, etc. when re-using this Task
            for different commands in a Flow; can also be provided at runtime
        shell: shell to run the command with; defaults to "bash"
        return_all: boolean specifying whether this task
            should return all lines of stdout as a list, or just the last line
            as a string; defaults to `False`
        log_stderr: boolean specifying whether this task should log
            the output in the case of a non-zero exit code; defaults to `False`. This
             actually logs both stderr and stdout and will only log the last line of
             output unless `return_all` is `True`
        stream_output: specifies whether this task should log
            the output as it occurs, and at what logging level. If `True` is passed,
            the logging level defaults to `INFO`; otherwise, any integer or string
            value that's passed will be treated as the log level, provided
            the `logging` library can successfully interpret it. If enabled,
            `log_stderr` will be ignored as the output will have already been
            logged. defaults to `False`

    Raises:
        TypeError: if `stream_output` is passed in as a string, but cannot
          successfully be converted to a numeric value by logging.getLevelName()

    Example:
        ```python
        from prefect import flow
        ```
    """
    logger = get_run_logger()

    current_env = os.environ.copy()
    current_env.update(env or {})

    with tempfile.NamedTemporaryFile(prefix="prefect-") as tmp:
        if helper_script:
            tmp.write(helper_script.encode())
            tmp.write(os.linesep.encode())
        tmp.write(command.encode())
        tmp.flush()
        with Popen(
            [shell, tmp.name],
            stdout=PIPE,
            stderr=STDOUT,
            env=current_env,
            # Windows does not use the PATH during subprocess creation
            # by default so we will use `shell` mode to do so
            shell=sys.platform == "win32",
        ) as sub_process:
            line = None
            lines = []
            for raw_line in iter(sub_process.stdout.readline, b""):
                line = raw_line.decode("utf-8").rstrip()

                if return_all:
                    lines.append(line)

                if stream_output:
                    logger.log(level=stream_output, msg=line)

            sub_process.wait()
            if sub_process.returncode:
                if log_stderr and not stream_output:
                    logger.exception("\n".join(lines) if return_all else line)
                msg = "Command failed with exit code {}".format(
                    sub_process.returncode,
                )
                raise RuntimeError(msg)

    return lines if return_all else line
