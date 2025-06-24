from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

print("Clearing Qdrant collection...")
client.delete_collection(collection_name="classgpt_chunks")
print("Collection deleted. It will be recreated when new embeddings are added.") 