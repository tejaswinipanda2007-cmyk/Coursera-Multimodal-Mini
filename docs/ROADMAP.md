# Coursera Multimodal Intelligence Platform — Solo Build Roadmap
### Scope: Text + Video-transcript-timestamps + Slides + Quiz + Discussion (simulated multimodal, real AI pipeline)
### Timeline: 6 weeks (fits 1–1.5 months) | Solo, but you wear a different "role hat" each week

---

## Week 1 — Product Manager + Data Engineer hat ✅ (mostly done)
**Goal:** Define scope, build the data foundation.
- [x] Define product scope (done — see chat)
- [x] Design common `Segment` schema (`data/schemas/asset_schema.py`)
- [x] Build sample multimodal dataset (`data/sample_assets/raw_assets.py`)
- [x] Build preprocessing/chunking pipeline (`ai/preprocessing/chunker.py`)
- [ ] Write `docs/architecture.md` (1 page: what the system does, diagram)
- [ ] Push initial commit to GitHub (private repo, like your chatbot project)

**Skill you're practicing:** scoping a fuzzy problem, writing clean data models.

---

## Week 2 — AI/ML Engineer hat (Embeddings + Vector Search)
**Goal:** Make content searchable by meaning, not just keywords.
- [ ] Generate embeddings for every Segment using Gemini Embedding API
- [ ] Store embeddings in ChromaDB (persistent local vector DB)
- [ ] Build a retrieval function: query → top-k relevant segments across ALL modalities
- [ ] Test retrieval quality manually with 5 sample queries

**Skill you're practicing:** embeddings, vector databases, semantic search — this is the #1 most-asked topic in AI/ML fresher interviews right now.

---

## Week 3 — AI/ML Engineer hat (LLM Synthesis + Prompt Engineering)
**Goal:** Turn retrieved evidence into a grounded, cited insight — the "smart" part.
- [ ] Design the synthesis prompt (role, task, evidence, constraints, output format)
- [ ] Call Gemini with retrieved segments → generate insight with citations
- [ ] Force structured output (JSON: insight, evidence_used, confidence, recommendation)
- [ ] Add a guardrail: if evidence is weak/empty, say "insufficient evidence" instead of guessing

**Skill you're practicing:** RAG synthesis, grounding, prompt design, structured outputs — exactly what your 37 Q&A agentic-AI prep covered.

---

## Week 4 — Backend Engineer hat (APIs + Database)
**Goal:** Wrap the AI pipeline in real APIs, like a real product would.
- [ ] FastAPI endpoints: `/assets`, `/query`, `/insights/{id}`, `/review-feedback`
- [ ] PostgreSQL (or Supabase) tables: assets, segments, queries, insights, reviewer_decisions
- [ ] Log every query + generated insight to the database
- [ ] Basic error handling (empty retrieval, API failure, bad input)

**Skill you're practicing:** API design, DB schema design — reusable for your SQL/backend interviews too.

---

## Week 5 — Frontend Engineer hat (Streamlit UI)
**Goal:** Make it usable and demo-able.
- [ ] Query Workspace page — ask a question, see the AI answer
- [ ] Evidence Panel — show which video/slide/quiz/discussion snippets backed the answer (with timestamps!)
- [ ] Simple Dashboard — segment counts per modality, recent queries
- [ ] Recommendation Review — approve/reject button, saves decision to DB

**Skill you're practicing:** product thinking — showing evidence builds trust, this is a real UX pattern in AI products.

---

## Week 6 — QA + Deployment + Documentation + PPT
**Goal:** Ship it and present it.
- [ ] Test edge cases: empty query, no evidence found, duplicate assets
- [ ] Deploy: Streamlit Cloud (frontend) + Render/Railway (backend) — free tiers
- [ ] Write final README (setup, architecture, screenshots, demo link)
- [ ] Record a 2–3 min demo video
- [ ] Build PPT (Problem → Architecture → Demo screenshots → Tech stack → What I learned)
- [ ] Write resume bullet points (see below)

---

## Resume Bullets (draft — refine after building)
- Built a multimodal RAG platform that unifies video transcripts, slides, quizzes, and
  discussion data into a single cross-modal retrieval and insight-generation pipeline.
- Designed a normalized data schema enabling semantic search across 4 content modalities
  using Gemini embeddings and ChromaDB vector search.
- Implemented a grounded LLM synthesis layer with citation tracking, preventing
  unsupported AI claims by enforcing evidence-only generation.
- Built and deployed a full-stack application (FastAPI + PostgreSQL + Streamlit) with
  a human-in-the-loop review workflow for AI-generated recommendations.

---

## Weekly Time Budget (realistic for a job-searching fresher)
~10-12 hours/week is enough if you follow this roadmap step by step. Don't try to build
everything from the original PRD — that's a full team's scope. This scoped version proves
the same core skills.
