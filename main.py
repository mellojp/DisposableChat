import os
import uuid
import json # Importe a biblioteca JSON
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException

# --- Configuração do App e Templates ---
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- Gerenciamento de Estado do Servidor ---

class ConnectionManager:
    """Gerencia as conexões WebSocket ativas para cada sala."""
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

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
            return len(self.active_connections[room_id]) == 0
        return False

    async def broadcast(self, message: str, room_id: str):
        """Envia uma mensagem para todos os clientes na mesma sala."""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

    async def broadcast_to_others(self, message: str, room_id: str, sender: WebSocket):
        """Envia uma mensagem para todos, exceto para o remetente."""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if connection != sender:
                    await connection.send_text(message)

# Instância única do gerenciador e um set para as salas ativas
manager = ConnectionManager()
active_rooms: set[str] = set()


# --- Endpoints HTTP ---

@app.get("/", response_class=HTMLResponse)
async def get_landing_page(request: Request):
    return templates.TemplateResponse("land.html", {"request": request})

@app.get("/sala/create")
async def create_room():
    room_id = str(uuid.uuid4().hex)[:10]
    active_rooms.add(room_id)
    print(f"Sala criada: {room_id}. Salas ativas: {active_rooms}")
    return RedirectResponse(url=f"/sala/{room_id}")

@app.post("/sala/join/{room_id}")
async def join_room(room_id: str):
    if room_id in active_rooms:
        return {"status": "ok", "room_id": room_id}
    else:
        raise HTTPException(status_code=404, detail="Sala não encontrada")

@app.get("/sala/{sala_id}", response_class=HTMLResponse)
async def get_chat_page(request: Request, sala_id: str):
    if sala_id in active_rooms:
        return templates.TemplateResponse("chat.html", {"request": request, "sala_id": sala_id})
    else:
        return HTMLResponse(content="<h1>Sala não encontrada ou expirou!</h1>", status_code=404)


# --- Endpoint WebSocket ---

# --- Endpoint WebSocket ---

@app.websocket("/ws/{sala_id}")
async def websocket_endpoint(websocket: WebSocket, sala_id: str):
    if sala_id not in active_rooms:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, sala_id)
    
    username = None # Começa como None
    try:
        # A primeira mensagem DEVE ser um JSON com o nome de usuário
        initial_data = await websocket.receive_json()
        # Pega o nome de usuário, removendo espaços em branco no início/fim
        username = initial_data.get("user", "").strip()

        # Se o nome de usuário estiver vazio ou for nulo, rejeita a conexão
        if not username:
            print(f"Conexão rejeitada para sala {sala_id}: nome de usuário não fornecido.")
            await websocket.close(code=1008) # Fecha a conexão
            manager.disconnect(websocket, sala_id) # Remove do gerenciador
            return

        # Se o nome for válido, anuncia a entrada do usuário
        await manager.broadcast(f'{{"user": "Sistema", "message": "{username} entrou na sala."}}', sala_id)
        
        # Continua o loop de mensagens normal
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            if data.get("type") == "typing":
                await manager.broadcast_to_others(data_str, sala_id, websocket)
            else:
                await manager.broadcast(data_str, sala_id)

    except WebSocketDisconnect:
        # Se o usuário nunca chegou a fornecer um nome válido, não há mensagem de saída a enviar
        if username:
            is_room_empty = manager.disconnect(websocket, sala_id)
            await manager.broadcast(f'{{"user": "Sistema", "message": "{username} saiu da sala."}}', sala_id)

            if is_room_empty:
                if sala_id in active_rooms:
                    active_rooms.remove(sala_id)
                    print(f"Sala {sala_id} ficou vazia e foi excluída. Salas ativas: {active_rooms}")
                    if sala_id in manager.active_connections:
                        del manager.active_connections[sala_id]
        else:
            # Apenas desconecta se o usuário saiu antes de se identificar
            manager.disconnect(websocket, sala_id)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)