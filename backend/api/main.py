"""
Backend API
Coursera Multimodal Intelligence Platform

This API connects the complete AI pipeline:

    Sample Assets
        ↓
    Preprocessing
        ↓
    Gemini Embeddings
        ↓
    ChromaDB Retrieval
        ↓
    Gemini Grounded Synthesis
        ↓
    Database Logging
        ↓
    Human Review
        ↓
    Dashboard Metrics

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


# ===================================================================
# IMPORTS
# ===================================================================

import sys
import os
import json
import traceback


# ===================================================================
# PROJECT ROOT
# ===================================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ===================================================================
# FASTAPI / PYDANTIC
# ===================================================================

from fastapi import (
    FastAPI,
    Depends,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import (
    BaseModel,
    Field
)


# ===================================================================
# DATABASE
# ===================================================================

from sqlalchemy.orm import Session

from backend.database.db import (
    init_db,
    get_db
)

from backend.database.models import (
    QueryLog,
    ReviewAction
)


# ===================================================================
# AI PIPELINE
# ===================================================================

from ai.preprocessing.chunker import (
    preprocess_all_assets
)

from ai.retrieval.retriever import (
    retrieve,
    index_segments,
    collection_count
)

from ai.synthesis.synthesizer import (
    synthesize_insight
)


# ===================================================================
# FASTAPI APPLICATION
# ===================================================================

app = FastAPI(
    title="Coursera Multimodal Intelligence Platform",
    version="1.0.0",
    description=(
        "Backend API for unified retrieval, grounded Gemini synthesis, "
        "human review feedback, and operational metrics."
    )
)


# ===================================================================
# CORS
# ===================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================================================================
# STARTUP
# ===================================================================

@app.on_event("startup")
def on_startup():
    """
    Initialize database tables when the application starts.
    """

    try:

        init_db()

        print(
            "Database initialized successfully."
        )

    except Exception as exc:

        print(
            "Database initialization failed:"
        )

        print(
            str(exc)
        )

        traceback.print_exc()

        # Do not silently continue if database initialization fails.
        raise


# ===================================================================
# REQUEST SCHEMAS
# ===================================================================

class QueryRequest(BaseModel):
    """
    Request body for the unified query endpoint.
    """

    query: str = Field(
        ...,
        min_length=1,
        description=(
            "Natural-language question about learner friction."
        )
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description=(
            "Maximum number of evidence pieces to retrieve."
        )
    )


class ReviewFeedbackRequest(BaseModel):
    """
    Request body for human review feedback.
    """

    query_log_id: str = Field(
        ...,
        min_length=1
    )

    decision: str = Field(
        ...,
        description=(
            "Review decision: approved, rejected, "
            "or needs_revision."
        )
    )

    reviewer_note: str = Field(
        default="",
        description="Optional reviewer comment."
    )


# ===================================================================
# HELPER
# ===================================================================

def ensure_index_ready() -> int:
    """
    Make sure ChromaDB contains searchable evidence.

    Render uses a separate runtime environment from the local machine.
    Therefore, the local ChromaDB data may not exist after deployment.

    For this demo build, if the ChromaDB collection is empty:

        1. Load sample assets
        2. Preprocess them
        3. Generate embeddings
        4. Store them in ChromaDB

    Returns:
        Number of searchable segments.
    """

    try:

        current_count = collection_count()

        print(
            f"Current ChromaDB collection count: "
            f"{current_count}"
        )

        # -----------------------------------------------------------
        # Already indexed
        # -----------------------------------------------------------

        if current_count > 0:

            return current_count

        # -----------------------------------------------------------
        # Collection empty
        # -----------------------------------------------------------

        print(
            "ChromaDB collection is empty."
        )

        print(
            "Starting automatic indexing of sample assets..."
        )

        # -----------------------------------------------------------
        # Preprocess
        # -----------------------------------------------------------

        segments = preprocess_all_assets()

        if not segments:

            raise RuntimeError(
                "No sample segments were generated "
                "during preprocessing."
            )

        print(
            f"Preprocessed {len(segments)} segments."
        )

        # -----------------------------------------------------------
        # Index
        # -----------------------------------------------------------

        index_segments(
            segments,
            clear_existing=False
        )

        # -----------------------------------------------------------
        # Verify
        # -----------------------------------------------------------

        final_count = collection_count()

        print(
            "ChromaDB indexing completed. "
            f"Collection now contains {final_count} segments."
        )

        if final_count == 0:

            raise RuntimeError(
                "Indexing completed but ChromaDB "
                "is still empty."
            )

        return final_count

    except Exception as exc:

        print(
            "ChromaDB initialization/indexing failed:"
        )

        print(
            str(exc)
        )

        traceback.print_exc()

        raise RuntimeError(
            f"Vector database initialization failed: {exc}"
        ) from exc


# ===================================================================
# POST /api/query
# ===================================================================

@app.post("/api/query")
def run_query(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Main unified query endpoint.

    Workflow:

        1. Validate query
        2. Ensure ChromaDB is ready
        3. Retrieve relevant evidence
        4. Generate grounded Gemini insight
        5. Store query and result in database
        6. Return evidence and insight
    """

    # =================================================================
    # 1. VALIDATE QUERY
    # =================================================================

    query = request.query.strip()

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )


    # =================================================================
    # 2. ENSURE CHROMADB IS READY
    # =================================================================

    try:

        available_count = ensure_index_ready()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Vector database error: {exc}"
            )
        )


    # =================================================================
    # 3. SAFE TOP-K
    # =================================================================

    actual_top_k = min(
        request.top_k,
        available_count
    )

    if actual_top_k <= 0:

        raise HTTPException(
            status_code=500,
            detail=(
                "No searchable evidence is available."
            )
        )


    # =================================================================
    # 4. RETRIEVAL
    # =================================================================

    try:

        print(
            f"Running retrieval for query: "
            f"'{query}' with top_k={actual_top_k}"
        )

        evidence = retrieve(
            query,
            top_k=actual_top_k
        )

        print(
            f"Retrieved {len(evidence)} evidence pieces."
        )

        # If retrieval unexpectedly returns nothing,
        # let the synthesis layer return insufficient evidence.
        if evidence is None:

            evidence = []

    except Exception as exc:

        print(
            "Retrieval failed:"
        )

        print(
            str(exc)
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Retrieval failed: {exc}"
            )
        ) from exc


    # =================================================================
    # 5. GEMINI SYNTHESIS
    # =================================================================

    try:

        print(
            "Starting Gemini synthesis..."
        )

        insight = synthesize_insight(
            query,
            evidence
        )

        print(
            "Gemini synthesis completed."
        )

    except Exception as exc:

        print(
            "Gemini synthesis failed:"
        )

        print(
            str(exc)
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Gemini synthesis failed: {exc}"
            )
        ) from exc


    # =================================================================
    # 6. DATABASE LOGGING
    # =================================================================

    try:

        confidence = (
            insight.get(
                "confidence",
                "unknown"
            )
            if isinstance(insight, dict)
            else "unknown"
        )

        log_entry = QueryLog(
            query_text=query,

            evidence_json=json.dumps(
                evidence,
                default=str
            ),

            insight_json=json.dumps(
                insight,
                default=str
            ),

            confidence=confidence
        )

        db.add(
            log_entry
        )

        db.commit()

        db.refresh(
            log_entry
        )

    except Exception as exc:

        db.rollback()

        print(
            "Database logging failed:"
        )

        print(
            str(exc)
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Database logging failed: {exc}"
            )
        ) from exc


    # =================================================================
    # 7. RESPONSE
    # =================================================================

    return {
        "status": "success",

        "query_log_id": log_entry.id,

        "query": query,

        "evidence_count": len(evidence),

        "evidence": evidence,

        "insight": insight
    }


