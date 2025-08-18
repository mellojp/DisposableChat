from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from ..models.session import CreateSessionRequest, SessionResponse
from ..services.session_manager import session_manager

router = APIRouter(prefix="/sessions", tags=["Sessions"])
security = HTTPBearer()

# Função auxiliar para validar sessões
async def get_current_session(token = Depends(security)):
    session = session_manager.get_session(token.credentials)
    if not session:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada")
    return session

@router.post("/", status_code=201)
async def create_session(request: CreateSessionRequest) -> dict:
    """Cria uma nova sessão de usuário"""
    username = request.username.strip()
    if not username or len(username) < 2:
        raise HTTPException(status_code=400, detail="Username deve ter pelo menos 2 caracteres")
    
    if len(username) > 50:
        raise HTTPException(status_code=400, detail="Username muito longo (máximo 50 caracteres)")
    
    session_id = session_manager.create_session(username)
    return {"session_id": session_id}

@router.get("/me")
async def get_current_session_info(session = Depends(get_current_session)) -> SessionResponse:
    """Obtém informações da sessão atual"""
    return SessionResponse(
        session_id=session.session_id,
        username=session.username,
        joined_rooms=session.joined_rooms
    )

@router.delete("/me")
async def delete_session(token = Depends(security)):
    """Encerra a sessão atual"""
    session_manager.remove_session(token.credentials)
    return {"message": "Sessão encerrada"}