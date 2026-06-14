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
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario     TEXT NOT NULL UNIQUE,
                criado_em   TEXT NOT NULL,
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


def clear_all():
    with _conn() as conn:
        conn.execute("DELETE FROM conversations")
        conn.execute("DELETE FROM sessions")
        conn.commit()
