# Coursera Multimodal Intelligence Platform

A production-ready Multimodal Retrieval-Augmented Generation (RAG) and Evaluation system built with FastAPI, Streamlit, and Google Gemini API. The platform supports complex text reasoning, image and document understanding, semantic retrieval, and structured output generation.

---

## 🌐 Live Deployments

- Frontend Application (Streamlit Cloud): https://coursera-multimodal-mini-pw8grrooksyszb9wj9hmq9.streamlit.app
- Backend API (Render): https://coursera-multimodal-mini.onrender.com
- Interactive API Docs (Swagger UI): https://coursera-multimodal-mini.onrender.com/docs

---

## 🧠 What This Project Does

The Coursera Multimodal Intelligence Platform processes course-related information from multiple sources and provides AI-powered answers and insights.

Users can interact with the application through a natural-language interface and, where supported, provide images or documents for multimodal understanding.

The platform combines:

- Text-based question answering and reasoning
- Image understanding
- Document understanding
- Context retrieval and preparation
- Retrieval-Augmented Generation (RAG)
- Structured response generation
- AI-powered evaluation

The system uses a decoupled frontend and backend architecture, making the application easier to develop, deploy, maintain, and scale.

---

## 🏗️ Architecture & System Workflow

```text
+-------------------------------------------------------------+
|                     User / Web Browser                      |
+-------------------------------------------------------------+
                               |
                               | (1) Submits Query + File (Image/Doc)
                               v
+-------------------------------------------------------------+
|                Streamlit Frontend Application               |
|      (Hosted on Streamlit Cloud / Port 8501 locally)        |
+-------------------------------------------------------------+
                               |
                               | (2) REST API Call (HTTP POST / JSON / Multipart)
                               v
+-------------------------------------------------------------+
|                     FastAPI Backend Engine                  |
|          (Hosted on Render / Port 8000 locally)             |
|  - Request Validation (Pydantic schemas)                    |
|  - CORS & Error Handling Middleware                         |
+-------------------------------------------------------------+
                               |
                               | (3) Context Retrieval & Payload Assembly
                               v
+-------------------------------------------------------------+
|                 Multimodal Pre-Processing Layer             |
|  - Document / Text Parsing                                  |
|  - Image Preparation & Encoding                             |
|  - Context Assembly for Grounded RAG                        |
+-------------------------------------------------------------+
                               |
                               | (4) Multimodal Prompt Execution
                               v
+-------------------------------------------------------------+
|                  Google Gemini API Gateway                  |
|  - Multimodal Vision & Text Reasoning                       |
|  - In-Context Evaluation & Structured Inference             |
+-------------------------------------------------------------+
                               |
                               | (5) Return Structured Response / Evaluation
                               v
+-------------------------------------------------------------+
|                     FastAPI Backend Engine                  |
|  - Formats output JSON & status checks                      |
+-------------------------------------------------------------+
                               |
                               | (6) Render UI Components
                               v
+-------------------------------------------------------------+
|             Streamlit Frontend (Response to User)           |
|  - Rendered Markdown, Confidence, and Source Context        |
+-------------------------------------------------------------+
```

### Workflow Explanation

1. **User Input**
   - The user submits a natural-language query and, where supported, an image or document through the Streamlit interface.

2. **Streamlit Frontend**
   - The frontend collects the input and sends it to the FastAPI backend through an HTTP request.

3. **FastAPI Backend**
   - The backend validates the request using Pydantic schemas and handles API-level processing, CORS, and errors.

4. **Multimodal Pre-Processing**
   - Text, documents, and images are prepared for processing, and relevant context is assembled for the RAG workflow.

5. **Google Gemini API**
   - Gemini processes the multimodal prompt and performs reasoning based on the supplied input and retrieved or prepared context.

6. **Structured Response**
   - The FastAPI backend receives the model output, formats the response, and performs status checks before returning the result.

7. **Streamlit Response**
   - The frontend displays the generated answer along with supported source context, confidence information, or evaluation results.

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
Users can submit natural-language questions and receive AI-generated responses based on the available input and context.

### 🖼️ Image Understanding
The platform supports multimodal processing of image inputs for AI-based understanding and reasoning.

### 📄 Document Understanding
Supported documents can be processed to allow the AI system to reason over document-based information.

### 🔎 Retrieval-Augmented Generation
Relevant information can be retrieved or prepared as context and supplied to the language model before response generation, helping keep the generated response connected to the available information.

