# Integrating shell commands into your dataflow with `prefect-shell`

<p align="center">
    <img src="https://user-images.githubusercontent.com/15331990/216169092-20cc6e77-ee3b-4aef-a8e7-02747eb5a549.png">
    <br>
    <a href="https://pypi.python.org/pypi/prefect-shell/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/prefect-shell?color=0052FF&labelColor=090422"></a>
    <a href="https://github.com/PrefectHQ/prefect-shell/" alt="Stars">
        <img src="https://img.shields.io/github/stars/PrefectHQ/prefect-shell?color=0052FF&labelColor=090422" /></a>
    <a href="https://pepy.tech/badge/prefect-shell/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/prefect-shell?color=0052FF&labelColor=090422" /></a>
    <a href="https://github.com/PrefectHQ/prefect-shell/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/PrefectHQ/prefect-shell?color=0052FF&labelColor=090422" /></a>
    <br>
    <a href="https://prefect-community.slack.com" alt="Slack">
        <img src="https://img.shields.io/badge/slack-join_community-red.svg?color=0052FF&labelColor=090422&logo=slack" /></a>
    <a href="https://discourse.prefect.io/" alt="Discourse">
        <img src="https://img.shields.io/badge/discourse-browse_forum-red.svg?color=0052FF&labelColor=090422&logo=discourse" /></a>
</p>

Visit the full docs [here](https://PrefectHQ.github.io/prefect-shell) to see additional examples and the API reference.

The prefect-shell collection makes it easy to execute shell commands in your Prefect flows. Check out the examples below to get started!

## Getting Started

### Integrate with Prefect flows

With prefect-shell, you can bring your trusty shell commands (and/or scripts) straight into the Prefect flow party, complete with awesome Prefect logging.

No more separate logs, just seamless integration. Let's get the shell-abration started!

```python
from prefect import flow
from datetime import datetime
from prefect_shell import ShellOperation

@flow
def download_data():
    today = datetime.today().strftime("%Y%m%d")

    # for short running operations, you can use the `run` method
    # which automatically manages the context
    ShellOperation(
        commands=[
            "mkdir -p data",
            "mkdir -p data/${today}"
        ],
        env={"today": today}
    ).run()

    # for long running operations, you can use a context manager
    with ShellOperation(
        commands=[
            "cd data/${today}",
            "curl -O https://masie_web.apps.nsidc.org/pub/DATASETS/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv",
        ],
        env={"today": today}
    ) as download_csv_operation:

        # trigger runs the process in the background
        download_csv_process = download_csv_operation.trigger()

        # then do other things here in the meantime, like download another file
        ...

        # when you're ready, wait for the process to finish
        download_csv_process.wait_for_completion()

        # if you'd like to get the output lines, you can use the `fetch_result` method
        output_lines = download_csv_process.fetch_result()

download_data()
```

## Resources

For more tips on how to use tasks and flows in a Collection, check out [Using Collections](https://orion-docs.prefect.io/collections/usage/)!

### Installation

Install `prefect-shell` with `pip`:

```bash
pip install -U prefect-shell
```

A list of available blocks in `prefect-shell` and their setup instructions can be found [here](https://PrefectHQ.github.io/prefect-shell/blocks-catalog).

Requires an installation of Python 3.7+.

We recommend using a Python virtual environment manager such as pipenv, conda or virtualenv.

These tasks are designed to work with Prefect 2. For more information about how to use Prefect, please refer to the [Prefect documentation](https://orion-docs.prefect.io/).

### Feedback

If you encounter any bugs while using `prefect-shell`, feel free to open an issue in the [prefect-shell](https://github.com/PrefectHQ/prefect-shell) repository.

If you have any questions or issues while using `prefect-shell`, you can find help in either the [Prefect Discourse forum](https://discourse.prefect.io/) or the [Prefect Slack community](https://prefect.io/slack).

Feel free to star or watch [`prefect-shell`](https://github.com/PrefectHQ/prefect-shell) for updates too!
 
### Contributing
 
If you'd like to help contribute to fix an issue or add a feature to `prefect-shell`, please [propose changes through a pull request from a fork of the repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).
 
Here are the steps:

1. [Fork the repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository)
2. [Clone the forked repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository)
3. Install the repository and its dependencies:
```
pip install -e ".[dev]"
```
4. Make desired changes
5. Add tests
6. Insert an entry to [CHANGELOG.md](https://github.com/PrefectHQ/prefect-shell/blob/main/CHANGELOG.md)
7. Install `pre-commit` to perform quality checks prior to commit:
```
pre-commit install
```
8. `git commit`, `git push`, and create a pull request
