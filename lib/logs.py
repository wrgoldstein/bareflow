"""
Utilities for interacting with kubernetes logs.
"""

import asyncio
import os
from tempfile import NamedTemporaryFile
from concurrent.futures import ThreadPoolExecutor

import boto3

from .database import query

BUCKET = os.getenv("BAREFLOW_BUCKET")

s3 = boto3.resource('s3')

executor = ThreadPoolExecutor(
    max_workers=10,
)

async def get_logs(pod_name: str):
    status = query.get_pod_status(pod_name)
    if status in ("Failed", "Succeeded"):
        # get logs from S3
        pass
    else:
        async for line in follow_logs(pod_name):
            yield line


async def follow_logs(pod_name: str):
    cmd = f"kubectl logs -n default {pod_name} --follow"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    return proc


async def persist_logs(pod_name: str):
    t = NamedTemporaryFile()
    cmd = f"kubectl logs -n default {pod_name} > {t.name}"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await proc.wait()
    s3.meta.client.upload_file(t.name, BUCKET, pod_name)
    t.close()
