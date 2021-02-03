import asyncio
import multiprocessing
from functools import partial
from typing import Any
from tempfile import NamedTemporaryFile
import tenacity
from kubernetes import client, config, watch

config.load_kube_config()
watcher = watch.Watch()
batch_v1 = client.BatchV1Api()
v1 = client.CoreV1Api()

# Cut down on verbosity
def wrapper(f, **kwargs):
    fp = partial(f, **kwargs)

    async def inner(**kwargs):
        try:
            result = fp(**kwargs)
            while not result.ready():
                await asyncio.sleep(1)
            return result.get()
        except client.exceptions.ApiException as e:
            if e.status == 404:
                # Not found
                return
            raise (e)

    return inner


v1_get_job_status = wrapper(batch_v1.read_namespaced_job_status, namespace="default", async_req=True)
v1_get_pods = wrapper(v1.list_namespaced_pod, namespace="default", async_req=True)
v1_get_pod_status = wrapper(v1.read_namespaced_pod_status, namespace="default", async_req=True)
v1_create_job = wrapper(batch_v1.create_namespaced_job, namespace="default", async_req=True)


@tenacity.retry(wait=tenacity.wait_fixed(3), stop=tenacity.stop_after_attempt(10))
async def get_pod_for_job(job: client.models.v1_job.V1Job,) -> client.models.v1_pod.V1Pod:
    "Waits 30 seconds for a pod to be available. Assumes one pod per job."
    pods = await v1_get_pods(label_selector=f"job-name={job.metadata.name}")
    return pods.items[0]


async def create_job(job: client.models.v1_job.V1Job):
    return await v1_create_job(body=job)

    # wait for process to finish
    # write file to S3
    # write to database
    # clean up log file on disk


async def create_and_follow_job(job: client.models.v1_job.V1Job):
    await create_job(job)
    yield dict(status="created")
    while True:
        res = await v1_get_job_status(name=job.metadata.name)
        if res is not None:
            pod = await get_pod_for_job(job)
            yield dict(pod_name=pod.metadata.name, status=pod.status.phase.lower())
            if pod.status.phase.lower() in ["succeeded", "failed"]:
                asyncio.create_task(persist_logs(pod.metadata.name))
                break
        else:
            print("job is missing", job.metadata.name)

        await asyncio.sleep(2)
