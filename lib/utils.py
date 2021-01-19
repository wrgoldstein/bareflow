import json
from functools import partial

dumps = partial(json.dumps, default=str)
loads = json.loads
