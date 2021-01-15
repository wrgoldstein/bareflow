import collections

from dateutil import parser


def parse_duration_from_step(step):
    started_at = step.get("started_at")
    ended_at = step.get("ended_at")
    if started_at is None or ended_at is None:
        return None

    started_at = parser.parse(started_at)
    ended_at = parser.parse(ended_at)

    return (ended_at - started_at).seconds

def compute_stats_for_flow_run(flow_run):
    step_count = collections.defaultdict(0)
    total_duration = 0
    for step in flow_run["flow_run_steps"]:
        if step["status"] in ["suceeded", "failed"]:
            duration = parse_duration_from_step(step)
            total_duration += duration
            step_count[step["status"]] += 1
        else:
            # not finished yet, don't calculate stats
            return 'unfinished', None

    if step_count["failed"] > 0:
        return "failed", {**step_count, "duration": total_duration}
    else:
        return "failed", {**step_count, "duration": total_duration}
