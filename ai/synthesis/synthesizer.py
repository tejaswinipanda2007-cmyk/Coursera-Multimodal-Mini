"""
LLM Synthesis Layer
-------------------

Generates grounded insights from retrieved evidence.

Primary model:
    gemini-3.5-flash

Fallback model:
    gemini-3.5-flash-lite

The system retries temporary Gemini errors such as:
    429 - rate limit
    500 - server error
    502 - bad gateway
    503 - unavailable
    504 - timeout

If the primary model remains unavailable, it automatically tries
the fallback model.
"""

import sys
import os
import json
import time

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
# GEMINI MODELS
# -------------------------------------------------------------------

PRIMARY_MODEL = "gemini-3.5-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"

# Keep this variable for compatibility with the rest of the project.
SYNTHESIS_MODEL = PRIMARY_MODEL

MAX_RETRIES = 3


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
# FORMAT EVIDENCE
# -------------------------------------------------------------------

def _format_evidence_block(evidence: list[dict]) -> str:
    """Convert retrieved evidence into a readable prompt block."""

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
            f"from '{source_title}'): {text}"
        )

    return "\n".join(lines)


# -------------------------------------------------------------------
# EXTRACT JSON
# -------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    """
    Safely extract a JSON object from Gemini output.
    Handles normal JSON, markdown fences, and extra text.
    """

    if not text:
        raise ValueError("Gemini returned an empty response.")

    cleaned = text.strip()

    # Remove markdown fences
    if cleaned.startswith("```"):

        cleaned = cleaned.replace("```json", "", 1)
        cleaned = cleaned.replace("```JSON", "", 1)
        cleaned = cleaned.replace("```", "", 1)
        cleaned = cleaned.strip()

    # Direct JSON parsing
    try:

        result = json.loads(cleaned)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # Try extracting JSON object from surrounding text
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")

    if first_brace != -1 and last_brace != -1:

        candidate = cleaned[
            first_brace:last_brace + 1
        ]

        try:

            result = json.loads(candidate)

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            pass

    raise ValueError(
        "Gemini response was not valid JSON."
    )


# -------------------------------------------------------------------
# NORMALIZE RESULT
# -------------------------------------------------------------------

def _normalize_result(
    result: dict,
    evidence: list[dict]
) -> dict:
    """Ensure the result follows the application's expected schema."""

    valid_segment_ids = {
        str(e.get("segment_id"))
        for e in evidence
        if e.get("segment_id") is not None
    }

    insight = result.get("insight")

    evidence_used = result.get(
        "evidence_used",
        []
    )

    confidence = str(
        result.get(
            "confidence",
            "low"
        )
    ).lower().strip()

    confidence_reason = result.get(
        "confidence_reason",
        "Confidence could not be determined reliably."
    )

    recommendation = result.get(
        "recommendation"
    )

    # Ensure evidence_used is a list
    if not isinstance(evidence_used, list):
        evidence_used = []

    # Keep only real segment IDs
    evidence_used = [
        str(segment_id)
        for segment_id in evidence_used
        if str(segment_id) in valid_segment_ids
    ]

    # Validate confidence
    if confidence not in {
        "high",
        "medium",
        "low"
    }:
        confidence = "low"

    # No evidence citation = low confidence
    if not evidence_used:
        confidence = "low"

    if insight is not None:
        insight = str(insight).strip()

    confidence_reason = str(
        confidence_reason
    ).strip()

    if recommendation is not None:
        recommendation = str(
            recommendation
        ).strip()

    return {
        "insight": insight,
        "evidence_used": evidence_used,
        "confidence": confidence,
        "confidence_reason": confidence_reason,
        "recommendation": recommendation,
    }


# -------------------------------------------------------------------
# CHECK WHETHER ERROR IS TEMPORARY
# -------------------------------------------------------------------

def _is_retryable_error(exc: Exception) -> bool:
    """
    Detect temporary Gemini/API errors where retrying makes sense.
    """

    status_code = getattr(
        exc,
        "status_code",
        None
    )

    if status_code in {
        429,
        500,
        502,
        503,
        504
    }:
        return True

    error_text = str(exc).lower()

    retry_keywords = [
        "429",
        "500",
        "502",
        "503",
        "504",
        "unavailable",
        "temporarily",
        "overloaded",
        "high demand",
        "timeout",
        "rate limit",
        "resource exhausted",
    ]

    return any(
        keyword in error_text
        for keyword in retry_keywords
    )


