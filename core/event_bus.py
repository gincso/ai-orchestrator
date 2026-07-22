import asyncio
import json
from datetime import datetime, timezone
from typing import Callable, AsyncGenerator

_subscribers: dict[str, list[Callable]] = {}
_sse_queues: dict[str, list[asyncio.Queue]] = {}


def publish(project_id: str, event_type: str, data: dict):
    payload = {
        "event": event_type,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    for cb in _subscribers.get(project_id, []):
        cb(payload)
    for q in _sse_queues.get(project_id, []):
        q.put_nowait(payload)


def subscribe(project_id: str, callback: Callable):
    _subscribers.setdefault(project_id, []).append(callback)


def unsubscribe(project_id: str, callback: Callable):
    _subscribers.get(project_id, []).remove(callback)


async def stream(project_id: str) -> AsyncGenerator[str, None]:
    q: asyncio.Queue = asyncio.Queue()
    _sse_queues.setdefault(project_id, []).append(q)
    try:
        while True:
            payload = await q.get()
            yield f"event: {payload['event']}\ndata: {json.dumps(payload)}\n\n"
    finally:
        _sse_queues.get(project_id, []).remove(q)
