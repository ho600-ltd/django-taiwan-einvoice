#!/usr/bin/env python

# WS client example

import asyncio, json
import websockets


async def hello():
    uri = "ws://localhost:8000/ws/chat/lobby/"
    async with websockets.connect(uri) as websocket:
        i = 0
        while True:
            print(i)
            J = await websocket.recv()
            message = json.loads(J)['message']
            print(f"< {message}")
            i += 1


if '__main__' == __name__:
    asyncio.get_event_loop().run_until_complete(hello())