# ===================================================================
# GET /api/insights/{query_log_id}
# ===================================================================

@app.get(
    "/api/insights/{query_log_id}"
)
def get_insight(
    query_log_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetch a previously generated insight,
    evidence, and review history.
    """

    # -----------------------------------------------------------------
    # Find query log
    # -----------------------------------------------------------------

    log_entry = (
        db.query(QueryLog)
        .filter(
            QueryLog.id == query_log_id
        )
        .first()
    )

    if not log_entry:

        raise HTTPException(
            status_code=404,
            detail="Insight not found."
        )


    # -----------------------------------------------------------------
    # Read stored JSON
    # -----------------------------------------------------------------

    try:

        evidence = json.loads(
            log_entry.evidence_json or "[]"
        )

        insight = json.loads(
            log_entry.insight_json or "{}"
        )

    except json.JSONDecodeError as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Stored insight data is corrupted: {exc}"
            )
        )


    # -----------------------------------------------------------------
    # Reviews
    # -----------------------------------------------------------------

    reviews = []

    for review in log_entry.reviews:

        reviews.append(
            {
                "decision": review.decision,

                "note": review.reviewer_note,

                "created_at": (
                    review.created_at.isoformat()
                    if review.created_at
                    else None
                )
            }
        )


    # -----------------------------------------------------------------
    # Response
    # -----------------------------------------------------------------

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

        "reviews": reviews
    }


# ===================================================================
# POST /api/review-feedback
# ===================================================================

@app.post(
    "/api/review-feedback"
)
def submit_review(
    request: ReviewFeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Record human review feedback.

    Allowed decisions:

        approved
        rejected
        needs_revision
    """

    # -----------------------------------------------------------------
    # Find query
    # -----------------------------------------------------------------

    log_entry = (
        db.query(QueryLog)
        .filter(
            QueryLog.id == request.query_log_id
        )
        .first()
    )

    if not log_entry:

        raise HTTPException(
            status_code=404,
            detail="Query log not found."
        )


    # -----------------------------------------------------------------
    # Validate decision
    # -----------------------------------------------------------------

    decision = (
        request.decision
        .strip()
        .lower()
    )

    allowed_decisions = {
        "approved",
        "rejected",
        "needs_revision"
    }

    if decision not in allowed_decisions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid decision value. "
                "Use: approved, rejected, "
                "or needs_revision."
            )
        )


    # -----------------------------------------------------------------
    # Save review
    # -----------------------------------------------------------------

    try:

        review = ReviewAction(
            query_log_id=request.query_log_id,

            decision=decision,

            reviewer_note=(
                request.reviewer_note.strip()
            )
        )

        db.add(
            review
        )

        db.commit()

    except Exception as exc:

        db.rollback()

        print(
            "Review logging failed:"
        )

        print(
            str(exc)
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not save review: {exc}"
            )
        ) from exc


    # -----------------------------------------------------------------
    # Response
    # -----------------------------------------------------------------

    return {
        "status": "recorded",

        "query_log_id": request.query_log_id,

        "decision": decision
    }


