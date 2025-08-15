from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import uuid

router = APIRouter()

# --- Gerenciamento de Estado do Servidor ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            return len(self.active_connections.get(room_id, [])) == 0
        return False
    
    async def broadcast(self, message: str, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

manager = ConnectionManager()
active_rooms: set[str] = set()


# --- Endpoints da API ---

@router.post("/rooms", tags=["API"])
async def create_room():
    """Cria uma nova sala de chat e retorna seu ID"""
    room_id = str(uuid.uuid4().hex)[:10]
    active_rooms.add(room_id)
    print(f"Sala criada: {room_id}. Salas ativas: {active_rooms}")
    return {"room_id": room_id}

@router.get("/rooms/{room_id}", tags=["API"])
async def get_room(room_id: str):
    """Verifica se uma sala de chat existe"""
    if room_id not in active_rooms:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    return {"room_id": room_id, "exists": True}


# --- Endpoint WebSocket ---

@router.websocket("/ws/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):
    if room_id not in active_rooms:
        await websocket.close(code=4000)
        return

    await manager.connect(websocket, room_id)
    await manager.broadcast(f'{{"type": "user_joined", "user": "{username}", "message": "{username} entrou na sala."}}', room_id)
    
    try:
        while True:
            data_str = await websocket.receive_text()
            await manager.broadcast(data_str, room_id)
    except WebSocketDisconnect:
        is_empty = manager.disconnect(websocket, room_id)
        await manager.broadcast(f'{{"type": "user_left", "user": "{username}", "message": "{username} saiu da sala."}}', room_id)
        if is_empty:
            if room_id in active_rooms:
                active_rooms.remove(room_id)
                print(f"Sala {room_id} ficou vazia e foi excluída.")
                if room_id in manager.active_connections:
                    del manager.active_connections[room_id]