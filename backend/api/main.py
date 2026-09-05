"""
Backend API
Coursera Multimodal Intelligence Platform

This API wraps the AI pipeline:
    preprocessing -> embeddings -> ChromaDB retrieval -> Gemini synthesis

Endpoints:
    POST /api/query
    GET  /api/insights/{id}
    POST /api/review-feedback
    GET  /api/metrics
    GET  /

Run locally:
    uvicorn backend.api.main:app --reload

Swagger:
    http://127.0.0.1:8000/docs
"""

import sys
import os
import json
import traceback

# -------------------------------------------------------------------
# Project root
# -------------------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# -------------------------------------------------------------------
# FastAPI / Pydantic
# -------------------------------------------------------------------

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# -------------------------------------------------------------------
# Database
# -------------------------------------------------------------------

from sqlalchemy.orm import Session

from backend.database.db import init_db, get_db
from backend.database.models import QueryLog, ReviewAction


# -------------------------------------------------------------------
# AI pipeline
# -------------------------------------------------------------------

from ai.preprocessing.chunker import preprocess_all_assets

from ai.retrieval.retriever import (
    retrieve,
    index_segments,
    collection_count,
)

from ai.synthesis.synthesizer import synthesize_insight


# -------------------------------------------------------------------
# FastAPI application
# -------------------------------------------------------------------

app = FastAPI(
    title="Coursera Multimodal Intelligence Platform (Solo Build)",
    version="1.0.0",
    description=(
        "Backend API for unified retrieval, grounded Gemini synthesis, "
        "human review feedback, and operational metrics."
    ),
)


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Startup
# -------------------------------------------------------------------

@app.on_event("startup")
def on_startup():
    """
    Initialize database tables when the API starts.
    """

    try:
        init_db()
        print("Database initialized successfully.")

    except Exception as exc:
        print("Database initialization failed:")
        print(str(exc))
        traceback.print_exc()


# -------------------------------------------------------------------
# Request schemas
# -------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Natural-language question about learner friction.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of evidence pieces to retrieve.",
    )


class ReviewFeedbackRequest(BaseModel):
    query_log_id: str

    decision: str
    # allowed values:
    # approved
    # rejected
    # needs_revision

    reviewer_note: str = ""


# -------------------------------------------------------------------
# Helper: make sure ChromaDB has data
# -------------------------------------------------------------------

def ensure_index_ready() -> int:
    """
    Make sure the ChromaDB collection contains searchable segments.

    Render uses a separate runtime environment from the local machine.
    Therefore the local chroma_db folder may not contain the indexed data.

    For this demo build, if the collection is empty:
        1. preprocess sample assets
        2. generate embeddings
        3. index them into ChromaDB

    Returns:
        Number of indexed segments.
    """

    try:
        current_count = collection_count()

        print(f"Current ChromaDB collection count: {current_count}")

        if current_count > 0:
            return current_count

        print("ChromaDB is empty.")
        print("Starting automatic indexing of sample assets...")

        segments = preprocess_all_assets()

        if not segments:
            raise RuntimeError(
                "No sample segments were generated during preprocessing."
            )

        print(f"Preprocessed {len(segments)} segments.")

        index_segments(
            segments,
            clear_existing=False,
        )

        final_count = collection_count()

        print(
            f"ChromaDB indexing completed. "
            f"Collection now contains {final_count} segments."
        )

        if final_count == 0:
            raise RuntimeError(
                "Indexing completed but ChromaDB is still empty."
            )

        return final_count

    except Exception as exc:
        print("ChromaDB initialization/indexing failed:")
        print(str(exc))
        traceback.print_exc()

        raise RuntimeError(
            f"Vector database initialization failed: {str(exc)}"
        )


# -------------------------------------------------------------------
# POST /api/query
# -------------------------------------------------------------------

@app.post("/api/query")
def run_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
):
    """
    Core unified query endpoint.

    Workflow:
        1. Validate query
        2. Ensure ChromaDB is indexed
        3. Retrieve relevant evidence
        4. Synthesize grounded insight with Gemini
        5. Store query + evidence + insight in database
        6. Return result
    """

    # ---------------------------------------------------------------
    # Validate query
    # ---------------------------------------------------------------

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    # ---------------------------------------------------------------
    # Ensure vector database is ready
    # ---------------------------------------------------------------

    try:
        available_count = ensure_index_ready()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Vector database error: {str(exc)}",
        )

    # ---------------------------------------------------------------
    # Prevent asking ChromaDB for more results than available
    # ---------------------------------------------------------------

    actual_top_k = min(
        request.top_k,
        available_count,
    )

    if actual_top_k <= 0:
        raise HTTPException(
            status_code=500,
            detail="No searchable evidence is available.",
        )

    # ---------------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------------

    try:
        print(
            f"Running retrieval for query: '{query}' "
            f"with top_k={actual_top_k}"
        )

        evidence = retrieve(
            query,
            top_k=actual_top_k,
        )

        print(
            f"Retrieved {len(evidence)} evidence pieces."
        )

    except Exception as exc:
        print("Retrieval failed:")
        print(str(exc))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(exc)}",
        )

    # ---------------------------------------------------------------
    # Gemini synthesis
    # ---------------------------------------------------------------

    try:
        print("Starting Gemini synthesis...")

        insight = synthesize_insight(
            query,
            evidence,
        )

        print("Gemini synthesis completed.")

    except Exception as exc:
        print("Gemini synthesis failed:")
        print(str(exc))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Gemini synthesis failed: {str(exc)}",
        )

    # ---------------------------------------------------------------
    # Database logging
    # ---------------------------------------------------------------

    try:
        log_entry = QueryLog(
            query_text=query,
            evidence_json=json.dumps(
                evidence,
                default=str,
            ),
            insight_json=json.dumps(
                insight,
                default=str,
            ),
            confidence=insight.get(
                "confidence",
                "unknown",
            ),
        )

        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

    except Exception as exc:
        db.rollback()

        print("Database logging failed:")
        print(str(exc))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Database logging failed: {str(exc)}",
        )

    # ---------------------------------------------------------------
    # Final response
    # ---------------------------------------------------------------

    return {
        "status": "success",
        "query_log_id": log_entry.id,
        "query": query,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "insight": insight,
    }


