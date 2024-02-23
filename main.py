
from enum import StrEnum
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn

app = FastAPI()
class PlayerConnection(BaseModel):
    connection_id: str
    websocket: WebSocket

    class Config:
        arbitrary_types_allowed = True


class ConnectionEventEnum(StrEnum):
    DISCONNECT = "DISCONNECT"
    CONNECT = "CONNECT"

class ConnectionEvent(BaseModel):
    event: ConnectionEventEnum
    connection_id: str


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[PlayerConnection] = []

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        player_connection = PlayerConnection(connection_id=client_id, websocket=websocket)
        self.active_connections.append(player_connection)
        
        connection_msg = ConnectionEvent(event=ConnectionEventEnum.CONNECT, connection_id=client_id).model_dump_json()
        await self.broadcast(connection_msg)
        return player_connection

    def disconnect(self, player_connection: PlayerConnection):
        self.active_connections.remove(player_connection)

    async def send_personal_message(self, message: str, player_connection: PlayerConnection):
        await player_connection.websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.websocket.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    player_connection = await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                json_data = json.loads(data)
                print(json_data)
                # await manager.broadcast({})
            except Exception:
                pass
            await manager.broadcast(str(data))
    except WebSocketDisconnect:
        manager.disconnect(player_connection)
        await manager.broadcast(ConnectionEvent(event=ConnectionEventEnum.DISCONNECT, connection_id=client_id))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9003, reload=False)