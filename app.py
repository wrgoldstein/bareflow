import asyncio
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

from aiofile import async_open
from sanic import Sanic, response
from sanic.websocket import WebSocketProtocol
from websockets.exceptions import ConnectionClosed

import service
from flow import create_job_object

app = Sanic("bare_flow")
app.static('/public', './build')

@app.route("/")
async def index(request):
    return await response.file('build/index.html')


@app.route("/dags/<dag>")
async def index_with_route(request, dag):
    return await response.file('build/index.html')


@app.route("/api/logs/<pod>")
async def logs(request, pod):
    async def main(res):
      async with async_open(f"pod-logs/{pod}", 'r') as afp:
          while True:
            line = await afp.readline()
            if line != "":
              await res.write(line)

    # obviously this will have to be extended to different task runs
    return response.stream(main)

@app.route("/run/<dag_id>", methods=["POST"])
async def run(request, dag_id):
    job = create_job_object(service.jobs[dag_id])
    pod_name = service.run_job(job)

    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     executor.submit(service.tail_pod_log, pod_name)

    service.tail_pod_log(pod_name)

    return response.json({
        "pod_name": pod_name
    })

clients = {}

@app.websocket("/ws")
async def feed(request, ws):
    _id = uuid.uuid4().hex
    clients[_id] = ws

    # Send the client its socket ID
    data = dict(type="sid", sid=_id)
    await ws.send(json.dumps(data))

    # Send initial dag details
    await ws.send(json.dumps(dict(type="dags", dags=service.jobs)))

    while True:
        try:
            data = json.loads(await ws.recv())
            if data["type"] == "requestConfigs":
                await send_config_names(ws)
        except ConnectionClosed:
            clients.pop(_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000, protocol=WebSocketProtocol)
