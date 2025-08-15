from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Importa as salas ativas do nosso módulo de API para verificar se uma sala existe
from .api import active_rooms

router = APIRouter()

# Configura o diretório de templates para este roteador
templates = Jinja2Templates(directory="client/templates")

@router.get("/", response_class=HTMLResponse, tags=["Pages"])
async def get_landing_page(request: Request):
    """Serve a página inicial (land.html)"""
    return templates.TemplateResponse("land.html", {"request": request})

@router.get("/sala/{sala_id}", response_class=HTMLResponse, tags=["Pages"])
async def get_chat_page(request: Request, sala_id: str):
    """Serve a página de chat se a sala existir"""
    if sala_id not in active_rooms:
        return HTMLResponse(content="<h1>Sala não encontrada ou expirou!</h1>", status_code=404)
    return templates.TemplateResponse("chat.html", {"request": request, "sala_id": sala_id})