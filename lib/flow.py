from collections import defaultdict
from datetime import datetime

from cron_descriptor import get_description
from croniter import croniter


# croniter base
base = datetime(2010, 1, 25, 4, 46)
flows = defaultdict(lambda: defaultdict(list))

# a simple way to register a job
def step(*, flow_id, name, image, command=None, schedule=None, depends_on=[]):
    # TODO topological sort
    flows[flow_id]["steps"].append(
        dict(
            name=name,
            flow_id=flow_id,
            image=image,
            command=command,
            depends_on=depends_on,
            schedule=schedule,
            schedule_words=get_description(schedule) if schedule else None,
            cronitor=croniter(schedule, base) if schedule else None,
        )
    )
