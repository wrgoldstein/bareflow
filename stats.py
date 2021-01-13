import collections
from datetime import datetime
from dateutil import parser


def parse_duration_from_step(step):
    started_at = step.get("started_at")
    ended_at = step.get("ended_at")
    if started_at is None or ended_at is None:
        return None
  
    started_at = parser.parse(started_at)
    ended_at = parser.parse(ended_at)

    return (ended_at - started_at).seconds