# ===================================================================
# GET /api/metrics
# ===================================================================

@app.get(
    "/api/metrics"
)
def get_metrics(
    db: Session = Depends(get_db)
):
    """
    Return basic metrics for the dashboard.
    """

    try:

        # -------------------------------------------------------------
        # Total queries
        # -------------------------------------------------------------

        total_queries = (
            db.query(QueryLog)
            .count()
        )


        # -------------------------------------------------------------
        # Total reviews
        # -------------------------------------------------------------

        total_reviews = (
            db.query(ReviewAction)
            .count()
        )


        # -------------------------------------------------------------
        # Confidence breakdown
        # -------------------------------------------------------------

        confidence_breakdown = {}

        for level in (
            "high",
            "medium",
            "low"
        ):

            confidence_breakdown[level] = (
                db.query(QueryLog)
                .filter(
                    QueryLog.confidence == level
                )
                .count()
            )


        # -------------------------------------------------------------
        # Review decision breakdown
        # -------------------------------------------------------------

        decision_breakdown = {}

        for decision in (
            "approved",
            "rejected",
            "needs_revision"
        ):

            decision_breakdown[decision] = (
                db.query(ReviewAction)
                .filter(
                    ReviewAction.decision == decision
                )
                .count()
            )


        # -------------------------------------------------------------
        # Response
        # -------------------------------------------------------------

        return {
            "total_queries": total_queries,

            "total_reviews": total_reviews,

            "confidence_breakdown": (
                confidence_breakdown
            ),

            "decision_breakdown": (
                decision_breakdown
            )
        }


    except Exception as exc:

        print(
            "Metrics query failed:"
        )

        print(
            str(exc)
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not load metrics: {exc}"
            )
        ) from exc


# ===================================================================
# GET /
# ===================================================================

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
        )
    }