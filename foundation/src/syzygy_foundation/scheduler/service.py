import asyncio
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

ScheduledTask = Callable[[], Awaitable[None]]


class Scheduler:
    def __init__(self) -> None:
        self._startup_tasks: list[tuple[str, ScheduledTask]] = []
        self._periodic_tasks: list[tuple[str, float, ScheduledTask]] = []
        self._running_tasks: list[asyncio.Task[None]] = []

    def startup_task(self, name: str, task: ScheduledTask) -> None:
        self._startup_tasks.append((name, task))

    def periodic_task(self, name: str, interval_seconds: float, task: ScheduledTask) -> None:
        self._periodic_tasks.append((name, interval_seconds, task))

    async def start(self) -> None:
        for name, task in self._startup_tasks:
            logger.info("scheduler_startup_task", extra={"task": name})
            await task()
        for name, interval_seconds, task in self._periodic_tasks:
            self._running_tasks.append(
                asyncio.create_task(self._run_periodic(name, interval_seconds, task))
            )

    async def stop(self) -> None:
        for task in self._running_tasks:
            task.cancel()
        if self._running_tasks:
            await asyncio.gather(*self._running_tasks, return_exceptions=True)
        self._running_tasks.clear()

    @property
    def running_task_count(self) -> int:
        return len(self._running_tasks)

    async def _run_periodic(
        self,
        name: str,
        interval_seconds: float,
        task: ScheduledTask,
    ) -> None:
        while True:
            await asyncio.sleep(interval_seconds)
            try:
                await task()
            except Exception:
                logger.exception("scheduler_periodic_task_failed", extra={"task": name})

