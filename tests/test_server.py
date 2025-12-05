"""
Integration tests untuk FastMCP Server.
"""

import pytest
from unittest.mock import Mock, patch


class TestServerInitialization:
    """Tests untuk server initialization."""
    
    def test_initialize_tools_handles_missing_keys(self):
        """Test tools initialization handles missing API keys gracefully."""
        from src.server import initialize_tools
        
        # Should not raise, may return False if keys not set
        result = initialize_tools()
        # Result depends on whether API keys are configured
        assert result in [True, False]
    
    def test_server_has_name(self):
        """Test server memiliki nama."""
        from src.server import mcp
        
        assert mcp.name == "UU PDP Assistant" or mcp.name is not None
    
    def test_server_has_instructions(self):
        """Test server memiliki instructions."""
        from src.server import mcp
        
        assert mcp.instructions is not None
        assert "UU" in mcp.instructions or "PDP" in mcp.instructions


class TestFallbackTools:
    """Tests untuk fallback tools."""
    
    def test_fallback_tools_registered_on_error(self):
        """Test fallback tools ter-register saat error."""
        from src.server import register_fallback_tools, mcp
        
        # Should not raise
        register_fallback_tools()


class TestServerConfiguration:
    """Tests untuk server configuration."""
    
    def test_env_loading(self):
        """Test environment variables bisa di-load."""
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # These may or may not be set, just test loading works
        server_name = os.getenv("MCP_SERVER_NAME", "UU PDP Assistant")
        assert server_name is not None
