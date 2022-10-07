import glob
import logging
import os
import sys

import pytest
from prefect import flow

from prefect_shell.commands import shell_run_command


@pytest.mark.skipif(sys.platform != "win32", reason="see test_commands.py")
def test_shell_run_command_error_windows(prefect_task_runs_caplog):
    @flow
    def test_flow():
        return shell_run_command(
            command="ls this/is/invalid", return_all=True, shell="powershell"
        )

    homedir = os.environ["USERPROFILE"]
    match = (
        f"ls : Cannot find path {homedir}\\this\\is\\invalid because it does not exist."
    )
    with pytest.raises(RuntimeError, match=match):
        test_flow()

    assert len(prefect_task_runs_caplog.records) == 0


@pytest.mark.skipif(sys.platform != "win32", reason="see test_commands.py")
def test_shell_run_command_windows(prefect_task_runs_caplog):
    prefect_task_runs_caplog.set_level(logging.INFO)
    echo_msg = "_THIS_ IS WORKING!!!!"

    @flow
    def test_flow():
        msg = shell_run_command(
            command=f"echo {echo_msg}", return_all=True, shell="powershell"
        )
        return " ".join(word.replace("\r", "") for word in msg)

    print(prefect_task_runs_caplog.text)

    assert test_flow() == echo_msg
    for record in prefect_task_runs_caplog.records:
        if echo_msg in record:
            break  # it's in the records
    else:
        raise AssertionError


@pytest.mark.skipif(sys.platform != "win32", reason="see test_commands.py")
def test_shell_run_command_stream_level_windows(prefect_task_runs_caplog):
    prefect_task_runs_caplog.set_level(logging.WARNING)
    echo_msg = "_THIS_ IS WORKING!!!!"

    @flow
    def test_flow():
        msg = shell_run_command(
            command=f"echo {echo_msg}",
            stream_level=logging.WARNING,
            return_all=True,
            shell="powershell",
        )
        return " ".join(word.replace("\r", "") for word in msg)

    print(prefect_task_runs_caplog.text)

    assert test_flow() == echo_msg
    assert echo_msg in prefect_task_runs_caplog.text.replace("\r\n\n", "").replace(
        "\r\n", " "
    )


@pytest.mark.skipif(sys.platform != "win32", reason="see test_commands.py")
def test_shell_run_command_helper_command_windows():
    @flow
    def test_flow():
        return shell_run_command(
            command="Get-Location",
            helper_command="cd $env:USERPROFILE",
            shell="powershell",
        )

    assert test_flow() == os.path.expandvars("$USERPROFILE")


@pytest.mark.skipif(sys.platform != "win32", reason="see test_commands.py")
def test_shell_run_command_return_all():
    @flow
    def test_flow():
        return shell_run_command(
            command="echo 'work!'; echo 'yes!'", return_all=True, shell="powershell"
        )

    result = test_flow()
    assert result[0].rstrip() == "work!"
    assert result[1].rstrip() == "yes!"


@pytest.mark.skipif(sys.platform != "win32", reason="see test_commands.py")
def test_shell_run_command_no_output_windows():
    @flow
    def test_flow():
        return shell_run_command(command="sleep 1", shell="powershell")

    assert test_flow() == ""


@pytest.mark.skipif(sys.platform != "win32", reason="see test_commands.py")
def test_shell_run_command_uses_current_env_windows():
    @flow
    def test_flow():
        return shell_run_command(
            command="echo $env:USERPROFILE", return_all=True, shell="powershell"
        )

    result = test_flow()
    assert result[0].rstrip() == os.environ["USERPROFILE"]


@pytest.mark.skipif(sys.platform != "win32", reason="see test_commands.py")
def test_shell_run_command_update_current_env_windows():
    @flow
    def test_flow():
        return shell_run_command(
            command="echo $env:USERPROFILE ; echo $env:TEST_VAR",
            helper_command="$env:TEST_VAR = 'test value'",
            env={"TEST_VAR": "test value"},
            return_all=True,
            shell="powershell",
        )

    result = test_flow()
    assert result[0] == os.environ["USERPROFILE"]
    assert result[1] == "test value"


@pytest.mark.skipif(sys.platform != "win32", reason="see test_commands.py")
def test_shell_run_command_ensure_suffix_ps1():
    @flow
    def test_flow():
        return shell_run_command(command="1 + 1", shell="powershell", extension=".zzz")

    result = test_flow()
    assert result == "2"


@pytest.mark.skipif(sys.platform != "win32", reason="see test_commands.py")
def test_shell_run_command_ensure_tmp_file_removed():
    @flow
    def test_flow():
        return shell_run_command(
            command="echo 'clean up after yourself!'", shell="powershell"
        )

    test_flow()
    temp_dir = os.environ["TEMP"]
    assert len(glob.glob(f"{temp_dir}\\prefect-*.ps1")) == 0
