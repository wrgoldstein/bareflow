import asyncio
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

from aiofile import async_open
from sanic import Sanic, response
from sanic.websocket import WebSocketProtocol
from websockets.exceptions import ConnectionClosed

import service

app = Sanic("bare_flow")
app.static('/public', './build')

@app.route("/")
async def index(request):
    return await response.file('build/index.html')


@app.route("/flows/<flow>")
async def index_with_route(request, flow):
    return await response.file('build/index.html')


@app.route("/api/logs/<pod>")
async def logs(request, pod):
    async def main(res):
    #TODO close request when pod is finished running
        async with async_open(f"pod-logs/{pod}", 'r') as afp:
            while True:
                line = await afp.readline()
                if line != "":
                    await res.write(line)

    # obviously this will have to be extended to different task runs
    return response.stream(main)


@app.route("/run/<flow_id>", methods=["POST"])
async def run(request, flow_id):
    flow = service.flows[flow_id]
    service.schedule_flow(flow_id, flow)
    # This will run the flow in the background. The status
    # will be updated in the `flow_runs` table in the database.
    
    return response.empty()


clients = {}

@app.websocket("/ws")
async def feed(request, ws):
    _id = uuid.uuid4().hex
    clients[_id] = ws

    # Send the client its socket ID
    data = dict(type="sid", sid=_id)
    await ws.send(json.dumps(data))

    # Send initial flow details
    await ws.send(json.dumps(dict(type="flows", flows=service.flows)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000, protocol=WebSocketProtocol)
