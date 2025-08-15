from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import api, pages

# Cria a instância principal da aplicação FastAPI
app = FastAPI(title="Disposable Chat")

# Monta o diretório 'static' para servir CSS, JS, etc.
app.mount("/static", StaticFiles(directory="client/static"), name="static")

# Inclui os roteadores na aplicação principal
app.include_router(pages.router)
app.include_router(api.router)

@app.get("/health", tags=["System"])
async def health_check():
    """Endpoint simples para verificar se a API está no ar."""
    return {"status": "ok"}