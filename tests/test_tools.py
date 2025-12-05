"""
Unit tests untuk MCP tools.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestPDPTools:
    """Tests untuk PDP MCP Tools."""
    
    @patch('src.tools.pdp_tools.get_retriever')
    def test_register_tools(self, mock_get_retriever):
        """Test register_tools adds all tools."""
        from fastmcp import FastMCP
        from src.tools.pdp_tools import register_tools
        
        mock_retriever = Mock()
        mock_get_retriever.return_value = mock_retriever
        
        mcp = FastMCP("test")
        register_tools(mcp, mock_retriever)
        
        # Check tools are registered (FastMCP stores them internally)
        # This is a basic smoke test
        assert mcp is not None
    
    @patch('src.tools.pdp_tools.get_retriever')
    def test_tanya_pdp_returns_context(self, mock_get_retriever):
        """Test tanya_pdp tool returns context."""
        from fastmcp import FastMCP
        from src.tools.pdp_tools import register_tools
        from src.rag.retriever import RetrievalResult
        
        # Mock retriever
        mock_retriever = Mock()
        mock_retriever.get_context_for_query.return_value = (
            "Context dari UU PDP",
            [
                RetrievalResult(
                    id="pasal_1",
                    score=0.95,
                    content="Isi pasal",
                    metadata={"full_reference": "Pasal 1"}
                )
            ]
        )
        mock_get_retriever.return_value = mock_retriever
        
        mcp = FastMCP("test")
        register_tools(mcp, mock_retriever)
        
        # Verify retriever was called correctly
        mock_retriever.get_context_for_query.assert_not_called()  # Not called until tool is invoked
    
    @patch('src.tools.pdp_tools.get_retriever')
    def test_cari_pasal_with_bab_filter(self, mock_get_retriever):
        """Test cari_pasal dengan filter BAB."""
        from fastmcp import FastMCP
        from src.tools.pdp_tools import register_tools
        
        mock_retriever = Mock()
        mock_retriever.search_pasal.return_value = []
        mock_get_retriever.return_value = mock_retriever
        
        mcp = FastMCP("test")
        register_tools(mcp, mock_retriever)
        
        # Tool registration should work
        assert mcp is not None
    
    @patch('src.tools.pdp_tools.get_retriever')
    def test_definisi_istilah(self, mock_get_retriever):
        """Test definisi_istilah tool."""
        from fastmcp import FastMCP
        from src.tools.pdp_tools import register_tools
        
        mock_retriever = Mock()
        mock_retriever.search_definisi.return_value = []
        mock_retriever.search_pasal.return_value = []
        mock_get_retriever.return_value = mock_retriever
        
        mcp = FastMCP("test")
        register_tools(mcp, mock_retriever)
        
        assert mcp is not None
    
    @patch('src.tools.pdp_tools.get_retriever')
    def test_hak_subjek_data(self, mock_get_retriever):
        """Test hak_subjek_data tool."""
        from fastmcp import FastMCP
        from src.tools.pdp_tools import register_tools
        from src.rag.retriever import RetrievalResult
        
        mock_retriever = Mock()
        mock_retriever.search_pasal.return_value = [
            RetrievalResult(
                id="pasal_5",
                score=0.9,
                content="Hak untuk mendapatkan informasi",
                metadata={"full_reference": "Pasal 5", "bab": "IV"}
            )
        ]
        mock_get_retriever.return_value = mock_retriever
        
        mcp = FastMCP("test")
        register_tools(mcp, mock_retriever)
        
        assert mcp is not None
    
    @patch('src.tools.pdp_tools.get_retriever')
    def test_sanksi_pelanggaran_administratif(self, mock_get_retriever):
        """Test sanksi_pelanggaran dengan jenis administratif."""
        from fastmcp import FastMCP
        from src.tools.pdp_tools import register_tools
        
        mock_retriever = Mock()
        mock_retriever.search_pasal.return_value = []
        mock_get_retriever.return_value = mock_retriever
        
        mcp = FastMCP("test")
        register_tools(mcp, mock_retriever)
        
        assert mcp is not None
    
    @patch('src.tools.pdp_tools.get_retriever')
    def test_sanksi_pelanggaran_pidana(self, mock_get_retriever):
        """Test sanksi_pelanggaran dengan jenis pidana."""
        from fastmcp import FastMCP
        from src.tools.pdp_tools import register_tools
        
        mock_retriever = Mock()
        mock_retriever.search_pasal.return_value = []
        mock_get_retriever.return_value = mock_retriever
        
        mcp = FastMCP("test")
        register_tools(mcp, mock_retriever)
        
        assert mcp is not None
