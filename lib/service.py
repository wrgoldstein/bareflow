"""
These functions are responsible for communicating between the API and kubernetes,
including creating jobs and keeping tabs on pod status and log output.
"""

import asyncio
import importlib.util
import json
import uuid
from typing import List
from datetime import datetime, timezone
from pathlib import Path

from kubernetes import client, config, watch

from .database import query
from . import utils
from .flow import flows



queue = None  # set by app.py to be on the same loop as the web server
scheduled_steps = set()

config.load_kube_config()
watcher = watch.Watch()
batch_v1 = client.BatchV1Api()
v1 = client.CoreV1Api()

websockets = {}

# Load all dags.. this should be more dynamical
paths = Path("flows").glob("*.py")  # TODO nested
for path in paths:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)


async def schedule_flow(flow_id: str, flow: dict):
    flow_run_steps = query.create_flow_run_and_steps(flow_id, flow["steps"])
    queue.put_nowait({"queued_at": datetime.today().isoformat(), "type": "event", "flow_run_steps": flow_run_steps})
    return flow_run_steps


def create_job_object(
    flow_run_step_id: int, params: dict
) -> client.models.v1_job.V1Job:
    # Configureate Pod template container
    unique_name = f"{params['name']}-{uuid.uuid4().hex[:6]}"
    container = client.V1Container(image_pull_policy="Never", **params)

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(
            labels={"app": "bareflow", "flow_run_step_id": f"{flow_run_step_id}"}
        ),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
    )

    # Create the specification of deployment
    spec = client.V1JobSpec(template=template, backoff_limit=1)

    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=unique_name),
        spec=spec,
    )

    return job


async def get_pod_for_job(
    job: client.models.v1_job.V1Job,
) -> client.models.v1_pod.V1Pod:
    """
    Get the pod associated with a given job.
    """
    job_start_time = None
    while job_start_time is None:  # TODO timeout?
        job_start_time = batch_v1.read_namespaced_job_status(
            namespace="default", name=job.metadata.name
        ).status.start_time

    pods = v1.list_namespaced_pod(
        namespace="default", label_selector=f"job-name={job.metadata.name}"
    )
    return pods.items[0]


async def wait_for_pod_status(pod_name: str, statuses: List[str]) -> str:
    """
    Wait until the pod has one of the statuses provided.
    """
    while True:
        res = v1.read_namespaced_pod_status(namespace="default", name=pod_name)
        if res.status.phase in statuses:
            return res.status.phase

        await asyncio.sleep(3)


async def update_step(flow_run_step_id: int, **kwargs):
    flow_run_step = query.update_flow_run_step(flow_run_step_id, **kwargs)
    queue.put_nowait({"queued_at": datetime.today().isoformat(), "type": "event", "flow_run_step": flow_run_step})


async def run_step(step: dict):
    flow_run_step_id = step.pop("id")
    await update_step(flow_run_step_id, status="starting")
    # TODO jesus.
    params = {k: v for k, v in step.items() if k not in ["flow_id", "outcome", "log_status", "stats", "status", "pod_name", "flow_run_id", "depends_on", "created_at", "started_at", "ended_at", "updated_at"]}
    job = create_job_object(flow_run_step_id, params)
    batch_v1.create_namespaced_job(body=job, namespace="default")
    pod = await get_pod_for_job(job)
    await update_step(
        flow_run_step_id,
        pod_name=pod.metadata.name,
        status="pending",
        started_at=datetime.now(timezone.utc),
    )

    # Wait for pod to leave the Pending state to begin tailing the log
    status = await wait_for_pod_status(
        pod.metadata.name, ["Succeeded", "Failed", "Unknown", "Running"]
    )
    await update_step(flow_run_step_id, status=status.lower())

    # Tail the kubernetes log to a local file; this is tricky to do using the client library
    log = await asyncio.create_subprocess_shell(
        f"kubectl logs -n default {pod.metadata.name} --follow > pod-logs/{pod.metadata.name}"
    )
    await update_step(flow_run_step_id, log_status="local")

    # wait for the pod to finish before terminating the log tailing subprocess
    status = await wait_for_pod_status(
        pod.metadata.name, ["Succeeded", "Failed", "Unknown"]
    )
    await update_step(
        flow_run_step_id, status=status.lower(), ended_at=datetime.now(timezone.utc)
    )
    scheduled_steps.remove(flow_run_step_id)
    log.terminate()