# -------------------------------------------------------------------
# CALL GEMINI WITH RETRIES
# -------------------------------------------------------------------

def _generate_with_retry(
    model: str,
    prompt: str
):
    """
    Call Gemini with retries for temporary failures.
    """

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            print(
                f"Gemini request: "
                f"{model} "
                f"(attempt {attempt}/{MAX_RETRIES})"
            )

            response = _client.models.generate_content(
                model=model,
                contents=prompt,
            )

            return response

        except Exception as exc:

            last_error = exc

            print(
                f"Gemini error on {model}: {exc}"
            )

            # Don't retry permanent errors
            if not _is_retryable_error(exc):
                raise

            # Wait before retrying
            if attempt < MAX_RETRIES:

                wait_seconds = attempt * 2

                print(
                    f"Retrying in "
                    f"{wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

    raise RuntimeError(
        f"Gemini model '{model}' failed "
        f"after {MAX_RETRIES} attempts: "
        f"{last_error}"
    )


# -------------------------------------------------------------------
# MAIN SYNTHESIS FUNCTION
# -------------------------------------------------------------------

def synthesize_insight(
    query: str,
    evidence: list[dict]
) -> dict:
    """
    Generate a grounded insight from retrieved evidence.

    Primary:
        gemini-3.5-flash

    Fallback:
        gemini-3.5-flash-lite
    """

    # ---------------------------------------------------------------
    # API KEY CHECK
    # ---------------------------------------------------------------

    if not _client:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Please add GEMINI_API_KEY to the environment variables."
        )

    # ---------------------------------------------------------------
    # QUERY CHECK
    # ---------------------------------------------------------------

    if not query or not query.strip():

        raise ValueError(
            "Query cannot be empty."
        )

    # ---------------------------------------------------------------
    # EVIDENCE CHECK
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
    # FORMAT EVIDENCE
    # ---------------------------------------------------------------

    evidence_block = _format_evidence_block(
        evidence
    )

    # ---------------------------------------------------------------
    # BUILD PROMPT
    # ---------------------------------------------------------------

    prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        query=query.strip(),
        evidence_block=evidence_block,
    )

    # ---------------------------------------------------------------
    # PRIMARY MODEL
    # ---------------------------------------------------------------

    try:

        response = _generate_with_retry(
            PRIMARY_MODEL,
            prompt
        )

        model_used = PRIMARY_MODEL

    except Exception as primary_error:

        print(
            "Primary Gemini model failed."
        )

        print(
            f"Primary error: {primary_error}"
        )

        # -----------------------------------------------------------
        # FALLBACK MODEL
        # -----------------------------------------------------------

        try:

            print(
                f"Trying fallback model: "
                f"{FALLBACK_MODEL}"
            )

            response = _generate_with_retry(
                FALLBACK_MODEL,
                prompt
            )

            model_used = FALLBACK_MODEL

        except Exception as fallback_error:

            raise RuntimeError(
                "Both Gemini synthesis models failed. "
                f"Primary: {primary_error}. "
                f"Fallback: {fallback_error}"
            ) from fallback_error

    # ---------------------------------------------------------------
    # READ RESPONSE
    # ---------------------------------------------------------------

    try:

        raw_text = response.text

    except Exception as exc:

        raise RuntimeError(
            f"Could not read Gemini response: {exc}"
        ) from exc

    if not raw_text or not raw_text.strip():

        raise RuntimeError(
            f"Gemini model '{model_used}' "
            "returned an empty response."
        )

    # ---------------------------------------------------------------
    # PARSE JSON
    # ---------------------------------------------------------------

    try:

        result = _extract_json(
            raw_text
        )

    except ValueError:

        return {
            "insight": None,
            "evidence_used": [],
            "confidence": "low",
            "confidence_reason": (
                "Gemini returned output that "
                "could not be parsed as valid JSON."
            ),
            "recommendation": None,
            "error": "invalid_model_output",
            "raw_output": raw_text,
            "model_used": model_used,
        }

    # ---------------------------------------------------------------
    # NORMALIZE
    # ---------------------------------------------------------------

    normalized_result = _normalize_result(
        result,
        evidence
    )

    # Add model information for debugging/audit
    normalized_result["model_used"] = model_used

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

    print(
        "\nRetrieving evidence...\n"
    )

    try:

        evidence = retrieve(
            test_query,
            top_k=5
        )

        print(
            f"Retrieved {len(evidence)} evidence pieces."
        )

        print(
            "\nSynthesizing insight...\n"
        )

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

        print(
            str(exc)
        )