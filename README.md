# prefect-shell

## Welcome!

`prefect-shell` is a collection of prebuilt Prefect tasks that can be used to quickly construct Prefect flows.

## Getting Started

### Python setup

Requires an installation of Python 3.7+.

We recommend using a Python virtual environment manager such as pipenv, conda or virtualenv.

These tasks are designed to work with Prefect 2.0. For more information about how to use Prefect, please refer to the [Prefect documentation](https://orion-docs.prefect.io/).

### Installation

Install `prefect-shell` with `pip`:

```bash
pip install prefect-shell
```

### Write and run a flow

```python
from prefect import flow
from prefect_shell import shell_run_command

@flow
def example_shell_run_command_flow():
    return shell_run_command(command="ls .", return_all=True)

example_shell_run_command_flow()
```

## Resources

If you encounter and bugs while using `prefect-shell`, feel free to open an issue in the [prefect-shell](https://github.com/PrefectHQ/prefect-shell) repository.

If you have any questions or issues while using `prefect-shell`, you can find help in either the [Prefect Discourse forum](https://discourse.prefect.io/) or the [Prefect Slack community](https://prefect.io/slack).

## Development

If you'd like to install a version of `prefect-shell` for development, clone the repository and perform an editable install with `pip`:

```bash
git clone https://github.com/PrefectHQ/prefect-shell.git

cd prefect-shell/

pip install -e ".[dev]"

# Install linting pre-commit hooks
pre-commit install
```
