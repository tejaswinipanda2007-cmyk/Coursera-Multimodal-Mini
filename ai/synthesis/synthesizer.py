"""
LLM Synthesis Layer (PRD Section 5.4 - "LLM Synthesis and Recommendation Generation")

This is the "smart" layer. It takes retrieved evidence (from retriever.py) and
asks Gemini to produce a GROUNDED insight - meaning every claim must be
traceable back to a specific piece of evidence we gave it. No guessing allowed.

Key design choices (and why):
1. We ask for STRUCTURED JSON output, not a free-text paragraph.
   Why: JSON can be stored in a database, rendered in a UI evidence panel,
   and validated programmatically. A paragraph can't.
2. The prompt explicitly tells the model NOT to use outside knowledge.
   Why: this is what "grounding" means - the model should only reason
   over the evidence we retrieved, not invent facts from its training data.
3. If evidence is weak/contradictory, the model must say so instead of
   forcing a confident-sounding answer.
   Why: PRD Section 5.4 - "The system must avoid generating claims that
   are not supported by retrieved evidence."
"""

import sys
import os
import json
from google import genai
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=API_KEY) if API_KEY else None

SYNTHESIS_MODEL = "gemini-3.6-flash"  # fast + cheap, good enough for structured synthesis


SYNTHESIS_PROMPT_TEMPLATE = """You are an AI assistant for Coursera's content team. Your job is to
analyze evidence retrieved from learner data (video transcripts, slides, quizzes,
discussion posts) and produce a grounded insight for a human reviewer.

STRICT RULES:
1. Use ONLY the evidence provided below. Do not use outside knowledge about the topic.
2. Every claim in your insight must be traceable to at least one evidence item.
3. If the evidence is weak, insufficient, or contradictory, say so honestly in
   the "confidence" field instead of forcing a confident answer.
4. Respond with ONLY valid JSON. No markdown formatting, no ```json fences, no preamble.

EDUCATOR QUESTION:
{query}

RETRIEVED EVIDENCE:
{evidence_block}

Respond in exactly this JSON shape:
{{
  "insight": "A 2-3 sentence explanation of the friction pattern found in the evidence.",
  "evidence_used": ["segment_id_1", "segment_id_2"],
  "confidence": "high" | "medium" | "low",
  "confidence_reason": "One sentence explaining the confidence level.",
  "recommendation": "One concrete, actionable suggestion for the content team."
}}
"""


def _format_evidence_block(evidence: list[dict]) -> str:
    """Turn the retriever's evidence list into a readable block for the prompt."""
    lines = []
    for e in evidence:
        ts = f" @ {e['timestamp']}" if e.get("timestamp") else ""
        lines.append(
            f"- [{e['segment_id']}] ({e['modality']}{ts}, from '{e['source_title']}'): {e['text']}"
        )
    return "\n".join(lines)


def synthesize_insight(query: str, evidence: list[dict]) -> dict:
    """
    Given a user query and the evidence retrieved for it, ask Gemini to
    produce a grounded, cited insight.

    Returns a dict matching the JSON shape in the prompt. If the model
    returns something that isn't valid JSON, we return an error dict
    instead of crashing - this is the "fail visibly" principle from the PRD.
    """
    if not _client:
        raise RuntimeError("GEMINI_API_KEY not set. Copy .env.example to .env and add your key.")

    if len(evidence) == 0:
        return {
            "insight": None,
            "evidence_used": [],
            "confidence": "low",
            "confidence_reason": "No evidence was retrieved for this query.",
            "recommendation": None,
            "error": "insufficient_evidence",
        }

    prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        query=query,
        evidence_block=_format_evidence_block(evidence),
    )

    response = _client.models.generate_content(
        model=SYNTHESIS_MODEL,
        contents=prompt,
    )

    raw_text = response.text.strip()

    # Defensive cleanup: sometimes models wrap JSON in ```json fences despite instructions
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json\n", "", 1).strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "insight": None,
            "evidence_used": [],
            "confidence": "low",
            "confidence_reason": "Model output could not be parsed as JSON.",
            "recommendation": None,
            "error": "invalid_model_output",
            "raw_output": raw_text,
        }

    return result


if __name__ == "__main__":
    from ai.retrieval.retriever import retrieve

    query = "Why are students confused about learning rate?"
    evidence = retrieve(query, top_k=5)

    print(f"Retrieved {len(evidence)} evidence pieces. Synthesizing insight...\n")
    insight = synthesize_insight(query, evidence)

    print(json.dumps(insight, indent=2))