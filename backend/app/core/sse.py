# # app/core/sse.py
# from sse_starlette.sse import EventSourceResponse
# import asyncio
# from typing import Any, Dict, List

# class SSEManager:
#     def __init__(self):
#         self._subscribers: List[asyncio.Queue] = []

#     async def subscribe(self) -> EventSourceResponse:
#         """
#         Subscribe to SSE stream. Returns an EventSourceResponse that keeps connection open.
#         """
#         queue = asyncio.Queue()
#         self._subscribers.append(queue)

#         async def event_generator():
#             try:
#                 while True:
#                     data = await queue.get()
#                     yield {
#                         "event": data.get("type", "message"),
#                         "data": data,
#                     }
#             except asyncio.CancelledError:
#                 # remove subscriber on disconnect
#                 self._subscribers.remove(queue)
#                 raise

#         return EventSourceResponse(event_generator())

#     def publish(self, data: Dict[str, Any], type: str = "message"):
#         """
#         Publish data to all active subscribers.
#         """
#         payload = {"type": type, **data}
#         for queue in list(self._subscribers):
#             try:
#                 queue.put_nowait(payload)
#             except asyncio.QueueFull:
#                 # drop subscriber if queue is blocked
#                 self._subscribers.remove(queue)

# # Singleton
# sse = SSEManager()


# app/core/sse.py
from fastapi.responses import StreamingResponse
import asyncio
from typing import Any, Dict, List, AsyncGenerator

class SSEManager:
    def __init__(self):
        self._subscribers: List[asyncio.Queue] = []

    async def subscribe(self) -> StreamingResponse:
        queue = asyncio.Queue()
        self._subscribers.append(queue)

        async def event_generator() -> AsyncGenerator[str, None]:
            try:
                while True:
                    data = await queue.get()
                    yield f"event: {data.get('type', 'message')}\ndata: {data}\n\n"
            except asyncio.CancelledError:
                self._subscribers.remove(queue)
                raise

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    def publish(self, data: Dict[str, Any], type: str = "message"):
        payload = {"type": type, **data}
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                self._subscribers.remove(queue)

# Singleton
sse = SSEManager()