# -------------------------------------------------------------------
# GET /api/insights/{query_log_id}
# -------------------------------------------------------------------

@app.get("/api/insights/{query_log_id}")
def get_insight(
    query_log_id: str,
    db: Session = Depends(get_db),
):
    """
    Fetch a previously generated insight and its review history.
    """

    log_entry = (
        db.query(QueryLog)
        .filter(QueryLog.id == query_log_id)
        .first()
    )

    if not log_entry:
        raise HTTPException(
            status_code=404,
            detail="Insight not found.",
        )

    try:
        evidence = json.loads(
            log_entry.evidence_json or "[]"
        )

        insight = json.loads(
            log_entry.insight_json or "{}"
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Stored insight data is corrupted.",
        )

    return {
        "query_log_id": log_entry.id,
        "query_text": log_entry.query_text,
        "evidence": evidence,
        "insight": insight,
        "created_at": (
            log_entry.created_at.isoformat()
            if log_entry.created_at
            else None
        ),
        "reviews": [
            {
                "decision": review.decision,
                "note": review.reviewer_note,
                "created_at": (
                    review.created_at.isoformat()
                    if review.created_at
                    else None
                ),
            }
            for review in log_entry.reviews
        ],
    }


# -------------------------------------------------------------------
# POST /api/review-feedback
# -------------------------------------------------------------------

@app.post("/api/review-feedback")
def submit_review(
    request: ReviewFeedbackRequest,
    db: Session = Depends(get_db),
):
    """
    Record a human reviewer's decision.

    Allowed decisions:
        approved
        rejected
        needs_revision
    """

    log_entry = (
        db.query(QueryLog)
        .filter(QueryLog.id == request.query_log_id)
        .first()
    )

    if not log_entry:
        raise HTTPException(
            status_code=404,
            detail="Query log not found.",
        )

    allowed_decisions = {
        "approved",
        "rejected",
        "needs_revision",
    }

    if request.decision not in allowed_decisions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid decision value. "
                "Use: approved, rejected, or needs_revision."
            ),
        )

    try:
        review = ReviewAction(
            query_log_id=request.query_log_id,
            decision=request.decision,
            reviewer_note=request.reviewer_note.strip(),
        )

        db.add(review)
        db.commit()

    except Exception as exc:
        db.rollback()

        print("Review logging failed:")
        print(str(exc))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Could not save review: {str(exc)}",
        )

    return {
        "status": "recorded",
        "query_log_id": request.query_log_id,
        "decision": request.decision,
    }


# -------------------------------------------------------------------
# GET /api/metrics
# -------------------------------------------------------------------

@app.get("/api/metrics")
def get_metrics(
    db: Session = Depends(get_db),
):
    """
    Basic operational metrics for the dashboard.
    """

    try:
        total_queries = (
            db.query(QueryLog)
            .count()
        )

        total_reviews = (
            db.query(ReviewAction)
            .count()
        )

        confidence_breakdown = {}

        for level in (
            "high",
            "medium",
            "low",
        ):
            confidence_breakdown[level] = (
                db.query(QueryLog)
                .filter(
                    QueryLog.confidence == level
                )
                .count()
            )

        decision_breakdown = {}

        for decision in (
            "approved",
            "rejected",
            "needs_revision",
        ):
            decision_breakdown[decision] = (
                db.query(ReviewAction)
                .filter(
                    ReviewAction.decision == decision
                )
                .count()
            )

        return {
            "total_queries": total_queries,
            "total_reviews": total_reviews,
            "confidence_breakdown": confidence_breakdown,
            "decision_breakdown": decision_breakdown,
        }

    except Exception as exc:
        print("Metrics query failed:")
        print(str(exc))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Could not load metrics: {str(exc)}",
        )


# -------------------------------------------------------------------
# GET /
# -------------------------------------------------------------------

@app.get("/")
def root():
    """
    Health-check endpoint.
    """

    return {
        "status": "ok",
        "message": (
            "Coursera Multimodal Intelligence Platform "
            "API is running."
        ),
    }