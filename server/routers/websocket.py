import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from server.services.connection_manager import connection_manager 
from server.services.room_manager import room_manager 

router = APIRouter(
    prefix="/ws",
    tags=["WebSocket"]
)

@router.websocket("/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):
    if not room_manager.room_exists(room_id):
        await websocket.close(code=1008) 
        return

    await connection_manager.connect(websocket, room_id)
    
    join_payload = {"type": "user_joined", "user": username, "message": f"{username} entrou na sala."}
    await connection_manager.broadcast(join_payload, room_id)
    
    try:
        while True:
            data_str = await websocket.receive_text()
            try:
                payload = json.loads(data_str)
                payload['user'] = username 
                await connection_manager.broadcast(payload, room_id)
            except json.JSONDecodeError:
                print(f"Mensagem mal formatada recebida de {username}")

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, room_id)
        left_payload = {"type": "user_left", "user": username, "message": f"{username} saiu da sala."}
        await connection_manager.broadcast(left_payload, room_id)