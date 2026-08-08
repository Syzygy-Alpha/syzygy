from syzygy_foundation.scheduler import Scheduler


async def test_scheduler_runs_startup_tasks() -> None:
    scheduler = Scheduler()
    calls: list[str] = []

    async def startup() -> None:
        calls.append("startup")

    scheduler.startup_task("startup", startup)

    await scheduler.start()
    await scheduler.stop()

    assert calls == ["startup"]

