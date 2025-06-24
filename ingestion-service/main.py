import os
import logging
import uuid
from typing import List

import redis
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form, Query
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests

from core.config import settings
from core.database import get_db
from core import models
from core.pdf_parser import extract_text_from_pdf
from core.chunking import chunk_text
from celery_config import celery_app
from shared.storage import upload_file_to_s3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ClassGPT Ingestion Service",
    description="Handles file uploads, class management, and queues documents for embedding.",
    version="1.0.0",
)

redis_client = redis.from_url(settings.REDIS_URL)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

QDRANT_URL = os.getenv("VECTOR_STORE_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "classgpt_chunks")

security = HTTPBearer()
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8002/me")

# Helper to get user_id from JWT
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    headers = {"Authorization": f"Bearer {credentials.credentials}"}
    try:
        resp = requests.get(AUTH_SERVICE_URL, headers=headers, timeout=5)
        resp.raise_for_status()
        return resp.json()["id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.on_event("startup")
def on_startup():
    """
    Check Redis connection on startup.
    """
    try:
        redis_client.ping()
        logger.info("Successfully connected to Redis.")
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        # Depending on the use case, you might want to exit the application
        # raise RuntimeError("Failed to connect to Redis") from e


@app.get("/health", status_code=200)
def health_check():
    """
    Health check endpoint to verify service is running.
    """
    return {"status": "ok"}


@app.get("/classes", status_code=200)
def get_classes(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """
    Returns a list of all classes.
    """
    classes = db.query(models.Class).filter(models.Class.user_id == user_id).all()
    return classes


@app.post("/classes", status_code=201)
def create_class(name: str = Form(...), db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """
    Creates a new class.
    """
    new_class = models.Class(name=name, user_id=user_id)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class


@app.delete("/classes/{class_id}", status_code=204)
def delete_class(class_id: uuid.UUID, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """
    Deletes a class and all associated documents.
    """
    db_class = db.query(models.Class).filter(models.Class.id == class_id, models.Class.user_id == user_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Associated documents are deleted via CASCADE in the database
    db.delete(db_class)
    db.commit()
    return


@app.post("/upload", status_code=200)
async def upload_files(
    class_id: uuid.UUID = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Accepts multiple file uploads for a given class and queues them for processing.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were sent.")

    # 1. Verify class exists
    db_class = db.query(models.Class).filter(models.Class.id == class_id, models.Class.user_id == user_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail=f"Class with ID {class_id} not found.")

    processed_files = []
    
    for file in files:
        file_bytes = await file.read()
        
        try:
            # Upload to S3
            s3_url = upload_file_to_s3(file_bytes, file.filename, user_id, class_id)

            # 4. Create a document record in the database
            new_document = models.Document(
                id=uuid.uuid4(),
                class_id=db_class.id,
                filename=file.filename,
                status="pending",
                user_id=user_id,
                s3_url=s3_url,
            )
            db.add(new_document)
            db.commit()
            db.refresh(new_document)

            # 5. Queue the document for processing using Celery
            # We'll use a simple task name that the embedding worker will handle
            celery_app.send_task(
                'tasks.process_document',
                args=[str(new_document.id), s3_url],
                queue='embedding_queue'
            )
            
            processed_files.append(file.filename)
            logger.info(f"Successfully saved and queued document: {file.filename} for class {db_class.name}")

        except Exception as e:
            logger.error(f"Failed to process file {file.filename}. Error: {e}")
            # Optionally, rollback the DB commit or handle partial failure
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Could not save or queue file: {file.filename}"
            )

    response_data = {
        "message": f"Successfully uploaded and queued {len(processed_files)} file(s).",
        "filenames": processed_files,
    }

    return response_data


@app.get("/documents", status_code=200)
def get_documents(class_id: uuid.UUID = Query(...), db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """
    Returns a list of all documents for a given class.
    """
    documents = db.query(models.Document).join(models.Class).filter(models.Class.id == class_id, models.Class.user_id == user_id).all()
    return [
        {
            "id": str(doc.id),
            "filename": doc.filename,
            "status": doc.status,
            "uploaded_at": doc.uploaded_at,
        }
        for doc in documents
    ]


@app.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """
    Deletes a single document by its UUID and removes corresponding embeddings from Qdrant.
    """
    db_doc = db.query(models.Document).join(models.Class).filter(models.Document.id == document_id, models.Class.user_id == user_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(db_doc)
    db.commit()
    # Delete corresponding embeddings from Qdrant
    try:
        client = QdrantClient(url=QDRANT_URL)
        client.delete(
            collection_name=QDRANT_COLLECTION,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=str(document_id))
                    )
                ]
            )
        )
        logger.info(f"Successfully deleted embeddings from Qdrant for document {document_id}")
    except Exception as e:
        logger.error(f"Failed to delete embeddings from Qdrant for document {document_id}: {e}")
    return


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 