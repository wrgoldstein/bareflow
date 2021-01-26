from croniter import croniter
from datetime import datetime
import asyncio
from . import step
from .finder import flows
from .utils import dumps
from .database import get_autocommit_conn_for, query

conn = get_autocommit_conn_for("bareflow")
curs = conn.cursor()


"""
1. On start up: make sure all state reflects what's in K8S
2. Load all flows: make sure flow records exist in db for each flow
3. Start scheduling
     -> send ready-to-run steps to k8s
     -> create steps for ready-to-run runs
"""
async def sync_k8s_state():
    """
    for each pod in each job: 
        * verify the pod state matches what's in the db.
        * if the pod is Running, start a log tailer process.
        * if the pod is Completed, verify its log has been uploaded to S3.
        
    """
    pass

async def sync_flows():
    """
    for each flow:
        if the flow ID exists in the flows table, continue
        create a record in the db 
    """
    pass

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

        for step in steps:
            asyncio.create_task(step.run_step(step))

        await create_steps_for_scheduled_runs()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(scheduler())
