"""This is an example flows module"""
from prefect import flow

from prefect_shell.tasks import (
    goodbye_prefect_shell,
    hello_prefect_shell,
)


@flow
def hello_and_goodbye():
    """
    Sample flow that says hello and goodbye!
    """
    print(hello_prefect_shell)
    print(goodbye_prefect_shell)
