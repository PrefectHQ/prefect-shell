# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Changed
- Improve error visibility on failure - [#17](https://github.com/PrefectHQ/prefect_shell/pull/17
- Updated tests to be compatible with core Prefect library (v2.0b9) and bumped required version - [#20](https://github.com/PrefectHQ/prefect_shell/pull/20)

### Deprecated

### Removed
- Removed `utils.run_shell_command`; can be accessed using `commands.run_shell_command.fn` - [#19](https://github.com/PrefectHQ/prefect_shell/pull/19)

### Fixed

- If no logger is provided, actually get a Prefect run logger - [#18](https://github.com/PrefectHQ/prefect_shell/pull/18)

### Security

## 0.1.0

Released on March 9th, 2022.

### Added

- `shell_run_command` task and utility - [#1](https://github.com/PrefectHQ/prefect_shell/pull/1)

