# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Deprecated

### Removed

### Fixed

### Security

## 0.1.5

Released on February 17, 2023.

### Changed
- Change the behavior of the `ShellOperation` `stream_output` parameter. Setting it to `False` will now only turn off the logging and not send `stdout` and `stderr` to `DEVNULL`. The previous behavior can be achieved by manually setting `stdout`/`stderr` to `DEVNULL` through the `open_kwargs` arguments. - [#67](https://github.com/PrefectHQ/prefect-shell/issues/67)

### Fixed
- Using `ShellOperation` on Windows - [#70](https://github.com/PrefectHQ/prefect-shell/issues/70)

## 0.1.4

Released on February 2nd, 2023.

### Added

- `ShellOperation` job block - [#55](https://github.com/PrefectHQ/prefect-shell/pull/55)

### Fixed

- If using PowerShell, set exit code to that of command - [#51](https://github.com/PrefectHQ/prefect-shell/pull/51)

## 0.1.3

Released on October 26th, 2022.

### Added

- Added `cwd` keyword argument in `shell_run_command` - [#41](https://github.com/PrefectHQ/prefect-shell/pull/41)

### Changed
- Have `shell_run_command` default to `shell="powershell" if sys.platform == "win32" else "bash"` - [#47](https://github.com/PrefectHQ/prefect-shell/pull/47)

## 0.1.2

Released on October 7th, 2022.

### Added

- Added `extension` keyword argument in `shell_run_command` - [#37](https://github.com/PrefectHQ/prefect-shell/pull/37)

### Fixed

- Use current environment in `shell_run_command` - [#28](https://github.com/PrefectHQ/prefect-shell/pull/28)
- Using `shell_run_command` on Windows environment - [#37](https://github.com/PrefectHQ/prefect-shell/pull/37)

## 0.1.1

Released on August 2nd, 2022.

### Changed

- Improve error visibility on failure - [#17](https://github.com/PrefectHQ/prefect-shell/pull/17)
- Updated tests to be compatible with core Prefect library (v2.0b9) and bumped required version - [#21](https://github.com/PrefectHQ/prefect-shell/pull/21)

### Fixed
- Fixed running commands that do not return any output - [#23](https://github.com/PrefectHQ/prefect-shell/pull/23)

### Removed
- Removed `utils.run_shell_command`; can be accessed using `commands.run_shell_command.fn` - [#19](https://github.com/PrefectHQ/prefect-shell/pull/19)

## 0.1.0

Released on March 9th, 2022.

### Added

- `shell_run_command` task and utility - [#1](https://github.com/PrefectHQ/prefect-shell/pull/1)
