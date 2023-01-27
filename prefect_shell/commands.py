"""Tasks for interacting with shell commands"""

import asyncio
import logging
import os
import shlex
import subprocess
import sys
import tempfile
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional, Union

import anyio
from anyio.abc import Process
from anyio.streams.text import TextReceiveStream
from prefect import task
from prefect.blocks.abstract import JobBlock, JobRun
from prefect.logging import get_run_logger
from prefect.utilities.asyncutils import sync_compatible
from prefect.utilities.processutils import open_process
from pydantic import DirectoryPath, Field, PrivateAttr


@task
async def shell_run_command(
    command: str,
    env: Optional[dict] = None,
    helper_command: Optional[str] = None,
    shell: Optional[str] = None,
    extension: Optional[str] = None,
    return_all: bool = False,
    stream_level: int = logging.INFO,
    cwd: Union[str, bytes, os.PathLike, None] = None,
) -> Union[List, str]:
    """
    Runs arbitrary shell commands.

    Args:
        command: Shell command to be executed; can also be
            provided post-initialization by calling this task instance.
        env: Dictionary of environment variables to use for
            the subprocess; can also be provided at runtime.
        helper_command: String representing a shell command, which
            will be executed prior to the `command` in the same process.
            Can be used to change directories, define helper functions, etc.
            for different commands in a flow.
        shell: Shell to run the command with.
        extension: File extension to be appended to the command to be executed.
        return_all: Whether this task should return all lines of stdout as a list,
            or just the last line as a string.
        stream_level: The logging level of the stream;
            defaults to 20 equivalent to `logging.INFO`.
        cwd: The working directory context the command will be executed within

    Returns:
        If return all, returns all lines as a list; else the last line as a string.

    Example:
        List contents in the current directory.
        ```python
        from prefect import flow
        from prefect_shell import shell_run_command

        @flow
        def example_shell_run_command_flow():
            return shell_run_command(command="ls .", return_all=True)

        example_shell_run_command_flow()
        ```
    """
    logger = get_run_logger()

    current_env = os.environ.copy()
    current_env.update(env or {})

    if shell is None:
        # if shell is not specified:
        # use powershell for windows
        # use bash for other platforms
        shell = "powershell" if sys.platform == "win32" else "bash"

    extension = ".ps1" if shell.lower() == "powershell" else extension

    tmp = tempfile.NamedTemporaryFile(prefix="prefect-", suffix=extension, delete=False)
    try:
        if helper_command:
            tmp.write(helper_command.encode())
            tmp.write(os.linesep.encode())
        tmp.write(command.encode())
        if shell.lower() == "powershell":
            # if powershell, set exit code to that of command
            tmp.write("\r\nExit $LastExitCode".encode())
        tmp.close()

        shell_command = [shell, tmp.name]

        lines = []
        async with await anyio.open_process(
            shell_command, env=current_env, cwd=cwd
        ) as process:
            async for text in TextReceiveStream(process.stdout):
                logger.log(level=stream_level, msg=text)
                lines.extend(text.rstrip().split("\n"))

            await process.wait()
            if process.returncode:
                stderr = "\n".join(
                    [text async for text in TextReceiveStream(process.stderr)]
                )
                if not stderr and lines:
                    stderr = f"{lines[-1]}\n"
                msg = (
                    f"Command failed with exit code {process.returncode}:\n" f"{stderr}"
                )
                raise RuntimeError(msg)
    finally:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)

    line = lines[-1] if lines else ""
    return lines if return_all else line


