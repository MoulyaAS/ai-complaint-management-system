# AI-Powered Customer Complaint Management System

Built for the AIVOA AI Product Engineer (Intern) assignment — an AI copilot that logs pharmaceutical customer complaints through natural language, document extraction, and automated risk assessment.

## What it does

The screen is split in two: a Log Customer Complaint form (left) and the AIVOA Copilot chat (right). The form cannot be typed into directly — every field is filled through the AI:

1. **Log Complaint (Tool 1):** Describe a complaint in plain English and the AI extracts the fields, fills the form, and generates a risk assessment.
2. **Edit Complaint (Tool 2):** Correct anything conversationally ("Sorry, the batch number is CHG260712A"). Only mentioned fields change; the rest are preserved, and risk is re-assessed.
3. **Document Extraction (Tool 3):** Upload a complaint PDF/email and the same pipeline extracts all fields. Post-extraction edits also work.

## Tech stack

- Frontend: React + Redux Toolkit (Vite), Google Inter font
- Backend: Python, FastAPI
- AI orchestration: LangGraph (3-node graph: extract -> merge -> assess)
- LLMs: Groq API
- Database: PostgreSQL via SQLAlchemy

### Note on models
The assignment specifies gemma2-9b-it, but Groq decommissioned that model. I kept the intended architecture — a small fast model for extraction and a large model for risk reasoning — using Groq's currently recommended replacements: openai/gpt-oss-20b (extraction) and openai/gpt-oss-120b (risk assessment).

## How it works

Every input (typed message, edit, or PDF text) goes through the same LangGraph pipeline:

1. extract node — small LLM returns ONLY the fields found in the message (JSON)
2. merge node — pure Python partial update: new fields overwrite, untouched fields survive (this is what makes editing work)
3. assess node — large LLM reads the full merged form and writes severity, recommended action, and risk details

The result is saved to Postgres and returned to the frontend, where Redux updates and the read-only form re-renders.

## Running locally

Backend (Python 3.11+, PostgreSQL running):

    cd backend
    python -m venv venv
    venv\Scripts\activate
    pip install fastapi uvicorn langchain-groq langgraph pydantic python-dotenv sqlalchemy psycopg2-binary pdfplumber python-multipart

Create backend/.env with:

    GROQ_API_KEY=your_groq_key
    DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres

Start it:

    uvicorn main:app --reload

Frontend:

    cd frontend
    npm install
    npm run dev

Open http://localhost:5173 (backend must be running on port 8000).