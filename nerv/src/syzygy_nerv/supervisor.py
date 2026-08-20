import os
import subprocess
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Protocol

from pydantic import BaseModel, Field

from syzygy_nerv.catalog import SurfaceCatalog, SurfaceEntry


class ProcessHandle(Protocol):
    pid: int

    def poll(self) -> int | None: ...

    def terminate(self) -> None: ...

    def kill(self) -> None: ...

    def wait(self, timeout: float | None = None) -> int: ...


class ModuleRuntimeStatus(BaseModel):
    name: str
    running: bool
    pid: int | None = None
    started_at: datetime | None = None
    command: list[str] = Field(default_factory=list)
    cwd: str
    log_path: str | None = None
    last_exit_code: int | None = None


class ModuleSupervisorError(ValueError):
    pass


@dataclass
class ManagedProcess:
    entry: SurfaceEntry
    process: ProcessHandle
    started_at: datetime
    log_handle: IO[str] | None
    log_path: Path | None
    last_exit_code: int | None = None


class ModuleSupervisor:
    def __init__(self, catalog: SurfaceCatalog, runtime_logs_dir: Path) -> None:
        self.catalog = catalog
        self.runtime_logs_dir = runtime_logs_dir
        self._processes: dict[str, ManagedProcess] = {}
        self._lock = threading.RLock()

    def start(self, name: str) -> ModuleRuntimeStatus:
        with self._lock:
            entry = self._entry(name)
            if not entry.launch_enabled:
                msg = f"Surface does not support launch actions: {name}"
                raise ModuleSupervisorError(msg)
            process = self._processes.get(name)
            if process is not None:
                self._refresh(name)
                process = self._processes.get(name)
                if process is not None and process.process.poll() is None:
                    return self._status_from_process(process)
            managed = self._spawn_process(entry)
            self._processes[name] = managed
            return self._status_from_process(managed)

    def stop(self, name: str) -> ModuleRuntimeStatus:
        with self._lock:
            entry = self._entry(name)
            self._refresh(name)
            process = self._processes.get(name)
            if process is None:
                return ModuleRuntimeStatus(
                    name=entry.name,
                    running=False,
                    command=entry.launch_command,
                    cwd=entry.cwd,
                )
            process.process.terminate()
            try:
                exit_code = process.process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                process.process.kill()
                exit_code = process.process.wait(timeout=5.0)
            process.last_exit_code = exit_code
            if process.log_handle is not None:
                process.log_handle.close()
            self._processes.pop(name, None)
            return ModuleRuntimeStatus(
                name=entry.name,
                running=False,
                command=entry.launch_command,
                cwd=entry.cwd,
                log_path=str(process.log_path) if process.log_path is not None else None,
                last_exit_code=exit_code,
            )

    def status(self, name: str) -> ModuleRuntimeStatus:
        with self._lock:
            entry = self._entry(name)
            self._refresh(name)
            process = self._processes.get(name)
            if process is None:
                return ModuleRuntimeStatus(
                    name=entry.name,
                    running=False,
                    command=entry.launch_command,
                    cwd=entry.cwd,
                )
            return self._status_from_process(process)

    def snapshot(self) -> dict[str, ModuleRuntimeStatus]:
        with self._lock:
            return {entry.name: self.status(entry.name) for entry in self.catalog.list()}

    def shutdown(self) -> None:
        names = [entry.name for entry in self.catalog.list() if entry.launch_enabled]
        for name in names:
            try:
                self.stop(name)
            except ModuleSupervisorError:
                continue

    def _entry(self, name: str) -> SurfaceEntry:
        entry = self.catalog.get(name)
        if entry is None:
            msg = f"Unknown surface: {name}"
            raise ModuleSupervisorError(msg)
        return entry

    def _refresh(self, name: str) -> None:
        process = self._processes.get(name)
        if process is None:
            return
        exit_code = process.process.poll()
        if exit_code is None:
            return
        process.last_exit_code = exit_code
        if process.log_handle is not None:
            process.log_handle.close()
        self._processes.pop(name, None)

    def _spawn_process(self, entry: SurfaceEntry) -> ManagedProcess:
        self.runtime_logs_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.runtime_logs_dir / f"{entry.name}.log"
        log_handle = log_path.open("a", encoding="utf-8")
        creationflags = 0
        if os.name == "nt" and hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        process = subprocess.Popen(
            entry.launch_command,
            cwd=Path(entry.cwd),
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            shell=False,
            creationflags=creationflags,
        )
        return ManagedProcess(
            entry=entry,
            process=process,
            started_at=datetime.now(UTC),
            log_handle=log_handle,
            log_path=log_path,
        )

    def _status_from_process(self, process: ManagedProcess) -> ModuleRuntimeStatus:
        running = process.process.poll() is None
        return ModuleRuntimeStatus(
            name=process.entry.name,
            running=running,
            pid=process.process.pid,
            started_at=process.started_at,
            command=process.entry.launch_command,
            cwd=process.entry.cwd,
            log_path=str(process.log_path) if process.log_path is not None else None,
            last_exit_code=process.last_exit_code,
        )
