from prefect import flow

from prefect_shell.tasks import (
    goodbye_prefect_shell,
    hello_prefect_shell,
)


def test_hello_prefect_shell():
    @flow
    def test_flow():
        return hello_prefect_shell()

    flow_state = test_flow()
    task_state = flow_state.result()
    assert task_state.result() == "Hello, prefect-shell!"


def goodbye_hello_prefect_shell():
    @flow
    def test_flow():
        return goodbye_prefect_shell()

    flow_state = test_flow()
    task_state = flow_state.result()
    assert task_state.result() == "Goodbye, prefect-shell!"
