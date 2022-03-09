import logging
import os

import pytest
from prefect import flow

from prefect_shell.commands import shell_run_command


def test_shell_run_command_error():
    @flow
    def test_flow():
        return shell_run_command(command="ls this/is/invalid")

    with pytest.raises(RuntimeError):
        test_flow().result(raise_on_failure=True)


def test_shell_run_command():
    @flow
    def test_flow():
        return shell_run_command(command="echo work!")

    assert test_flow().result().result() == "work!"


def test_shell_run_command_stream_level(caplog):
    @flow
    def test_flow():
        return shell_run_command(
            command="echo work!",
            stream_level=logging.WARNING,
        )

    test_flow()
    for record in caplog.records:
        assert record.levelname == "DEBUG"


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
