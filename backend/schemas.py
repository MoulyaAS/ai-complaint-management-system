# schemas.py
# This file defines the STRUCTURE of our complaint form.
# Think of it as the blank paper form itself: what boxes exist and what type each box is.

from pydantic import BaseModel
from typing import Optional

# "Optional[str] = None" means: this box CAN be empty (None = empty).
# That is important because the AI fills only the fields it finds in the user's message.

class ComplaintForm(BaseModel):
    # ---- Complaint details (left form) ----
    complainant_name: Optional[str] = None      # who complained, e.g. "Apollo Pharmacy"
    product_name: Optional[str] = None          # e.g. "Amoxicillin capsules"
    product_strength: Optional[str] = None      # e.g. "500 mg" or "IP/BP"
    batch_number: Optional[str] = None          # e.g. "BMX24602"
    manufacturing_date: Optional[str] = None    # e.g. "2025-03-10"
    expiry_date: Optional[str] = None           # e.g. "2027-03-09"
    affected_quantity: Optional[str] = None     # e.g. "48 capsules" or "50 kg 2 HDPE drums"
    complaint_description: Optional[str] = None # the issue, e.g. "discolored capsules"

    # ---- AI Risk Assessment (bottom of the form) ----
    severity: Optional[str] = None              # "Minor" / "Major" / "Critical"
    recommended_action: Optional[str] = None    # e.g. "Route to QA investigation"
    risk_details: Optional[str] = None          # AI's explanation of the risk


class ChatRequest(BaseModel):
    # This is the shape of what the FRONTEND SENDS US on every chat message:
    message: str                                # what the user typed
    current_form_state: ComplaintForm           # the form as it looks right now