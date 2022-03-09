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
