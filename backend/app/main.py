from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Optional
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Role = Literal["user", "assistant", "system"]

class ChatMsg(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMsg]
    model: Optional[str] = "llama3.1:8b"

class ChatResponse(BaseModel):
    reply: str

OLLAMA_URL = "http://10.25.1.49:8000/chat"

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    payload = {
        "model": req.model,
        "messages": [m.model_dump() for m in req.messages],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(OLLAMA_URL, json=payload)
            r.raise_for_status()
            data = r.json()

        reply = (data.get("message") or {}).get("content", "")
        if not reply:
            raise HTTPException(status_code=502, detail=f"Empty reply from Ollama: {data}")

        return {"reply": reply}

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to Ollama at http://10.25.1.49:8000/chat. Is Ollama running?",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e.response.text}")
