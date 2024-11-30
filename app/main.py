from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .config import settings
from app.services.auth import init_db

app = FastAPI(title="Dateonic API")

# Event startup musi być po utworzeniu app
@app.on_event("startup")
async def startup_event():
    init_db()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dodajemy wszystkie routery
app.include_router(router, prefix="/api")