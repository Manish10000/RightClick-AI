"""
RAG Service - Core functionality for document processing and retrieval
"""
from pathlib import Path
import os

from app.embeddings import get_embedding_generator
from app.chunking import DocumentChunker
from app.storage import get_storage
from app.config import CHUNK_SIZE, CHUNK_OVERLAP
import numpy as np
from numpy.linalg import norm
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid
from PyPDF2 import PdfReader
import shutil

logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG service for document processing and retrieval"""
    
    def __init__(self):
        """Initialize RAG service"""
        self.embedding_gen = None
        self.chunker = DocumentChunker()
        self.storage = None
        self._initialize()
    
    def _initialize(self):
        """Initialize components"""
        try:
            logger.info("Initializing RAG service...")
            
            # Initialize embedding generator
            self.embedding_gen = get_embedding_generator()
            logger.info("✅ Embedding generator initialized")
            
            # Initialize storage
            self.storage = get_storage()
            logger.info("✅ Storage initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    def process_pdf(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Process a PDF file and store chunks
        
        Args:
            file_path: Path to PDF file
            file_name: Original file name
            
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Processing PDF: {file_name}")
            
            # Read PDF
            reader = PdfReader(file_path)
            num_pages = len(reader.pages)
            
            # Extract text
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            if not text.strip():
                raise ValueError("No text could be extracted from PDF")
            
            # Create chunks
            chunks_data = []
            for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
                chunk_text = text[i:i + CHUNK_SIZE]
                if chunk_text.strip():
                    chunks_data.append({
                        'content': chunk_text,
                        'chunk_id': len(chunks_data),
                        'metadata': {
                            'file_name': file_name,
                            'total_pages': num_pages
                        }
                    })
            
            # Generate embeddings
            contents = [c['content'] for c in chunks_data]
            embeddings = self.embedding_gen.embed_batch(contents)
            
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Store nodes
            for chunk_data, embedding in zip(chunks_data, embeddings):
                # Convert embedding to list if it's a numpy array
                if hasattr(embedding, 'tolist'):
                    embedding_list = embedding.tolist()
                else:
                    embedding_list = embedding
                    
                node_data = {
                    '_id': str(uuid.uuid4()),
                    'document_id': doc_id,
                    'content': chunk_data['content'],
                    'embedding': embedding_list,
                    'file_path': file_name,
                    'file_name': file_name,
                    'chunk_index': chunk_data['chunk_id'],
                    'total_pages': num_pages,
                    'is_summary': False,
                    'uploaded_at': datetime.utcnow()
                }
                self.storage.save_node(node_data)
            
            # Save document metadata
            doc_metadata = {
                'document_id': doc_id,
                'file_name': file_name,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'file_type': 'pdf',
                'num_pages': num_pages,
                'num_chunks': len(chunks_data),
                'uploaded_at': datetime.utcnow(),
                'processed': True
            }
            self.storage.save_document_metadata(doc_metadata)
            
            logger.info(f"✅ Processed {file_name}: {len(chunks_data)} chunks")
            
            return {
                'document_id': doc_id,
                'num_chunks': len(chunks_data),
                'num_pages': num_pages
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_name}: {e}")
            raise
    
    def process_text(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Process a text file and store chunks

        Args:
            file_path: Path to text file
            file_name: Original file name

        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Processing text file: {file_name}")

            # Read text file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            if not text.strip():
                raise ValueError("No text could be extracted from file")

            # Create chunks
            chunks_data = []
            for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
                chunk_text = text[i:i + CHUNK_SIZE]
                if chunk_text.strip():
                    chunks_data.append({
                        'content': chunk_text,
                        'chunk_id': len(chunks_data),
                        'metadata': {
                            'file_name': file_name
                        }
                    })

            # Generate embeddings
            contents = [c['content'] for c in chunks_data]
            embeddings = self.embedding_gen.embed_batch(contents)

            # Generate document ID
            doc_id = str(uuid.uuid4())

            # Store nodes
            for chunk_data, embedding in zip(chunks_data, embeddings):
                # Convert embedding to list if it's a numpy array
                if hasattr(embedding, 'tolist'):
                    embedding_list = embedding.tolist()
                else:
                    embedding_list = embedding

                node_data = {
                    '_id': str(uuid.uuid4()),
                    'document_id': doc_id,
                    'content': chunk_data['content'],
                    'embedding': embedding_list,
                    'file_path': file_name,
                    'file_name': file_name,
                    'chunk_index': chunk_data['chunk_id'],
                    'is_summary': False,
                    'uploaded_at': datetime.utcnow()
                }
                self.storage.save_node(node_data)

            # Save document metadata
            file_ext = Path(file_path).suffix.lower()[1:]  # Remove the dot
            doc_metadata = {
                'document_id': doc_id,
                'file_name': file_name,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'file_type': file_ext,
                'num_chunks': len(chunks_data),
                'uploaded_at': datetime.utcnow(),
                'processed': True
            }
            self.storage.save_document_metadata(doc_metadata)

            logger.info(f"✅ Processed {file_name}: {len(chunks_data)} chunks")

            return {
                'document_id': doc_id,
                'num_chunks': len(chunks_data)
            }

        except Exception as e:
            logger.error(f"Error processing text file {file_name}: {e}")
            raise

    def process_document(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Process a document file (PDF or text) and store chunks

        Args:
            file_path: Path to document file
            file_name: Original file name

        Returns:
            Dictionary with processing results
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.pdf':
            return self.process_pdf(file_path, file_name)
        elif file_ext in ['.txt', '.md']:
            return self.process_text(file_path, file_name)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def search(self, query: str, top_k: int = 5, similarity_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        try:
            # Get query embedding
            query_embeddings = self.embedding_gen.embed_batch([query])
            query_embedding = query_embeddings[0]
            
            # Get all nodes
            all_nodes = self.storage.get_all_nodes()
            
            if not all_nodes:
                return []
            
            # Calculate similarities
            results = []
            for node in all_nodes:
                node_emb = np.array(node['embedding'])
                query_emb = np.array(query_embedding)
                
                # Cosine similarity
                similarity = np.dot(query_emb, node_emb) / (norm(query_emb) * norm(node_emb))
                
                if similarity >= similarity_threshold:
                    results.append({
                        'content': node['content'],
                        'file_path': node.get('file_name', node.get('file_path', 'Unknown')),
                        'chunk_index': node.get('chunk_index', 0),
                        'score': float(similarity),
                        'metadata': {
                            'document_id': node.get('document_id', ''),
                            'total_pages': node.get('total_pages', 0)
                        }
                    })
            
            # Sort by similarity
            results.sort(reverse=True, key=lambda x: x['score'])
            
            # Return top K
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    def chat(self, message: str, context_chunks: int = 3, model: str = "llama3.1:8b") -> Dict[str, Any]:
        """
        Chat with documents using Ollama with intelligent RAG decision
        
        Args:
            message: User message
            context_chunks: Number of context chunks to include
            model: Ollama model to use
            
        Returns:
            Chat response with sources (if RAG was used)
        """
        try:
            import requests
            from app.config import OLLAMA_BASE_URL
            
            ollama_url = f"{OLLAMA_BASE_URL}/api/generate"
            
            # Step 1: Ask AI if it needs document context
            decision_prompt = f"""You are a helpful assistant with access to a document database. 
