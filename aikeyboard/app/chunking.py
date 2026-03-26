"""
Smart document chunking module for AI Keyboard
"""
import PyPDF2
import os
from typing import List, Dict, Tuple
from app.config import CHUNK_SIZE, CHUNK_OVERLAP
import hashlib
import logging

# Additional config
MIN_CHUNK_SIZE = 100
SUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.md']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunker:
    """Handles intelligent document chunking"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target size for each chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk text into overlapping segments
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries
        """
        if not text or len(text) < MIN_CHUNK_SIZE:
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If not at the end, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for delimiter in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
                    last_delimiter = text.rfind(delimiter, start, end)
                    if last_delimiter != -1:
                        end = last_delimiter + len(delimiter)
                        break
            
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) >= MIN_CHUNK_SIZE:
                chunk_data = {
                    "content": chunk_text,
                    "chunk_id": chunk_id,
                    "start_pos": start,
                    "end_pos": end,
                    "metadata": metadata or {}
                }
                chunks.append(chunk_data)
                chunk_id += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap if end < len(text) else end
        
        return chunks
    
    def extract_pdf_text(self, pdf_path: str) -> List[Tuple[str, int]]:
        """
        Extract text from PDF with page numbers
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of (text, page_number) tuples
        """
        pages = []
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append((text, page_num + 1))
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
        
        return pages
    
    def chunk_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Chunk PDF document
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of chunk dictionaries
        """
        all_chunks = []
        pages = self.extract_pdf_text(pdf_path)
        
        for text, page_num in pages:
            metadata = {
                "source": pdf_path,
                "page": page_num,
                "file_type": "pdf"
            }
            chunks = self.chunk_text(text, metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"Chunked PDF {pdf_path}: {len(pages)} pages → {len(all_chunks)} chunks")
        return all_chunks
    
    def chunk_text_file(self, file_path: str) -> List[Dict]:
        """
        Chunk text file
        
        Args:
            file_path: Path to text file
            
        Returns:
            List of chunk dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            metadata = {
                "source": file_path,
                "file_type": os.path.splitext(file_path)[1][1:]
            }
            chunks = self.chunk_text(text, metadata)
            logger.info(f"Chunked file {file_path}: {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []
    
    def chunk_document(self, file_path: str) -> List[Dict]:
        """
        Chunk any supported document type
        
        Args:
            file_path: Path to document
            
        Returns:
            List of chunk dictionaries
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self.chunk_pdf(file_path)
        elif ext in ['.txt', '.md', '.py', '.js', '.ts', '.java', '.cpp', '.c']:
            return self.chunk_text_file(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return []
    
    def generate_chunk_hash(self, content: str) -> str:
        """Generate unique hash for chunk content"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
