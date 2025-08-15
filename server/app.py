from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import pages, rooms, websocket

app = FastAPI(
    title="Disposable Chat API",
    description="Uma API para criar salas de chat em tempo real.",
    version="1.0.0"
)


app.mount("/static", StaticFiles(directory="client/static"), name="static")

app.include_router(pages.router)
app.include_router(rooms.router)
app.include_router(websocket.router)

@app.get("/health", tags=["System"])
async def health_check():
    """Endpoint simples para verificar se a API está no ar."""
    return {"status": "ok"}