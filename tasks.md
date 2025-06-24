# ✅ ClassGPT MVP Task Plan

Each task is small, testable, and agent-friendly.

---

## 🔹 Phase 1: Boilerplate Setup

### `task-01`: Initialize Git repository and monorepo structure
- Create `classgpt/` directory
- Add subfolders: `frontend`, `ingestion-service`, `embedding-worker`, `query-service`, `shared`
- Add `.gitignore`, `README.md`

### `task-02`: Create and configure `docker-compose.yml`
- Set up placeholder services for: frontend, ingestion-service, embedding-worker, query-service, redis
- Add health checks for each
- Verify all services build and run with `docker-compose up`

### `task-03`: Set up shared `.env` and bind service-specific ones
- Add variables for Redis URL, API base, OpenAI key
- Use `dotenv` package in each Python service to load variables

---

## 🔹 Phase 2: Frontend Scaffold

### `task-04`: Bootstrap React + Vite + Tailwind project
- In `frontend/`, scaffold app with `create-vite`
- Configure Tailwind + PostCSS
- Set up routing with React Router (2 routes: `/upload`, `/chat`)

### `task-05`: Build class selector sidebar component
- Dropdown + create-new-class modal
- Store selected class in global context

### `task-06`: Implement file upload UI
- File input with multiple file support
- Class-specific document submission

---

## 🔹 Phase 3: Ingestion Service (Typed PDFs)

### `task-07`: Set up FastAPI ingestion service
- Create `/upload` POST route that accepts `multipart/form-data`
- Log filenames and save to `uploads/`

### `task-08`: Implement PDF parsing with `PyMuPDF`
- Extract full text from uploaded PDF
- Return string output for testing

### `task-09`: Chunk parsed text (sentence-based)
- Split text into ~200-word chunks with 20-word overlap
- Return array of chunks

---

## 🔹 Phase 4: Embedding Worker

### `task-10`: Set up Celery worker (Redis backend)
- Connect to Redis and log startup
- Define simple test task (e.g. add numbers)

### `task-11`: Embed chunked text using `all-MiniLM-L6-v2`
- Accept array of chunks, return list of (chunk, embedding) tuples
- Use HuggingFace Transformers or SentenceTransformers

### `task-12`: Store embeddings in FAISS index
- Initialize per-class FAISS index
- Add chunk embeddings with doc ID and metadata

---

## 🔹 Phase 5: Query Service

### `task-13`: Set up FastAPI query service
- Create `/query` POST route that accepts question + class ID

### `task-14`: Implement FAISS top-k retrieval
- Load index by class ID
- Return top 5 matching chunks by cosine similarity

### `task-15`: Construct RAG prompt and call OpenAI API
- Inject top-k chunks into system prompt
- Call GPT-4 or GPT-3.5 and return output string

---

## 🔹 Phase 6: Integrate Frontend Query UI

### `task-16`: Build chat input + message display
- Chat bubble layout with user and system messages
- Highlight citations with links (fake for now)

### `task-17`: Connect to query API from frontend
- On submit, POST question + class to `/query`
- Display streaming or full answer in chat

---

## 🔹 Phase 7: Minimal Database (Optional MVP)

### `task-18`: Add SQLite or Postgres container + init
- One table for `classes(id, name)`
- One table for `documents(id, class_id, filename, status)`

### `task-19`: Log upload + job completion
- Update document status from “pending” → “indexed”

---

## 🔹 Phase 8: Test + Finalize MVP

### `task-20`: Upload + parse test PDF
- Confirm PDF text appears in terminal

### `task-21`: Query with test prompt
- Confirm returned RAG response includes a valid summary

### `task-22`: End-to-end test
- Upload → embed → query from UI

