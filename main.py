"""
LLM Chat Playground
-------------------s
A FastAPI backend that exposes:
  - /api/chat       -> chat completions via Groq
  - /api/models     -> list of selectable Groq text models
  - /api/techniques -> list of selectable prompt-engineering techniques
  - /              -> serves the single-page front-end

Environment variables required:
  GROQ_API_KEY    -> from https://console.groq.com
"""

import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from groq import Groq

from prompts import TECHNIQUES, VALID_TECHNIQUE_IDS, build_system_prompt

load_dotenv()

app = FastAPI(title="LLM Chat Playground")

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Selectable Groq text models shown in the dropdown.
# These are current production / preview chat models on GroqCloud.
GROQ_TEXT_MODELS: List[str] = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "moonshotai/kimi-k2-instruct-0905",
    "qwen/qwen3-32b",
    "deepseek-r1-distill-llama-70b",
    "gemma2-9b-it",
]

# Lazily-created client so the server can still boot without a key set.
_groq_client: Optional[Groq] = None


def get_groq_client() -> Groq:
    global _groq_client
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not set. Add it to your .env file.",
        )
    if _groq_client is None:
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


# ----------------------------------------------------------------------------
# Request / response schemas
# ----------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    technique: str = "zero_shot"
    custom_system_prompt: str = ""
    user_message: str
    history: List[ChatMessage] = []
    temperature: float = 0.7


class ChatResponse(BaseModel):
    response: str
    model: str
    system_prompt: str


# ----------------------------------------------------------------------------
# API routes
# ----------------------------------------------------------------------------

@app.get("/api/models")
def list_models():
    """Return the model list used to populate the dropdown."""
    return {"text_models": GROQ_TEXT_MODELS}


@app.get("/api/techniques")
def list_techniques():
    """Return the prompt-engineering techniques used to fill the dropdown."""
    return {"techniques": TECHNIQUES}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Send a chat completion request to Groq and return the reply text.

    The system prompt is built from the chosen prompt-engineering technique
    (see prompts.py); prior turns supplied in `history` give the model
    short-term memory of the conversation.
    """
    if not req.user_message.strip():
        raise HTTPException(status_code=400, detail="User message cannot be empty.")

    if req.technique not in VALID_TECHNIQUE_IDS:
        raise HTTPException(
            status_code=400, detail=f"Unknown technique: {req.technique}"
        )

    client = get_groq_client()

    system_prompt = build_system_prompt(req.technique, req.custom_system_prompt)

    messages = [{"role": "system", "content": system_prompt}]
    # Replay prior turns so the model has short-term memory of the conversation.
    for msg in req.history:
        if msg.role in ("user", "assistant") and msg.content.strip():
            messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.user_message})

    try:
        completion = client.chat.completions.create(
            model=req.model,
            messages=messages,
            temperature=req.temperature,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Groq error: {e}")

    text = completion.choices[0].message.content or ""
    return ChatResponse(response=text, model=req.model, system_prompt=system_prompt)


# ----------------------------------------------------------------------------
# Static front-end
# ----------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)