import fitz  # PyMuPDF
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

def extract_text_by_page(file_path: str) -> Optional[List[Tuple[int, str]]]:
    """
    Extract text content from a PDF file, per page.
    Returns a list of (page_number, text) tuples.
    """
    try:
        doc = fitz.open(file_path)
        pages = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            pages.append((page_num + 1, text))  # 1-based page numbers
        doc.close()
        logger.info(f"Extracted {len(pages)} pages from PDF: {file_path}")
        return pages
    except Exception as e:
        logger.error(f"Failed to extract text from PDF {file_path}: {e}")
        return None

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file as a single string.
    Returns the concatenated text from all pages.
    """
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        logger.info(f"Extracted text from PDF: {file_path}")
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF {file_path}: {e}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}") 