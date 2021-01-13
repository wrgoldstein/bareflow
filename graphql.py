import os
import requests
import json

url = os.getenv("HASURA_ENDPOINT", "http://localhost:8080/v1/graphql")

def create_flow_run_and_steps(flow_id: str, steps: list):
    flow_run_steps = []
    for step in steps:
        name = step["name"]
        image = step["image"]
        command = step["command"]
        flow_run_step = f'{{ name: "{name}", image: "{image}", command: {json.dumps(command)},  status: "created" }}'

        flow_run_steps.append(flow_run_step)
    
    flow_run_steps = ",\n".join(flow_run_steps)

    q = f"""
    mutation MyMutation {{
        insert_flow_runs_one(object: {{
            flow_run_steps: {{   data: [{flow_run_steps}] }},
            flow_id: "{flow_id}", 
            status: "created"
        }}) 
        {{
            id
            created_at
            flow_id
            flow_run_steps {{ 
                id
                name
                image
                command
                status
            }}
        }}
    }}
    """
    return requests.post(url, json=dict(query=q)).json()["data"]['insert_flow_runs_one']


def update_flow_run(flow_run_id, **kwargs):
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
            status
        }}
    }}
    """
    return requests.post(url, json=dict(query=q)).json()["data"]


def update_flow_run_step(flow_run_step_id, **kwargs):
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
            status
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
    return requests.post(url, json=dict(query=q)).json()["data"]["update_flow_run_steps_by_pk"]


def get_flow_run(flow_run_id, **kwargs):
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
                    pod_name
                    status
                }}
            }}
        }}
        """
    return requests.post(url, json=dict(query=q)).json()["data"]["flow_runs"]


def get_flow_run_step(flow_run_step_id: int):
    q = f"""
    query MyQuery {{
        flow_run_steps(where: {{ id: {{_eq: {flow_run_step_id}  }}  }}) {{
            command
            image
            pod_name
            status
        }}
    }}
    """
    return requests.post(url, json=dict(query=q)).json()["data"]["flow_run_steps"][0]


def get_flow_run_steps_by_nin_status(status: list):
    status = f"""{','.join([f'"{x}"' for x in status])}"""
    q = f"""
    query MyQuery {{
        flow_run_steps(where: {{status: {{_nin: [{status}] }} }}) {{
            id
            name
            image
            status
            pod_name
            command
        }}
    }}
    """
    return requests.post(url, json=dict(query=q)).json()["data"]["flow_run_steps"]


def get_flow_runs():
    q = """
    query MyQuery {
        flow_runs {
            id
            flow_id
            flow_run_steps {
                started_at
                ended_at
                status
                name
                pod_name
                image
                command
            }
        }
    }
    """
    return requests.post(url, json=dict(query=q)).json()["data"]["flow_runs"]
