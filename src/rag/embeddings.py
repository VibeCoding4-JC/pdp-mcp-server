"""
Gemini Embeddings handler untuk PDP MCP Server.
"""

import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class EmbeddingClient:
    """Client untuk generate embeddings menggunakan Google Gemini."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Inisialisasi Gemini embedding client.
        
        Args:
            api_key: Gemini API key (default dari env GEMINI_API_KEY)
            model: Model embedding (default dari env atau text-embedding-004)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=self.api_key)
    
    def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding untuk satu teks.
        
        Args:
            text: Teks yang akan di-embed
            
        Returns:
            Vector embedding (list of floats)
        """
        # Truncate text jika terlalu panjang (max ~10000 chars untuk Gemini)
        max_chars = 10000
        if len(text) > max_chars:
            text = text[:max_chars]
        
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_document"
        )
        
        return result['embedding']
    
    def embed_query(self, text: str) -> list[float]:
        """
        Generate embedding untuk query (pencarian).
        
        Args:
            text: Query teks
            
        Returns:
            Vector embedding (list of floats)
        """
        max_chars = 10000
        if len(text) > max_chars:
            text = text[:max_chars]
        
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        
        return result['embedding']
    
    def embed_batch(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """
        Generate embeddings untuk batch teks.
        
        Args:
            texts: List of teks yang akan di-embed
            batch_size: Ukuran batch per request
            
        Returns:
            List of vector embeddings
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Truncate each text
            max_chars = 10000
            batch = [t[:max_chars] if len(t) > max_chars else t for t in batch]
            
            # Gemini embed_content supports batch
            result = genai.embed_content(
                model=self.model,
                content=batch,
                task_type="retrieval_document"
            )
            
            all_embeddings.extend(result['embedding'])
        
        return all_embeddings
    
    def get_dimension(self) -> int:
        """
        Get dimensi embedding untuk model yang digunakan.
        
        Returns:
            Dimensi embedding (768 untuk text-embedding-004)
        """
        # Gemini text-embedding-004 = 768 dimensions
        return 768


# Singleton instance
_client: Optional[EmbeddingClient] = None


def get_embedding_client() -> EmbeddingClient:
    """Get singleton embedding client instance."""
    global _client
    if _client is None:
        _client = EmbeddingClient()
    return _client
