"""
Database Models (PRD Section 5.4 - "Human Review, Governance, and Feedback")

We use SQLAlchemy (an ORM - Object Relational Mapper) so we write Python
classes instead of raw SQL. SQLAlchemy translates our Python code into SQL
commands behind the scenes.

We use SQLite for local development (zero setup, single file database).
For deployment, this same code works with PostgreSQL - only the connection
string in db.py changes. This is one of the benefits of using an ORM.

Two tables:
  1. QueryLog     - every question asked + the AI's generated insight
  2. ReviewAction - a human reviewer's decision on a QueryLog (approve/reject/edit)
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone
import uuid

Base = declarative_base()


class QueryLog(Base):
    """One row = one educator question + the evidence retrieved + the AI insight generated."""
    __tablename__ = "query_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())[:8])
    query_text = Column(Text, nullable=False)
    evidence_json = Column(Text)       # the raw evidence list, stored as JSON text
    insight_json = Column(Text)        # the synthesized insight, stored as JSON text
    confidence = Column(String)        # "high" | "medium" | "low" - duplicated here for easy filtering
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reviews = relationship("ReviewAction", back_populates="query_log")


class ReviewAction(Base):
    """One row = one human reviewer decision on a QueryLog's insight."""
    __tablename__ = "review_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_log_id = Column(String, ForeignKey("query_logs.id"), nullable=False)
    decision = Column(String, nullable=False)   # "approved" | "rejected" | "needs_revision"
    reviewer_note = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    query_log = relationship("QueryLog", back_populates="reviews")
