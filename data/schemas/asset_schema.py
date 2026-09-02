"""
Common schema for all asset types (video transcript, slide/text, quiz, discussion).

Why this matters (PRD Section 5.4):
"All modality records must use consistent schemas for source ID, segment ID,
modality, timestamp, topic, and permissions."

Instead of storing video/slide/quiz/discussion differently, we normalize
EVERYTHING into this one shape. This is what makes "cross-modal retrieval"
possible later - the retrieval layer doesn't care what modality it is,
it just searches over a list of Segment objects.
"""

from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Segment:
    """
    One retrievable, citable 'chunk' of content.
    A single video transcript becomes MANY Segment objects (one per chunk).
    """
    segment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str = ""            # which asset this came from, e.g. "video_001"
    modality: str = ""             # "video" | "slide" | "quiz" | "discussion"
    topic: str = ""                # concept/topic tag, e.g. "Newton's Second Law"
    text: str = ""                 # the actual chunked content
    timestamp: Optional[str] = None  # e.g. "00:04:12" - only for video
    source_title: str = ""         # human-readable name, e.g. "Lecture 3: Motion"

    def to_dict(self):
        return {
            "segment_id": self.segment_id,
            "source_id": self.source_id,
            "modality": self.modality,
            "topic": self.topic,
            "text": self.text,
            "timestamp": self.timestamp,
            "source_title": self.source_title,
        }
