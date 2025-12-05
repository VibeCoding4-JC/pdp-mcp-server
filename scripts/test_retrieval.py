"""
Script untuk testing retrieval dari Pinecone.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.retriever import PDPRetriever
from dotenv import load_dotenv

load_dotenv()


def test_queries():
    """Test berbagai query terhadap knowledge base."""
    
    print("=" * 60)
    print("PDP Retrieval Test")
    print("=" * 60)
    
    try:
        retriever = PDPRetriever()
        print("✅ Retriever initialized\n")
    except Exception as e:
        print(f"❌ Error initializing retriever: {e}")
        return
    
    # Test queries
    test_cases = [
        {
            "query": "Apa yang dimaksud dengan data pribadi?",
            "description": "Definisi data pribadi"
        },
        {
            "query": "Apa saja hak-hak subjek data pribadi?",
            "description": "Hak subjek data"
        },
        {
            "query": "Bagaimana sanksi pidana pelanggaran data pribadi?",
            "description": "Sanksi pidana"
        },
        {
            "query": "Apa kewajiban pengendali data pribadi?",
            "description": "Kewajiban pengendali"
        },
        {
            "query": "Bagaimana transfer data pribadi ke luar negeri?",
            "description": "Transfer data lintas batas"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {test['description']}")
        print(f"Query: {test['query']}")
        print("-" * 60)
        
        try:
            context, results = retriever.get_context_for_query(
                test["query"],
                top_k=3
            )
            
            print(f"Found {len(results)} results:")
            for j, result in enumerate(results, 1):
                print(f"\n  [{j}] Score: {result.score:.4f}")
                print(f"      Ref: {result.metadata.get('full_reference', 'N/A')}")
                print(f"      Content: {result.content[:150]}...")
            
            print(f"\n📝 Built Context ({len(context)} chars):")
            print(context[:500] + "..." if len(context) > 500 else context)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_queries()
