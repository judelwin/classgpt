import os
from typing import List

# OpenAI
import openai

# Sentence Transformers
from sentence_transformers import SentenceTransformer

class EmbeddingProvider:
    """
    Abstract embedding provider interface.
    """
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str = None, model: str = "text-embedding-ada-002"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        openai.api_key = self.api_key

    def embed(self, texts: List[str]) -> List[List[float]]:
        # OpenAI API supports batching up to 2048 tokens per request
        response = openai.embeddings.create(input=texts, model=self.model)
        return [d.embedding for d in response.data]

class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, show_progress_bar=False).tolist()

def get_embedding_provider() -> EmbeddingProvider:
    """
    Factory to select embedding provider based on environment/config.
    """
    provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
    if provider == "openai":
        return OpenAIEmbeddingProvider()
    elif provider == "local":
        return LocalEmbeddingProvider()
    else:
        raise ValueError(f"Unknown EMBEDDING_PROVIDER: {provider}") 