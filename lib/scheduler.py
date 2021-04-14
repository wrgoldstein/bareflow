import asyncio
from datetime import datetime
from typing import List

from croniter import croniter

from . import step
from .database import get_autocommit_conn_for, query
from .finder import flows
from .utils import dumps

conn = get_autocommit_conn_for("bareflow")
curs = conn.cursor()


"""
1. On start up: make sure all state reflects what's in K8S
2. Load all flows: make sure flow records exist in db for each flow
3. Start scheduling
     -> send ready-to-run steps to k8s
     -> create steps for ready-to-run runs
"""

async def schedule_flow(flow_id: str, flow: dict) -> List[dict]:
    return query.create_flow_run_and_steps(flow_id, flow["steps"])


async def sync_k8s_state():
    """
    for each step in each job: 
        * verify the pod state matches what's in the db.
        * if the pod is Running, start a log tailer process.
        * if the pod is Completed, verify its log has been uploaded to S3.
    """
    pass

async def sync_flows():
    """
    Intention here is to make sure the db has up to date
    information about flows we want to define.
    """
    pass


async def insert_new_flows():
    """
    Create a record for each flow if it doesn't exist already
    """
    db_flows = query.get_flows()
    db_flow_ids = [flow["id"] for flow in db_flows]
    for flow_id in flows.keys():
        if flow_id not in db_flow_ids:
            query.insert_flow(flow_id)

    for flow_id in set(db_flow_ids) - set(flows.keys()):
        # Remove any flow that no longer exists
        query.delete_flow_by_id(flow_id)


async def create_steps_for_scheduled_runs():
    pass


async def scheduler():
    """
    The scheduler is responsible for polling the database for run steps that
    should be sent to the kubernetes cluster.
    """

    await sync_k8s_state()
    await sync_flows()

    conn = get_autocommit_conn_for("bareflow")

    print("Scheduling...")
    while True:
        steps = query.get_unscheduled_flow_run_steps()

        for run_step in steps:
            asyncio.create_task(step.run_step(run_step))

        await create_steps_for_scheduled_runs()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(scheduler())
