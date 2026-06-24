# 🧪 LLM Chat Playground

A small web app for experimenting with **Large Language Models** — text chat via
[Groq](https://groq.com) — with a focus on **prompt-engineering techniques** and
**short-term memory**. Built with **Python + FastAPI** and a polished
single-page front-end.

This was built as an onboarding project to learn the foundations of LLMs and
how to wire them into a real application.

---

## ✨ Features

| # | Feature |
|---|---------|
| 1 | Chatbot using Groq models |
| 2 | Dropdown to select the Groq text model |
| 3 | Prompt-engineering technique selector (zero-shot, role, few-shot, output-format, step-by-step, custom) |
| 4 | Custom system-prompt input |
| 5 | Short-term memory (last 7 turns sent as context) |
| 6 | Inspect the exact system prompt used for each reply |

---

## 🗂️ Project structure

```
llm-playground/
├── main.py              # FastAPI backend (chat, models, techniques, static)
├── prompts.py           # Prompt-engineering techniques + build_system_prompt()
├── requirements.txt     # Python dependencies
├── .env                 # Your API key (gitignored)
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

### 3. Add your API key
Create a `.env` file in the project root with your key:
```
GROQ_API_KEY=your_groq_api_key_here
```
- **Groq key** (free): https://console.groq.com/keys

### 4. Run
```bash
uvicorn main:app --reload
```
Open **http://localhost:8000** in your browser.

---

## 🔌 API reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET`  | `/api/models` | Returns the text-model list used to fill the dropdown |
| `GET`  | `/api/techniques` | Returns the prompt-engineering techniques for the dropdown |
| `POST` | `/api/chat` | `{model, technique, custom_system_prompt, user_message, history}` → Groq reply + the system prompt used |

Interactive docs are available at **http://localhost:8000/docs** (FastAPI/Swagger).
