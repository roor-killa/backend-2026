
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_route#, documents, drive, chat
from app.database import create_tables

app = FastAPI(
    title="KaribDocs API",
    description="🌴 Backoffice intelligent de gestion documentaire — Université des Antilles",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    create_tables()

app.include_router(auth_route.router, prefix="/auth", tags=["Authentification"])
# app.include_router(documents.router, prefix="/documents", tags=["Documents"])
# app.include_router(drive.router,     prefix="/drive",     tags=["Google Drive"])
# app.include_router(chat.router,      prefix="/chat",      tags=["Chatbot IA"])

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "KaribDocs", "version": "1.0.0"}