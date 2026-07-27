# agent.py
# The AI brain: a LangGraph "flowchart" with 3 steps (nodes):
#   1. extract  -> AI reads the user's message, returns ONLY the fields it found (JSON)
#   2. merge    -> we combine those new fields into the existing form (partial update)
#   3. assess   -> a second AI call looks at the FULL form and writes the risk assessment
# Every chat message (typed or from a PDF) flows through these same 3 steps.

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing import TypedDict

load_dotenv()  # reads GROQ_API_KEY from the .env file

# ---- The two AI models (from the assignment) ----
# gemma2 = fast, good enough for pulling fields out of text
extractor_llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)   # small+fast: extraction
risk_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)       # big+smart: risk reasoning

# ---- The "clipboard" that travels through the flowchart ----
# Each node reads from it and writes to it.
class AgentState(TypedDict):
    user_message: str      # what the user typed (or PDF text)
    current_form: dict     # the form BEFORE this message
    extracted_fields: dict # what the AI found in the message (step 1 output)
    updated_form: dict     # the form AFTER merging (step 2 output, then step 3 adds risk)


# ---------- NODE 1: EXTRACT ----------
def extract_node(state: AgentState) -> dict:
    prompt = f"""You are a data extraction assistant for a pharmaceutical complaint system.

Here is the complaint form's CURRENT state:
{json.dumps(state['current_form'], indent=2)}

Here is the user's new message:
"{state['user_message']}"

Extract ONLY the fields mentioned or corrected in this message.
Return a JSON object using ONLY these keys (skip keys not mentioned):
complainant_name, product_name, product_strength, batch_number,
manufacturing_date, expiry_date, affected_quantity, complaint_description

Rules:
- Return ONLY the JSON object. No explanations, no markdown, no ``` fences.
- If the message corrects an existing value, return the NEW value.
- Do not invent data that is not in the message.
"""
    response = extractor_llm.invoke(prompt)
    text = response.content.strip()

    # Safety net: models sometimes wrap JSON in ```json ... ``` anyway. Strip it.
    if text.startswith("```"):
        text = text.split("```")[1].replace("json", "", 1).strip()

    try:
        fields = json.loads(text)
    except json.JSONDecodeError:
        fields = {}  # if AI returned garbage, change nothing rather than crash

    return {"extracted_fields": fields}


# ---------- NODE 2: MERGE (no AI here - pure Python) ----------
def merge_node(state: AgentState) -> dict:
    updated = dict(state["current_form"])          # copy of the old form
    for key, value in state["extracted_fields"].items():
        if value is not None and value != "":       # only real values overwrite
            updated[key] = value
    return {"updated_form": updated}
    # This tiny function is why editing one field never erases the others.


# ---------- NODE 3: RISK ASSESSMENT ----------
def assess_node(state: AgentState) -> dict:
    form = state["updated_form"]
    prompt = f"""You are a pharmaceutical quality (QMS) risk assessor.

Here is a customer complaint:
{json.dumps(form, indent=2)}

Assess the risk. Return ONLY a JSON object with exactly these keys:
- "severity": one of "Minor", "Major", "Critical"
  (Critical = patient safety danger e.g. contamination/wrong drug;
   Major = quality defect e.g. discoloration, broken capsules;
   Minor = cosmetic/packaging issue with no product impact)
- "recommended_action": one short sentence, e.g. "Route to QA investigation and issue replacement"
- "risk_details": 1-2 sentences explaining your reasoning

Return ONLY the JSON. No markdown fences.
"""
    response = risk_llm.invoke(prompt)
    text = response.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1].replace("json", "", 1).strip()

    try:
        risk = json.loads(text)
    except json.JSONDecodeError:
        risk = {}

    updated = dict(state["updated_form"])
    updated["severity"] = risk.get("severity")
    updated["recommended_action"] = risk.get("recommended_action")
    updated["risk_details"] = risk.get("risk_details")
    return {"updated_form": updated}


# ---------- WIRE THE FLOWCHART TOGETHER ----------
graph = StateGraph(AgentState)
graph.add_node("extract", extract_node)
graph.add_node("merge", merge_node)
graph.add_node("assess", assess_node)

graph.set_entry_point("extract")       # start here
graph.add_edge("extract", "merge")     # extract -> merge
graph.add_edge("merge", "assess")      # merge -> assess
graph.add_edge("assess", END)          # done

agent = graph.compile()                # the runnable flowchart


# The function the rest of our app will call:
def run_agent(user_message: str, current_form: dict) -> dict:
    result = agent.invoke({
        "user_message": user_message,
        "current_form": current_form,
        "extracted_fields": {},
        "updated_form": {},
    })
    return result["updated_form"]