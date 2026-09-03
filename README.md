# Coursera Multimodal Intelligence Platform

A production-ready Multimodal Retrieval-Augmented Generation (RAG) and Evaluation system built with FastAPI, Streamlit, and Google Gemini API. The platform supports complex text reasoning, image and document understanding, semantic retrieval, and structured output generation.

---

## 🌐 Live Deployments

- Frontend Application (Streamlit Cloud): https://tejaswinipanda2007-cmyk-coursera-multimodal-mini.streamlit.app
- Backend API (Render): https://coursera-multimodal-mini.onrender.com
- Interactive API Docs (Swagger UI): https://coursera-multimodal-mini.onrender.com/docs

---

## 🧠 What This Project Does

The Coursera Multimodal Intelligence Platform processes course-related information from multiple sources and provides AI-powered answers and insights.

Users can interact with the application through a natural-language interface and use Gemini-powered reasoning for tasks involving:

- Text-based questions and reasoning
- Image understanding
- Document understanding
- Retrieval of relevant information
- Structured response generation
- Evaluation of generated responses

The system separates the frontend interface from the backend AI/API layer, making the application easier to develop, deploy, and maintain.

---

## 🏗️ Architecture

User Input
↓
Streamlit Frontend
↓
FastAPI Backend
↓
Google Gemini API
↓
Retrieval / Multimodal Processing
↓
AI Reasoning & Structured Output
↓
Response to User

### Processing Flow

1. The user submits a text query and, where supported, an image or document.
2. The Streamlit frontend sends the request to the FastAPI backend.
3. The backend validates and processes the incoming request.
4. Relevant content is retrieved or prepared as context for the AI model.
5. Google Gemini performs reasoning over the provided context and multimodal inputs.
6. The backend returns the generated result in a structured response.
7. Streamlit presents the result to the user.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Programming Language | Python |
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | Streamlit |
| Multimodal AI | Google Gemini API |
| API Documentation | Swagger UI / OpenAPI |
| Version Control | GitHub |
| Backend Deployment | Render |
| Frontend Deployment | Streamlit Community Cloud |

---

## ✨ Key Features

### 💬 Natural-Language Reasoning

Users can submit natural-language questions and receive AI-generated responses based on the available context.

### 🖼️ Image Understanding

The platform supports multimodal processing where image inputs can be provided for AI-based understanding and reasoning.

### 📄 Document Understanding

Supported documents can be processed, allowing the AI system to reason over document-based information.

### 🔎 Retrieval-Augmented Generation

Relevant information can be retrieved and supplied as context to the language model before generating a response, helping make responses more relevant to the provided information.

### 📊 Structured Evaluation

The project includes structured evaluation capabilities for assessing generated outputs where implemented in the application.

### 🔌 API-Based Architecture

FastAPI provides a separate backend layer for handling API requests, processing inputs, and communicating with the Gemini API.

### 🖥️ Interactive User Interface

Streamlit provides an easy-to-use interface for interacting with the AI application without requiring users to directly call backend APIs.

---

## 📂 Repository Structure

Coursera-Multimodal-Mini/
│
├── backend/
│   ├── api/
│   │   └── main.py
│   │
│   └── ...
│
├── frontend/
│   └── app.py
│
├── requirements.txt
└── README.md

---

## 🚀 Local Development Setup

### 1. Clone the Repository

    git clone https://github.com/tejaswinipanda2007-cmyk/Coursera-Multimodal-Mini.git
    cd Coursera-Multimodal-Mini

### 2. Create a Virtual Environment

    python -m venv venv

Windows:

    venv\Scripts\activate

macOS/Linux:

    source venv/bin/activate

### 3. Install Dependencies

    pip install -r requirements.txt

### 4. Configure Environment Variables

Create a .env file in the project root:

    GEMINI_API_KEY=your_gemini_api_key_here

Never commit your real API key to GitHub.

### 5. Start the Backend

    uvicorn backend.api.main:app --reload

Local backend:

    http://localhost:8000

Swagger documentation:

    http://localhost:8000/docs

### 6. Start the Frontend

Open a second terminal:

    streamlit run frontend/app.py

Local frontend:

    http://localhost:8501

---

## 🔌 API

The backend exposes REST API endpoints through FastAPI.

The complete list of available routes and their request/response schemas can be explored through the deployed Swagger documentation:

Swagger UI: https://coursera-multimodal-mini.onrender.com/docs

---

## 💡 Example Use Cases

- Asking questions about course-related content
- Analyzing information contained in an image
- Asking questions about a supported document
- Retrieving relevant context before generating an answer
- Generating structured AI responses
- Evaluating generated responses

Example queries:

> What concepts are learners struggling with the most?

> Explain the information shown in this image.

> Summarize the important points from this document.

> What evidence supports this answer?

---

## 🎯 Design Decisions

### Multimodal Input

The system is designed to work with more than one type of input, including text and supported image/document inputs.

### Retrieval Before Generation

Where retrieval is used, relevant information is prepared as context before the generation step. This helps the model produce responses more closely connected to the available source information.

### Decoupled Frontend and Backend

Streamlit handles the user interface, while FastAPI handles backend processing and API communication. This allows the components to be maintained and deployed independently.

### API-First Backend

FastAPI exposes documented API routes through OpenAPI/Swagger, making the backend easier to test and integrate with other clients.

---

## 🔒 Security & Best Practices

- Sensitive credentials such as Gemini API keys are managed through environment variables.
- Real API keys should never be committed to version control.
- .env files should be excluded from Git tracking.
- CORS and API configuration should be reviewed before production use.
- The frontend and backend are deployed as separate services.
- GitHub-based deployment can automatically redeploy services after changes are pushed to the configured branch.

---

## ⚠️ Limitations

- AI-generated responses depend on the quality and completeness of the provided or retrieved information.
- Multimodal understanding depends on the capabilities and limitations of the selected Gemini model.
- Evaluation results should be interpreted as supporting information rather than absolute ground truth.
- Production-scale usage may require additional authentication, monitoring, rate limiting, and database infrastructure.

---

## 🚀 Future Improvements

- Add authentication and role-based access control.
- Improve retrieval using hybrid search and reranking.
- Add more comprehensive automated evaluation metrics.
- Introduce persistent production-grade database storage.
- Add monitoring, logging, and observability.
- Improve document and image processing pipelines.
- Add automated API and retrieval test coverage.
- Improve scalability for larger datasets and concurrent users.

---

## 👤 Author

Tejaswini Panda

Built as an individual project to explore Generative AI, Multimodal AI, RAG, semantic retrieval, FastAPI backend development, and interactive Streamlit applications.