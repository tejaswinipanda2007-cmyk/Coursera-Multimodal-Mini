# Coursera Multimodal Intelligence Platform (Solo Scoped Version)

A scaled-down, solo-buildable version of a multimodal RAG platform that unifies
video transcripts, slides, quizzes, and discussion data into a single cross-modal
retrieval and insight-generation pipeline.

See `docs/ROADMAP.md` for the full 6-week build plan.

## Setup
1. `pip install -r requirements.txt`
2. `cp .env.example .env` and add your `GEMINI_API_KEY`
3. Run `python3 ai/retrieval/retriever.py` to index sample data and test a query

## Status
- [x] Week 1: Data schema, sample dataset, preprocessing/chunking
- [x] Week 2: Embeddings (Gemini) + ChromaDB vector store + retrieval
- [ ] Week 3: LLM synthesis with citations
- [ ] Week 4: FastAPI backend + PostgreSQL
- [ ] Week 5: Streamlit frontend
- [ ] Week 6: QA, deployment, docs, PPT
