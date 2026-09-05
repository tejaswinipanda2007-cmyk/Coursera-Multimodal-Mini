"""
LLM Synthesis Layer
--------------------

Takes retrieved evidence and asks Gemini to generate a grounded insight.

Important:
- Gemini can ONLY use the retrieved evidence.
- Every claim should be traceable to evidence.
- Output is expected as JSON.
- Weak or missing evidence should result in low confidence.
- The implementation is intentionally defensive so API/model output
  does not crash the FastAPI backend.
"""

import sys
import os
import json
from typing import Any

from google import genai
from dotenv import load_dotenv


# -------------------------------------------------------------------
# PROJECT PATH
# -------------------------------------------------------------------

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)


# -------------------------------------------------------------------
# ENVIRONMENT
# -------------------------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

_client = genai.Client(api_key=API_KEY) if API_KEY else None


# -------------------------------------------------------------------
# GEMINI MODEL
# -------------------------------------------------------------------

SYNTHESIS_MODEL = "gemini-3.5-flash"


# -------------------------------------------------------------------
# PROMPT
# -------------------------------------------------------------------

SYNTHESIS_PROMPT_TEMPLATE = """
You are an AI assistant for Coursera's content team.

Your task is to analyze ONLY the retrieved evidence provided below
and generate a grounded insight for a human reviewer.

STRICT RULES:

1. Use ONLY the evidence provided below.
2. Do NOT use outside knowledge.
3. Do NOT invent facts.
4. Every claim in the insight must be supported by at least one
   evidence item.
5. Use the segment IDs from the evidence when identifying evidence.
6. If the evidence is weak or insufficient, use "low" confidence.
7. If the evidence is contradictory, mention the uncertainty.
8. Keep the insight concise and specific.
9. Return ONLY valid JSON.
10. Do not return markdown.
11. Do not use ```json fences.
12. Do not add any explanation before or after the JSON.

EDUCATOR QUESTION:
{query}

RETRIEVED EVIDENCE:
{evidence_block}

Return exactly this JSON structure:

{{
  "insight": "A concise 2-3 sentence explanation of the learning friction pattern.",
  "evidence_used": ["segment_id_1", "segment_id_2"],
  "confidence": "high",
  "confidence_reason": "One sentence explaining why this confidence level was selected.",
  "recommendation": "One concrete and actionable suggestion for the content team."
}}
"""


# -------------------------------------------------------------------
# EVIDENCE FORMATTER
# -------------------------------------------------------------------

def _format_evidence_block(evidence: list[dict]) -> str:
    """
    Convert retrieved evidence into a readable prompt block.
    """

    lines = []

    for e in evidence:

        segment_id = e.get("segment_id", "unknown")
        modality = e.get("modality", "unknown")
        timestamp = e.get("timestamp")
        source_title = e.get("source_title", "unknown source")
        text = e.get("text", "")

        timestamp_text = ""

        if timestamp:
            timestamp_text = f" @ {timestamp}"

        lines.append(
            f"- [{segment_id}] "
            f"({modality}{timestamp_text}, "
            f"from '{source_title}'): "
            f"{text}"
        )

    return "\n".join(lines)


