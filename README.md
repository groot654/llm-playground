# 🧪 LLM & Image Generation Playground

A small web app for experimenting with **Large Language Models** (text chat via
[Groq](https://groq.com)) and **image generation** (via Google
[Gemini](https://ai.google.dev)). Built with **Python + FastAPI** and a simple
single-page front-end.

This was built as an onboarding project to learn the foundations of LLMs and
how to wire them into a real application.

---

## ✨ Features

| # | Feature | Where |
|---|---------|-------|
| 1 | Chatbot using Groq models | left panel |
| 2 | Dropdown to select the Groq text model | left panel |
| 3 | System prompt input | left panel |
| 4 | User message input | left panel |
| 5 | Response display area | left panel |
| 6 | Image generation using Gemini | right panel |
| 7 | Dropdown to select the image model | right panel |
| 8 | Prompt box for image generation | right panel |
| 9 | Display area for generated images | right panel |

---

## 🗂️ Project structure

```
llm-playground/
├── main.py              # FastAPI backend (chat, image, models, static)
├── requirements.txt     # Python dependencies
├── .env.example         # Template for your API keys
├── .gitignore
├── README.md
└── static/
    └── index.html       # Single-page front-end (HTML + CSS + JS)
```

---

## 🚀 Setup & run

### 1. Clone and create a virtual environment
```bash
git clone https://github.com/<your-username>/llm-playground.git
cd llm-playground
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API keys
Copy the template and fill in your keys:
```bash
cp .env.example .env
```
Then edit `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```
- **Groq key** (free): https://console.groq.com/keys
- **Gemini key** (free tier): https://aistudio.google.com/app/apikey

### 4. Run
```bash
uvicorn main:app --reload
```
Open **http://localhost:8000** in your browser.

---

## 🔌 API reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET`  | `/api/models` | Returns the lists used to fill the two dropdowns |
| `POST` | `/api/chat` | `{model, system_prompt, user_message}` → Groq reply |
| `POST` | `/api/generate-image` | `{model, prompt}` → base64 image |

Interactive docs are available at **http://localhost:8000/docs** (FastAPI/Swagger).

---

## 🧠 LLM foundations (quick notes)

A few concepts this project demonstrates:

- **Tokens** – models read and write text in chunks called tokens, not whole
  words. Cost and context limits are measured in tokens.
- **System vs. user messages** – the *system prompt* sets the assistant's
  behavior and persona; the *user message* is the actual query. This app exposes
  both so you can see how the system prompt steers responses.
- **Temperature** – controls randomness. Lower = more deterministic, higher =
  more creative. Set to `0.7` by default here.
- **Inference providers** – Groq runs open models (Llama, GPT-OSS, Qwen, etc.)
  on specialized hardware for very fast responses, using an OpenAI-compatible
  API.
- **Multimodal generation** – Gemini's image models take a text prompt and
  return image data inline, which this app decodes and renders in the browser.

---

## 📦 Models available in the app

**Groq text models:** `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`,
`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `moonshotai/kimi-k2-instruct-0905`,
`qwen/qwen3-32b`, `deepseek-r1-distill-llama-70b`, `gemma2-9b-it`

**Gemini image models:** `gemini-2.5-flash-image` (free tier),
`gemini-3.1-flash-image-preview`, `gemini-3-pro-image-preview`

> Note: model availability and free-tier quotas change over time. The
> `gemini-2.5-flash-image` model is the one with a usable free API tier; the
> Pro image model generally requires billing enabled.

---

## ⚠️ Notes

- Never commit your `.env` file — it's already in `.gitignore`.
- If image generation returns an error about quota, you've likely hit the
  free-tier limit; try again later or switch to `gemini-2.5-flash-image`.
