from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional
import csv, io

from app.database import init_db, create_conversation, add_message, list_conversations, get_messages, clear_conversation, get_all_messages
from app.chatbot import generate_reply

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="AI Customer Support Chatbot", version="1.0.0",
              description="Local FAQ retrieval chatbot with conversational logging.")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

@app.on_event("startup")
def startup():
    init_db()

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[int] = None

@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "database": "sqlite", "mode": "local-faq"}

@app.get("/api/conversations")
def conversations():
    return {"conversations": list_conversations()}

@app.get("/api/conversations/{conversation_id}/messages")
def conversation_messages(conversation_id: int):
    items = get_messages(conversation_id)
    if items is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "messages": items}

@app.post("/api/chat")
def chat(payload: ChatRequest):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be blank.")
    conversation_id = payload.conversation_id
    if conversation_id is None:
        conversation_id = create_conversation()
    elif get_messages(conversation_id) is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    history = get_messages(conversation_id) or []
    reply, intent, confidence = generate_reply(message, history)
    add_message(conversation_id, "user", message)
    add_message(conversation_id, "assistant", reply, intent=intent, confidence=confidence)
    return {"conversation_id": conversation_id, "reply": reply, "intent": intent, "confidence": round(confidence, 3)}

@app.delete("/api/conversations/{conversation_id}")
def clear_chat(conversation_id: int):
    if not clear_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True, "conversation_id": conversation_id}

@app.get("/api/export.csv")
def export_csv():
    rows = get_all_messages()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["conversation_id", "role", "message", "timestamp", "intent", "confidence"])
    writer.writerows([[r["conversation_id"], r["role"], r["content"], r["created_at"], r.get("intent", ""), r.get("confidence", "")] for r in rows])
    data = io.BytesIO(buffer.getvalue().encode("utf-8-sig"))
    return StreamingResponse(data, media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="chatbot_conversations.csv"'})
