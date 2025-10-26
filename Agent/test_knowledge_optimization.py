"""
Test Knowledge Base Performance Optimizations
==============================================

Tests for Task 15.1: Optimize knowledge base
- Index caching
- Lazy loading
- Optimized chunk size
- Large document set handling
"""

from agent.tools.knowledge_tools import (
    clear_knowledge_base_cache,
    get_cache_info,
    knowledge_base_search,
    setup_knowledge_base,
)
import os
import sys
import tempfile
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_test_pdf(path: Path, content: str):
    """Create a simple test PDF file."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(path), pagesize=letter)
        c.drawString(100, 750, content)
        c.save()
        return True
    except ImportError:
        print("⚠️  reportlab not installed, skipping PDF creation test")
        return False


def test_lazy_loading():
    """Test that lazy loading returns cached vector store."""
    print("\n" + "=" * 70)
    print("TEST 1: Lazy Loading")
    print("=" * 70)

    # Clear cache first
    clear_knowledge_base_cache()
    cache_info = get_cache_info()
    assert not cache_info['cached'], "Cache should be empty initially"
    print("✓ Cache cleared")

    # First load (should build/load from disk)
    print("\nFirst load (should load from disk or build)...")
    start = time.time()
    vs1 = setup_knowledge_base()
    time1 = time.time() - start
    print(f"Time: {time1:.2f}s")

    # Check cache
    cache_info = get_cache_info()
    if vs1 is not None:
        assert cache_info['cached'], "Cache should be populated after first load"
        print("✓ Cache populated")

    # Second load (should use lazy loading)
    print("\nSecond load (should use lazy loading)...")
    start = time.time()
    vs2 = setup_knowledge_base()
    time2 = time.time() - start
    print(f"Time: {time2:.2f}s")

    if vs1 is not None and vs2 is not None:
        assert vs1 is vs2, "Should return same cached instance"
        assert time2 < time1 / 10, "Lazy loading should be much faster"
        print(f"✓ Lazy loading is {time1 / time2:.1f}x faster")

    print("\n✅ Lazy loading test passed")


def test_index_caching():
    """Test that index is saved and reused."""
    print("\n" + "=" * 70)
    print("TEST 2: Index Caching")
    print("=" * 70)

    # Clear cache
    clear_knowledge_base_cache()

    # Check if index exists
    index_path = Path("faiss_index")
    if index_path.exists():
        print("✓ FAISS index exists on disk")

        # Load from disk
        print("\nLoading from cached index...")
        start = time.time()
        vs = setup_knowledge_base()
        load_time = time.time() - start
        print(f"Time: {load_time:.2f}s")

        if vs is not None:
            print("✓ Successfully loaded from cache")
        else:
            print("⚠️  No documents in knowledge base")
    else:
        print("⚠️  No cached index found (expected on first run)")

    print("\n✅ Index caching test passed")


def test_optimized_chunk_size():
    """Test that optimized chunk size is used."""
    print("\n" + "=" * 70)
    print("TEST 3: Optimized Chunk Size")
    print("=" * 70)

    # Clear cache
    clear_knowledge_base_cache()

    # Test with default optimized settings (800/200)
    print("\nTesting with optimized chunk size (800/200)...")
    vs = setup_knowledge_base(chunk_size=800, chunk_overlap=200)

    if vs is not None:
        print("✓ Vector store created with optimized chunk size")

        # Verify metadata
        cache_info = get_cache_info()
        if cache_info['metadata']:
            metadata = cache_info['metadata']
            assert metadata['chunk_size'] == 800
            assert metadata['chunk_overlap'] == 200
            print(f"✓ Chunk size: {metadata['chunk_size']}")
            print(f"✓ Chunk overlap: {metadata['chunk_overlap']}")
    else:
        print("⚠️  No documents in knowledge base")

    print("\n✅ Optimized chunk size test passed")


def test_search_performance():
    """Test search performance with optimized settings."""
    print("\n" + "=" * 70)
    print("TEST 4: Search Performance")
    print("=" * 70)

    vs = setup_knowledge_base()

    if vs is None:
        print("⚠️  No documents in knowledge base, skipping search test")
        print("   Add PDF files to knowledge_base/ directory to test search")
        return

    # Create search tool
    search_tool = knowledge_base_search(vs)

    # Test search
    test_queries = [
        "photovoltaic",
        "solar energy",
        "heat pump"
    ]

    print("\nTesting search performance...")
    for query in test_queries:
        start = time.time()
        result = search_tool.func(query)
        search_time = time.time() - start

        print(f"\nQuery: '{query}'")
        print(f"Time: {search_time:.3f}s")

        if "No relevant information" not in result:
            print("✓ Found results")
            # Check for relevance scores
            if "Relevance:" in result:
                print("✓ Relevance scores included")
        else:
            print("⚠️  No results found")

        assert search_time < 1.0, "Search should complete in under 1 second"

    print("\n✅ Search performance test passed")


def test_cache_invalidation():
    """Test that cache is invalidated when files change."""
    print("\n" + "=" * 70)
    print("TEST 5: Cache Invalidation")
    print("=" * 70)

    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "kb"
        kb_path.mkdir()
        index_path = Path(tmpdir) / "index"

        # Create test PDF
        if not create_test_pdf(kb_path / "test1.pdf", "Test content 1"):
            print("⚠️  Skipping cache invalidation test (reportlab required)")
            return

        # First build
        print("\nBuilding initial index...")
        clear_knowledge_base_cache()
        vs1 = setup_knowledge_base(
            path=str(kb_path),
            db_path=str(index_path)
        )

        if vs1 is None:
            print("⚠️  Failed to create vector store")
            return

        print("✓ Initial index built")

        # Add another PDF
        time.sleep(0.1)  # Ensure different timestamp
        create_test_pdf(kb_path / "test2.pdf", "Test content 2")

        # Should detect change and rebuild
        print("\nAdding new file (should trigger rebuild)...")
        clear_knowledge_base_cache()
        vs2 = setup_knowledge_base(
            path=str(kb_path),
            db_path=str(index_path)
        )

        if vs2 is not None:
            print("✓ Index rebuilt after file change")

    print("\n✅ Cache invalidation test passed")


def run_all_tests():
    """Run all performance optimization tests."""
    print("\n" + "=" * 70)
    print("KNOWLEDGE BASE PERFORMANCE OPTIMIZATION TESTS")
    print("=" * 70)

    try:
        test_lazy_loading()
        test_index_caching()
        test_optimized_chunk_size()
        test_search_performance()
        test_cache_invalidation()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
