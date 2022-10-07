import logging
import os
import sys

import pytest
from prefect import flow

from prefect_shell.commands import shell_run_command


@pytest.mark.skipif(sys.platform == "win32", reason="see test_commands_windows.py")
def test_shell_run_command_error(prefect_task_runs_caplog):
    @flow
    def test_flow():
        return shell_run_command(command="ls this/is/invalid")

    match = "No such file or directory"
    with pytest.raises(RuntimeError, match=match):
        test_flow()

    assert len(prefect_task_runs_caplog.records) == 0


@pytest.mark.skipif(sys.platform == "win32", reason="see test_commands_windows.py")
def test_shell_run_command(prefect_task_runs_caplog):
    prefect_task_runs_caplog.set_level(logging.INFO)
    echo_msg = "_THIS_ IS WORKING!!!!"

    @flow
    def test_flow():
        return shell_run_command(command=f"echo {echo_msg}")

    assert test_flow() == echo_msg
    assert echo_msg in prefect_task_runs_caplog.text


@pytest.mark.skipif(sys.platform == "win32", reason="see test_commands_windows.py")
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


@pytest.mark.skipif(sys.platform == "win32", reason="see test_commands_windows.py")
def test_shell_run_command_helper_command():
    @flow
    def test_flow():
        return shell_run_command(command="pwd", helper_command="cd $HOME")

    assert test_flow() == os.path.expandvars("$HOME")


@pytest.mark.skipif(sys.platform == "win32", reason="see test_commands_windows.py")
def test_shell_run_command_return_all():
    @flow
    def test_flow():
        return shell_run_command(command="echo work! && echo yes!", return_all=True)

    assert test_flow() == ["work!", "yes!"]


@pytest.mark.skipif(sys.platform == "win32", reason="see test_commands_windows.py")
def test_shell_run_command_no_output():
    @flow
    def test_flow():
        return shell_run_command(command="sleep 1")

    assert test_flow() == ""


@pytest.mark.skipif(sys.platform == "win32", reason="see test_commands_windows.py")
def test_shell_run_command_uses_current_env():
    @flow
    def test_flow():
        return shell_run_command(command="echo $HOME")

    assert test_flow() == os.environ["HOME"]


@pytest.mark.skipif(sys.platform == "win32", reason="see test_commands_windows.py")
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
