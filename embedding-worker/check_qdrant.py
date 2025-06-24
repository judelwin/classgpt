from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
points, _ = client.scroll(collection_name="classgpt_chunks", limit=10)

print("Checking Qdrant payloads...")
print(f"Found {len(points)} points in collection 'classgpt_chunks'")
print()

for i, point in enumerate(points):
    print(f"Point {i+1}:")
    print(f"  ID: {point.id}")
    print(f"  Payload: {point.payload}")
    print() 