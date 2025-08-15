from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from server.services.room_manager import room_manager

router = APIRouter()

# Configura o diretório de templates para este roteador
templates = Jinja2Templates(directory="client/templates")

@router.get("/", response_class=HTMLResponse, tags=["Pages"])
async def get_landing_page(request: Request):
    """Serve a página inicial (land.html)"""
    return templates.TemplateResponse("land.html", {"request": request})

@router.get("/sala/{sala_id}", response_class=HTMLResponse, tags=["Pages"])
async def get_chat_page(request: Request, sala_id: str):
    """Serve a página de chat da sala caso exista"""
    if not room_manager.room_exists(sala_id):
        return HTMLResponse(content="<h1>Sala não encontrada ou expirou!</h1>", status_code=404)
    return templates.TemplateResponse("chat.html", {"request": request, "sala_id": sala_id})