"""
Pinecone client wrapper untuk PDP MCP Server
"""

import os
from typing import Optional
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()


class PineconeClient:
    """Client untuk berinteraksi dengan Pinecone vector database."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None
    ):
        """
        Inisialisasi Pinecone client.
        
        Args:
            api_key: Pinecone API key (default dari env PINECONE_API_KEY)
            index_name: Nama index Pinecone (default dari env PINECONE_INDEX_NAME)
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "pdp-knowledge")
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY is required")
        
        # Inisialisasi Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self._index = None
    
    def create_index_if_not_exists(
        self,
        dimension: int = 1536,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1"
    ) -> None:
        """
        Buat index jika belum ada.
        
        Args:
            dimension: Dimensi vector (1536 untuk OpenAI text-embedding-3-small)
            metric: Metrik similarity (cosine, euclidean, dotproduct)
            cloud: Cloud provider
            region: Region
        """
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating index '{self.index_name}'...")
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region
                )
            )
            print(f"Index '{self.index_name}' created successfully!")
        else:
            print(f"Index '{self.index_name}' already exists.")
    
    @property
    def index(self):
        """Get atau create index instance."""
        if self._index is None:
            self._index = self.pc.Index(self.index_name)
        return self._index
    
    def upsert_vectors(
        self,
        vectors: list[dict],
        namespace: str = ""
    ) -> dict:
        """
        Upsert vectors ke Pinecone.
        
        Args:
            vectors: List of dict dengan format:
                     [{"id": "...", "values": [...], "metadata": {...}}, ...]
            namespace: Namespace untuk vectors
            
        Returns:
            Response dari Pinecone
        """
        return self.index.upsert(vectors=vectors, namespace=namespace)
    
    def query(
        self,
        vector: list[float],
        top_k: int = 5,
        namespace: str = "",
        filter: Optional[dict] = None,
        include_metadata: bool = True
    ) -> dict:
        """
        Query vectors dari Pinecone.
        
        Args:
            vector: Query vector
            top_k: Jumlah hasil yang dikembalikan
            namespace: Namespace untuk query
            filter: Metadata filter
            include_metadata: Sertakan metadata dalam hasil
            
        Returns:
            Query results dari Pinecone
        """
        return self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=namespace,
            filter=filter,
            include_metadata=include_metadata
        )
    
    def delete_all(self, namespace: str = "") -> None:
        """
        Hapus semua vectors dalam namespace.
        
        Args:
            namespace: Namespace untuk dihapus
        """
        self.index.delete(delete_all=True, namespace=namespace)
        print(f"All vectors in namespace '{namespace}' deleted.")
    
    def get_stats(self) -> dict:
        """
        Get statistik index.
        
        Returns:
            Index statistics
        """
        return self.index.describe_index_stats()


# Singleton instance
_client: Optional[PineconeClient] = None


def get_pinecone_client() -> PineconeClient:
    """Get singleton Pinecone client instance."""
    global _client
    if _client is None:
        _client = PineconeClient()
    return _client