async def reattach_to_step(step: dict):
    """
    Try to pick up any steps we've lost track of (steps not created, queued, succeeded, or failed)
    """
    pod_name = step.get("pod_name")
    if pod_name is not None:
        log = await asyncio.create_subprocess_shell(
            f"kubectl logs -n default {pod_name} --follow > pod-logs/{pod_name}"
        )
        status = await wait_for_pod_status(pod_name, ["Succeeded", "Failed", "Unknown"])
        await update_step(step["id"], status=status.lower())
        log.terminate()
    else:
        # As far as we can tell this was never even started
        asyncio.create_task(run_step(step))
        await update_step(step["id"], status="queued")


def get_flows() -> dict:
    """
    Get recent run stats (success/fail and duration).

    Rolls up individual steps to get a total duration and status for the run,
    which is shown in the index view.
    """
    # To make state management easier on the client, we do not nest
    # run steps inside their runs.
    flow_run_steps = query.get_flow_runs(25)
    return dict(flows=flows, flow_run_steps=flow_run_steps)


async def upstream_steps_succeeded(step):
    flow_run_id = step["flow_run_id"]
    depends_on = step.get("depends_on")
    if not depends_on:
        return True

    flow_run_steps = query.get_flow_run_steps_by_run_id_and_name(flow_run_id, tuple(step["depends_on"]))
    if any([s["status"] in ["failed","canceled"] for s in flow_run_steps]):
        # There was a failure upstream, skip this step
        await update_step(step["id"], status="skipped")
        return False
    
    if all([s["status"] in ["succeeded"] for s in flow_run_steps]):
        return True

    # Otherwise, there's still a step we're waiting for
    return False


async def scheduler():
    """
    The scheduler is responsible for polling the database for run steps that
    should be sent to the kubernetes cluster.
    """
    closed_statuses = ["queued", "succeeded", "failed", "running", "skipped"]

    # First pick up anything we've dropped
    unscheduled_flow_run_steps = query.get_flow_run_steps_by_nin_status(
        closed_statuses
    )
    for step in unscheduled_flow_run_steps:
        await reattach_to_step(step)

    while True:
        # Check if any run steps are eligible to be sent to kubernetes
        unscheduled_flow_run_steps = query.get_flow_run_steps_by_nin_status(
            closed_statuses
        )

        # TODO actual logging
        for step in unscheduled_flow_run_steps:
            if step["id"] not in scheduled_steps:
                if await upstream_steps_succeeded(step):
                    scheduled_steps.add(step["id"])
                    asyncio.create_task(run_step(step))

        # TODO Check if any flows should be scheduled by cron
        # # mega mega hack bad bad bad change this
        # flow_run_steps = query.get_flow_run_steps_by_nin_status([])
        # max_times = {}
        # ongoing = set()
        # for step in flow_run_steps:
        #     flow_id = step["flow_id"]
        #     if flow_id in ongoing:
        #         continue

        #     if step["status"] in ["failed", "succeeded"]:
        #         if flow_id not in max_times:
        #             max_times[flow_id] = step["ended_at"]
        #         else:
        #             max_times[flow_id] = max(max_times["flow_id"], step["ended_at"])
        #     else:
        #         ongoing.add(flow_id)

        # for flow in flows:
        #     if flow["croniter"] is not None:
        #         cr = flow["croniter"]
        #         breakpoint()
        #         flow_runs
                # cr.
                # NEED TO MAKE the db just SQL no hasura
                # megahack time
                


        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(scheduler())
