import asyncio
import json

import aiofiles
from sanic import Sanic, response
from sanic.websocket import WebSocketProtocol

from lib import service, pod_log

app = Sanic("bare_flow")
app.static("/public", "./build")


USERS = set()


def get_users():
    return len(USERS)


async def eventing(queue):
    while True:
        event = await queue.get()
        if USERS:
            await asyncio.wait([user.send(json.dumps(event)) for user in USERS])
        queue.task_done()
        await asyncio.sleep(3)


async def register(websocket):
    USERS.add(websocket)


async def unregister(websocket):
    USERS.remove(websocket)


@app.route("/")
async def index(request):
    return await response.file("build/index.html")


@app.route("/flows/<flow>")
async def index_with_route(request, flow):
    return await response.file("build/index.html")


@app.route("/api/logs/<pod>")
async def logs(request, pod):
    return await pod_log.tail_log(pod)


@app.route("/run/<flow_id>", methods=["POST"])
async def run(request, flow_id):
    flow = service.flows[flow_id]
    flow_run = await service.schedule_flow(flow_id, flow)
    # This will run the flow in the background. The status
    # will be updated in the `flow_runs` table in the database.
    return response.json(flow_run)


clients = {}


async def msg(ws, type, **body):
    await ws.send(json.dumps(dict(type=type, **body)))


@app.websocket("/ws")
async def feed(request, ws):
    await register(ws)
    try:
        # Send initial flow details
        await msg(ws, "initialize", **service.get_flows())
        async for message in ws:
            # We don't expect to receive any messages but this keeps the connection alive
            json.loads(message)
    finally:
        await unregister(ws)


@app.listener("after_server_start")
def start_scheduler(app, loop):
    app.add_task(service.scheduler())
    app.queue = asyncio.Queue(loop=loop)
    service.queue = app.queue
    app.add_task(eventing(app.queue))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000, protocol=WebSocketProtocol)
