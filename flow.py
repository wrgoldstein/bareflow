import uuid
import pathlib
import inspect

from kubernetes import client
from cron_descriptor import get_description

# todo: actual DAG
jobs = {}

# a simple way to register a job
def job(*, name, image, command, schedule):
    jobs[name] = dict(
        name=name,
        image=image,
        command=command,
        schedule=schedule,
        schedule_words=get_description(schedule)
    )

def k8s_job_params(params):
    filtered = ['schedule', 'schedule_words']
    return {k:v for k,v in params.items() if k not in filtered}

def create_job_object(params):
    params = k8s_job_params(params)
    # Configureate Pod template container
    unique_name = f"{params['name']}-{uuid.uuid4().hex[:6]}"
    container = client.V1Container(**params)
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": params["name"]}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
    
    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=4)
    
    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=unique_name),
        spec=spec)

    return job