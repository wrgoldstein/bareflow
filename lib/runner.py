"""
These functions are responsible for communicating between the API and kubernetes,
including creating jobs and keeping tabs on pod status and log output.
"""
from typing import List

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
    step_id = job.metadata.labels["step_id"].split("-")[1]
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
