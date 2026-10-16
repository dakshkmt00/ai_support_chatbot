from pathlib import Path
import sqlite3
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "data" / "chatbot.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT 'New conversation',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role TEXT NOT NULL CHECK(role IN ('user','assistant')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            intent TEXT,
            confidence REAL
        );
        CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, id);
        """)

def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def create_conversation():
    stamp = now()
    with connect() as conn:
        cur = conn.execute("INSERT INTO conversations(title, created_at, updated_at) VALUES(?,?,?)",
                           ("New conversation", stamp, stamp))
        return cur.lastrowid

def add_message(conversation_id, role, content, intent=None, confidence=None):
    stamp = now()
    with connect() as conn:
        conn.execute("""INSERT INTO messages(conversation_id, role, content, created_at, intent, confidence)
                        VALUES(?,?,?,?,?,?)""",
                     (conversation_id, role, content, stamp, intent, confidence))
        if role == "user":
            count = conn.execute("SELECT COUNT(*) FROM messages WHERE conversation_id=? AND role='user'",
                                 (conversation_id,)).fetchone()[0]
            if count == 1:
                title = content[:42] + ("…" if len(content) > 42 else "")
                conn.execute("UPDATE conversations SET title=?, updated_at=? WHERE id=?",
                             (title, stamp, conversation_id))
            else:
                conn.execute("UPDATE conversations SET updated_at=? WHERE id=?", (stamp, conversation_id))

def list_conversations():
    with connect() as conn:
        rows = conn.execute("""SELECT c.id, c.title, c.created_at, c.updated_at,
                            (SELECT COUNT(*) FROM messages m WHERE m.conversation_id=c.id) AS message_count
                            FROM conversations c ORDER BY c.updated_at DESC""").fetchall()
        return [dict(r) for r in rows]

def get_messages(conversation_id):
    with connect() as conn:
        exists = conn.execute("SELECT id FROM conversations WHERE id=?", (conversation_id,)).fetchone()
        if not exists:
            return None
        rows = conn.execute("""SELECT id, conversation_id, role, content, created_at, intent, confidence
                               FROM messages WHERE conversation_id=? ORDER BY id""", (conversation_id,)).fetchall()
        return [dict(r) for r in rows]

def clear_conversation(conversation_id):
    with connect() as conn:
        exists = conn.execute("SELECT id FROM conversations WHERE id=?", (conversation_id,)).fetchone()
        if not exists:
            return False
        conn.execute("DELETE FROM conversations WHERE id=?", (conversation_id,))
        return True

def get_all_messages():
    with connect() as conn:
        rows = conn.execute("""SELECT conversation_id, role, content, created_at, intent, confidence
                               FROM messages ORDER BY conversation_id, id""").fetchall()
        return [dict(r) for r in rows]
