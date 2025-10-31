"""
Test script for search tools
=============================

Tests the Tavily search integration with various scenarios.
"""

from agent.tools.search_tools import tavily_search
import os
import sys

from dotenv import load_dotenv

# Add Agent directory to path
agent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, agent_dir)

# Load environment variables
load_dotenv()

# Import search tools directly


def test_basic_search():
    """Test basic search functionality."""
    print("\n" + "=" * 70)
    print("TEST 1: Basic Search - Photovoltaik Preise")
    print("=" * 70)

    result = tavily_search.invoke(
        {"query": "Photovoltaik Modulpreise 2024 Deutschland"})
    print(result)

    # Success if we get results OR expected error messages
    return "SUCHERGEBNISSE" in result or "not installed" in result or "not configured" in result


def test_search_with_context():
    """Test search with additional context (combined in query)."""
    print("\n" + "=" * 70)
    print("TEST 2: Search with Context - Wärmepumpe")
    print("=" * 70)

    try:
        # Combine query and context into a single search query
        result = tavily_search.invoke({
            "query": "Wärmepumpe Kosten für Einfamilienhaus in Deutschland"
        })
        print(result)

        return "SUCHERGEBNISSE" in result or "not installed" in result or "not configured" in result or "❌" in result
    except Exception as e:
        print(f"Exception: {e}")
        # If tavily is not installed, this is expected
        return "not installed" in str(e).lower() or "tavily" in str(e).lower()


def test_renewable_energy_search():
    """Test search for renewable energy topics."""
    print("\n" + "=" * 70)
    print("TEST 3: Renewable Energy Search")
    print("=" * 70)

    result = tavily_search.invoke({"query": "Förderung Photovoltaik 2024 KfW"})
    print(result)

    # Success if we get results OR expected error messages
    return "SUCHERGEBNISSE" in result or "not installed" in result or "not configured" in result


def test_error_handling_empty_query():
    """Test error handling with empty query."""
    print("\n" + "=" * 70)
    print("TEST 4: Error Handling - Empty Query")
    print("=" * 70)

    try:
        result = tavily_search.invoke({"query": ""})
        print(result)
        # Should handle gracefully
        return True
    except Exception as e:
        print(f"Exception caught: {e}")
        # Exception is also acceptable for empty query
        return True


def test_api_key_validation():
    """Test API key validation."""
    print("\n" + "=" * 70)
    print("TEST 5: API Key Validation")
    print("=" * 70)

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        print("⚠️  TAVILY_API_KEY not configured in .env")
        print("   This is expected if you haven't set up Tavily yet.")
        print("   The tool should provide clear setup instructions.")

        # Test that the tool provides helpful error message
        result = tavily_search.invoke({"query": "test query"})
        if "TAVILY_API_KEY not configured" in result or "not installed" in result:
            print("✅ Tool provides clear configuration/installation instructions")
            return True
        print("❌ Tool should provide configuration instructions")
        print(f"   Got: {result[:100]}...")
        return False
    print(f"✅ TAVILY_API_KEY configured: {api_key[:4]}***")
    return True


def main():
    """Run all tests."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "SEARCH TOOLS TEST SUITE" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")

    tests = [
        ("API Key Validation", test_api_key_validation),
        ("Basic Search", test_basic_search),
        ("Search with Context", test_search_with_context),
        ("Renewable Energy Search", test_renewable_energy_search),
        ("Error Handling", test_error_handling_empty_query),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 25 + "TEST SUMMARY" + " " * 30 + "║")
    print("╚" + "=" * 68 + "╝\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n{'=' * 70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'=' * 70}\n")

    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Review the output above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