class ShellProcess(JobRun):
    """
    A class representing a run of a shell job.
    """

    def __init__(self, shell_operation: "ShellCommand", process: Process):
        self._shell_operation = shell_operation
        self._process = process
        self._output = []

    @property
    def pid(self) -> int:
        """
        The PID of the process.

        Returns:
            The PID of the process.
        """
        return self._process.pid

    @property
    def return_code(self) -> Optional[int]:
        """
        The return code of the process.

        Returns:
            The return code of the process, or `None` if the process is still running.
        """
        return self._process.returncode

    async def _capture_output(self, source):
        """
        Capture output from source.
        """
        async for text in TextReceiveStream(source):
            if self._shell_operation.stream_output:
                self.logger.info(text)
            self._output.append(text)

    @sync_compatible
    async def wait_for_completion(self):
        """
        Wait for the shell operation to complete.
        """
        try:
            self.logger.debug(f"Waiting for PID {self._process.pid} to complete.")
            await asyncio.gather(
                self._capture_output(self._process.stdout),
                self._capture_output(self._process.stderr),
            )
        finally:
            self.logger.info(
                f"PID {self._process.pid} completed with return code "
                f"{self._process.returncode}."
            )

    @sync_compatible
    async def fetch_result(self) -> List[str]:
        """
        Retrieve the results of the shell operation and return them.

        Returns:
            The lines output from the shell operation as a list.
        """
        return self._output


class ShellCommand(JobBlock):
    """
    A block representing a shell command.

    It is recommended to use this block as a context manager, which will automatically
    close all of its opened processes when the context is exited. If not, the user
    should call `close` to ensure all processes are closed.

    Attributes:
        command: The command to run.
        stream_output: Whether to stream output.
        env: Environment variables to use for the subprocess.
        working_dir: The working directory context the command will be executed within.

    Examples:
        Load a configured block:
        ```python
        from prefect_shell import ShellCommand

        shell_command = ShellCommand.load("BLOCK_NAME")
        ```
    """

    command: str = Field(default=..., description="The command to run.")
    stream_output: bool = Field(default=True, description="Whether to stream output.")
    env: Dict[str, str] = Field(
        default_factory=dict,
        title="Environment Variables",
        description="Environment variables to use for the subprocess.",
    )
    working_dir: DirectoryPath = Field(
        default=None,
        title="Working Directory",
        description=(
            "The working directory context the command will be executed within."
        ),
    )

    _exit_stack: AsyncExitStack = PrivateAttr(
        default_factory=AsyncExitStack,
    )

    @sync_compatible
    async def trigger(self, **open_kwargs: Dict[str, Any]) -> ShellProcess:
        """
        Triggers a shell operation and returns the shell operation run object
        to track the execution of the run. This method is ideal for long-lasting
        shell operations; for short-lasting shell operations, it is recommended
        to use `run` instead.

        Args:
            **open_kwargs: Additional keyword arguments to pass to `open_process`

        Returns:
            A `ShellProcess` object.
        """
        command_args = shlex.split(self.command)

        input_env = os.environ.copy()
        input_env.update(self.env)

        self.logger.debug("Preparing to execute {command_args} in {self.working_dir!r}")
        process = await self._exit_stack.enter_async_context(
            open_process(
                command_args,
                stdout=subprocess.PIPE if self.stream_output else subprocess.DEVNULL,
                stderr=subprocess.PIPE if self.stream_output else subprocess.DEVNULL,
                env=input_env,
                cwd=self.working_dir,
                **open_kwargs,
            )
        )
        self.logger.info(f"Opened PID {process.pid} for {self.command!r}.")
        return ShellProcess(shell_operation=self, process=process)

    @sync_compatible
    async def run(self, **open_kwargs: Dict[str, Any]) -> List[str]:
        """
        Triggers a shell operation, but unlike the trigger method,
        additionally waits and fetches the result. This is a convenience
        method for short-lasting shell operations.

        Args:
            **open_kwargs: Additional keyword arguments to pass to `open_process`

        Returns:
            The lines output from the shell operation as a list.
        """
        job_run = await self.trigger(**open_kwargs)
        await job_run.wait_for_completion()
        return await job_run.fetch_result()

    @sync_compatible
    async def close(self):
        """
        Close the job block.
        """
        await self._exit_stack.aclose()
        self.logger.info("Successfully closed all open processes.")

    async def aclose(self):
        """
        Asynchronous version of the close method.
        """
        await self.close()

    async def __aenter__(self) -> "ShellCommand":
        """
        Asynchronous version of the enter method.
        """
        return self

    async def __aexit__(self, *exc_info):
        """
        Asynchronous version of the exit method.
        """
        await self.close()

    def __enter__(self) -> "ShellCommand":
        """
        Enter the context of the job block.
        """
        return self

    def __exit__(self, *exc_info):
        """
        Exit the context of the job block.
        """
        self.close()
