# 🎓 Coursera Multimodal Intelligence Platform

An end-to-end **Retrieval-Augmented Generation (RAG)** platform that brings together course-related information from multiple content sources such as **video transcripts, presentation content, quizzes, and discussion data**.

The system converts the available course information into **structured text segments with modality and metadata**, generates embeddings, retrieves relevant evidence using semantic search, and uses **Google Gemini** to generate grounded responses.

The goal is to help users understand **learner difficulties, confusing concepts, and course-related questions** using evidence retrieved from different course-content sources.

---

## 🌐 Live Deployments

- **Frontend Application:** https://tejaswinipanda2007-cmyk-coursera-multimodal-mini.streamlit.app
- **Backend API:** https://coursera-multimodal-mini.onrender.com
- **Swagger API Documentation:** https://coursera-multimodal-mini.onrender.com/docs

---

## 🧠 What This Project Does

Online course information is distributed across different sources such as:

- Video transcripts
- Presentation/slide content represented as text
- Quiz questions and related information
- Discussion/forum content

Instead of processing these sources separately, this project converts their usable information into a common **structured text representation** along with relevant metadata.

A user can then ask a natural-language question such as:

> **"What concepts are learners struggling with the most?"**

The system retrieves semantically relevant course-content segments and provides them as context to Google Gemini for generating a grounded response.

### Core Workflow

1. Course information is prepared as structured text.
2. Text is divided into meaningful segments/chunks.
3. Each segment is associated with metadata such as content type and timestamp/source information where available.
4. Gemini embeddings are generated for the text segments.
5. ChromaDB stores the embeddings and performs semantic retrieval.
6. Relevant evidence is retrieved for the user's query.
7. Retrieved evidence is provided to Google Gemini.
8. Gemini generates a context-aware response.
9. The application presents the generated response through the Streamlit interface.

---

## 🏗️ Architecture & System Workflow

```text
+-------------------------------------------------------------+
|                     User / Web Browser                      |
+-------------------------------------------------------------+
                              |
                              | (1) Natural-Language Query
                              v
+-------------------------------------------------------------+
|                Streamlit Frontend Application               |
|      Interactive interface for submitting user queries      |
+-------------------------------------------------------------+
                              |
                              | (2) API Request
                              v
+-------------------------------------------------------------+
|                     FastAPI Backend Engine                  |
|          Handles API requests and application logic         |
+-------------------------------------------------------------+
                              |
                              | (3) Query Processing
                              v
+-------------------------------------------------------------+
|              Text & Metadata Processing Layer              |
|  - Structured text segments                                 |
|  - Content-type metadata                                    |
|  - Source / timestamp metadata where available             |
+-------------------------------------------------------------+
                              |
                              | (4) Semantic Search
                              v
+-------------------------------------------------------------+
|                         ChromaDB                            |
|             Vector Storage & Similarity Retrieval           |
+-------------------------------------------------------------+
                              |
                              | (5) Relevant Evidence
                              v
+-------------------------------------------------------------+
|                    Google Gemini API                        |
|       Context-based Response Generation / Synthesis         |
+-------------------------------------------------------------+
                              |
                              | (6) Generated Response
                              v
+-------------------------------------------------------------+
|                     FastAPI Backend                         |
|              Formats and returns the response               |
+-------------------------------------------------------------+
                              |
                              | (7) Response Display
                              v
+-------------------------------------------------------------+
|                  Streamlit Frontend                         |
|       Displays the generated answer and context             |
+-------------------------------------------------------------+
```

### Architecture Explanation

#### 1. User Input

The user enters a natural-language question through the Streamlit application.

Example:

> What concepts are learners struggling with the most?

#### 2. Streamlit Frontend

Streamlit provides the interactive user interface and sends the user's query to the FastAPI backend.

#### 3. FastAPI Backend

FastAPI receives the request and manages the application's backend/API workflow.

#### 4. Text & Metadata Representation

Course information from different sources is represented as structured text segments.

Each segment can contain metadata such as:

- Content type
- Source information
- Timestamp information where available
- Other relevant metadata

This text-based representation allows information from different course-content sources to participate in the same retrieval workflow.

#### 5. Embeddings & Retrieval

Text segments are converted into vector embeddings using the Google Gemini API.

The embeddings are stored in **ChromaDB**, which performs semantic similarity search to retrieve the most relevant content for a user query.

#### 6. RAG Generation

The retrieved evidence is passed to Google Gemini as context.

Gemini uses the retrieved context to generate a response based on the available course information.

#### 7. Response

The generated response is returned through the FastAPI backend and displayed to the user through the Streamlit frontend.

---

## 🔄 RAG Pipeline

