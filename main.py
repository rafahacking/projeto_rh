import os
import secrets
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

import db
from agents.hr_agent import get_hr_response
from rag.ingest import ingest_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    # Pré-carrega o modelo de embeddings na RAM para evitar delay na primeira requisição
    try:
        from rag.retriever import retrieve
        retrieve("warmup")
        print("RAG model loaded and ready.")
    except Exception:
        pass
    yield


app = FastAPI(title="RH Inteligente", version="2.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

_security = HTTPBasic()


def _verify_admin(credentials: HTTPBasicCredentials = Depends(_security)):
    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
    ok_user = secrets.compare_digest(credentials.username.encode(), admin_user.encode())
    ok_pass = secrets.compare_digest(credentials.password.encode(), admin_pass.encode())
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ── Modelos ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    mensagem: str
    usuario: str = "Rafael Nunes"
    contador_mensagens: int = 0


# ── Rotas públicas ───────────────────────────────────────────────────────────

@app.get("/")
async def home():
    return FileResponse("static/index.html")


@app.get("/admin")
async def admin_page():
    return FileResponse("static/admin.html")


@app.get("/api/health")
async def health():
    return {"status": "online", "servico": "RH Inteligente", "versao": "2.0.0"}


@app.get("/api/history/{usuario}")
def history(usuario: str):
    return {"historico": db.get_history(usuario)}


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
            detail="GROQ_API_KEY não configurada. Adicione no arquivo .env.",
        )

    try:
        db.upsert_session(request.usuario)
        historico = db.get_history(request.usuario)
        db.save_message(request.usuario, "user", request.mensagem)

        print(f"\n{'='*60}")
        print(f"[INPUT]  usuario={request.usuario} | msg={request.mensagem!r}")

        resultado = get_hr_response(
            mensagem=request.mensagem,
            usuario=request.usuario,
            historico=historico,
            contador_mensagens=request.contador_mensagens,
        )

        print(f"[OUTPUT] found={not resultado.get('sem_resposta')} | escalar={resultado.get('deve_escalar')} | fontes={resultado.get('fontes')} | resposta={resultado['resposta'][:120]!r}")
        print(f"{'='*60}\n")

        db.save_message(request.usuario, "assistant", resultado["resposta"])

        if resultado.get("sem_resposta"):
            db.save_unanswered(request.usuario, request.mensagem)

        return {
            "resposta": resultado["resposta"],
            "fontes": resultado.get("fontes", []),
            "deve_escalar": resultado.get("deve_escalar", False),
            "fundamentada": resultado.get("fundamentada", True),
        }

    except Exception as e:
        err = str(e).lower()
        if "rate limit" in err or "ratelimit" in err or "tokens per day" in err:
            raise HTTPException(
                status_code=429,
                detail=(
                    "O assistente atingiu o limite de uso do dia no serviço de IA. "
                    "Por favor, aguarde alguns minutos e tente novamente."
                ),
            )
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {str(e)}")


# ── Rotas admin (Basic Auth) ─────────────────────────────────────────────────

@app.get("/admin/stats")
def admin_stats(_: str = Depends(_verify_admin)):
    return db.get_stats()


@app.get("/admin/unanswered")
def admin_unanswered(
    limit: int = 50,
    _: str = Depends(_verify_admin),
):
    questions = db.get_unanswered(limit=limit)
    return {"perguntas": questions, "total": len(questions)}


@app.patch("/admin/unanswered/{question_id}/reviewed")
def admin_mark_reviewed(
    question_id: int,
    _: str = Depends(_verify_admin),
):
    db.mark_reviewed(question_id)
    return {"ok": True}


@app.delete("/admin/unanswered/{question_id}")
def admin_delete_unanswered(
    question_id: int,
    _: str = Depends(_verify_admin),
):
    db.delete_unanswered(question_id)
    return {"ok": True}


@app.post("/admin/ingest")
def admin_ingest(
    docs_path: str | None = None,
    _: str = Depends(_verify_admin),
):
    path = docs_path or os.getenv("RAG_DOCS_PATH")
    if not path:
        raise HTTPException(
            status_code=400,
            detail="Configure RAG_DOCS_PATH no .env ou passe docs_path na requisição.",
        )
    try:
        count = ingest_all(path)
        return {"ok": True, "chunks_indexados": count}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na ingestão: {str(e)}")
