from fastapi import APIRouter, HTTPException
from server.services.room_manager import room_manager

router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)

@router.post("/", status_code=201)
async def create_room():
    """Cria uma nova sala de chat e retorna seu ID."""
    room_id = room_manager.create_room()
    return {"room_id": room_id}

@router.get("/")
async def list_active_rooms():
    """Lista todas as salas ativas."""
    return {"rooms": room_manager.list_rooms()}

@router.get("/{room_id}")
async def get_room(room_id: str):
    """Verifica se uma sala de chat existe."""
    if not room_manager.room_exists(room_id):
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    return {"room_id": room_id, "exists": True}