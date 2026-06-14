from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

import db
from agents.hr_agent import get_hr_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="RH Inteligente", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    mensagem: str
    usuario: str = "Rafael Nunes"
    contador_mensagens: int = 0


@app.get("/")
async def home():
    return FileResponse("static/index.html")


@app.get("/api/health")
async def health():
    return {"status": "online", "servico": "RH Inteligente"}


@app.get("/api/history/{usuario}")
def history(usuario: str):
    historico = db.get_history(usuario)
    return {"historico": historico}


@app.delete("/api/clear")
def clear():
    db.clear_all()
    return {"ok": True}


@app.post("/api/chat")
def chat(request: ChatRequest):
    if not request.mensagem.strip():
        raise HTTPException(status_code=400, detail="Mensagem é obrigatória")

    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY não configurada. Copie .env.example para .env e adicione sua chave.",
        )

    try:
        db.upsert_session(request.usuario)

        # Fetch history BEFORE saving current message so the agent context is clean
        historico = db.get_history(request.usuario)

        db.save_message(request.usuario, "user", request.mensagem)

        resposta = get_hr_response(
            mensagem=request.mensagem,
            usuario=request.usuario,
            historico=historico,
            contador_mensagens=request.contador_mensagens,
        )

        db.save_message(request.usuario, "assistant", resposta)
        return {"resposta": resposta}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {str(e)}")
