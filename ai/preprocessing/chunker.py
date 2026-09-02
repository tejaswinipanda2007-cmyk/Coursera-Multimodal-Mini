"""
Preprocessing Layer (PRD Section 5.4 - "Preprocessing and Data Normalization")

Job: take RAW_ASSETS (any modality) and turn each into a list of Segment
objects using the common schema. This is what lets a video's transcript
and a discussion post live in the SAME searchable index later.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from data.schemas.asset_schema import Segment
from data.sample_assets.raw_assets import RAW_ASSETS


def chunk_asset(asset: dict) -> list[Segment]:
    """Convert one raw asset dict into a list of Segment objects."""
    segments = []
    for timestamp, text in asset["content"]:
        seg = Segment(
            source_id=asset["source_id"],
            modality=asset["modality"],
            topic=asset["topic"],
            text=text,
            timestamp=timestamp,
            source_title=asset["source_title"],
        )
        segments.append(seg)
    return segments


def preprocess_all_assets() -> list[Segment]:
    """Run chunking over every asset in RAW_ASSETS. Returns a flat list of Segments."""
    all_segments = []
    for asset in RAW_ASSETS:
        all_segments.extend(chunk_asset(asset))
    return all_segments


if __name__ == "__main__":
    segments = preprocess_all_assets()
    print(f"Total segments created: {len(segments)}\n")
    for s in segments:
        tag = f"[{s.modality}]"
        ts = f" @ {s.timestamp}" if s.timestamp else ""
        print(f"{tag:12s}{ts:12s} {s.text[:70]}")
