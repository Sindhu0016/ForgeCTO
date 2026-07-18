import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


@dataclass
class ProgressEvent:
    step: str
    status: str
    message: str
    partial: dict[str, Any] | None = None


class EventBus:
    """In-memory pub/sub for SSE progress per project."""

    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = defaultdict(list)
        self._history: dict[str, list[ProgressEvent]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def publish(self, project_id: str, event: ProgressEvent) -> None:
        async with self._lock:
            self._history[project_id].append(event)
            queues = list(self._queues.get(project_id, []))
        for q in queues:
            await q.put(event)

    async def subscribe(self, project_id: str) -> AsyncIterator[ProgressEvent]:
        q: asyncio.Queue = asyncio.Queue()
        async with self._lock:
            self._queues[project_id].append(q)
            history = list(self._history.get(project_id, []))
        for event in history:
            yield event
        try:
            while True:
                event = await q.get()
                yield event
                if event.status == "failed":
                    break
                if event.status == "completed" and event.step == "done":
                    break
        finally:
            async with self._lock:
                if project_id in self._queues and q in self._queues[project_id]:
                    self._queues[project_id].remove(q)

    def history(self, project_id: str) -> list[ProgressEvent]:
        return list(self._history.get(project_id, []))


event_bus = EventBus()
