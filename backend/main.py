# main.py
# The web server. It exposes two "doors" (endpoints):
#   POST /chat   -> user typed a message           -> run the agent -> return updated form
#   POST /upload -> user uploaded a PDF            -> extract text  -> run the agent -> return updated form
# The React frontend will knock on these doors.

import json
import pdfplumber

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from schemas import ChatRequest
from agent import run_agent
from database import save_complaint

app = FastAPI(title="Complaint Management API")

# ---- CORS: allow the frontend to call us ----
# Browsers block websites from calling other addresses unless the server says "it's fine".
# Our React app will live at localhost:5173, so we whitelist it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    # Just to confirm the server is alive when you visit it in a browser.
    return {"status": "running"}


@app.post("/chat")
def chat(request: ChatRequest):
    # request.message           = what the user typed
    # request.current_form_state = the form right now (frontend sends it every time)
    # .model_dump() converts the Pydantic object into a plain dict for the agent.
   updated_form = run_agent(request.message, request.current_form_state.model_dump())
   complaint_id = save_complaint(updated_form)
   return {"form": updated_form, "complaint_id": complaint_id}


@app.post("/upload")
def upload(file: UploadFile = File(...), current_form_state: str = Form("{}")):
    # Files can't travel as JSON, so the form state arrives as a JSON *string* -> parse it.
    current_form = json.loads(current_form_state)

    # Pull all text out of the PDF, page by page.
    text = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"

    # Reuse the SAME agent - a PDF is just a long "message". Tool 3 = Tool 1 with more text.
    message = f"Extract complaint information from this document:\n{text}"
    updated_form = run_agent(message, current_form)
    complaint_id = save_complaint(updated_form)
    return {"form": updated_form, "complaint_id": complaint_id}