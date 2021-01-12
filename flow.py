import uuid
import pathlib
import inspect

from kubernetes import client
from cron_descriptor import get_description
from collections import defaultdict
# todo: actual DAG
flows = defaultdict(list)

# a simple way to register a job
def step(*, flow_id, name, image, command):
    #TODO topological sort
    flows[flow_id].append(dict(
        name=name,
        flow_id=flow_id,
        image=image,
        command=command,
        # schedule=schedule,
        # schedule_words=get_description(schedule)
    ))
