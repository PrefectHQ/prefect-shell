# prefect-shell

<p align="center">
    <a href="https://pypi.python.org/pypi/prefect-shell/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/prefect-shell?color=0052FF&labelColor=090422"></a>
    <a href="https://github.com/PrefectHQ/prefect-shell/" alt="Stars">
        <img src="https://img.shields.io/github/stars/PrefectHQ/prefect-shell?color=0052FF&labelColor=090422" /></a>
    <a href="https://pepy.tech/badge/prefect-shell/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/prefect-shell?color=0052FF&labelColor=090422" /></a>
    <a href="https://github.com/PrefectHQ/prefect-shell/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/PrefectHQ/prefect-shell?color=0052FF&labelColor=090422" /></a>
    <br>
    <a href="https://prefect-shell-community.slack.com" alt="Slack">
        <img src="https://img.shields.io/badge/slack-join_community-red.svg?color=0052FF&labelColor=090422&logo=slack" /></a>
    <a href="https://discourse.prefect-shell.io/" alt="Discourse">
        <img src="https://img.shields.io/badge/discourse-browse_forum-red.svg?color=0052FF&labelColor=090422&logo=discourse" /></a>
</p>


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

Then, register to [view the block](https://orion-docs.prefect.io/ui/blocks/) on Prefect Cloud:

```bash
prefect block register -m prefect_shell.credentials
```

Note, to use the `load` method on Blocks, you must already have a block document [saved through code](https://orion-docs.prefect.io/concepts/blocks/#saving-blocks) or [saved through the UI](https://orion-docs.prefect.io/ui/blocks/).

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

Feel free to star or watch [`prefect-shell`](https://github.com/PrefectHQ/prefect-shell) for updates too!

## Development

If you'd like to install a version of `prefect-shell` for development, clone the repository and perform an editable install with `pip`:

```bash
git clone https://github.com/PrefectHQ/prefect-shell.git

cd prefect-shell/

pip install -e ".[dev]"

# Install linting pre-commit hooks
pre-commit install
```
