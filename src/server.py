"""
FastMCP Server untuk UU Perlindungan Data Pribadi (UU PDP).

Server ini menyediakan tools untuk menjawab pertanyaan seputar
UU No. 27 Tahun 2022 tentang Perlindungan Data Pribadi menggunakan
RAG (Retrieval-Augmented Generation) dengan Pinecone vector database.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP(
    name=os.getenv("MCP_SERVER_NAME", "UU PDP Assistant"),
    instructions="""
    Anda adalah asisten yang membantu menjawab pertanyaan tentang 
    Undang-Undang Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi (UU PDP).
    
    Gunakan tools yang tersedia untuk mencari informasi yang relevan dari UU PDP.
    Selalu berikan referensi pasal yang digunakan dalam jawaban Anda.
    Jawab dalam Bahasa Indonesia.
    
    Tools yang tersedia:
    1. tanya_pdp - Untuk pertanyaan umum tentang UU PDP
    2. cari_pasal - Untuk mencari pasal berdasarkan keyword
    3. definisi_istilah - Untuk mencari definisi istilah hukum
    4. hak_subjek_data - Untuk menjelaskan hak-hak subjek data
    5. kewajiban_pengendali - Untuk menjelaskan kewajiban pengendali data
    6. sanksi_pelanggaran - Untuk menjelaskan sanksi pelanggaran
    """
)


def initialize_tools():
    """Initialize dan register tools ke MCP server."""
    try:
        from src.tools.pdp_tools import register_tools
        from src.rag.retriever import PDPRetriever
        
        # Initialize retriever
        retriever = PDPRetriever()
        
        # Register tools
        register_tools(mcp, retriever)
        
        print("✅ Tools registered successfully")
        return True
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize tools: {e}")
        print("   Server will start without RAG capabilities.")
        print("   Make sure to set PINECONE_API_KEY and OPENAI_API_KEY in .env")
        
        # Register fallback tools
        register_fallback_tools()
        return False


def register_fallback_tools():
    """Register fallback tools jika RAG tidak tersedia."""
    
    @mcp.tool()
    def tanya_pdp(pertanyaan: str) -> str:
        """
        Menjawab pertanyaan tentang UU PDP.
        
        Args:
            pertanyaan: Pertanyaan tentang UU PDP
            
        Returns:
            Jawaban
        """
        return """
        Maaf, server belum terkonfigurasi dengan benar.
        
        Pastikan:
        1. PINECONE_API_KEY sudah diset di .env
        2. OPENAI_API_KEY sudah diset di .env
        3. Data sudah di-ingest ke Pinecone (jalankan scripts/ingest_data.py)
        
        Silakan hubungi administrator untuk bantuan.
        """
    
    @mcp.tool()
    def server_status() -> str:
        """
        Cek status server.
        
        Returns:
            Status server
        """
        return """
        Server Status: Running (Limited Mode)
        
        RAG capabilities: ❌ Not configured
        
        Untuk mengaktifkan fitur penuh:
        1. Set PINECONE_API_KEY di .env
        2. Set OPENAI_API_KEY di .env
        3. Jalankan: python scripts/ingest_data.py
        4. Restart server
        """


def main():
    """Main entry point untuk menjalankan server."""
    print("=" * 50)
    print("UU PDP MCP Server")
    print("=" * 50)
    
    # Initialize tools
    print("\n🔧 Initializing tools...")
    initialize_tools()
    
    # Run server
    print("\n🚀 Starting MCP server...")
    print(f"   Server name: {mcp.name}")
    print("\n" + "=" * 50)
    
    mcp.run()


if __name__ == "__main__":
    main()
