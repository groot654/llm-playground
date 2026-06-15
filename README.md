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
