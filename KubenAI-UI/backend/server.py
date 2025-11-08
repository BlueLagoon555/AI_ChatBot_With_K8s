# backend/server.py
import os
import logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# Do not load a build-time .env file here; prefer runtime environment variables
# If you need to load a .env for local development, consider using docker-compose
# or an explicit dev script. We intentionally avoid calling load_dotenv() here
# to prevent baked-in values from taking precedence.

# --- Config ---
CHAT_API_TYPE = os.getenv("CHAT_API_TYPE", "digitalocean").lower()
DO_BASE = os.getenv("DIGITALOCEAN_INFERENCE_ENDPOINT", "").rstrip("/")
DO_MODEL = os.getenv("DIGITALOCEAN_MODEL", "openai-gpt-oss-120b")
DO_API_KEY = os.getenv("DIGITALOCEAN_API_KEY", "")  # accept raw token or "Bearer ..."

# Normalize Authorization header
if DO_API_KEY and not DO_API_KEY.lower().startswith("bearer "):
    DO_AUTH_HEADER = f"Bearer {DO_API_KEY}"
else:
    DO_AUTH_HEADER = DO_API_KEY

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger("backend")

app = FastAPI(title="Chat Backend")

# CORS
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 200
    temperature: Optional[float] = 0.7
    model: Optional[str] = None  # allow override


@app.get("/healthz")
def healthz():
    return {"ok": True, "mode": CHAT_API_TYPE}


@app.post("/api/chat")
def chat(req: ChatRequest):
    if CHAT_API_TYPE != "digitalocean":
        raise HTTPException(
            status_code=500, detail="Backend is not in DigitalOcean mode."
        )

    if not DO_BASE or not DO_AUTH_HEADER:
        raise HTTPException(
            status_code=500, detail="DigitalOcean endpoint or API key not configured."
        )

    model = req.model or DO_MODEL
    url = f"{DO_BASE}/chat/completions"  # DO base already includes /v1
    headers = {
        "Content-Type": "application/json",
        "Authorization": DO_AUTH_HEADER,
    }
    payload: Dict[str, Any] = {
        "model": model,
        "messages": [m.dict() for m in req.messages],
        "max_tokens": req.max_tokens,
        "temperature": req.temperature,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code >= 400:
            logger.error("DO error %s: %s", resp.status_code, resp.text)
            raise HTTPException(status_code=resp.status_code, detail=resp.text)

        data = resp.json()
        # Standard OpenAI-like payload shape
        content = data["choices"][0]["message"]["content"]
        return {"content": content, "raw": data}
    except requests.RequestException as e:
        logger.exception("Network error talking to DO")
        raise HTTPException(status_code=502, detail=str(e))
