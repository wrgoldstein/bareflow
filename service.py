"""
1. Be able to send a hello world job to k8s by script and parse output [x]
2. Write the most basic UI
3. Write the most basic scheduler
4. Implement dependencies
5. Separate library code from dags
"""

import importlib.util
import uuid
# from concurrent.futures import ThreadPoolExecutor #TODO
from pathlib import Path

from kubernetes import client, config, watch
from flow import jobs

paths = Path('dags').glob('*.py')  #TODO nested
for path in paths:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)


config.load_kube_config()
watcher = watch.Watch()
batch_v1 = client.BatchV1Api()
v1 = client.CoreV1Api()


def run_job(job):
    # todo: threadpool / async
    job_name = job.metadata.name
    api_response = batch_v1.create_namespaced_job(
            body=job,
            namespace="default"
    )

    status = None
    while status is None:  #TODO timeout
        print('.', uuid.uuid4().hex)
        status = batch_v1.read_namespaced_job_status(namespace="default", name=job.metadata.name).status.start_time

    print(f"status: {status}", )
    
    pods = v1.list_namespaced_pod(namespace='default', label_selector='job-name={}'.format(job_name))
    pod = pods.items[0]  #TODO: don't just naively get the first pod

    running = False
    while not running:  #TODO timeout
        running = v1.read_namespaced_pod_status(namespace="default", name=pod.metadata.name).status.phase == "Running"

    for e in watcher.stream(v1.read_namespaced_pod_log, name=pod.metadata.name, namespace="default"):
        print(e)
