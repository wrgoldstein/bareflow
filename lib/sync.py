"""
If the scheduler goes down unexpectedly or if the database becomes out of sync
with kubernetes in any way, these functions should allow us to resume operations
on restart. 

If expiring old metadata in the database is needed to preserve fast query times
and not require a large database instance, that will happen here too.
"""

from .database import query
from .finder import flows


async def sync_pods_state():
    """
    for each step in each job: 
        * verify the pod state matches what's in the db.
        * if the pod is Running, start a log tailer process.
        * if the pod is Completed, verify its log has been uploaded to S3.
    """
    #TODO
    pass


async def insert_new_flows():
    """
    Create a record for each flow if it doesn't exist already.
    """
    db_flows = query.get_flows()
    db_flow_ids = [flow["id"] for flow in db_flows]
    for flow_id in flows.keys():
        if flow_id not in db_flow_ids:
            query.insert_flow(flow_id)

    for flow_id in set(db_flow_ids) - set(flows.keys()):
        # Remove any flow that no longer exists
        query.delete_flow_by_id(flow_id)
