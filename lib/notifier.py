import asyncio
from .utils import dumps, loads
from .database import get_autocommit_conn_for

conn = get_autocommit_conn_for("bareflow")
curs = conn.cursor()

USERS = set()


async def register(websocket):
    USERS.add(websocket)


async def unregister(websocket):
    USERS.remove(websocket)


async def notify():
    conn = get_autocommit_conn_for("bareflow")
    curs = conn.cursor()
    curs.execute("LISTEN updates")
    while True:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            event = dict(type="event", event=loads(notify.payload))
            if USERS:
                await asyncio.wait([user.send(dumps(event)) for user in USERS])

        await asyncio.sleep(1)
