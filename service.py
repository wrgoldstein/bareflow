"""
1. Be able to send a hello world job to k8s by script and parse output [x]
2. Write the most basic UI
3. Write the most basic scheduler
4. Implement dependencies
5. Separate library code from dags
"""
import asyncio
import collections
import functools
import importlib.util
import itertools
import json
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from kubernetes import client, config, watch

import graphql
import stats
from flow import flows

queue = None

# Load all dags.. this should be more dynamical
paths = Path('flows').glob('*.py')  #TODO nested
for path in paths:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)


async def schedule_flow(flow_id: str, flow: dict):
    flow_run = graphql.create_flow_run_and_steps(flow_id, flow["steps"])
    queue.put_nowait({"type": "event", "flow_run": flow_run})
    for ws in websockets.values():
        print("sending", ws)
        await ws.send(json.dumps(dict(type="event", msg="hellooo")))
    flow_run_id = flow_run['id']
    flow_run_step_ids = [x['id'] for x in flow_run['flow_run_steps']]


config.load_kube_config()
watcher = watch.Watch()
batch_v1 = client.BatchV1Api()
v1 = client.CoreV1Api()

websockets = {}

def create_job_object(flow_run_step_id, params):
    # Configureate Pod template container
    unique_name = f"{params['name']}-{uuid.uuid4().hex[:6]}"
    container = client.V1Container(**params)

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "bareflow", "flow_run_step_id": f"{flow_run_step_id}"}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
    
    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=4)  #TODO RETRIES????
    
    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=unique_name),
        spec=spec)

    return job


async def get_pod_for_job(job):
    job_start_time = None
    while job_start_time is None:  #TODO timeout?
        job_start_time = batch_v1.read_namespaced_job_status(namespace="default", name=job.metadata.name).status.start_time
    
    pods = v1.list_namespaced_pod(namespace='default', label_selector=f'job-name={job.metadata.name}')
    return pods.items[0]  # one pod per job


async def wait_for_pod_status(pod, statuses):
    while True:
        res = v1.read_namespaced_pod_status(namespace="default", name=pod.metadata.name)
        if res.status.phase in statuses:
            return res.status.phase
        
        await asyncio.sleep(3)


async def run_step(step):
    flow_run_step_id = step.pop("id")
    job = create_job_object(flow_run_step_id, step)
    _api_response = batch_v1.create_namespaced_job(
            body=job,
            namespace="default"
    )
    pod = await get_pod_for_job(job)
    graphql.update_flow_run_step(flow_run_step_id, status="started", started_at=datetime.now(timezone.utc))

    # Wait for pod to leave the Pending state to begin tailing the log
    status = await wait_for_pod_status(pod, ["Succeeded", "Failed", "Unknown", "Running"])
    graphql.update_flow_run_step(flow_run_step_id, status=status.lower())

    # this is tricky to do in python
    log = await asyncio.create_subprocess_shell(f"kubectl logs -n default {pod.metadata.name} --follow > pod-logs/{pod.metadata.name}")
    graphql.update_flow_run_step(flow_run_step_id, log_status="local")

    # wait for the pod to finish before terminating the log tailing subprocess
    status = await wait_for_pod_status(pod, ["Succeeded", "Failed", "Unknown"])

    graphql.update_flow_run_step(flow_run_step_id, status=status.lower(), ended_at=datetime.now(timezone.utc))
    
    log.terminate()


def get_flows():
    """
    Get recent run stats (success/fail and duration).
    """

    #TODO this is embarrassing garbage but on the clock
    flow_runs = graphql.get_flow_runs()
    groups = {}
    for key, group in itertools.groupby(flow_runs, lambda x: x["flow_id"]):
        groups[key] = []
        for run in group:
            groups[key].append(run)
    res = {}
    for flow_id in flows.keys():
        res[flow_id] = { "runs": [] }
        group = groups.get(flow_id, [])
        for run in group:
            durations = [x for x in [stats.parse_duration_from_step(step) for step in run["flow_run_steps"]] if x]
            succeeded = all([step["status"] == "succeeded" for step in run["flow_run_steps"]])
        
            run["duration"] = sum(durations)
            run["status"] = "succeeded" if succeeded else "failed"
            res[flow_id]["runs"].append(run)
    return res

async def scheduler():
    while True:
        # Check if any run steps are eligible to be sent to kubernetes

        #TODO eventually there will be some dependency management to do here, but for now
        # any step that has been put in the database will be run immediately.
        eligible_flow_run_steps = graphql.get_flow_run_steps_by_status(["created"])

        #TODO actual logging

        for step in eligible_flow_run_steps:
            asyncio.create_task(run_step(step))
            graphql.update_flow_run_step(step["id"], status="queued")

            #TODO update the flow run itself (if this is the last step of the run)

        #TODO Check if any flows have been scheduled
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(scheduler())
