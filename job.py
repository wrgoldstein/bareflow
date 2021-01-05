"""
1. Be able to send a hello world job to k8s by script and parse output [x]
2. Write the most basic UI
3. Write the most basic scheduler
4. Implement dependencies
5. Separate library code from dags
"""
from enum import unique
import uuid
from kubernetes import client, config, watch


def create_job_object(**params):
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
    print(unique_name)
    return job



if __name__ == "__main__":
    import sys
    import importlib

    name = sys.argv[1]
    params = importlib.import_module(name).job()
    params['name'] = "pi"#name.replace(".", "_").strip()
    print(params)

    job = create_job_object(**params)
    config.load_kube_config()
    watcher = watch.Watch()

    
    batch_v1 = client.BatchV1Api()
    v1 = client.CoreV1Api()

    api_response = batch_v1.create_namespaced_job(
            body=job,
            namespace="default"
    )

    
    job_name = job.metadata.name
    status = None
    while status is None:  # todo timeout
        print('.', uuid.uuid4().hex)
        status = batch_v1.read_namespaced_job_status(namespace="default", name=job.metadata.name).status.start_time

    print(f"status: {status}", )
    
    pods = v1.list_namespaced_pod(namespace='default', label_selector='job-name={}'.format(job_name))
    pod = pods.items[0]  # todo: don't just naively get the first pod

    running = False
    while not running:  # todo timeout
        running = v1.read_namespaced_pod_status(namespace="default", name=pod.metadata.name).status.phase == "Running"

    for e in watcher.stream(v1.read_namespaced_pod_log, name=pod.metadata.name, namespace="default"):
        print(e)
