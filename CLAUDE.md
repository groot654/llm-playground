# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A FastAPI backend (`main.py`) with a small prompt-technique helper (`prompts.py`), plus a single static page (`static/index.html`) that lets you experiment with text chat via Groq. The focus is prompt-engineering techniques and browser-side short-term memory. There are no tests, no build step, and no framework beyond FastAPI/uvicorn.

## Commands

```bash
# Activate the existing venv (Windows / PowerShell)
.\venv\Scripts\activate

pip install -r requirements.txt        # install deps
uvicorn main:app --reload              # run dev server -> http://localhost:8000
python main.py                         # equivalent; runs uvicorn on 0.0.0.0:8000 with reload
```

- Interactive API docs (Swagger): http://localhost:8000/docs
- Requires `GROQ_API_KEY` in a `.env` file (loaded via `python-dotenv`).

## Architecture

The whole backend lives in `main.py`. Key design points worth knowing before editing:

- **Lazy, key-tolerant client.** `get_groq_client()` builds the SDK client on first use and raises an HTTP 500 (not a startup crash) when the key is missing. This is deliberate so the server boots without a key set — keep this pattern when adding new providers.
- **Models are a hardcoded list**, not discovered from the provider: `GROQ_TEXT_MODELS` near the top of `main.py`. `/api/models` just returns this list to populate the front-end dropdown. To add/remove a selectable model, edit this constant. Note the README's model list and this constant can drift — keep them in sync.
- **Prompt techniques live in `prompts.py`.** `TECHNIQUES` (id/label list) and `build_system_prompt(technique, custom_text)` map a technique id (zero_shot, role, few_shot, output_format, step_by_step, custom) to a system prompt. `/api/techniques` returns `TECHNIQUES` to populate the dropdown; `/api/chat` calls `build_system_prompt` to construct the system message. To add a technique, extend both `TECHNIQUES` and the branch logic in `build_system_prompt`. Unknown ids are rejected with 400 (validated against `VALID_TECHNIQUE_IDS`).
- **Short-term memory is client-side.** The front-end keeps the last ~7 turns and sends them as `history` on each `/api/chat` call; the backend replays them as prior `user`/`assistant` turns before the new message. The server is stateless — it stores no conversation.
- **Provider errors** from Groq are caught and re-raised as HTTP 502 with the provider message included; input validation errors are 400.
- **Front-end** is a single self-contained HTML/CSS/JS file (settings sidebar + chat column), served via `FileResponse` at `/` and mounted static at `/static`. It calls the three JSON endpoints directly; there is no bundler.

## Endpoints

- `GET /api/models` → `{text_models}`
- `GET /api/techniques` → `{techniques: [{id, label}, ...]}`
- `POST /api/chat` → `{model, technique, custom_system_prompt, user_message, history, temperature}` → `{response, model, system_prompt}` via Groq (OpenAI-compatible `chat.completions.create`). `history` is a list of `{role, content}` prior turns; `system_prompt` in the response is the prompt that was actually built and used.
