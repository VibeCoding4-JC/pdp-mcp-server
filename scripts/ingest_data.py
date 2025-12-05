"""
Script untuk ingest data ke Pinecone vector database.
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.embeddings import EmbeddingClient
from src.rag.pinecone_client import PineconeClient
from dotenv import load_dotenv

load_dotenv()


def load_knowledge_base(json_path: str) -> dict:
    """
    Load knowledge base dari JSON file.
    
    Args:
        json_path: Path ke file JSON
        
    Returns:
        Knowledge base dictionary
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def prepare_vectors(
    knowledge_base: dict,
    embedding_client: EmbeddingClient
) -> list[dict]:
    """
    Prepare vectors untuk di-upsert ke Pinecone.
    
    Args:
        knowledge_base: Knowledge base dictionary
        embedding_client: Embedding client instance
        
    Returns:
        List of vectors ready for upsert
    """
    vectors = []
    pasal_list = knowledge_base.get("pasal", [])
    
    print(f"Generating embeddings for {len(pasal_list)} pasal...")
    
    # Prepare texts for batch embedding
    texts = []
    for pasal in pasal_list:
        # Gunakan content_with_context jika ada, otherwise content
        text = pasal.get("content_with_context", pasal.get("content", ""))
        texts.append(text)
    
    # Generate embeddings in batch
    embeddings = embedding_client.embed_batch(texts)
    
    # Create vectors with metadata
    for i, pasal in enumerate(pasal_list):
        vector = {
            "id": pasal["id"],
            "values": embeddings[i],
            "metadata": {
                "bab": pasal.get("bab", ""),
                "bab_title": pasal.get("bab_title", ""),
                "pasal": pasal.get("pasal", ""),
                "content": pasal.get("content", "")[:1000],  # Limit metadata size
                "full_reference": pasal.get("full_reference", ""),
                "type": "pasal"
            }
        }
        vectors.append(vector)
    
    # Process definisi if any
    definisi_list = knowledge_base.get("definisi", [])
    if definisi_list:
        print(f"Generating embeddings for {len(definisi_list)} definisi...")
        
        def_texts = []
        for definisi in definisi_list:
            text = f"{definisi['istilah']}: {definisi['definisi']}"
            def_texts.append(text)
        
        def_embeddings = embedding_client.embed_batch(def_texts)
        
        for i, definisi in enumerate(definisi_list):
            vector = {
                "id": definisi["id"],
                "values": def_embeddings[i],
                "metadata": {
                    "istilah": definisi.get("istilah", ""),
                    "definisi": definisi.get("definisi", "")[:1000],
                    "sumber": definisi.get("sumber", ""),
                    "type": "definisi"
                }
            }
            vectors.append(vector)
    
    return vectors


def main():
    """Main function untuk ingest data ke Pinecone."""
    # Paths
    script_dir = Path(__file__).parent.parent
    json_path = script_dir / "src" / "data" / "pdp_knowledge.json"
    
    print("=" * 50)
    print("PDP Knowledge Base Ingestion")
    print("=" * 50)
    
    # Check if knowledge base exists
    if not json_path.exists():
        print(f"Error: Knowledge base not found at {json_path}")
        print("Please run extract_pdf.py first.")
        return
    
    # Load knowledge base
    print(f"\n📚 Loading knowledge base from {json_path}...")
    knowledge_base = load_knowledge_base(str(json_path))
    print(f"   - Pasal: {len(knowledge_base.get('pasal', []))}")
    print(f"   - Definisi: {len(knowledge_base.get('definisi', []))}")
    
    # Initialize clients
    print("\n🔧 Initializing clients...")
    try:
        embedding_client = EmbeddingClient()
        print("   ✅ Embedding client ready")
    except ValueError as e:
        print(f"   ❌ Embedding client error: {e}")
        print("   Please set OPENAI_API_KEY in .env file")
        return
    
    try:
        pinecone_client = PineconeClient()
        print("   ✅ Pinecone client ready")
    except ValueError as e:
        print(f"   ❌ Pinecone client error: {e}")
        print("   Please set PINECONE_API_KEY in .env file")
        return
    
    # Create index if not exists
    print("\n📦 Checking Pinecone index...")
    pinecone_client.create_index_if_not_exists(
        dimension=embedding_client.get_dimension(),
        metric="cosine"
    )
    
    # Prepare vectors
    print("\n🔄 Preparing vectors...")
    vectors = prepare_vectors(knowledge_base, embedding_client)
    print(f"   Total vectors: {len(vectors)}")
    
    # Upsert to Pinecone
    print("\n📤 Upserting to Pinecone...")
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        pinecone_client.upsert_vectors(batch)
        print(f"   Uploaded batch {i // batch_size + 1}/{(len(vectors) - 1) // batch_size + 1}")
    
    # Verify
    print("\n📊 Verifying upload...")
    stats = pinecone_client.get_stats()
    print(f"   Index stats: {stats}")
    
    print("\n✅ Ingestion complete!")
    print(f"   Total vectors in index: {stats.get('total_vector_count', 'N/A')}")


if __name__ == "__main__":
    main()
