# NERV Local Launcher

## Created

- Added `nerv/scripts/start-nerv.ps1` for local one-command startup.
- Reuses a healthy local NERV instance instead of starting a duplicate server.
- Waits for `/health` before opening the dashboard in the default browser.
- Writes launcher stdout and stderr to ignored runtime log files.
- Supports `SYZYGY_NERV_PYTHON_EXECUTABLE` to select a known-good Python runtime.

## Scope Boundary

The launcher remains local-only. It does not publish NERV, expose local
operations to GitHub, register system startup tasks, or repair Python
installations automatically.

## Validation

- PowerShell parser validation covers the launcher syntax.
- `git diff --check` passed.
- NERV Python tests continue to rely on the GitHub Actions environment while
  the current local `.venv` base interpreter remains unusable.
