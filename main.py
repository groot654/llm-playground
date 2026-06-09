"""
LLM & Image Generation Playground
-----------------------------------
A FastAPI backend that exposes:
  - /api/chat       -> chat completions via Groq
  - /api/models     -> list of selectable Groq text models
  - /api/generate-image -> image generation via Google Gemini
  - /              -> serves the single-page front-end

Environment variables required:
  GROQ_API_KEY    -> from https://console.groq.com
  GEMINI_API_KEY  -> from https://aistudio.google.com/app/apikey
"""

import os
import base64
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from groq import Groq
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI(title="LLM & Image Generation Playground")

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

# Selectable Gemini image generation models shown in the dropdown.
# gemini-2.5-flash-image (Nano Banana) is the one available on the free tier.
GEMINI_IMAGE_MODELS: List[str] = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image-preview",
]

# Lazily-created clients so the server can still boot without keys set.
_groq_client: Optional[Groq] = None
_gemini_client: Optional[genai.Client] = None


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


def get_gemini_client() -> genai.Client:
    global _gemini_client
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not set. Add it to your .env file.",
        )
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client


# ----------------------------------------------------------------------------
# Request / response schemas
# ----------------------------------------------------------------------------

class ChatRequest(BaseModel):
    model: str
    system_prompt: str = ""
    user_message: str
    temperature: float = 0.7


class ChatResponse(BaseModel):
    response: str
    model: str


class ImageRequest(BaseModel):
    model: str
    prompt: str


class ImageResponse(BaseModel):
    image_base64: str
    mime_type: str
    model: str


# ----------------------------------------------------------------------------
# API routes
# ----------------------------------------------------------------------------

@app.get("/api/models")
def list_models():
    """Return the model lists used to populate the two dropdowns."""
    return {
        "text_models": GROQ_TEXT_MODELS,
        "image_models": GEMINI_IMAGE_MODELS,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Send a chat completion request to Groq and return the reply text."""
    if not req.user_message.strip():
        raise HTTPException(status_code=400, detail="User message cannot be empty.")

    client = get_groq_client()

    messages = []
    if req.system_prompt.strip():
        messages.append({"role": "system", "content": req.system_prompt})
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
    return ChatResponse(response=text, model=req.model)


@app.post("/api/generate-image", response_model=ImageResponse)
def generate_image(req: ImageRequest):
    """Generate an image with Gemini and return it as base64."""
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Image prompt cannot be empty.")

    client = get_gemini_client()

    try:
        result = client.models.generate_content(
            model=req.model,
            contents=req.prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini error: {e}")

    # Walk the response parts and pull out the first inline image.
    for candidate in result.candidates or []:
        for part in candidate.content.parts or []:
            if getattr(part, "inline_data", None) and part.inline_data.data:
                raw = part.inline_data.data
                # SDK may hand back bytes or an already-encoded string.
                if isinstance(raw, bytes):
                    b64 = base64.b64encode(raw).decode("utf-8")
                else:
                    b64 = raw
                return ImageResponse(
                    image_base64=b64,
                    mime_type=part.inline_data.mime_type or "image/png",
                    model=req.model,
                )

    raise HTTPException(
        status_code=502,
        detail="No image was returned. The model may have refused the prompt "
               "or the free-tier quota was exceeded.",
    )


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
