"""
Embedding generation module for AI Keyboard
"""
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL
import numpy as np
from typing import List, Union

# Default batch size
BATCH_SIZE = 32


class EmbeddingGenerator:
    """Handles text embedding generation with batching support"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize embedding model"""
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Embedding dimension: {self.dimension}")
    
    def embed_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text
        
        Args:
            text: Single string or list of strings
            
        Returns:
            Embedding vector(s)
        """
        if isinstance(text, str):
            return self.model.encode(text, convert_to_numpy=True).tolist()
        else:
            # Batch processing for multiple texts
            return self.model.encode(
                text,
                batch_size=BATCH_SIZE,
                show_progress_bar=len(text) > 100,
                convert_to_numpy=True
            ).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        return self.embed_text(texts)
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


# Global embedding generator instance
_embedding_generator = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create global embedding generator instance"""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator


def embed_text(text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """Convenience function to embed text"""
    return get_embedding_generator().embed_text(text)
