import os
import fitz  # PyMuPDF
from celery import current_task, Task
from celery_config import celery_app, settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json
from embedding_providers import get_embedding_provider
import openai
from qdrant_utils import upsert_embeddings
from core.pdf_parser import extract_text_by_page
from core.chunking import chunk_text
import requests

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task(bind=True)
def process_document(self, document_id: int, file_url: str):
    """
    Process a document: download from S3, extract text, chunk, generate embeddings, and store chunks in database.
    """
    # Download file from S3
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        file_bytes = response.content
    except Exception as e:
        raise Exception(f"Failed to download file from S3: {e}")
    # Continue with PDF/text extraction using file_bytes
    try:
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting document processing...'}
        )
        
        # Get document info including class_id
        db = SessionLocal()
        try:
            query = text("SELECT class_id FROM documents WHERE id = :document_id")
            result = db.execute(query, {'document_id': document_id}).fetchone()
            if not result:
                raise Exception(f"Document {document_id} not found")
            class_id = result[0]
        finally:
            db.close()
        
        # Extract text per page
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Extracting text from PDF...'}
        )
        pages = extract_text_by_page(file_bytes)
        if not pages or not any(text.strip() for _, text in pages):
            raise Exception("No text content extracted from PDF")
        
        # Chunk per page, track page_number
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Chunking text...'}
        )
        all_chunks = []
        all_metadata = []
        for page_number, page_text in pages:
            page_chunks = chunk_text(page_text)
            for chunk in page_chunks:
                all_chunks.append(chunk)
                all_metadata.append({"class_id": str(class_id), "page_number": page_number})
        
        # Generate embeddings
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'Generating embeddings...'}
        )
        
        embedding_provider = get_embedding_provider()
        embeddings = embedding_provider.embed(all_chunks)
        
        # For now, just print the shape for demo
        print(f"Generated {len(embeddings)} embeddings for document {document_id}")
        
        # Store chunks in database
        self.update_state(
            state='PROGRESS',
            meta={'current': 70, 'total': 100, 'status': 'Storing chunks in database...'}
        )
        
        store_chunks_in_database(document_id, all_chunks)
        
        # Update document status
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Updating document status...'}
        )
        
        update_document_status(document_id, "processed")
        
        upsert_embeddings(str(document_id), all_chunks, embeddings, all_metadata)
        
        return {
            'status': 'success',
            'document_id': document_id,
            'chunks_created': len(all_chunks)
        }
        
    except Exception as e:
        # Update document status to failed
        try:
            update_document_status(document_id, "failed")
        except:
            pass
        
        raise Exception(f"Document processing failed: {str(e)}")

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def store_chunks_in_database(document_id: int, chunks: list):
    """Store text chunks in the database"""
    db = SessionLocal()
    try:
        for i, chunk in enumerate(chunks):
            # Insert chunk into database
            query = text("""
                INSERT INTO document_chunks (document_id, chunk_index, content, created_at)
                VALUES (:document_id, :chunk_index, :content, NOW())
            """)
            
            db.execute(query, {
                'document_id': document_id,
                'chunk_index': i,
                'content': chunk
            })
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to store chunks in database: {str(e)}")
    finally:
        db.close()

def update_document_status(document_id: int, status: str):
    """Update document status in database"""
    db = SessionLocal()
    try:
        query = text("""
            UPDATE documents 
            SET status = :status, updated_at = NOW()
            WHERE id = :document_id
        """)
        
        db.execute(query, {
            'document_id': document_id,
            'status': status
        })
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to update document status: {str(e)}")
    finally:
        db.close() 