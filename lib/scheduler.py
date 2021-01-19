"""
These functions are responsible for communicating between the API and kubernetes,
including creating jobs and keeping tabs on pod status and log output.
"""
import signal
import functools
import asyncio
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from kubernetes import client, config, watch

from . import kube
from .utils import dumps
from .database import get_autocommit_conn_for, query
from .job import create_job_object

conn = get_autocommit_conn_for("bareflow")
curs = conn.cursor()

running = set()


async def schedule_flow(flow_id: str, flow: dict) -> List[dict]:
    return query.create_flow_run_and_steps(flow_id, flow["steps"])


async def update_step_with_latest(job):
    pod = await kube.get_pod_for_job(job)
    # TODO what if the pod has been deleted?
    step_id = job.metadata.labels.step_id
    query.update_flow_run_step(int(step_id), status=pod.status.phase.lower())


async def run_step(step: dict):
    if step["id"] in running:
        return
    running.add(step["id"])
    job = create_job_object(step)
    try:

        print("trying to run ", job.metadata.name)
        async for update in kube.create_and_follow_job(job):
            step = query.update_flow_run_step(step["id"], **update)
            print("Notifying update", step)
            curs.execute("NOTIFY updates, %s", (dumps(step),))

    except kube.client.exceptions.ApiException as e:
        if e.status == 409:
            print("Job name conflict, this probably means a step was rescheduled")
            await update_step_with_latest(job)
            return
        raise (e)
    finally:
        if step["id"] in running:
            running.remove(step["id"])


async def scheduler():
    """
    The scheduler is responsible for polling the database for run steps that
    should be sent to the kubernetes cluster.
    """

    # TODO: [reliability] sync back up on startup
    conn = get_autocommit_conn_for("bareflow")
    curs = conn.cursor()
    print("Scheduling...")
    try:
        while True:
            steps = query.get_unscheduled_flow_run_steps()

            for step in steps:
                asyncio.create_task(run_step(step))

                # curs.execute(f"NOTIFY flow_run_steps, %s", (dumps(step), ))
                # print(f"scheduled step: {step['id']}")

            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("shit!")


# async def poll_for_notifications():
#     curs.execute(f"LISTEN flow_run_steps")
#     print("Listening...")
#     while True:
#         conn.poll()
#         while conn.notifies:
#             notify = conn.notifies.pop(0)
#             step = json.loads(notify.payload)
#             if step["id"] not in running:
#                 asyncio.create_task(run_step(step))
#         await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(scheduler())
