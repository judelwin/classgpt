# 🧠 ClassGPT Architecture

A scalable, modular Retrieval-Augmented Generation (RAG) system designed for multi-class academic document ingestion, semantic search, and LLM-based Q&A.

---

## 🗂️ Project Structure

```bash
classgpt/
├── docker-compose.yml
├── .env
├── frontend/                     # React + Tailwind UI
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/                  # API wrapper functions
│   │   ├── context/              # Global state (e.g., user, class selection)
│   │   └── App.tsx
│   └── package.json
├── ingestion-service/           # PDF/slide parsing + OCR
│   ├── main.py
│   ├── parser.py
│   ├── ocr.py
│   └── requirements.txt
├── embedding-worker/            # Celery worker for embedding jobs
│   ├── worker.py
│   ├── embeddings.py
│   ├── tasks.py
│   └── requirements.txt
├── query-service/               # RAG pipeline + search endpoint
│   ├── app.py
│   ├── retriever.py
│   ├── rag.py
│   ├── routes/
│   │   └── query.py
│   └── requirements.txt
├── vector-store/                # FAISS or Qdrant server (may be internal container or external DB)
│   └── (optional custom setup)
├── api-gateway/                 # Optionally route between services
│   └── main.py
├── shared/                      # Common logic used across services
│   ├── chunking.py
│   ├── utils.py
│   └── schema.py
└── database/                    # PostgreSQL schema and migrations
    ├── init.sql
    └── docker-entrypoint.sh
```

---

## 🔄 Service Responsibilities

| Service            | Role                                                                 |
|--------------------|----------------------------------------------------------------------|
| `frontend`         | UI for uploading files, selecting classes, querying, and viewing responses |
| `ingestion-service`| Extracts text from PDFs, slides, and handwritten notes using OCR     |
| `embedding-worker` | Converts text chunks into embeddings and stores in vector DB         |
| `query-service`    | Handles RAG pipeline: top-k retrieval + LLM query + citation response |
| `vector-store`     | Stores and indexes embeddings (FAISS or Qdrant)                      |
| `database`         | Stores class metadata, document links, and job state                 |

---

## 🧠 Data Flow & State Management

### 🎓 Class-Based State
- Each user creates "classes" (e.g., CMSC351)
- Each class has its own document set and vector index namespace

### 📁 Upload Pipeline
1. User uploads file to `/upload` (frontend → ingestion-service)
2. `ingestion-service` parses + runs OCR (if needed)
3. Chunks are sent to `embedding-worker` via Redis/Celery
4. Embeddings are stored in `vector-store` (FAISS/Qdrant) under class ID
5. Metadata and status are recorded in PostgreSQL

### 🔍 Query Pipeline
1. User enters question in UI for a specific class
2. Query sent to `query-service` with class ID
3. Top-k chunks are retrieved from `vector-store`
4. Chunks + query passed to LLM (OpenAI or local via LangChain)
5. LLM returns answer + source links
6. UI displays final response with inline citations

---

## 📦 Docker Compose Configuration (`docker-compose.yml`)

```yaml
version: '3.9'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://localhost:8000

  ingestion-service:
    build: ./ingestion-service
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379

  embedding-worker:
    build: ./embedding-worker
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379

  query-service:
    build: ./query-service
    ports:
      - "8000:8000"
    depends_on:
      - vector-store
      - db

  vector-store:
    image: qdrant/qdrant
    ports:
      - "6333:6333"

  db:
    image: postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: classgpt
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password

  redis:
    image: redis:alpine
```

---

## 🗃️ PostgreSQL Database Schema (Simplified)

```sql
CREATE TABLE classes (
  id UUID PRIMARY KEY,
  user_id UUID,
  name TEXT
);

CREATE TABLE documents (
  id UUID PRIMARY KEY,
  class_id UUID REFERENCES classes(id),
  filename TEXT,
  status TEXT,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chunks (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  chunk_index INT,
  content TEXT,
  embedding VECTOR(384) -- if stored outside FAISS/Qdrant
);
```

---

## 🧱 Component Stack

| Layer            | Tech Stack                        |
|------------------|------------------------------------|
| Frontend         | React, Tailwind, Axios, Context API |
| Backend APIs     | FastAPI or Flask                   |
| Workers          | Celery + Redis                     |
| Embeddings       | SentenceTransformers (MiniLM)      |
| Vector Store     | FAISS (local) or Qdrant (remote)   |
| LLM Integration  | OpenAI API or local (Ollama, HuggingFace) |
| OCR              | Tesseract / Google Cloud Vision    |
| Containerization | Docker, Docker Compose             |
| Deployment       | Vercel (frontend), Render/Fly.io (services) |

