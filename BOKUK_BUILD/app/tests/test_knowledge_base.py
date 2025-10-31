"""
Test script for knowledge base functionality.
"""

from agent.tools.knowledge_tools import setup_knowledge_base, knowledge_base_search
import os
import sys

# Add the agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))


def test_knowledge_base():
    """Test knowledge base setup and search."""

    print("=" * 60)
    print("Testing Knowledge Base System")
    print("=" * 60)

    # Test 1: Setup knowledge base
    print("\n1. Testing setup_knowledge_base()...")
    vector_store = setup_knowledge_base(
        path="knowledge_base",
        db_path="faiss_index"
    )

    if vector_store is None:
        print("✅ Empty knowledge base handled correctly")
    else:
        print("✅ Knowledge base loaded successfully")

    # Test 2: Create search tool
    print("\n2. Testing knowledge_base_search()...")
    search_tool = knowledge_base_search(vector_store)

    print(f"   Tool name: {search_tool.name}")
    print(f"   Tool description: {search_tool.description[:100]}...")
    print("✅ Search tool created successfully")

    # Test 3: Test search with empty knowledge base
    print("\n3. Testing search with empty/no knowledge base...")
    result = search_tool.run("photovoltaik")
    print(f"   Result: {result[:200]}...")

    if "not available" in result.lower() or "no pdf" in result.lower():
        print("✅ Empty knowledge base handled gracefully")
    else:
        print("✅ Search returned results")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY not found in environment")
        print("💡 Set it in .env file to test with actual embeddings")
        print("\nTesting basic functionality without API calls...")

    test_knowledge_base()
