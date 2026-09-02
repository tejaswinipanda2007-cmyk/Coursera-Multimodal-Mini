"""
Backend API (PRD Section 7.3 - "Backend and API Approach")

This wraps our AI pipeline (retrieval + synthesis) behind HTTP endpoints,
so any frontend (Streamlit, React, curl, Postman) can use it without
knowing any Python internals.

Endpoints:
  POST /api/query            -> run the full pipeline for a question, log it, return the insight
  GET  /api/insights/{id}    -> fetch a previously generated insight by its ID
  POST /api/review-feedback  -> record a human reviewer's decision on an insight
  GET  /api/metrics          -> basic usage stats for the Operations Dashboard

Run this with:  uvicorn backend.api.main:app --reload
Then open:      http://127.0.0.1:8000/docs   <- interactive API testing page (auto-generated!)
"""

import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.db import init_db, get_db
from backend.database.models import QueryLog, ReviewAction
from ai.retrieval.retriever import retrieve
from ai.synthesis.synthesizer import synthesize_insight

app = FastAPI(title="Coursera Multimodal Intelligence Platform (Solo Build)")

# Allows a frontend running on a different port (e.g. Streamlit on :8501) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()  # creates database tables on first run


# ---- Request/response schemas (Pydantic validates incoming JSON automatically) ----

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class ReviewFeedbackRequest(BaseModel):
    query_log_id: str
    decision: str  # "approved" | "rejected" | "needs_revision"
    reviewer_note: str = ""


# ---- Endpoints ----

@app.post("/api/query")
def run_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    The core endpoint. Given a question:
    1. Retrieve relevant evidence across all modalities
    2. Synthesize a grounded, cited insight via Gemini
    3. Log everything to the database
    4. Return the insight + its DB record ID (used later for review-feedback)
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    evidence = retrieve(request.query, top_k=request.top_k)
    insight = synthesize_insight(request.query, evidence)

    log_entry = QueryLog(
        query_text=request.query,
        evidence_json=json.dumps(evidence),
        insight_json=json.dumps(insight),
        confidence=insight.get("confidence", "unknown"),
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return {
        "query_log_id": log_entry.id,
        "evidence": evidence,
        "insight": insight,
    }


@app.get("/api/insights/{query_log_id}")
def get_insight(query_log_id: str, db: Session = Depends(get_db)):
    """Fetch a previously generated insight and its review history."""
    log_entry = db.query(QueryLog).filter(QueryLog.id == query_log_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Insight not found.")

    return {
        "query_log_id": log_entry.id,
        "query_text": log_entry.query_text,
        "evidence": json.loads(log_entry.evidence_json),
        "insight": json.loads(log_entry.insight_json),
        "created_at": log_entry.created_at.isoformat(),
        "reviews": [
            {"decision": r.decision, "note": r.reviewer_note, "created_at": r.created_at.isoformat()}
            for r in log_entry.reviews
        ],
    }


@app.post("/api/review-feedback")
def submit_review(request: ReviewFeedbackRequest, db: Session = Depends(get_db)):
    """A human reviewer approves, rejects, or requests revision on an insight."""
    log_entry = db.query(QueryLog).filter(QueryLog.id == request.query_log_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Query log not found.")

    if request.decision not in ("approved", "rejected", "needs_revision"):
        raise HTTPException(status_code=400, detail="Invalid decision value.")

    review = ReviewAction(
        query_log_id=request.query_log_id,
        decision=request.decision,
        reviewer_note=request.reviewer_note,
    )
    db.add(review)
    db.commit()

    return {"status": "recorded", "query_log_id": request.query_log_id, "decision": request.decision}


@app.get("/api/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """Basic stats for the Operations Dashboard (PRD Section 5.2)."""
    total_queries = db.query(QueryLog).count()
    total_reviews = db.query(ReviewAction).count()

    confidence_breakdown = {}
    for level in ("high", "medium", "low"):
        confidence_breakdown[level] = (
            db.query(QueryLog).filter(QueryLog.confidence == level).count()
        )

    decision_breakdown = {}
    for decision in ("approved", "rejected", "needs_revision"):
        decision_breakdown[decision] = (
            db.query(ReviewAction).filter(ReviewAction.decision == decision).count()
        )

    return {
        "total_queries": total_queries,
        "total_reviews": total_reviews,
        "confidence_breakdown": confidence_breakdown,
        "decision_breakdown": decision_breakdown,
    }


@app.get("/")
def root():
    return {"status": "ok", "message": "Coursera Multimodal Intelligence Platform API is running."}
