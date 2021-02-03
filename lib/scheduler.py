from croniter import croniter
from datetime import datetime
import asyncio
from . import runner, sync
from .database import get_autocommit_conn_for, query


conn = get_autocommit_conn_for("bareflow")
curs = conn.cursor()


async def scheduler():
    """
    The scheduler is responsible for polling the database for run steps that
    should be sent to the kubernetes cluster.
    """

    await sync.sync_pods_state()
    await sync.insert_new_flows()

    print("Scheduling...")
    while True:
        steps = query.get_unscheduled_flow_run_steps()

        for step in steps:
            asyncio.create_task(runner.run_step(step))

        await create_steps_for_scheduled_runs()
        await asyncio.sleep(1)


async def create_steps_for_scheduled_runs():
    """
    baseline = max(enabled_at, last_start_at)
    next_run_at = croniter('*/3 * * * *', enabled_at).get_next()
    if enabled and not_currently_running and next_run_at < right_now():
        schedule_next_run()
    """

    #TODO

    pass


if __name__ == "__main__":
    asyncio.run(scheduler())
