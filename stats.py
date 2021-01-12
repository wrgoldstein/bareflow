import collections
from datetime import datetime


def parse_duration_from_step(step):
    started_at = step.get("started_at")
    ended_at = step.get("ended_at")
    if started_at is None or ended_at is None:
        return None
  
    started_at = datetime.fromisoformat(started_at)
    ended_at = datetime.fromisoformat(ended_at)

    return (ended_at - started_at).seconds


def roll_up_stats(stats):
    rollup = collections.defaultdict(list)
    for run in stats:
        steps = run["flow_run_steps"]
        durations = [x for x in [parse_duration_from_step(step) for step in steps] if x]
        statuses = [step["status"] for step in steps]

        status = "succeeded"
        if "failed" in statuses:
            status = "failed"

        #TODO good lord

        rollup[run["flow_id"]].append(
            dict(
                flow_run_id=run["id"],
                run_duration=sum(durations),
                status=status,
                steps=steps
            )
        )

    return rollup