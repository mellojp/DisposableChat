from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import pages, rooms, websocket, sessions

app = FastAPI(
    title="Disposable Chat API",
    description="Uma API para criar salas de chat em tempo real com sistema de sessões.",
    version="2.0.0"
)

# Arquivos estáticos
app.mount("/static", StaticFiles(directory="client/static"), name="static")

# Routers
app.include_router(pages.router)
app.include_router(sessions.router) 
app.include_router(rooms.router)
app.include_router(websocket.router)

@app.get("/health", tags=["System"])
async def health_check():
    """Endpoint simples para verificar se a API está no ar."""
    return {"status": "ok", "version": "2.0.0"}