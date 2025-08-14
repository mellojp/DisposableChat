import os
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Set

# --- Configuração do App e Templates ---
app = FastAPI()

# Monta a pasta 'static' para servir arquivos como CSS e JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura o diretório de templates para servir o HTML
templates = Jinja2Templates(directory="templates")


# --- Gerenciamento de Estado do Servidor ---

class ConnectionManager:
    """Gerencia as conexões WebSocket ativas para cada sala."""
    def __init__(self):
        # Dicionário para mapear sala_id para uma lista de conexões WebSocket
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        """Aceita uma nova conexão e a adiciona à sala."""
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        """Remove uma conexão da sala."""
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            # Retorna True se a sala ficou vazia, False caso contrário
            return len(self.active_connections[room_id]) == 0
        return False

    async def broadcast(self, message: str, room_id: str):
        """Envia uma mensagem para todos os clientes na mesma sala."""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

# Instância única do gerenciador e um set para as salas ativas
manager = ConnectionManager()
active_rooms: Set[str] = set()


# --- Endpoints HTTP ---

@app.get("/", response_class=HTMLResponse)
async def get_landing_page(request: Request):
    """Serve a página inicial (landing page)."""
    return templates.TemplateResponse("land.html", {"request": request})

@app.get("/sala/create")
async def create_room():
    """Cria uma nova sala com um ID único e a adiciona à lista de salas ativas."""
    room_id = str(uuid.uuid4().hex)[:6]  # Gera um ID curto
    active_rooms.add(room_id)
    print(f"Sala criada: {room_id}. Salas ativas: {active_rooms}")
    # Redireciona o usuário para a página da sala (o JS do frontend fará isso)
    # Apenas retornamos o ID para ser usado pelo frontend
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/sala/{room_id}")

@app.post("/sala/join/{room_id}")
async def join_room(room_id: str):
    """Verifica se uma sala existe antes de permitir o join."""
    if room_id in active_rooms:
        return {"status": "ok", "room_id": room_id}
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Sala não encontrada")

@app.get("/sala/{sala_id}", response_class=HTMLResponse)
async def get_chat_page(request: Request, sala_id: str):
    """Serve a página de chat se a sala existir."""
    if sala_id in active_rooms:
        return templates.TemplateResponse("chat.html", {"request": request, "sala_id": sala_id})
    else:
        return HTMLResponse(content="<h1>Sala não encontrada ou expirou!</h1>", status_code=404)


# --- Endpoint WebSocket ---

@app.websocket("/ws/{sala_id}")
async def websocket_endpoint(websocket: WebSocket, sala_id: str):
    """Lida com a conexão WebSocket para uma sala de chat."""
    if sala_id not in active_rooms:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, sala_id)
    
    # Informa a todos na sala que um novo usuário entrou
    initial_data = await websocket.receive_json()
    username = initial_data.get("user", "Anônimo")
    await manager.broadcast(f'{{"user": "Sistema", "message": "{username} entrou na sala."}}', sala_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Envia a mensagem para todos na sala
            await manager.broadcast(data, sala_id)
    except WebSocketDisconnect:
        # --- LÓGICA PRINCIPAL PARA EXCLUIR A SALA ---
        # 1. Desconecta o usuário
        is_room_empty = manager.disconnect(websocket, sala_id)
        
        # Informa que o usuário saiu
        await manager.broadcast(f'{{"user": "Sistema", "message": "{username} saiu da sala."}}', sala_id)

        # 2. Se a sala ficou vazia, remove-a da lista de salas ativas
        if is_room_empty:
            if sala_id in active_rooms:
                active_rooms.remove(sala_id)
                print(f"Sala {sala_id} ficou vazia e foi excluída. Salas ativas: {active_rooms}")
                # Também remove a entrada do dicionário no manager para limpar a memória
                del manager.active_connections[sala_id]


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