Analyze the following user question and determine if you need to search the document database to answer it.

Respond with ONLY "YES" if you need documents (questions about specific policies, procedures, facts from documents).
Respond with ONLY "NO" if you can answer without documents (general questions, greetings, explanations of common concepts).

User question: {message}

Do you need to search the document database? (YES/NO):"""
            
            logger.info("Step 1: Checking if RAG data is needed...")
            
            decision_response = requests.post(
                ollama_url,
                json={
                    "model": model,
                    "prompt": decision_prompt,
                    "stream": False
                },
                timeout=30
            )
            
            needs_rag = False
            if decision_response.status_code == 200:
                decision = decision_response.json().get('response', '').strip().upper()
                needs_rag = 'YES' in decision[:10]
                logger.info(f"RAG needed: {needs_rag}")
            
            # Step 2: If RAG is needed, retrieve documents
            if needs_rag:
                logger.info("Step 2: Retrieving relevant documents...")
                sources = self.search(message, top_k=context_chunks)
                
                if sources:
                    context = "\n\n".join([
                        f"[Document {i+1}] {s['content']}" 
                        for i, s in enumerate(sources)
                    ])
                    
                    prompt = f"""Based on the following document excerpts, please answer the user's question. 
If the answer is not in the documents, say so clearly.

Documents:
{context}

