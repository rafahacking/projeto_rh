import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "rh_chat.db"


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario       TEXT NOT NULL UNIQUE,
                criado_em     TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario   TEXT NOT NULL,
                role      TEXT NOT NULL,
                conteudo  TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS unanswered_questions (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario   TEXT NOT NULL,
                pergunta  TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                revisado  INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


def upsert_session(usuario: str):
    now = datetime.now().isoformat()
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO sessions (usuario, criado_em, atualizado_em)
            VALUES (?, ?, ?)
            ON CONFLICT(usuario) DO UPDATE SET atualizado_em = excluded.atualizado_em
            """,
            (usuario, now, now),
        )
        conn.commit()


def save_message(usuario: str, role: str, conteudo: str):
    now = datetime.now().isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO conversations (usuario, role, conteudo, timestamp) VALUES (?, ?, ?, ?)",
            (usuario, role, conteudo, now),
        )
        conn.commit()


def get_history(usuario: str) -> list:
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT role, conteudo, timestamp
            FROM conversations
            WHERE usuario = ?
            ORDER BY id ASC
            """,
            (usuario,),
        ).fetchall()
    return [dict(row) for row in rows]


def save_unanswered(usuario: str, pergunta: str):
    now = datetime.now().isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO unanswered_questions (usuario, pergunta, timestamp) VALUES (?, ?, ?)",
            (usuario, pergunta, now),
        )
        conn.commit()


def get_unanswered(limit: int = 100) -> list:
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                usuario,
                pergunta,
                timestamp,
                revisado,
                COUNT(*) OVER (PARTITION BY lower(trim(pergunta))) AS frequencia
            FROM unanswered_questions
            ORDER BY frequencia DESC, timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def mark_reviewed(question_id: int):
    with _conn() as conn:
        conn.execute(
            "UPDATE unanswered_questions SET revisado = 1 WHERE id = ?",
            (question_id,),
        )
        conn.commit()


def delete_unanswered(question_id: int):
    with _conn() as conn:
        conn.execute("DELETE FROM unanswered_questions WHERE id = ?", (question_id,))
        conn.commit()


def clear_all():
    with _conn() as conn:
        conn.execute("DELETE FROM conversations")
        conn.execute("DELETE FROM sessions")
        conn.commit()


def get_stats() -> dict:
    with _conn() as conn:
        total_user = conn.execute(
            "SELECT COUNT(*) FROM conversations WHERE role = 'user'"
        ).fetchone()[0]

        total_unanswered = conn.execute(
            "SELECT COUNT(*) FROM unanswered_questions"
        ).fetchone()[0]

        msgs_por_dia = conn.execute(
            """
            SELECT date(timestamp) AS dia, COUNT(*) AS total
            FROM conversations
            WHERE role = 'user' AND timestamp >= date('now', '-6 days')
            GROUP BY date(timestamp)
            ORDER BY dia ASC
            """
        ).fetchall()

        unanswered_por_dia = conn.execute(
            """
            SELECT date(timestamp) AS dia, COUNT(*) AS total
            FROM unanswered_questions
            WHERE timestamp >= date('now', '-6 days')
            GROUP BY date(timestamp)
            ORDER BY dia ASC
            """
        ).fetchall()

    return {
        "total_mensagens": total_user,
        "total_sem_resposta": total_unanswered,
        "total_respondidas": max(0, total_user - total_unanswered),
        "msgs_por_dia": [dict(r) for r in msgs_por_dia],
        "unanswered_por_dia": [dict(r) for r in unanswered_por_dia],
    }
