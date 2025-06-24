import re
import logging
from typing import List

logger = logging.getLogger(__name__)

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using regex."""
    # Simple sentence splitter (can be improved with nltk or spacy)
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_endings.split(text.strip())
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 20) -> List[str]:
    """Split text into chunks with overlap - simplified version."""
    try:
        # Split into words first
        words = text.split()
        logger.info(f"Text has {len(words)} words")
        
        if len(words) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(words):
            # Calculate end position for this chunk
            end = min(start + chunk_size, len(words))
            
            # Create chunk
            chunk_words = words[start:end]
            chunk = ' '.join(chunk_words)
            chunks.append(chunk)
            
            logger.info(f"Created chunk {len(chunks)} with {len(chunk_words)} words")
            
            # Move start position for next chunk (with overlap)
            start = max(start + 1, end - overlap)
            
            # Safety check to prevent infinite loop
            if start >= len(words):
                break
        
        logger.info(f"Total chunks created: {len(chunks)}")
        return chunks
        
    except Exception as e:
        logger.error(f"Error in chunk_text: {e}")
        # Return the original text as a single chunk if chunking fails
        return [text] 