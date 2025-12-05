"""
Unit tests untuk RAG retriever.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestRetrievalResult:
    """Tests untuk RetrievalResult dataclass."""
    
    def test_to_context_with_full_reference(self):
        """Test to_context dengan full_reference."""
        from src.rag.retriever import RetrievalResult
        
        result = RetrievalResult(
            id="pasal_1",
            score=0.95,
            content="Ini adalah isi pasal.",
            metadata={
                "full_reference": "BAB I - KETENTUAN UMUM, Pasal 1",
                "pasal": "1"
            }
        )
        
        context = result.to_context()
        
        assert "BAB I - KETENTUAN UMUM, Pasal 1" in context
        assert "Ini adalah isi pasal." in context
    
    def test_to_context_without_full_reference(self):
        """Test to_context tanpa full_reference."""
        from src.rag.retriever import RetrievalResult
        
        result = RetrievalResult(
            id="pasal_5",
            score=0.85,
            content="Isi pasal lainnya.",
            metadata={"pasal": "5"}
        )
        
        context = result.to_context()
        
        assert "Pasal 5" in context
        assert "Isi pasal lainnya." in context


class TestPDPRetriever:
    """Tests untuk PDPRetriever class."""
    
    @patch('src.rag.retriever.get_embedding_client')
    @patch('src.rag.retriever.get_pinecone_client')
    def test_search_returns_results(self, mock_pinecone, mock_embedding):
        """Test search mengembalikan hasil."""
        from src.rag.retriever import PDPRetriever
        
        # Mock embedding
        mock_embed_client = Mock()
        mock_embed_client.embed_text.return_value = [0.1] * 1536
        mock_embedding.return_value = mock_embed_client
        
        # Mock pinecone
        mock_pc_client = Mock()
        mock_pc_client.query.return_value = {
            "matches": [
                {
                    "id": "pasal_1",
                    "score": 0.95,
                    "metadata": {
                        "content": "Test content",
                        "full_reference": "Pasal 1"
                    }
                }
            ]
        }
        mock_pinecone.return_value = mock_pc_client
        
        retriever = PDPRetriever()
        results = retriever.search("test query")
        
        assert len(results) == 1
        assert results[0].id == "pasal_1"
        assert results[0].score == 0.95
    
    @patch('src.rag.retriever.get_embedding_client')
    @patch('src.rag.retriever.get_pinecone_client')
    def test_search_with_filter(self, mock_pinecone, mock_embedding):
        """Test search dengan filter."""
        from src.rag.retriever import PDPRetriever
        
        mock_embed_client = Mock()
        mock_embed_client.embed_text.return_value = [0.1] * 1536
        mock_embedding.return_value = mock_embed_client
        
        mock_pc_client = Mock()
        mock_pc_client.query.return_value = {"matches": []}
        mock_pinecone.return_value = mock_pc_client
        
        retriever = PDPRetriever()
        retriever.search("test", filter_type="pasal", filter_bab="I")
        
        # Verify filter was passed
        call_args = mock_pc_client.query.call_args
        assert call_args[1]["filter"] is not None
    
    @patch('src.rag.retriever.get_embedding_client')
    @patch('src.rag.retriever.get_pinecone_client')
    def test_build_context(self, mock_pinecone, mock_embedding):
        """Test build_context dari results."""
        from src.rag.retriever import PDPRetriever, RetrievalResult
        
        mock_embedding.return_value = Mock()
        mock_pinecone.return_value = Mock()
        
        retriever = PDPRetriever()
        
        results = [
            RetrievalResult(
                id="1",
                score=0.9,
                content="Content 1",
                metadata={"full_reference": "Pasal 1"}
            ),
            RetrievalResult(
                id="2",
                score=0.8,
                content="Content 2",
                metadata={"full_reference": "Pasal 2"}
            )
        ]
        
        context = retriever.build_context(results)
        
        assert "Pasal 1" in context
        assert "Content 1" in context
        assert "Pasal 2" in context
        assert "Content 2" in context
        assert "---" in context  # Separator


class TestEmbeddingClient:
    """Tests untuk EmbeddingClient (Gemini)."""
    
    @patch('src.rag.embeddings.genai')
    def test_embed_text(self, mock_genai):
        """Test embed_text single text."""
        from src.rag.embeddings import EmbeddingClient
        
        # Mock response
        mock_genai.embed_content.return_value = {'embedding': [0.1] * 768}
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = EmbeddingClient()
            embedding = client.embed_text("test text")
        
        assert len(embedding) == 768
    
    @patch('src.rag.embeddings.genai')
    def test_get_dimension(self, mock_genai):
        """Test get_dimension untuk Gemini model."""
        from src.rag.embeddings import EmbeddingClient
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = EmbeddingClient()
            # Gemini text-embedding-004 returns 768 dimensions
            assert client.get_dimension() == 768
    
    @patch('src.rag.embeddings.genai')
    def test_embed_query(self, mock_genai):
        """Test embed_query untuk retrieval query."""
        from src.rag.embeddings import EmbeddingClient
        
        mock_genai.embed_content.return_value = {'embedding': [0.2] * 768}
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = EmbeddingClient()
            embedding = client.embed_query("test query")
        
        assert len(embedding) == 768
        # Verify task_type is retrieval_query
        mock_genai.embed_content.assert_called_with(
            model=client.model,
            content="test query",
            task_type="retrieval_query"
        )


class TestPineconeClient:
    """Tests untuk PineconeClient."""
    
    @patch('src.rag.pinecone_client.Pinecone')
    def test_init_with_api_key(self, mock_pinecone):
        """Test initialization dengan API key."""
        from src.rag.pinecone_client import PineconeClient
        
        client = PineconeClient(api_key="test-key", index_name="test-index")
        
        assert client.api_key == "test-key"
        assert client.index_name == "test-index"
    
    @patch('src.rag.pinecone_client.Pinecone')
    def test_query(self, mock_pinecone):
        """Test query vectors."""
        from src.rag.pinecone_client import PineconeClient
        
        mock_index = Mock()
        mock_index.query.return_value = {"matches": []}
        
        mock_pc = Mock()
        mock_pc.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc
        
        client = PineconeClient(api_key="test-key")
        result = client.query(vector=[0.1] * 1536, top_k=5)
        
        assert "matches" in result
        mock_index.query.assert_called_once()
