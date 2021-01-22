import asyncio
import aiofiles
import os
from sanic import response
from pathlib import Path

from . import kube

log_dir = "pod-logs"

logs = [x.stem for x in Path(log_dir).glob("*") if not x.stem.startswith(".")]


async def in_use(file_path):
    proc = await asyncio.create_subprocess_shell(
        f"fuser -- {file_path}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    output = await proc.communicate()
    own_pid = os.getpid()
    pids = [int(x) for x in output[0].decode().split(" ")]
    other_pids = set(pids) - set([own_pid])
    return True if other_pids else False


async def tail(pod_name: str, tell=None):
    file_path = f"{log_dir}/{pod_name}"
    if not Path(file_path).exists():
        yield 'NOT FOUND'

    async with aiofiles.open(file_path, "r") as f:
        if tell is not None:
            await f.seek(tell)

        async for line in f:
            yield line

        if await in_use(file_path):
            await asyncio.sleep(1)
            count = 0
            async for line in tail(file_path, await f.tell()):
                count += 1
                yield line
