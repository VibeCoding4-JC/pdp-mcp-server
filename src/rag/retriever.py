"""
RAG Retriever untuk PDP MCP Server.
Menangani similarity search dan context building.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from .embeddings import EmbeddingClient, get_embedding_client
from .pinecone_client import PineconeClient, get_pinecone_client

load_dotenv()


@dataclass
class RetrievalResult:
    """Hasil retrieval dari vector database."""
    id: str
    score: float
    content: str
    metadata: dict
    
    def to_context(self) -> str:
        """Convert ke format context untuk LLM."""
        ref = self.metadata.get("full_reference", f"Pasal {self.metadata.get('pasal', 'N/A')}")
        return f"[{ref}]\n{self.content}"


class PDPRetriever:
    """Retriever untuk knowledge base UU PDP."""
    
    def __init__(
        self,
        embedding_client: Optional[EmbeddingClient] = None,
        pinecone_client: Optional[PineconeClient] = None
    ):
        """
        Inisialisasi retriever.
        
        Args:
            embedding_client: Client untuk generate embeddings
            pinecone_client: Client untuk Pinecone
        """
        self.embedding_client = embedding_client or get_embedding_client()
        self.pinecone_client = pinecone_client or get_pinecone_client()
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_type: Optional[str] = None,
        filter_bab: Optional[str] = None
    ) -> list[RetrievalResult]:
        """
        Search dokumen yang relevan dengan query.
        
        Args:
            query: Query text
            top_k: Jumlah hasil yang dikembalikan
            filter_type: Filter berdasarkan type (pasal/definisi)
            filter_bab: Filter berdasarkan BAB
            
        Returns:
            List of RetrievalResult
        """
        # Generate query embedding (use embed_query for better retrieval)
        if hasattr(self.embedding_client, 'embed_query'):
            query_embedding = self.embedding_client.embed_query(query)
        else:
            query_embedding = self.embedding_client.embed_text(query)
        
        # Build filter
        pinecone_filter = None
        if filter_type or filter_bab:
            pinecone_filter = {}
            if filter_type:
                pinecone_filter["type"] = {"$eq": filter_type}
            if filter_bab:
                pinecone_filter["bab"] = {"$eq": filter_bab}
        
        # Query Pinecone
        results = self.pinecone_client.query(
            vector=query_embedding,
            top_k=top_k,
            filter=pinecone_filter,
            include_metadata=True
        )
        
        # Convert to RetrievalResult
        retrieval_results = []
        for match in results.get("matches", []):
            result = RetrievalResult(
                id=match["id"],
                score=match["score"],
                content=match["metadata"].get("content", ""),
                metadata=match["metadata"]
            )
            retrieval_results.append(result)
        
        return retrieval_results
    
    def search_pasal(
        self,
        query: str,
        top_k: int = 5,
        bab: Optional[str] = None
    ) -> list[RetrievalResult]:
        """
        Search pasal yang relevan dengan query.
        
        Args:
            query: Query text
            top_k: Jumlah hasil
            bab: Filter berdasarkan BAB (I, II, III, dst)
            
        Returns:
            List of RetrievalResult untuk pasal
        """
        return self.search(
            query=query,
            top_k=top_k,
            filter_type="pasal",
            filter_bab=bab
        )
    
    def search_definisi(
        self,
        query: str,
        top_k: int = 3
    ) -> list[RetrievalResult]:
        """
        Search definisi yang relevan dengan query.
        
        Args:
            query: Query text (istilah yang dicari)
            top_k: Jumlah hasil
            
        Returns:
            List of RetrievalResult untuk definisi
        """
        return self.search(
            query=query,
            top_k=top_k,
            filter_type="definisi"
        )
    
    def build_context(
        self,
        results: list[RetrievalResult],
        max_tokens: int = 3000
    ) -> str:
        """
        Build context string dari hasil retrieval.
        
        Args:
            results: List of RetrievalResult
            max_tokens: Maksimum approximate tokens (chars / 4)
            
        Returns:
            Context string untuk LLM
        """
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # Approximate conversion
        
        for result in results:
            context = result.to_context()
            
            if total_chars + len(context) > max_chars:
                # Truncate if exceeds limit
                remaining = max_chars - total_chars
                if remaining > 100:
                    context = context[:remaining] + "..."
                    context_parts.append(context)
                break
            
            context_parts.append(context)
            total_chars += len(context)
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_context_for_query(
        self,
        query: str,
        top_k: int = 5,
        max_tokens: int = 3000
    ) -> tuple[str, list[RetrievalResult]]:
        """
        Get context dan results untuk query.
        
        Args:
            query: Query text
            top_k: Jumlah hasil
            max_tokens: Max tokens untuk context
            
        Returns:
            Tuple of (context string, list of results)
        """
        results = self.search(query, top_k=top_k)
        context = self.build_context(results, max_tokens=max_tokens)
        return context, results


# Singleton instance
_retriever: Optional[PDPRetriever] = None


def get_retriever() -> PDPRetriever:
    """Get singleton retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = PDPRetriever()
    return _retriever