User's question: {message}

Your response:"""
                else:
                    prompt = f"""I searched the document database but found no relevant documents for your question.

Question: {message}

Please provide a general answer or let the user know that specific information is not available in the documents:"""
                    sources = []
                
                logger.info("Generating answer with document context...")
            else:
                logger.info("Step 2: Answering without RAG data...")
                sources = []
                prompt = f"""You are a helpful AI assistant. Answer the user's question directly and naturally.

User's question: {message}

Your response:"""
            
            # Generate final response
            response = requests.post(
                ollama_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                ai_response = response.json().get('response', 'No response generated')
            else:
                ai_response = f"Error: {response.status_code}"
            
            return {
                'response': ai_response,
                'sources': sources,
                'model': model,
                'used_rag': needs_rag,
                'num_sources': len(sources)
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """Get all documents"""
        try:
            all_nodes = self.storage.get_all_nodes()
            
            # Group by document
            docs = {}
            for node in all_nodes:
                doc_id = node.get('document_id', 'unknown')
                if doc_id not in docs:
                    docs[doc_id] = {
                        'id': doc_id,
                        'file_name': node.get('file_name', 'Unknown'),
                        'file_path': node.get('file_path', ''),
                        'num_chunks': 0,
                        'total_pages': node.get('total_pages', 0),
                        'uploaded_at': node.get('uploaded_at', datetime.utcnow())
                    }
                docs[doc_id]['num_chunks'] += 1
            
            return list(docs.values())
            
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks"""
        try:
            all_nodes = self.storage.get_all_nodes()
            deleted_count = 0
            
            for node in all_nodes:
                if node.get('document_id') == document_id:
                    self.storage.delete_node(node['_id'])
                    deleted_count += 1
            
            # Also delete document metadata
            try:
                self.storage.metadata.delete_many({"document_id": document_id})
            except:
                pass
            
            logger.info(f"Deleted document {document_id}: {deleted_count} chunks")
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            all_nodes = self.storage.get_all_nodes()
            documents = self.get_documents()
            
            total_size = sum(
                len(node.get('content', '').encode('utf-8')) 
                for node in all_nodes
            )
            
            return {
                'total_documents': len(documents),
                'total_chunks': len(all_nodes),
                'total_size_bytes': total_size,
                'documents': documents
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        try:
            from app.config import OLLAMA_BASE_URL
            
            # Check MongoDB
            mongodb_connected = False
            try:
                self.storage.get_all_nodes()
                mongodb_connected = True
            except:
                pass
            
            # Check Ollama
            ollama_available = False
            try:
                import requests
                response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
                ollama_available = response.status_code == 200
            except:
                pass
            
            # Get stats
            stats = self.get_stats()
            
            return {
                'status': 'healthy' if mongodb_connected else 'degraded',
                'mongodb_connected': mongodb_connected,
                'ollama_available': ollama_available,
                'embedding_model': 'all-MiniLM-L6-v2',
                'total_documents': stats['total_documents'],
                'total_chunks': stats['total_chunks']
            }
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Global service instance
_rag_service = None

def get_rag_service() -> RAGService:
    """Get or create RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
