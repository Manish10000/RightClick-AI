"""
Secure RAG Service with user isolation
"""
from pathlib import Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
import json
from datetime import datetime

from app.embeddings import get_embedding_generator
from app.chunking import DocumentChunker
from app.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.database.models import User, Document, KnowledgeBaseEntry
from app.files.storage_manager import StorageManager
import numpy as np
from numpy.linalg import norm
import logging

logger = logging.getLogger(__name__)


class SecureRAGService:
    """Secure RAG service with user-level data isolation"""
    
    def __init__(self):
        """Initialize secure RAG service"""
        self.embedding_gen = get_embedding_generator()
        self.chunker = DocumentChunker()
    
    def process_document(
        self,
        db: Session,
        user: User,
        file_path: str,
        file_name: str,
        file_content
    ) -> Dict[str, Any]:
        """
        Process a document for a specific user
        
        Args:
            db: Database session
            user: User object
            file_path: Path to file
            file_name: Original filename
            file_content: File content
            
        Returns:
            Processing result
        """
        try:
            logger.info(f"Processing document for user {user.id}: {file_name}")
            
            # Save file to user's directory
            file_id, saved_path = StorageManager.save_uploaded_file(
                user.id, file_content, file_name
            )
            
            # Determine file type
            file_ext = Path(file_name).suffix.lower()
            
            # Extract text based on file type
            if file_ext == '.pdf':
                from PyPDF2 import PdfReader
                reader = PdfReader(saved_path)
                text = ""
                num_pages = len(reader.pages)
                for page in reader.pages:
                    text += page.extract_text()
            else:
                # Text file
                with open(saved_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                num_pages = None
            
            if not text.strip():
                raise ValueError("No text could be extracted from file")
            
            # Create chunks
            chunks_data = []
            for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
                chunk_text = text[i:i + CHUNK_SIZE]
                if chunk_text.strip():
                    chunks_data.append({
                        'content': chunk_text,
                        'chunk_id': len(chunks_data)
                    })
            
            # Generate embeddings
            contents = [c['content'] for c in chunks_data]
            embeddings = self.embedding_gen.embed_batch(contents)
            
            # Create document record
            document = Document(
                user_id=user.id,
                document_id=file_id,
                file_name=file_name,
                file_path=saved_path,
                file_type=file_ext[1:],  # Remove dot
                file_size=Path(saved_path).stat().st_size,
                num_chunks=len(chunks_data),
                num_pages=num_pages,
                processed=True
            )
            db.add(document)
            db.flush()  # Get document ID
            
            # Create knowledge base entries
            for chunk_data, embedding in zip(chunks_data, embeddings):
                # Convert embedding to JSON string
                if hasattr(embedding, 'tolist'):
                    embedding_list = embedding.tolist()
                else:
                    embedding_list = embedding
                
                entry = KnowledgeBaseEntry(
                    user_id=user.id,
                    document_id=document.id,
                    entry_id=str(uuid.uuid4()),
                    content=chunk_data['content'],
                    chunk_index=chunk_data['chunk_id'],
                    embedding=json.dumps(embedding_list)
                )
                db.add(entry)
            
            db.commit()
            db.refresh(document)
            
            logger.info(f"✅ Processed {file_name}: {len(chunks_data)} chunks")
            
            return {
                'document_id': document.document_id,
                'num_chunks': len(chunks_data),
                'num_pages': num_pages
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing document: {e}")
            raise
    
    def search(
        self,
        db: Session,
        user: User,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search user's knowledge base
        
        Args:
            db: Database session
            user: User object
            query: Search query
            top_k: Number of results
            similarity_threshold: Minimum similarity
            
        Returns:
            Search results (user-isolated)
        """
        try:
            # Get query embedding
            query_embeddings = self.embedding_gen.embed_batch([query])
            query_embedding = np.array(query_embeddings[0])
            
            # Get user's knowledge base entries
            entries = db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.user_id == user.id
            ).all()
            
            if not entries:
                return []
            
            # Calculate similarities
            results = []
            for entry in entries:
                # Parse embedding from JSON
                entry_embedding = np.array(json.loads(entry.embedding))
                
                # Cosine similarity
                similarity = np.dot(query_embedding, entry_embedding) / (
                    norm(query_embedding) * norm(entry_embedding)
                )
                
                if similarity >= similarity_threshold:
                    # Get document info
                    document = db.query(Document).filter(
                        Document.id == entry.document_id
                    ).first()
                    
                    results.append({
                        'content': entry.content,
                        'file_path': document.file_name if document else 'Unknown',
                        'chunk_index': entry.chunk_index,
                        'score': float(similarity),
                        'metadata': {
                            'document_id': document.document_id if document else '',
                            'total_pages': document.num_pages if document else 0
                        }
                    })
            
            # Sort by similarity
            results.sort(reverse=True, key=lambda x: x['score'])
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    def chat(
        self,
        db: Session,
        user: User,
        message: str,
        context_chunks: int = 3,
        model: str = "llama3.1:8b"
    ) -> Dict[str, Any]:
        """
        Chat with user's documents using Ollama
        
        Args:
            db: Database session
            user: User object
            message: User message
            context_chunks: Number of context chunks
            model: Ollama model
            
        Returns:
            Chat response with sources
        """
        try:
            import requests
            from app.config import OLLAMA_BASE_URL
            
            ollama_url = f"{OLLAMA_BASE_URL}/api/generate"
            
            # Step 1: Clean and enhance the query
            enhanced_query = message.strip()
            
            # Basic query cleaning for common patterns
            if "what is your have worked on" in enhanced_query.lower():
                enhanced_query = enhanced_query.lower().replace("what is your have worked on", "what have you worked on with")
            
            logger.info(f"Original query: {message}")
            logger.info(f"Enhanced query: {enhanced_query}")
            
            # Step 2: Determine if RAG is needed
            decision_prompt = f"""You are a helpful assistant with access to a document database containing user's resume and personal information. 
Analyze the following user question and determine if you need to search the document database to answer it.

Respond with ONLY "YES" if you need documents for questions about:
- Personal experience, projects, work history
- Skills, technologies, certifications
- Education, background
- Specific achievements or accomplishments
- "What have you worked on", "your experience", "your projects", etc.

Respond with ONLY "NO" if you can answer without documents:
- General explanations of concepts
- How-to questions
- Theoretical questions

User question: {enhanced_query}

Do you need to search the document database? (YES/NO):"""
            
            # Step 2: Determine if RAG is needed - use keyword-based approach for better reliability
            needs_rag = False
            
            # Keywords that indicate personal/resume questions
            personal_keywords = [
                'your', 'you', 'experience', 'worked', 'projects', 'skills', 
                'background', 'education', 'certification', 'achievement',
                'portfolio', 'resume', 'cv', 'career', 'job', 'work'
            ]
            
            query_lower = enhanced_query.lower()
            if any(keyword in query_lower for keyword in personal_keywords):
                needs_rag = True
                logger.info(f"RAG triggered by keywords in query: {enhanced_query}")
            else:
                # Fallback to AI decision for edge cases
                decision_prompt = f"""You are a helpful assistant with access to a document database containing user's resume and personal information. 
Analyze the following user question and determine if you need to search the document database to answer it.

Respond with ONLY "YES" if you need documents for questions about:
- Personal experience, projects, work history
- Skills, technologies, certifications
- Education, background
- Specific achievements or accomplishments

Respond with ONLY "NO" if you can answer without documents:
- General explanations of concepts
- How-to questions
- Theoretical questions

User question: {enhanced_query}

Do you need to search the document database? (YES/NO):"""
                
                logger.info("Using AI decision for RAG...")
                
                decision_response = requests.post(
                    ollama_url,
                    json={"model": model, "prompt": decision_prompt, "stream": False},
                    timeout=30
                )
                
                if decision_response.status_code == 200:
                    decision = decision_response.json().get('response', '').strip().upper()
                    needs_rag = 'YES' in decision[:10]
                    logger.info(f"AI decision: {decision} -> RAG: {needs_rag}")
            
            logger.info(f"Final RAG decision: {needs_rag}")
            
            # Step 3: Retrieve documents if needed
            if needs_rag:
                logger.info("Retrieving relevant documents...")
                sources = self.search(db, user, enhanced_query, top_k=context_chunks)
                
                if sources:
                    context = "\n\n".join([
                        f"[Document {i+1}] {s['content']}" 
                        for i, s in enumerate(sources)
                    ])
                    
                    prompt = f"""You are responding to questions about a person based on their resume/documents. Answer in first person as if you are that person speaking directly to the questioner.

Documents about the person:
{context}

User's question: {enhanced_query}

IMPORTANT INSTRUCTIONS:
- Answer in first person (use "I", "my", "me") as if you are the person described in the documents
- Extract the person's name and details from the documents provided
- Be conversational and natural
- Do NOT use markdown formatting (no *, **, #, etc.)
- Use simple bullet points with • or - only when listing items
- Be concise but friendly
- Start your response immediately with the answer
- If the documents don't contain enough information to answer the question, politely say you don't have that information available

Your response:"""
                else:
                    prompt = f"""I searched my documents but couldn't find specific information to answer your question.

Question: {enhanced_query}

Please respond politely in first person that you don't have that information available:"""
                    sources = []
            else:
                logger.info("Answering without RAG data...")
                sources = []
                prompt = f"""You are a helpful AI assistant. Answer the user's question directly.

User's question: {enhanced_query}

Your response:"""
            
            # Generate response
            response = requests.post(
                ollama_url,
                json={"model": model, "prompt": prompt, "stream": False},
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
    
    def chat_direct(
        self,
        message: str,
        model: str = "llama3.1:8b"
    ) -> Dict[str, Any]:
        """
        Direct chat with AI without RAG (no document context)
        
        Args:
            message: User message
            model: Ollama model
            
        Returns:
            Direct AI response without RAG
        """
        try:
            import requests
            from app.config import OLLAMA_BASE_URL
            
            ollama_url = f"{OLLAMA_BASE_URL}/api/generate"
            
            # Enhanced prompt for direct responses
            prompt = f"""You are a helpful AI assistant. Answer the user's question directly and concisely.

IMPORTANT INSTRUCTIONS:
- Answer directly without introductory phrases
- Do NOT use markdown formatting (no *, **, #, etc.)
- Be concise and specific
- Start your response immediately with the answer

User's question: {message}

Your response:"""
            
            logger.info("Generating direct AI response (no RAG)...")
            
            # Generate response
            response = requests.post(
                ollama_url,
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=60
            )
            
            if response.status_code == 200:
                ai_response = response.json().get('response', 'No response generated').strip()
            else:
                ai_response = f"Error: {response.status_code}"
            
            return {
                'response': ai_response,
                'sources': [],
                'model': model,
                'used_rag': False,
                'num_sources': 0
            }
            
        except Exception as e:
            logger.error(f"Direct chat error: {e}")
            raise
    
    def get_user_documents(self, db: Session, user: User) -> List[Dict[str, Any]]:
        """
        Get all documents for a user
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            List of user's documents
        """
        documents = db.query(Document).filter(
            Document.user_id == user.id
        ).all()
        
        return [
            {
                'id': doc.document_id,
                'file_name': doc.file_name,
                'file_path': doc.file_path,
                'num_chunks': doc.num_chunks,
                'total_pages': doc.num_pages,
                'uploaded_at': doc.uploaded_at
            }
            for doc in documents
        ]
    
    def delete_document(self, db: Session, user: User, document_id: str) -> bool:
        """
        Delete a user's document
        
        Args:
            db: Database session
            user: User object
            document_id: Document ID
            
        Returns:
            True if deleted
        """
        try:
            # Find document (user-isolated)
            document = db.query(Document).filter(
                Document.document_id == document_id,
                Document.user_id == user.id  # Security: ensure user owns document
            ).first()
            
            if not document:
                return False
            
            # Delete file from storage
            StorageManager.delete_file(user.id, document.file_path)
            
            # Delete database records (cascades to knowledge base entries)
            db.delete(document)
            db.commit()
            
            logger.info(f"Deleted document {document_id} for user {user.id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting document: {e}")
            raise
    
    def get_user_stats(self, db: Session, user: User) -> Dict[str, Any]:
        """
        Get statistics for a user
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            User statistics
        """
        documents = db.query(Document).filter(
            Document.user_id == user.id
        ).all()
        
        total_chunks = db.query(KnowledgeBaseEntry).filter(
            KnowledgeBaseEntry.user_id == user.id
        ).count()
        
        total_size = sum(doc.file_size for doc in documents)
        
        return {
            'total_documents': len(documents),
            'total_chunks': total_chunks,
            'total_size_bytes': total_size,
            'documents': self.get_user_documents(db, user)
        }


# Global service instance
_secure_rag_service = None


def get_secure_rag_service() -> SecureRAGService:
    """Get or create secure RAG service instance"""
    global _secure_rag_service
    if _secure_rag_service is None:
        _secure_rag_service = SecureRAGService()
    return _secure_rag_service
