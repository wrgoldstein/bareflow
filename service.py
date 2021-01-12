"""
1. Be able to send a hello world job to k8s by script and parse output [x]
2. Write the most basic UI
3. Write the most basic scheduler
4. Implement dependencies
5. Separate library code from dags
"""

import importlib.util
import uuid
from pathlib import Path
import asyncio
import sys
from contextlib import contextmanager
from kubernetes import client, config, watch
import graphql
from flow import flows


# Load all dags.. this should be more dynamical
paths = Path('dags').glob('*.py')  #TODO nested
for path in paths:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)


def schedule_flow(flow_id: str, steps: list):
    flow_run = graphql.create_flow_run_and_steps(flow_id, steps)
    flow_run_id = flow_run['id']
    flow_run_step_ids = [x['id'] for x in flow_run['flow_run_steps']]


config.load_kube_config()
watcher = watch.Watch()
batch_v1 = client.BatchV1Api()
v1 = client.CoreV1Api()


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
    graphql.update_flow_run_step(flow_run_step_id, status="started")

    # Wait for pod to leave the Pending state to begin tailing the log
    status = await wait_for_pod_status(pod, ["Succeeded", "Failed", "Unknown", "Running"])
    graphql.update_flow_run_step(flow_run_step_id, status=status.lower())

    # this is tricky to do in python
    log = await asyncio.create_subprocess_shell(f"kubectl logs -n default {pod.metadata.name} --follow > pod-logs/{pod.metadata.name}")
    graphql.update_flow_run_step(flow_run_step_id, log_status="local")

    # wait for the pod to finish before terminating the log tailing subprocess
    status = await wait_for_pod_status(pod, ["Succeeded", "Failed", "Unknown"])
    graphql.update_flow_run_step(flow_run_step_id, status=status.lower())
    
    log.terminate()


async def scheduler():
    while True:
        print("Looking for steps to run")
        # Check if any run steps are eligible to be sent to kubernetes

        #TODO eventually there will be some dependency management to do here, but for now
        # any step that has been put in the database will be run immediately.
        eligible_flow_run_steps = graphql.get_flow_run_steps_with_status(["created"])

        #TODO actual logging
        print(f"found {len(eligible_flow_run_steps)}")

        for step in eligible_flow_run_steps:
            asyncio.create_task(run_step(step))
            graphql.update_flow_run_step(step["id"], status="queued")

        #TODO Check if any flows have been scheduled
        await asyncio.sleep(5)


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    asyncio.run(scheduler())
