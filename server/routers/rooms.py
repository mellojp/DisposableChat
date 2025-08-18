from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from ..models.room import RoomResponse, RoomListResponse
from ..services import room_manager, session_manager, message_manager, connection_manager

router = APIRouter(prefix="/rooms", tags=["Rooms"])
security = HTTPBearer()

# Função auxiliar para validar sessões
async def get_current_session(token = Depends(security)):
    session = session_manager.get_session(token.credentials)
    if not session:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada")
    return session

@router.post("/", status_code=201)
async def create_room(session = Depends(get_current_session)):
    """Cria uma nova sala de chat e adiciona à sessão do usuário"""
    room_id = room_manager.create_room()
    session_manager.add_room_to_session(session.session_id, room_id)
    return {"room_id": room_id}

@router.get("/")
async def list_user_rooms(session = Depends(get_current_session)) -> RoomListResponse:
    """Lista as salas que o usuário participa"""
    # Filtra apenas salas que ainda existem
    valid_rooms = [room_id for room_id in session.joined_rooms 
                   if room_manager.room_exists(room_id)]
    
    # Atualiza a sessão removendo salas inexistentes
    session.joined_rooms = valid_rooms
    
    return RoomListResponse(rooms=valid_rooms)

@router.get("/all")
async def list_all_active_rooms() -> RoomListResponse:
    """Lista todas as salas ativas (sem autenticação necessária)"""
    return RoomListResponse(rooms=room_manager.list_rooms())

@router.get("/{room_id}")
async def get_room_info(room_id: str) -> RoomResponse:
    """Verifica se uma sala existe e retorna informações básicas"""
    if not room_manager.room_exists(room_id):
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    user_count = connection_manager.get_room_user_count(room_id)
    return RoomResponse(room_id=room_id, exists=True, user_count=user_count)

@router.post("/{room_id}/join")
async def join_room(room_id: str, session = Depends(get_current_session)):
    """Adiciona uma sala à lista de salas do usuário"""
    if not room_manager.room_exists(room_id):
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    session_manager.add_room_to_session(session.session_id, room_id)
    return {"message": f"Entrou na sala {room_id}"}

@router.delete("/{room_id}/leave")
async def leave_room(room_id: str, session = Depends(get_current_session)):
    """Remove uma sala da lista de salas do usuário"""
    session_manager.remove_room_from_session(session.session_id, room_id)
    return {"message": f"Saiu da sala {room_id}"}

@router.get("/{room_id}/messages")
async def get_room_messages(room_id: str, limit: int = 50, 
                           session = Depends(get_current_session)):
    """Obtém o histórico de mensagens de uma sala"""
    if not room_manager.room_exists(room_id):
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    messages = message_manager.get_room_messages(room_id, limit)
    return {"messages": [msg.model_dump() for msg in messages]}
