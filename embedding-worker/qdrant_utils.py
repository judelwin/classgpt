import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from typing import List, Dict

QDRANT_URL = os.getenv("VECTOR_STORE_URL", "http://vector-store:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "classgpt_chunks")

# Default vector size for OpenAI ada-002 and MiniLM
VECTOR_SIZE = int(os.getenv("EMBEDDING_DIM", "1536"))

client = QdrantClient(url=QDRANT_URL)

def ensure_collection():
    try:
        # Try to create the collection, ignore if it already exists
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
    except Exception as e:
        # Collection already exists, which is fine
        pass

def upsert_embeddings(document_id: str, chunks: List[str], embeddings: List[List[float]], metadata: List[Dict]):
    ensure_collection()
    points = []
    for i, (chunk, embedding, meta) in enumerate(zip(chunks, embeddings, metadata)):
        point = PointStruct(
            id=str(uuid.uuid4()),  # Unique UUID for each chunk
            vector=embedding,
            payload={
                "document_id": document_id,
                "chunk_index": i,
                "content": chunk,
                **meta
            }
        )
        points.append(point)
    client.upsert(collection_name=COLLECTION_NAME, points=points) 