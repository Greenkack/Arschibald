"""
Test Call Protocol Logic - Task 5.2 Verification
=================================================

Verifies that all call protocol requirements are implemented:
- Knowledge preparation step
- Argument structure building
- Objection handling logic
- Closing and next-step generation

Requirements: 4.2, 4.3, 4.4
"""

from agent.tools.call_protocol import (
    CallProtocolManager,
    build_argument_structure,
    generate_closing_statement,
    get_call_protocol,
    handle_objection,
)
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_knowledge_preparation_step():
    """Test knowledge preparation protocol exists."""
    print("\n1. Testing Knowledge Preparation Step...")

    protocol = get_call_protocol('preparation')
    assert protocol is not None, "Preparation protocol not found"
    assert protocol.phase == 'Knowledge Preparation'
    assert 'Search knowledge base' in protocol.strategies[0]
    assert len(protocol.key_points) >= 3

    print("   ✅ Knowledge preparation protocol implemented")
    print(f"   - Strategies: {len(protocol.strategies)}")
    print(f"   - Key points: {len(protocol.key_points)}")


def test_argument_structure_building():
    """Test argument structure building logic."""
    print("\n2. Testing Argument Structure Building...")

    customer_need = "Reduce monthly energy costs"
    facts = [
        "Average 40% reduction in electricity bills",
        "Payback period of 8-10 years",
        "25-year warranty on solar modules"
    ]

    argument = build_argument_structure(customer_need, facts)

    assert customer_need in argument
    assert "DATA-DRIVEN ARGUMENT" in argument
    assert facts[0] in argument
    assert "VALIDATE THE NEED" in argument
    assert "PRESENT SOLUTION" in argument

    print("   ✅ Argument structure building implemented")
    print(f"   - Customer need addressed: '{customer_need}'")
    print(f"   - Facts integrated: {len(facts)}")


def test_objection_handling_logic():
    """Test objection handling logic."""
    print("\n3. Testing Objection Handling Logic...")

    # Test common objections
    objections = [
        ('Das ist zu teuer', 'Investition'),
        ('Ich habe keine Zeit', 'Zeit'),
        ('Mein Dach ist nicht geeignet', 'Dach'),
        ('Die Technik ist noch nicht ausgereift', 'Technik'),
    ]

    handled_count = 0
    for objection, keyword in objections:
        response = handle_objection(objection)
        assert response is not None
        assert "OBJECTION DETECTED" in response
        assert "VALIDATE" in response
        assert "CLARIFY" in response
        assert "RESPOND" in response
        assert "CONFIRM" in response
        handled_count += 1

    print("   ✅ Objection handling logic implemented")
    print(f"   - Objections handled: {handled_count}")
    print("   - 4-step process: VALIDATE → CLARIFY → RESPOND → CONFIRM")


def test_closing_and_next_steps():
    """Test closing statement generation."""
    print("\n4. Testing Closing and Next-Step Generation...")

    call_summary = "Discussed 10kW PV system with battery storage"
    next_step = "Send detailed calculation and schedule site visit"

    closing = generate_closing_statement(call_summary, next_step)

    assert call_summary in closing
    assert next_step in closing
    assert "Vielen Dank" in closing or "zusammenfassen" in closing

    print("   ✅ Closing statement generation implemented")
    print("   - Summary included: Yes")
    print("   - Next steps included: Yes")


def test_all_call_phases():
    """Test all call phases are implemented."""
    print("\n5. Testing All Call Phases...")

    manager = CallProtocolManager()
    phases = manager.get_all_phases()

    required_phases = [
        'preparation',
        'opening',
        'discovery',
        'presentation',
        'objection_handling',
        'closing'
    ]

    for phase in required_phases:
        assert phase in phases, f"Missing phase: {phase}"
        protocol = manager.get_protocol(phase)
        assert protocol is not None
        assert len(protocol.strategies) > 0
        assert len(protocol.key_points) > 0

    print("   ✅ All call phases implemented")
    print(f"   - Total phases: {len(phases)}")
    for phase in phases:
        protocol = manager.get_protocol(phase)
        print(f"   - {phase}: {protocol.objective}")


def test_objection_handling_protocol():
    """Test objection handling protocol has comprehensive responses."""
    print("\n6. Testing Objection Handling Protocol...")

    protocol = get_call_protocol('objection_handling')
    assert protocol is not None
    assert len(protocol.common_objections) >= 3

    # Verify each objection has both question and response
    for obj in protocol.common_objections:
        assert 'objection' in obj
        assert 'response' in obj
        assert len(obj['response']) > 50  # Substantial response

    print("   ✅ Objection handling protocol comprehensive")
    print(f"   - Common objections: {len(protocol.common_objections)}")


def run_all_tests():
    """Run all call protocol tests."""
    print("\n" + "=" * 60)
    print("CALL PROTOCOL LOGIC TEST SUITE - TASK 5.2")
    print("=" * 60)

    try:
        test_knowledge_preparation_step()
        test_argument_structure_building()
        test_objection_handling_logic()
        test_closing_and_next_steps()
        test_all_call_phases()
        test_objection_handling_protocol()

        print("\n" + "=" * 60)
        print("✅ ALL TASK 5.2 REQUIREMENTS VERIFIED")
        print("=" * 60)
        print("\nImplemented:")
        print("  ✓ Knowledge preparation step")
        print("  ✓ Argument structure building")
        print("  ✓ Objection handling logic")
        print("  ✓ Closing and next-step generation")
        print("\n" + "=" * 60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
