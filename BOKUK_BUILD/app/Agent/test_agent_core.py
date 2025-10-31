"""
Test Agent Core Implementation
===============================

Tests for the AgentCore class to verify proper initialization and execution.
"""

from Agent.agent.tools.knowledge_tools import setup_knowledge_base
from Agent.agent.errors import ConfigurationError
from Agent.agent.agent_core import AgentCore
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_agent_initialization():
    """Test that AgentCore initializes correctly."""
    print("\n" + "=" * 80)
    print("TEST 1: Agent Initialization")
    print("=" * 80)

    try:
        # Set up knowledge base
        print("Setting up knowledge base...")
        vector_store = setup_knowledge_base()

        # Initialize agent
        print("Initializing AgentCore...")
        agent = AgentCore(vector_store)

        print("✅ Agent initialized successfully")
        print(f"   - Model: {agent.llm.model_name}")
        print(f"   - Tools registered: {len(agent.tools)}")
        print(f"   - Tool names: {', '.join(agent.get_tool_names())}")

        return True

    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease ensure OPENAI_API_KEY is set in your .env file")
        return False
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_status():
    """Test agent status reporting."""
    print("\n" + "=" * 80)
    print("TEST 2: Agent Status")
    print("=" * 80)

    try:
        vector_store = setup_knowledge_base()
        agent = AgentCore(vector_store)

        status = agent.get_status()

        print("Agent Status:")
        for key, value in status.items():
            if key == 'tools':
                print(f"  - {key}:")
                for tool in value:
                    print(f"      • {tool}")
            else:
                print(f"  - {key}: {value}")

        print("✅ Status retrieved successfully")
        return True

    except Exception as e:
        print(f"❌ Status test failed: {e}")
        return False


def test_simple_task():
    """Test agent with a simple task."""
    print("\n" + "=" * 80)
    print("TEST 3: Simple Task Execution")
    print("=" * 80)

    try:
        vector_store = setup_knowledge_base()
        agent = AgentCore(vector_store)

        # Simple task: list files in workspace
        task = "List all files in the agent workspace directory"
        print(f"\nTask: {task}\n")

        result = agent.run(task)

        if result['success']:
            print("\n✅ Task completed successfully")
            print(f"   - Execution time: {result['execution_time']:.2f}s")
            print(f"   - Output preview: {result['output'][:200]}...")
            return True
        print(f"\n❌ Task failed: {result.get('error', 'Unknown error')}")
        if 'solution' in result:
            print(f"   Solution: {result['solution']}")
        return False

    except Exception as e:
        print(f"❌ Task execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_management():
    """Test conversation memory."""
    print("\n" + "=" * 80)
    print("TEST 4: Memory Management")
    print("=" * 80)

    try:
        vector_store = setup_knowledge_base()
        agent = AgentCore(vector_store)

        # Check initial memory
        status_before = agent.get_status()
        print(f"Memory messages before: {status_before['memory_messages']}")

        # Clear memory
        agent.clear_memory()

        status_after = agent.get_status()
        print(
            f"Memory messages after clear: {
                status_after['memory_messages']}")

        print("✅ Memory management working correctly")
        return True

    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("KAI AGENT CORE TEST SUITE")
    print("=" * 80)

    tests = [
        test_agent_initialization,
        test_agent_status,
        test_memory_management,
        test_simple_task,  # Run this last as it takes longer
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ All tests passed!")
    else:
        print(f"❌ {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
