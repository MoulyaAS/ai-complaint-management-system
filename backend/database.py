# database.py
# Connects to PostgreSQL and defines the "complaints" table.
# Every time the AI updates the form, we save a snapshot here.
# In a real QMS, records like this are a legal/compliance requirement.

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

load_dotenv()

# Reads: postgresql://postgres:postgres@localhost:5432/postgres from .env
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True)          # auto-numbered
    created_at = Column(DateTime, default=datetime.utcnow)

    complainant_name = Column(String)
    product_name = Column(String)
    product_strength = Column(String)
    batch_number = Column(String)
    manufacturing_date = Column(String)
    expiry_date = Column(String)
    affected_quantity = Column(String)
    complaint_description = Column(Text)
    severity = Column(String)
    recommended_action = Column(Text)
    risk_details = Column(Text)


# Create the table in Postgres if it doesn't exist yet (runs on import)
Base.metadata.create_all(engine)


def save_complaint(form: dict) -> int:
    """Save one snapshot of the form. Returns the new row's id."""
    session = SessionLocal()
    complaint = Complaint(**{k: v for k, v in form.items() if hasattr(Complaint, k)})
    session.add(complaint)
    session.commit()
    new_id = complaint.id
    session.close()
    return new_id