# AI-Powered Customer Support Chatbot

A beginner-friendly B.Tech internship/practical project built with Python, FastAPI, SQLite, NLTK, HTML, CSS and JavaScript. It runs locally and does not require a paid API key or a downloaded transformer model.

## Features

- Responsive dark-blue support dashboard with chat-history sidebar and suggested prompts.
- Local FAQ retrieval, text normalization, regex tokenization, optional NLTK Porter stemming and Dice similarity.
- Basic context handling for short follow-up prompts such as “tell me more”.
- Unknown-question fallback rather than pretending every question is understood.
- SQLite persistence for conversations, messages, timestamps, predicted intent and similarity score.
- Load previous conversations, delete a conversation, and export all messages to CSV.
- Input length validation, blank-message validation, API error handling and health endpoint.
- Automated API tests with pytest.

## Architecture

```text
Browser (HTML/CSS/JS)
        | fetch /api/chat and history endpoints
        v
FastAPI (app/main.py) ----> chatbot logic (app/chatbot.py) ----> faqs.json
        |
        v
SQLite database (app/data/chatbot.db)
```

## Requirements

- Python 3.11 or newer (Python 3.11–3.13 are recommended for broad package compatibility).
- macOS Terminal.
- Internet is required for the first pip installation. The application itself runs offline after dependencies are installed. Google Fonts are optional and only affect typography; system fonts are used if offline.

## Setup on macOS

From the directory containing this README:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000**. API documentation is at **http://127.0.0.1:8000/docs** and health status at **http://127.0.0.1:8000/api/health**.

If `python3` is not Python 3.11+, install a compatible Python version and use its executable to create the environment. On a Mac with Homebrew, for example: `brew install python@3.12`, then `/opt/homebrew/bin/python3.12 -m venv .venv` (Apple Silicon) or use the corresponding Homebrew path on Intel Macs.

Stop the server with `Ctrl+C`. Reactivation in a later terminal: `cd ai_support_chatbot && source .venv/bin/activate`.

## Test

With the virtual environment active:

```bash
python -m pytest -q
```

Tests cover health, FAQ response, unknown-question fallback, database logging, invalid input and CSV export.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Serve the chatbot frontend |
| GET | `/api/health` | Health-check |
| GET | `/api/conversations` | List saved conversations |
| GET | `/api/conversations/{id}/messages` | Read conversation messages |
| POST | `/api/chat` | Generate and log a response |
| DELETE | `/api/conversations/{id}` | Delete a conversation and its messages |
| GET | `/api/export.csv` | Export all conversation logs |

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \\
  -H 'Content-Type: application/json' \\
  -d '{"message":"How can I track my order?"}'
```

## Database

`conversations` stores conversation ID, title and created/updated timestamps. `messages` stores each user/assistant message, role, timestamp, intent and similarity score. Foreign keys ensure that deleting a conversation also deletes its messages. The database is initialized automatically at startup.

## What “AI/NLP” means in this project

This is a **lightweight retrieval chatbot**, not a trained neural network or a generative LLM. It normalizes text, tokenizes words with regular expressions, optionally stems tokens using NLTK's PorterStemmer, compares question tokens with FAQ questions/examples using Dice similarity, and returns the best FAQ when the score reaches a threshold. It has a small context rule for short follow-up questions. There is no training phase and no paid API. NLTK's PorterStemmer does not need a separate corpus download. If NLTK is unavailable, the app falls back to unstemmed tokens.

## Customizing FAQs

Edit `app/data/faqs.json`. Each item has `intent`, `question`, `examples`, and `answer`. Add real, verified policy details before using this in an actual business. The supplied return/refund/delivery content is illustrative and must be reviewed.

## Limitations and future improvements

- FAQ matching can miss paraphrases and does not learn from conversations.
- Context support is deliberately simple and is not full multi-turn reasoning.
- No authentication, role-based access, rate limiting or production deployment configuration.
- Add semantic embeddings (e.g. Sentence Transformers), a trained intent classifier, multilingual support, analytics, user authentication, human-agent handoff and privacy/retention controls for a production version.
- Never place secrets in frontend code. Review logs and data retention before deploying.

## Project tree

```text
ai_support_chatbot/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── chatbot.py
│   ├── data/faqs.json
│   └── static/{index.html,styles.css,app.js}
├── tests/test_app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── Internship_Practical_Report.docx
```
# ai_support_chatbot
# AI_Chatbot
