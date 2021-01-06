import uuid
import json
from sanic import Sanic, response
from sanic.websocket import WebSocketProtocol

import service

app = Sanic("bare_flow")

app.static('/public', './build')


@app.route("/")
async def index(request):
    return await response.file('build/index.html')

@app.route("/dags")
async def dags(request): 
    return response.json({"dags": []}) 

@app.route("/run")
async def run(request): 
    return response.text("ok")


clients = {}

@app.websocket("/ws")
async def feed(request, ws):
    _id = uuid.uuid4().hex
    clients[_id] = ws

    # Send the client its socket ID
    data = dict(type="sid", sid=_id)
    await ws.send(json.dumps(data))

    # Send initial dag details
    jobs = [j['details'] for j in service.jobs.values()]
    await ws.send(json.dumps(dict(type="dags", dags=jobs)))

    while True:
        try:
            data = json.loads(await ws.recv())
            if data["type"] == "requestConfigs":
                await send_config_names(ws)
        except ConnectionClosed:
            clients.pop(_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000, protocol=WebSocketProtocol)
