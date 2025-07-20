import asyncio
from typing import Dict

progress_store: Dict[str, int] = {}


async def long_running_task(task_id: str):
    for i in range(1, 101):
        await asyncio.sleep(0.6)
        progress_store[task_id] = i
