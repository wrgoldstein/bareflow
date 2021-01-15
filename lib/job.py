import inspect
import uuid

from kubernetes import client

container_params = inspect.getargspec(client.V1Container)[0]


def create_job_object(step: dict) -> client.models.v1_job.V1Job:
    "Create a Kubernetes V1Job manifest from a dictionary"
    # Configureate Pod template container
    unique_name = f"{step['name']}-{step['id']}"

    params = {k: v for k, v in step.items() if k in container_params}
    container = client.V1Container(image_pull_policy="Never", **params)

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "bareflow"}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
    )

    # Create the specification of deployment
    spec = client.V1JobSpec(template=template, backoff_limit=0)
    labels = dict(step_id=f"step-{step['id']}")
    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=unique_name, labels=labels),
        spec=spec,
    )

    return job
