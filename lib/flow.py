from collections import defaultdict

flows = defaultdict(lambda: defaultdict(list))

# a simple way to register a job
def step(*, flow_id, name, image, command, depends_on=[]):
    # TODO topological sort
    flows[flow_id]["steps"].append(
        dict(
            name=name,
            flow_id=flow_id,
            image=image,
            command=command,
            depends_on=depends_on
            # schedule=schedule,
            # schedule_words=get_description(schedule)
        )
    )
