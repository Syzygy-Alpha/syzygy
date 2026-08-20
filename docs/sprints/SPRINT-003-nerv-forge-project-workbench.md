# Sprint 003 - NERV Forge Project Workbench

## Context

NERV already launches known module services and provides quick reads for their
most useful endpoints. Forge already has a mature local contract for registered
projects, declarative project commands, command planning, and confirmed
execution.

The next useful NERV increment is to make that existing Forge contract visible
and operable from the command center without giving NERV filesystem access or a
generic command runner.

## Sprint Goal

Provide a lightweight NERV workbench for projects registered in Forge and their
declared commands.

## In Scope

- typed HTTP client for Forge project and command contracts
- list registered Forge projects and their declared commands in NERV
- inspect a command plan in the existing operations console
- confirmed command execution through Forge
- test coverage and documentation

## Out of Scope

- project registration or project creation from NERV
- arbitrary command input or shell execution
- Git mutations from NERV
- filesystem access by NERV
- persistent command history inside NERV
- internal app lifecycle management

## Safety Boundary

NERV only calls Forge's project-command endpoints. Forge remains the authority
for command discovery, planning, allow-list enforcement, execution timeout, and
command history.

NERV requires confirmation in the browser and `confirm=true` in its API before
asking Forge to execute. It requests a fresh Forge plan and refuses to call the
run endpoint when that plan is not allowed.

## Exit Criteria

- NERV shows Forge registered projects and declared commands
- a command plan is visible before execution
- a confirmed allowed command can run through the NERV UI
- a blocked Forge plan cannot reach Forge's run endpoint through NERV
