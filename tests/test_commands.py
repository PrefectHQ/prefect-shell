import logging
import os
import sys
from pathlib import Path

import pytest
from prefect import flow
from prefect.testing.utilities import AsyncMock

from prefect_shell.commands import ShellOperation, shell_run_command

if sys.platform == "win32":
    pytest.skip(reason="see test_commands_windows.py", allow_module_level=True)


def test_shell_run_command_error(prefect_task_runs_caplog):
    @flow
    def test_flow():
        return shell_run_command(command="ls this/is/invalid")

    match = "No such file or directory"
    with pytest.raises(RuntimeError, match=match):
        test_flow()

    assert len(prefect_task_runs_caplog.records) == 7


def test_shell_run_command(prefect_task_runs_caplog):
    prefect_task_runs_caplog.set_level(logging.INFO)
    echo_msg = "_THIS_ IS WORKING!!!!"

    @flow
    def test_flow():
        return shell_run_command(command=f"echo {echo_msg}")

    assert test_flow() == echo_msg
    assert echo_msg in prefect_task_runs_caplog.text


def test_shell_run_command_stream_level(prefect_task_runs_caplog):
    prefect_task_runs_caplog.set_level(logging.WARNING)
    echo_msg = "_THIS_ IS WORKING!!!!"

    @flow
    def test_flow():
        return shell_run_command(
            command=f"echo {echo_msg}",
            stream_level=logging.WARNING,
        )

    assert test_flow() == echo_msg
    assert echo_msg in prefect_task_runs_caplog.text


def test_shell_run_command_helper_command():
    @flow
    def test_flow():
        return shell_run_command(command="pwd", helper_command="cd $HOME")

    assert test_flow() == os.path.expandvars("$HOME")


def test_shell_run_command_cwd():
    @flow
    def test_flow():
        return shell_run_command(command="pwd", cwd=Path.home())

    assert test_flow() == os.fspath(Path.home())


def test_shell_run_command_return_all():
    @flow
    def test_flow():
        return shell_run_command(command="echo work! && echo yes!", return_all=True)

    assert test_flow() == ["work!", "yes!"]


def test_shell_run_command_no_output():
    @flow
    def test_flow():
        return shell_run_command(command="sleep 1")

    assert test_flow() == ""


def test_shell_run_command_uses_current_env():
    @flow
    def test_flow():
        return shell_run_command(command="echo $HOME")

    assert test_flow() == os.environ["HOME"]


def test_shell_run_command_update_current_env():
    @flow
    def test_flow():
        return shell_run_command(
            command="echo $HOME && echo $TEST_VAR",
            env={"TEST_VAR": "test value"},
            return_all=True,
        )

    result = test_flow()
    assert result[0] == os.environ["HOME"]
    assert result[1] == "test value"


class AsyncIter:
    def __init__(self, items):
        self.items = items

    async def __aiter__(self):
        for item in self.items:
            yield item


@pytest.mark.parametrize("shell", [None, "bash", "zsh"])
def test_shell_run_command_override_shell(shell, monkeypatch):
    open_process_mock = AsyncMock()
    stdout_mock = AsyncMock()
    stdout_mock.receive.side_effect = lambda: b"received"
    open_process_mock.return_value.__aenter__.return_value = AsyncMock(
        stdout=stdout_mock
    )
    open_process_mock.return_value.__aenter__.return_value.returncode = 0
    monkeypatch.setattr("anyio.open_process", open_process_mock)
    monkeypatch.setattr("prefect_shell.commands.TextReceiveStream", AsyncIter)

    @flow
    def test_flow():
        return shell_run_command(
            command="echo 'testing'",
            shell=shell,
        )

    test_flow()
    assert open_process_mock.call_args_list[0][0][0][0] == shell or "bash"


class TestShellOperation:
    def test_run_error(self):
        with ShellOperation(commands=["ls this/is/invalid"]) as op:
            with pytest.raises(RuntimeError, match="return code"):
                op.run()

    def test_run_output(self, prefect_task_runs_caplog):
        with ShellOperation(commands=["echo 'testing\nthe output'", "echo good"]) as op:
            assert op.run() == ["testing", "the output", "good"]
        records = prefect_task_runs_caplog.records
        assert len(records) == 4
        assert "triggered with 2 commands running" in records[0].message
        assert "stream output:\ntesting\nthe output\ngood" in records[1].message
        assert "completed with return code 0" in records[2].message
        assert "closed all open processes" in records[3].message

    def test_current_env(self):
        with ShellOperation(commands=["echo $HOME"]) as op:
            assert op.run() == [os.environ["HOME"]]

    def test_updated_env(self):
        with ShellOperation(commands=["echo $HOME"]) as op:
            op = ShellOperation(env={"HOME": "test_home"})
            assert op.run() == ["test_home"]

    def test_cwd(self):
        with ShellOperation(commands=["pwd"], working_dir=Path.home()) as op:
            assert op.run() == [os.fspath(Path.home())]

    @pytest.mark.parametrize("shell", [None, "bash", "zsh"])
    def test_updated_shell(self, monkeypatch, shell):
        open_process_mock = AsyncMock(name="open_process")
        stdout_mock = AsyncMock(name="stdout_mock")
        stdout_mock.receive.side_effect = lambda: b"received"
        open_process_mock.return_value.__aenter__.return_value = AsyncMock(
            stdout=stdout_mock
        )
        open_process_mock.return_value.returncode = 0
        monkeypatch.setattr("anyio.open_process", open_process_mock)
        monkeypatch.setattr("prefect_shell.commands.TextReceiveStream", AsyncIter)

        with ShellOperation(commands=["pwd"], working_dir=Path.home()) as op:
            op.run(shell=shell)

        assert open_process_mock.call_args_list[0][0][0][0] == shell or "bash"
