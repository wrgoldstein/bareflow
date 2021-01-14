import os
import requests
import json
from typing import List

url = os.getenv("HASURA_ENDPOINT", "http://localhost:8080/v1/graphql")


def create_flow_run_and_steps(flow_id: str, steps: List[dict]) -> dict:
    flow_run_steps = []
    for step in steps:
        name = step["name"]
        image = step["image"]
        command = step["command"]
        depends_on = step["depends_on"]
        flow_run_step = f"""
        {{ name: "{name}", depends_on: {json.dumps(depends_on)}, image: "{image}", command: {json.dumps(command)},  status: "created" }}
        """

        flow_run_steps.append(flow_run_step)

    flow_run_steps = ",\n".join(flow_run_steps)

    q = f"""
            mutation CreateRun {{
            insert_flow_runs(objects: [
                {{ 
                    flow_id: "{flow_id}", 
                    flow_run_steps: {{
                        data: [{flow_run_steps}]
                    }} 
                }}]) 
                {{
                returning {{
                    id
                    flow_id
                    flow_run_steps {{
                        id
                        flow_run_id
                        name
                        image
                        command
                        status
                    }}
                }}
            }}
        }}
    """
    return requests.post(url, json=dict(query=q)).json()["data"]["insert_flow_runs"]["returning"]


def update_flow_run(flow_run_id: int, **kwargs) -> dict:
    _set = ""
    for key, value in kwargs.items():
        _set += f'\n{key}: "{value}"\n'

    q = f"""
    mutation UpdateFlowRun {{
        update_flow_runs_by_pk (
            pk_columns: {{ id: {flow_run_id} }}
            _set: {{ {_set} }}
        ) {{
            id
            flow_id
            status
        }}
    }}
    """
    return requests.post(url, json=dict(query=q)).json()["data"]


def update_flow_run_step(flow_run_step_id: int, **kwargs) -> dict:
    _set = ""
    for key, value in kwargs.items():
        _set += f'\n{key}: "{value}"\n'

    q = f"""
    mutation UpdateFlowRun {{
        update_flow_run_steps_by_pk (
            pk_columns: {{ id: {flow_run_step_id} }}
            _set: {{ {_set} }}
        ) {{
            id
            name
            flow_run_id
            status
            image
            command
            pod_name
            started_at
            ended_at
            flow_run {{
                flow_id
                id
            }}
        }}
    }}
    """
    res = requests.post(url, json=dict(query=q)).json()
    return res["data"]["update_flow_run_steps_by_pk"]


def get_flow_run(flow_run_id: int, **kwargs) -> dict:
    q = f"""
        query MyQuery {{
            flow_runs(where: {{id: {{_eq: {flow_run_id} }} }}) {{
                id
                started_at
                status
                updated_at
                flow_id
                created_at
                ended_at
                flow_run_steps {{
                    id
                    name
                    flow_run_id
                    image
                    command
                    pod_name
                    status
                }}
            }}
        }}
        """
    return requests.post(url, json=dict(query=q)).json()["data"]["flow_runs"]


def get_flow_run_step(flow_run_step_id: int) -> dict:
    q = f"""
    query MyQuery {{
        flow_run_steps(where: {{ id: {{_eq: {flow_run_step_id}  }}  }}) {{
            id
            name
            flow_run_id
            command
            image
            pod_name
            status
        }}
    }}
    """
    return requests.post(url, json=dict(query=q)).json()["data"]["flow_run_steps"][0]


def get_flow_run_steps_by_nin_status(status: list) -> dict:
    status = f"""{','.join([f'"{x}"' for x in status])}"""
    q = f"""
    query MyQuery {{
        flow_run_steps(where: {{status: {{_nin: [{status}] }} }}) {{
            id
            flow_run_id
            name
            image
            status
            pod_name
            command
        }}
    }}
    """
    return requests.post(url, json=dict(query=q)).json()["data"]["flow_run_steps"]


def get_flow_runs(limit: int) -> dict:
    q = f"""
    query MyQuery {{
        flow_runs (
            order_by: {{ id: desc }}
            limit: {limit}
        ) {{
            id
            flow_id
            flow_run_steps {{
                id
                flow_run_id
                started_at
                ended_at
                status
                name
                pod_name
                image
                command
            }}
        }}
    }}
    """
    return requests.post(url, json=dict(query=q)).json()["data"]["flow_runs"]
