"""
Test Telephony Tools
====================

Simple tests to verify telephony tools functionality.
"""

from agent.tools.telephony_tools import (
    CallTranscript,
    get_telephony_tools,
)
from agent.tools.call_protocol import (
    CallProtocolManager,
    format_protocol_guide,
    get_call_protocol,
    handle_objection,
)
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_call_transcript():
    """Test CallTranscript dataclass."""
    from datetime import datetime

    transcript = CallTranscript(
        call_id="TEST-001",
        phone_number="+49123456789",
        goal="Test call",
        started_at=datetime.now()
    )

    # Add messages
    transcript.add_message("KAI", "Hello, this is KAI")
    transcript.add_message("CUSTOMER", "Hi, I'm interested")

    # Add notes
    transcript.add_note("Customer seems interested")

    # Set outcome
    transcript.outcome = "Consultation scheduled"
    transcript.next_steps = "Send calculation via email"

    # Get summary
    summary = transcript.get_summary()

    assert "TEST-001" in summary
    assert "+49123456789" in summary
    assert "Hello, this is KAI" in summary
    assert "Customer seems interested" in summary
    assert "Consultation scheduled" in summary

    print("✅ CallTranscript test passed")


def test_call_protocol_manager():
    """Test CallProtocolManager."""
    manager = CallProtocolManager()

    # Test get all phases
    phases = manager.get_all_phases()
    assert 'preparation' in phases
    assert 'opening' in phases
    assert 'objection_handling' in phases
    assert 'closing' in phases

    # Test get protocol
    protocol = manager.get_protocol('opening')
    assert protocol is not None
    assert protocol.phase == 'Opening & Rapport Building'
    assert len(protocol.strategies) > 0
    assert len(protocol.key_points) > 0

    print("✅ CallProtocolManager test passed")


def test_protocol_functions():
    """Test protocol helper functions."""

    # Test get_call_protocol
    protocol = get_call_protocol('objection_handling')
    assert protocol is not None
    assert 'Objection Handling' in protocol.phase

    # Test format_protocol_guide
    guide = format_protocol_guide('presentation')
    assert 'CALL PROTOCOL' in guide
    assert 'OBJECTIVE' in guide
    assert 'STRATEGIES' in guide

    # Test handle_objection
    response = handle_objection('Das ist zu teuer')
    assert 'OBJECTION DETECTED' in response
    assert 'VALIDATE' in response

    print("✅ Protocol functions test passed")


def test_telephony_tools_list():
    """Test that telephony tools are available."""
    tools = get_telephony_tools()

    assert len(tools) > 0

    # Check for core tools
    tool_names = [tool.name for tool in tools]
    assert 'start_interactive_call' in tool_names
    assert 'update_call_summary' in tool_names
    assert 'continue_call_conversation' in tool_names
    assert 'end_call' in tool_names

    # Check for protocol tools
    assert 'get_call_protocol_guide' in tool_names
    assert 'handle_customer_objection' in tool_names

    print(f"✅ Telephony tools test passed ({len(tools)} tools available)")


def test_objection_handling():
    """Test objection handling logic."""
    manager = CallProtocolManager()

    # Test common objections
    objections = [
        'Das ist zu teuer',
        'Ich habe keine Zeit',
        'Mein Dach ist nicht geeignet',
    ]

    for objection in objections:
        response = manager.get_objection_response(objection)
        if response:
            assert len(response) > 0
            print(f"  ✓ Found response for: {objection}")

    print("✅ Objection handling test passed")


def test_argument_structure():
    """Test argument structure building."""
    manager = CallProtocolManager()

    customer_need = "Reduce energy costs"
    facts = [
        "Average savings of 40% on electricity bills",
        "Payback period of 8-10 years",
        "25-year warranty on modules",
    ]

    argument = manager.build_argument_structure(customer_need, facts)

    assert customer_need in argument
    assert "DATA-DRIVEN ARGUMENT" in argument
    assert facts[0] in argument

    print("✅ Argument structure test passed")


def test_closing_statement():
    """Test closing statement generation."""
    manager = CallProtocolManager()

    summary = "We discussed a 10kW system with battery storage"
    next_step = "Send detailed calculation and schedule site visit"

    closing = manager.generate_closing_statement(summary, next_step)

    assert summary in closing
    assert next_step in closing
    assert "Vielen Dank" in closing

    print("✅ Closing statement test passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TELEPHONY TOOLS TEST SUITE")
    print("=" * 60 + "\n")

    try:
        test_call_transcript()
        test_call_protocol_manager()
        test_protocol_functions()
        test_telephony_tools_list()
        test_objection_handling()
        test_argument_structure()
        test_closing_statement()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
