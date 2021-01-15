import asyncio
import json

from sanic import Sanic, response
from sanic.websocket import WebSocketProtocol

from lib import flow_finder, tail, notifier, scheduler
from lib.utils import dumps
from lib.database import query


app = Sanic("bare_flow")
app.static("/public", "./build")


@app.route("/")
async def index(request):
    return await response.file("build/index.html")


@app.route("/flows/<flow>")
async def index_with_route(request, flow):
    return await response.file("build/index.html")


@app.route("/api/logs/<pod>")
async def logs(request, pod):
    async def main(res):
        async for line in tail.tail(pod):
            await res.write(line)

    return response.stream(main)


@app.route("/run/<flow_id>", methods=["POST"])
async def run(request, flow_id):
    flow = flow_finder.flows[flow_id]
    flow_run_steps = await scheduler.schedule_flow(flow_id, flow)
    # This will run the flow in the background. The status
    # will be updated in the `flow_runs` table in the database.
    return response.json(flow_run_steps, dumps=dumps)


clients = {}


async def msg(ws, type, **body):
    await ws.send(dumps(dict(type=type, **body)))


@app.websocket("/ws")
async def feed(request, ws):
    await notifier.register(ws)
    try:
        # Send initial flow details
        data = dict(flows=flow_finder.flows, flow_run_steps=query.get_steps_for_n_flow_runs(25))
        await msg(ws, "initialize", **data)
        async for message in ws:
            # We don't expect to receive any messages but this keeps the connection alive
            json.loads(message)
    finally:
        await notifier.unregister(ws)


@app.listener("after_server_start")
def start_scheduler(app, loop):
    app.add_task(notifier.notify())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, protocol=WebSocketProtocol)
