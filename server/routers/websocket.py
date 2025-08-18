import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from ..services import connection_manager, room_manager, session_manager, message_manager

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, 
                           session_id: str = Query(...)):
    
    # Valida sessão
    session = session_manager.get_session(session_id)
    if not session:
        await websocket.close(code=1008)
        return
    
    username = session.username
    
    # Valida sala
    if not room_manager.room_exists(room_id):
        await websocket.close(code=1008) 
        return

    await connection_manager.connect(websocket, room_id)
    
    # Adiciona sala à sessão do usuário se não estiver lá
    session_manager.add_room_to_session(session_id, room_id)
    
    # Registra mensagem de entrada e envia
    join_message = message_manager.add_message(
        room_id, "user_joined", username, f"{username} entrou na sala."
    )
    await connection_manager.broadcast(join_message.model_dump(), room_id)
    
    try:
        while True:
            data_str = await websocket.receive_text()
            try:
                payload = json.loads(data_str)
                
                if payload.get('type') == 'chat':
                    content = payload.get('message', '').strip()
                    if content:  # Só salva se não estiver vazio
                        # Salva mensagem no backend
                        message = message_manager.add_message(
                            room_id, 'chat', username, content
                        )
                        await connection_manager.broadcast(message.model_dump(), room_id)
                        
                elif payload.get('type') == 'typing':
                    # Não salva typing, apenas broadcast
                    payload['user'] = username
                    await connection_manager.broadcast(payload, room_id)
                    
            except json.JSONDecodeError:
                print(f"Mensagem mal formatada recebida de {username}")

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, room_id)
        
        # Registra mensagem de saída
        leave_message = message_manager.add_message(
            room_id, "user_left", username, f"{username} saiu da sala."
        )
        await connection_manager.broadcast(leave_message.model_dump(), room_id)