### 📊 Structured Evaluation
The project includes structured evaluation capabilities for assessing generated outputs where enabled by the application workflow.

### 🔌 API-Based Architecture
FastAPI provides a dedicated backend layer for request validation, processing, AI communication, and structured responses.

### 🖥️ Interactive User Interface
Streamlit provides an interactive interface for submitting queries and displaying AI-generated results.

### ☁️ Cloud Deployment
The backend is deployed on Render and the frontend is deployed on Streamlit Community Cloud, allowing the application to be accessed online.

---

## 📂 Repository Structure

```text
Coursera-Multimodal-Mini/
│
├── backend/
│   ├── api/
│   │   └── main.py          # FastAPI application, CORS setup, and API routes
│   │
│   └── ...
│
├── frontend/
│   └── app.py               # Streamlit application
│
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## 🚀 Local Development Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/tejaswinipanda2007-cmyk/Coursera-Multimodal-Mini.git]
(https://github.com/tejaswinipanda2007-cmyk/Coursera-Multimodal-Mini.git)
cd Coursera-Multimodal-Mini
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
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
GEMINI_API_KEY=your_gemini_api_key_here
```

*Never commit your real API key to GitHub.*

### 5. Start the Backend
```bash
uvicorn backend.api.main:app --reload
```

- Local backend: `http://localhost:8000`
- Swagger documentation: `http://localhost:8000/docs`

### 6. Start the Frontend
Open a second terminal:
```bash
streamlit run frontend/app.py
```

- Local frontend: `http://localhost:8501`

---

## 🔌 API

The backend exposes REST API endpoints through FastAPI.

The complete list of available routes, request schemas, response schemas, and testing options can be explored through the deployed Swagger documentation:

Swagger UI: https://coursera-multimodal-mini.onrender.com/docs

---

## 💡 Example Use Cases

- Asking questions about course-related content
- Analyzing information contained in an image
- Asking questions about a supported document
- Retrieving relevant context before generating an answer
- Generating structured AI responses
- Evaluating generated responses
- Understanding learner-related course information

### Example Queries

> What concepts are learners struggling with the most?

> Explain the information shown in this image.

> Summarize the important points from this document.

> What evidence supports this answer?

---

## 📊 Example Output

**Query:**  
*What concepts are learners struggling with the most?*

**Example Insight:**  
The system retrieves relevant course content and uses the available context to generate an evidence-based response identifying concepts associated with learner difficulties.

*Note: Actual output depends on the input data, uploaded content, retrieval results, and Gemini response.*

---

## 🎯 Design Decisions

### Multimodal Input
The system is designed to work with multiple input types, including text and supported image/document inputs.

### Retrieval Before Generation
Where retrieval is used, relevant information is prepared as context before the generation step. This helps the model produce responses that are more closely connected to the available source information.

### Decoupled Frontend and Backend
Streamlit handles the user interface, while FastAPI handles backend processing and API communication. This allows both components to be developed and deployed independently.

### API-First Backend
FastAPI exposes documented API routes through OpenAPI/Swagger, making the backend easier to test and integrate with other clients.

### Cloud-Based Deployment
The backend and frontend are hosted as separate services using Render and Streamlit Community Cloud respectively.

---

## 🔒 Security & Best Practices

- Sensitive credentials such as Gemini API keys are managed through environment variables.
- Real API keys should never be committed to version control.
- `.env` files should be excluded from Git tracking.
- CORS configuration should be reviewed before production use.
- Error handling is implemented at the API layer.
- The frontend and backend are deployed as separate services.
- GitHub-based deployment can automatically redeploy configured services after changes are pushed to the main branch.

---

## ⚠️ Limitations

- AI-generated responses depend on the quality and completeness of the provided or retrieved information.
- Multimodal understanding depends on the capabilities and limitations of the selected Gemini model.
- Evaluation results should be interpreted as supporting information rather than absolute ground truth.
- Production-scale usage may require additional authentication, monitoring, rate limiting, and database infrastructure.
- Response quality may vary depending on the complexity of the input and available context.

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
- Add richer analytics for learner-friction detection.

---

## 👤 Author

**Tejaswini Panda**

Built as an individual project to explore **Generative AI, Multimodal AI, RAG, semantic retrieval, FastAPI backend development, cloud deployment, and interactive Streamlit applications**.