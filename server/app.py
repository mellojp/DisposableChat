from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import rooms, websocket, sessions

app = FastAPI(
    title="Live Chat API",
    description="Uma API para criar salas de chat em tempo real com sistema de sessões.",
    version="2.0.0"
)

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://mellojp.github.io",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routers
app.include_router(sessions.router) 
app.include_router(rooms.router)
app.include_router(websocket.router)

@app.get("/health", tags=["System"])
async def health_json():
    return {"status": "ok", "version": "2.0.0"}

@app.head("/ping")
async def ping():
    return Response(status_code=200)
