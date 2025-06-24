# 🧠 ClassGPT

A scalable, modular Retrieval-Augmented Generation (RAG) system designed for multi-class academic document ingestion, semantic search, and LLM-based Q&A.

## 🎯 Overview

ClassGPT allows students and educators to:
- Upload academic documents (PDFs, slides, notes) organized by class
- Ask questions about course materials using natural language
- Receive AI-generated answers with source citations
- Maintain separate knowledge bases for different courses

## 🏗️ Architecture

The system consists of several microservices:

- **Frontend**: React + Tailwind UI for file uploads and chat interface
- **Ingestion Service**: PDF parsing and OCR for document processing
- **Embedding Worker**: Converts text chunks to embeddings using Celery
- **Query Service**: RAG pipeline with semantic search and LLM integration
- **Vector Store**: FAISS/Qdrant for embedding storage and retrieval
- **Database**: PostgreSQL for metadata and job tracking

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### Running with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd classgpt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Query Service API: http://localhost:8000
- Vector Store: http://localhost:6333

### Local Development

1. Install dependencies for each service:
```bash
# Frontend
cd frontend
npm install

# Python services
cd ../ingestion-service
pip install -r requirements.txt

cd ../embedding-worker
pip install -r requirements.txt

cd ../query-service
pip install -r requirements.txt
```

2. Start services individually (see individual service READMEs for details)

## 📁 Project Structure

```
classgpt/
├── frontend/              # React + Tailwind UI
├── ingestion-service/     # PDF/slide parsing + OCR
├── embedding-worker/      # Celery worker for embedding jobs
├── query-service/         # RAG pipeline + search endpoint
├── shared/               # Common logic used across services
├── database/             # PostgreSQL schema and migrations
├── docker-compose.yml    # Service orchestration
└── README.md
```

## 🔧 Configuration

Key environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key for LLM queries
- `REDIS_URL`: Redis connection string for Celery
- `DATABASE_URL`: PostgreSQL connection string
- `VECTOR_STORE_URL`: Qdrant connection string

## 📚 Usage

1. **Create a Class**: Use the class selector to create a new course
2. **Upload Documents**: Drag and drop PDFs, slides, or notes
3. **Ask Questions**: Type questions about your course materials
4. **Get Answers**: Receive AI-generated responses with source citations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions, please open an issue on GitHub or contact the development team.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.9+

### Quick Start

1. **Start the backend services:**
   ```bash
   docker-compose up -d
   ```
   This starts all backend services (database, auth, ingestion, query, etc.)

2. **Start the frontend in development mode:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The frontend will run on `http://localhost:5173` with hot reloading and API proxying.

3. **Register and login:**
   - Visit `http://localhost:5173`
   - Register with any email/password
   - You'll be automatically logged in

### Why This Setup?

- **Frontend in dev mode**: Uses Vite's built-in proxy for API calls, making development seamless
- **Backend in Docker**: Ensures consistent environment and easy service orchestration
- **Production ready**: When deploying, each service gets its own URL, no proxy needed

### API Endpoints

- **Auth Service**: `http://localhost:8002` (via proxy `/auth/*`)
- **Ingestion Service**: `http://localhost:8001` (via proxy `/classes/*`, `/upload/*`, `/documents/*`)
- **Query Service**: `http://localhost:8000` (via proxy `/query/*`)

## Production Deployment

Each service can be deployed independently:
- **Frontend**: Vercel, Netlify, or any static hosting
- **Backend Services**: Railway, Google Cloud Run, AWS ECS, etc.
- **Database**: Supabase, AWS RDS, etc.
- **Vector Store**: Qdrant Cloud or self-hosted
- **Storage**: AWS S3, Google Cloud Storage, etc.

## Features

- [x] User authentication
- [x] PDF document upload and processing
- [x] Document chunking and embedding
- [x] Vector search and retrieval
- [x] AI-powered Q&A interface
- [x] Class/course organization
- [ ] Real-time chat interface
- [ ] Document annotation
- [ ] Collaborative features
