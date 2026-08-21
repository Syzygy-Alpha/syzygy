# Sprint 004 - NERV Local Launcher

## Context

NERV is intentionally a local service because it controls processes and reads
local Forge project contracts. Its GitHub Actions workflow validates code, but
it cannot safely launch or operate the dashboard on the user's computer.

The remaining friction is starting NERV and opening its local URL manually.

## Sprint Goal

Provide a one-command Windows launcher that starts NERV and opens the local
dashboard when it is ready.

## In Scope

- PowerShell launcher for the local NERV server
- healthcheck wait before opening the browser
- reuse an already running NERV instance
- explicit runtime selection and local launcher logs
- documentation and activity log

## Out of Scope

- GitHub Pages or remote deployment
- remote control of local modules
- system startup registration or Task Scheduler changes
- a desktop package or tray application
- automatic Python installation or virtual environment repair

## Exit Criteria

- one PowerShell command starts NERV and opens its dashboard
- the launcher does not spawn a second server when NERV is already healthy
- startup failures point to local log files
