# AI Agent Platform

An intelligent AI Agent built using FastAPI, Groq LLM, and Dynamic Function Calling.

## Features

- Weather Information Tool
- Email Automation Tool
- Database Search Tool
- Web Search Tool
- Dynamic Function Calling
- Conversation History Management

## Tech Stack

- Python
- FastAPI
- Groq LLM
- OpenAI SDK
- HTML
- CSS
- JavaScript

## Project Structure

backend/
├── app.py
├── tools/
│   ├── weather_tool.py
│   ├── email_tool.py
│   ├── db_tool.py
│   └── search_tool.py

frontend/
├── index.html
├── style.css
└── app.js

## Setup

1. Clone repository
2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create `.env`

```env
GROQ_API_KEY=your_key
WEATHER_API_KEY=your_key
EMAIL_ADDRESS=your_email
EMAIL_PASSWORD=your_app_password
```

4. Run backend

```bash
uvicorn backend.app:app --reload
```

5. Open frontend

```bash
python -m http.server 5500
```

## Demo

Supports:
- Weather queries
- Email sending
- Database search
- Web search

## Author

Sowmya Vankayalapati
