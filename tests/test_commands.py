import logging
import os

import pytest
from prefect import flow

from prefect_shell.commands import shell_run_command


@pytest.fixture
def prefect_caplog(caplog):
    logger = logging.getLogger("prefect")

    # TODO: Determine a better pattern for this and expose for all tests
    logger.propagate = True

    try:
        yield caplog
    finally:
        logger.propagate = False


@pytest.fixture
def prefect_task_runs_caplog(prefect_caplog):
    logger = logging.getLogger("prefect.task_runs")

    # TODO: Determine a better pattern for this and expose for all tests
    logger.propagate = True

    try:
        yield prefect_caplog
    finally:
        logger.propagate = False


def test_shell_run_command_error(prefect_task_runs_caplog):
    @flow
    def test_flow():
        return shell_run_command(command="ls this/is/invalid")

    match = "No such file or directory"
    with pytest.raises(RuntimeError, match=match):
        test_flow().result(raise_on_failure=True)

    assert len(prefect_task_runs_caplog.records) == 0


def test_shell_run_command(prefect_task_runs_caplog):
    prefect_task_runs_caplog.set_level(logging.INFO)
    echo_msg = "_THIS_ IS WORKING!!!!"

    @flow
    def test_flow():
        return shell_run_command(command=f"echo {echo_msg}")

    assert test_flow().result().result() == echo_msg
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

    assert test_flow().result().result() == echo_msg
    assert echo_msg in prefect_task_runs_caplog.text


def test_shell_run_command_helper_command():
    @flow
    def test_flow():
        return shell_run_command(command="pwd", helper_command="cd $HOME")

    assert test_flow().result().result() == os.path.expandvars("$HOME")


def test_shell_run_command_return_all():
    @flow
    def test_flow():
        return shell_run_command(command="echo work! && echo yes!", return_all=True)

    assert test_flow().result().result() == ["work!", "yes!"]
