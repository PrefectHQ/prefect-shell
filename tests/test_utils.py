import logging

from prefect_shell.utils import shell_run_command


async def test_shell_run_command_stream_level(caplog):
    logger = logging.getLogger("prefect")
    logger.propagate = True  # required for caplog
    await shell_run_command(
        command="echo work!", stream_level=logging.WARNING, logger=logger
    )
    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == "WARNING"


async def test_shell_run_command_without_logger_still_logs(caplog):
    caplog.set_level(logging.INFO)
    await shell_run_command(command="echo 1; echo 2")
    await shell_run_command(command="echo 3")
    records = caplog.records
    assert len(records) == 2
    for i, record in enumerate(records):
        assert record.levelname == "INFO"
        if i == 0:
            assert record.message == "1\n2\n"
        else:
            assert record.message == "3\n"