```text
Course Content
(Video Transcripts / Slides / Quizzes / Discussions)
                    ↓
          Text Preprocessing
                    ↓
            Text Chunking
                    ↓
     Structured Text + Metadata
                    ↓
          Gemini Embeddings
                    ↓
              ChromaDB
                    ↓
        Semantic Similarity Search
                    ↓
          Relevant Evidence
                    ↓
          Google Gemini LLM
                    ↓
         Grounded AI Response
                    ↓
          Streamlit Frontend
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Backend API | FastAPI |
| Vector Store | ChromaDB |
| Embeddings | Google Gemini API |
| LLM | Google Gemini API |
| Database / Metadata | SQLite |
| ORM / Database Layer | SQLAlchemy |
| Deployment | Streamlit Community Cloud, Render |
| API Documentation | Swagger UI |
| Version Control | Git, GitHub |

---

## ✨ Key Features

### 🔎 Semantic Retrieval

The system retrieves relevant course-content segments based on the semantic meaning of the user's query rather than relying only on exact keyword matching.

### 📚 Cross-Source Course Retrieval

Information originating from different course-content sources can be represented in a common text-based format, allowing the retrieval system to search across them together.

### 🤖 AI-Powered Response Generation

Google Gemini generates responses using the retrieved course-content evidence as context.

### 🧩 Metadata-Aware Retrieval

Content segments can retain metadata such as content type and timestamp/source information where available.

### 🔄 Retrieval-Augmented Generation

The system separates retrieval from generation:

1. Retrieve relevant evidence.
2. Provide the evidence to the LLM.
3. Generate a response based on the retrieved context.

### 🖥️ Interactive Web Interface

Streamlit provides a simple interface for submitting questions and viewing generated responses.

### 🔌 Decoupled Frontend and Backend

The application separates the Streamlit frontend from the FastAPI backend, making the components easier to develop and deploy independently.

---

## 📂 Project Structure

```text
Coursera-Multimodal-Mini/
│
├── backend/
│   └── api/
│       └── main.py
│
├── frontend/
│   └── app.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Setup & Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/tejaswinipanda2007-cmyk/Coursera-Multimodal-Mini.git
cd Coursera-Multimodal-Mini
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

If the application requires a backend URL configuration:

```env
BACKEND_URL=http://localhost:8000
```

**Do not commit the `.env` file or real API keys to GitHub.**

### 5. Start the FastAPI Backend

```bash
uvicorn backend.api.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

### 6. Start the Streamlit Frontend

Open another terminal:

```bash
streamlit run frontend/app.py
```

Frontend:

```text
http://localhost:8501
```

---

## 🔌 API Endpoints

The project exposes backend APIs for the application's query and insight workflow.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/query` | Runs the retrieval and response-generation workflow |
| `GET` | `/api/insights/{id}` | Retrieves a previously generated insight |
| `POST` | `/api/review-feedback` | Records review feedback |
| `GET` | `/api/metrics` | Retrieves application/review metrics |

For interactive API testing, open:

```text
https://coursera-multimodal-mini.onrender.com/docs
```

---

## 💡 Example Queries

You can ask questions such as:

- **What concepts are learners struggling with the most?**
- **What do learners find confusing about learning rate?**
- **Where are learners experiencing friction in the course?**
- **Summarize the relationship between gradient descent and loss optimization.**

---

## 📊 Example Output

### Query

> What do learners find confusing about learning rate?

### Example Insight

> Learners appear to be confusing learning rate with the number of training epochs. Relevant evidence can be traced to lecture and assessment content discussing optimization.

### Example Recommendation

> Clarify the distinction between learning rate and epochs using a simple explanation in the relevant lecture section.

> **Note:** This is an illustrative example of the type of response the system is designed to generate. Actual output depends on the indexed course data and retrieved evidence.

---

## 🎯 Design Decisions

### Text-Based Multimodal Representation

Although the project works with information originating from different sources such as video transcripts, slides, quizzes, and discussions, the usable content is represented as **structured text segments with metadata**.

This design allows the system to perform cross-source semantic retrieval without requiring a separate computer-vision pipeline.

### Vector Retrieval

**ChromaDB** is used as the vector store for semantic similarity search over embedded course-content segments.

### Gemini Embeddings

Google Gemini is used to generate embeddings for the structured text content.

### LLM-Based Synthesis

Retrieved evidence is passed to Google Gemini to generate a response based on the available context.

### Structured Application Architecture

**FastAPI** handles backend/API responsibilities, while **Streamlit** provides the interactive user interface.

---

## 🔒 Security

- API credentials are stored using environment variables.
- `.env` should be excluded from version control using `.gitignore`.
- Real API keys should never be committed to the repository.
- `.env.example` can be used to document required environment variables without exposing credentials.

---

## ⚠️ Limitations

- The current implementation uses **structured text representations** rather than direct computer-vision processing of raw images or videos.
- Presentation/slide information is handled through its available text representation rather than image understanding.
- The quality of generated responses depends on the quality and coverage of the indexed course content.
- Sample data may not represent the complexity of a production-scale learning platform.
- LLM-generated responses should be reviewed before being used for important instructional decisions.

---

## 🚀 Future Improvements

- Add richer processing for native video and image/slide content.
- Improve retrieval using hybrid search and reranking.
- Expand evaluation using retrieval and answer-quality metrics.
- Add authentication and role-based access control.
- Move from SQLite to a production-grade PostgreSQL setup.
- Introduce monitoring and observability.
- Improve learner-friction detection using dedicated analytics and ML models.

---

## 👤 Author

**Tejaswini Panda**

Built as an individual project to explore:

- Retrieval-Augmented Generation (RAG)
- Semantic Retrieval
- Generative AI
- Vector Databases
- Backend API Development
- Interactive AI Applications

---

## 📌 Important Implementation Note

This project uses the term **"multimodal"** because it brings together information originating from multiple course-content sources/modalities.

The current implementation does **not** perform direct image understanding, raw document/image upload processing, or computer-vision analysis.

Instead, the usable information from these sources is represented as **structured text + metadata** and processed through the same semantic retrieval and RAG pipeline.