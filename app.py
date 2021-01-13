import asyncio
import json
import uuid

from aiofile import async_open
from sanic import Sanic, response
from sanic.websocket import WebSocketProtocol
from websockets.exceptions import ConnectionClosed

import service

app = Sanic("bare_flow")
app.static('/public', './build')


USERS = set()

def get_users():
    return len(USERS)

async def eventing(queue):
    while True:
        try:
            print("notifying")
            print("len users", len(USERS), get_users())
            event = await queue.get()
            if USERS:
                await asyncio.wait([user.send(json.dumps(event)) for user in USERS])
            queue.task_done()
            await asyncio.sleep(3)
        except:
            print("the actual exception was here?")


async def register(websocket):
    USERS.add(websocket)

async def unregister(websocket):
    USERS.remove(websocket)



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

    return response.stream(main)


@app.route("/run/<flow_id>", methods=["POST"])
async def run(request, flow_id):
    flow = service.flows[flow_id]
    await service.schedule_flow(flow_id, flow)
    # This will run the flow in the background. The status
    # will be updated in the `flow_runs` table in the database.
    
    return response.empty()


clients = {}

async def msg(ws, type, **body):
    await ws.send(json.dumps(dict(type=type, **body)))

@app.websocket("/ws")
async def feed(request, ws):
    print("WHAA")
    await register(ws)
    print("LEN", len(USERS))
    try:
        # Send initial flow details
        await msg(ws, "flows", flows=service.get_flows())
        async for message in ws:
            # we don't expect to receive any messages
            data = json.loads(message)
    finally:
        print("unregistering that fool")
        await unregister(ws)


@app.listener('after_server_start')
def start_scheduler(app, loop):
    app.add_task(service.scheduler())
    app.queue = asyncio.Queue(loop=loop)
    service.queue = app.queue
    app.add_task(eventing(app.queue))
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000, protocol=WebSocketProtocol)
