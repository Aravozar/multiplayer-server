import asyncio
import websockets.client
from main import ConnectionEvent, ConnectionEventEnum
from uuid import uuid4

client_id = uuid4()
async def async_main():
    async with websockets.client.connect(f"ws://localhost:9003/ws/{client_id}") as websocket:
        print("got here")
        await websocket.send("test")


if __name__ == "__main__":
    asyncio.run(async_main())