from datetime import UTC, datetime
from pathlib import Path

from syzygy_nerv.catalog import SurfaceCatalog, SurfaceEntry
from syzygy_nerv.config import Settings
from syzygy_nerv.supervisor import ManagedProcess, ModuleSupervisor


class FakeProcess:
    def __init__(self, pid: int = 4242) -> None:
        self.pid = pid
        self.returncode: int | None = None

    def poll(self) -> int | None:
        return self.returncode

    def terminate(self) -> None:
        self.returncode = 0

    def kill(self) -> None:
        self.returncode = -9

    def wait(self, timeout: float | None = None) -> int:
        return 0 if self.returncode is None else self.returncode


class FakeSupervisor(ModuleSupervisor):
    def _spawn_process(self, entry: SurfaceEntry) -> ManagedProcess:
        return ManagedProcess(
            entry=entry,
            process=FakeProcess(),
            started_at=datetime.now(UTC),
            log_handle=None,
            log_path=Path(entry.cwd) / "fake.log",
        )


def build_supervisor(tmp_path: Path) -> FakeSupervisor:
    settings = Settings(workspace_root=tmp_path, runtime_logs_dir=tmp_path / "logs")
    catalog = SurfaceCatalog(settings)
    return FakeSupervisor(catalog=catalog, runtime_logs_dir=settings.runtime_logs_dir)


def test_supervisor_starts_and_stops_launchable_surface(tmp_path: Path) -> None:
    supervisor = build_supervisor(tmp_path)

    started = supervisor.start("foundation")
    stopped = supervisor.stop("foundation")

    assert started.running is True
    assert started.pid == 4242
    assert stopped.running is False
    assert stopped.last_exit_code == 0


def test_supervisor_reports_non_launchable_surface(tmp_path: Path) -> None:
    supervisor = build_supervisor(tmp_path)

    status = supervisor.status("nerv")

    assert status.running is False
    assert status.command