# -------------------------------------------------------------------
# SAFE JSON EXTRACTION
# -------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    """
    Safely extract a JSON object from Gemini output.

    Handles:
    - normal JSON
    - ```json ... ``` output
    - extra text surrounding JSON
    """

    if not text:
        raise ValueError("Gemini returned an empty response.")

    cleaned = text.strip()

    # Remove markdown fences if present
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1)
        cleaned = cleaned.replace("```JSON", "", 1)
        cleaned = cleaned.replace("```", "", 1)
        cleaned = cleaned.strip()

    # First attempt: direct JSON parsing
    try:
        result = json.loads(cleaned)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # Second attempt:
    # Extract everything between first { and last }
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")

    if first_brace != -1 and last_brace != -1:
        json_candidate = cleaned[first_brace:last_brace + 1]

        try:
            result = json.loads(json_candidate)

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            pass

    raise ValueError("Gemini response was not valid JSON.")


# -------------------------------------------------------------------
# RESULT NORMALIZER
# -------------------------------------------------------------------

def _normalize_result(
    result: dict,
    evidence: list[dict]
) -> dict:
    """
    Make sure the returned result always follows the application's
    expected structure.
    """

    valid_segment_ids = {
        str(e.get("segment_id"))
        for e in evidence
        if e.get("segment_id") is not None
    }

    insight = result.get("insight")

    evidence_used = result.get("evidence_used", [])

    confidence = str(
        result.get("confidence", "low")
    ).lower().strip()

    confidence_reason = result.get(
        "confidence_reason",
        "Confidence could not be determined reliably."
    )

    recommendation = result.get("recommendation")

    # Make sure evidence_used is a list
    if not isinstance(evidence_used, list):
        evidence_used = []

    # Keep only evidence IDs that actually exist
    evidence_used = [
        str(segment_id)
        for segment_id in evidence_used
        if str(segment_id) in valid_segment_ids
    ]

    # Valid confidence values only
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"

    # If Gemini claims high confidence but did not cite evidence,
    # downgrade it.
    if not evidence_used:
        confidence = "low"

    # Ensure strings are returned
    if insight is not None:
        insight = str(insight).strip()

    confidence_reason = str(confidence_reason).strip()

    if recommendation is not None:
        recommendation = str(recommendation).strip()

    return {
        "insight": insight,
        "evidence_used": evidence_used,
        "confidence": confidence,
        "confidence_reason": confidence_reason,
        "recommendation": recommendation,
    }


# -------------------------------------------------------------------
# MAIN SYNTHESIS FUNCTION
# -------------------------------------------------------------------

def synthesize_insight(
    query: str,
    evidence: list[dict]
) -> dict:
    """
    Generate a grounded insight using Gemini.

    Parameters
    ----------
    query:
        User's question.

    evidence:
        Retrieved evidence from the vector database.

    Returns
    -------
    dict:
        Structured insight containing:
        - insight
        - evidence_used
        - confidence
        - confidence_reason
        - recommendation
    """

    # ---------------------------------------------------------------
    # Validate Gemini configuration
    # ---------------------------------------------------------------

    if not _client:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Please add GEMINI_API_KEY to the environment variables."
        )

    # ---------------------------------------------------------------
    # Validate query
    # ---------------------------------------------------------------

    if not query or not query.strip():

        raise ValueError(
            "Query cannot be empty."
        )

    # ---------------------------------------------------------------
    # Handle no evidence
    # ---------------------------------------------------------------

    if not evidence:

        return {
            "insight": None,
            "evidence_used": [],
            "confidence": "low",
            "confidence_reason": (
                "No evidence was retrieved for this query."
            ),
            "recommendation": None,
            "error": "insufficient_evidence",
        }

    # ---------------------------------------------------------------
    # Format evidence
    # ---------------------------------------------------------------

    evidence_block = _format_evidence_block(evidence)

    # ---------------------------------------------------------------
    # Build prompt
    # ---------------------------------------------------------------

    prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        query=query.strip(),
        evidence_block=evidence_block,
    )

    # ---------------------------------------------------------------
    # Call Gemini
    # ---------------------------------------------------------------

    try:

        response = _client.models.generate_content(
            model=SYNTHESIS_MODEL,
            contents=prompt,
        )

    except Exception as exc:

        raise RuntimeError(
            f"Gemini synthesis request failed: {exc}"
        ) from exc

    # ---------------------------------------------------------------
    # Read Gemini response
    # ---------------------------------------------------------------

    try:

        raw_text = response.text

    except Exception as exc:

        raise RuntimeError(
            f"Could not read Gemini response: {exc}"
        ) from exc

    if not raw_text or not raw_text.strip():

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    # ---------------------------------------------------------------
    # Parse JSON
    # ---------------------------------------------------------------

    try:

        result = _extract_json(raw_text)

    except ValueError as exc:

        return {
            "insight": None,
            "evidence_used": [],
            "confidence": "low",
            "confidence_reason": (
                "Gemini returned an output that could not be parsed "
                "as valid JSON."
            ),
            "recommendation": None,
            "error": "invalid_model_output",
            "raw_output": raw_text,
        }

    # ---------------------------------------------------------------
    # Normalize result
    # ---------------------------------------------------------------

    normalized_result = _normalize_result(
        result,
        evidence
    )

    return normalized_result


# -------------------------------------------------------------------
# LOCAL TEST
# -------------------------------------------------------------------

if __name__ == "__main__":

    from ai.retrieval.retriever import retrieve

    test_query = (
        "What are the main learning friction points "
        "identified across the course content?"
    )

    print("\nRetrieving evidence...\n")

    try:

        evidence = retrieve(
            test_query,
            top_k=5
        )

        print(
            f"Retrieved {len(evidence)} evidence pieces."
        )

        print("\nSynthesizing insight...\n")

        insight = synthesize_insight(
            test_query,
            evidence
        )

        print(
            json.dumps(
                insight,
                indent=2,
                ensure_ascii=False
            )
        )

    except Exception as exc:

        print(
            "\nSynthesis test failed:"
        )

        print(str(exc))