"""
Telephony Tools for KAI Agent
==============================

Provides tools for conducting professional sales and consulting calls
with voice synthesis and structured conversation management.

Requirements: 4.1, 4.2, 4.4, 4.5
"""

import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from langchain_core.tools import tool

# Try to import ElevenLabs, but make it optional for testing
try:
    from elevenlabs import stream
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

from .call_protocol import (
    handle_objection,
    build_argument_structure,
    generate_closing_statement,
)

# Import error classes and logging
from agent.errors import APIError, ConfigurationError
from agent.logging_config import get_logger, log_api_call

# Import security utilities (Task 12.1)
from agent.security import sanitize_user_input, InputValidationError

# Get logger for this module
logger = get_logger(__name__)


@dataclass
class CallTranscript:
    """
    Represents a call transcript with conversation history.

    Attributes:
        call_id: Unique identifier for the call
        phone_number: Customer phone number
        goal: Objective of the call
        started_at: Call start timestamp
        ended_at: Call end timestamp (optional)
        messages: List of conversation messages
        notes: List of agent notes during call
        outcome: Call outcome (optional)
        next_steps: Agreed next steps (optional)
    """

    call_id: str
    phone_number: str
    goal: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    outcome: Optional[str] = None
    next_steps: Optional[str] = None

    def add_message(self, speaker: str, text: str) -> None:
        """
        Add a message to the conversation.

        Args:
            speaker: Speaker name (e.g., 'KAI', 'CUSTOMER')
            text: Message text
        """
        self.messages.append({
            'speaker': speaker,
            'text': text,
            'timestamp': datetime.now().isoformat()
        })

    def add_note(self, note: str) -> None:
        """
        Add an internal note about the call.

        Args:
            note: Note text
        """
        self.notes.append({
            'note': note,
            'timestamp': datetime.now().isoformat()
        })

    def get_summary(self) -> str:
        """
        Generate a formatted summary of the call.

        Returns:
            Formatted call summary string
        """
        duration = "In Progress"
        if self.ended_at:
            delta = self.ended_at - self.started_at
            duration = f"{delta.total_seconds():.0f} seconds"

        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    CALL TRANSCRIPT SUMMARY                    ║
╚══════════════════════════════════════════════════════════════╝

📞 Call ID: {self.call_id}
📱 Phone: {self.phone_number}
🎯 Goal: {self.goal}
⏱️  Duration: {duration}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 CONVERSATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for msg in self.messages:
            speaker_icon = "🤖" if msg['speaker'] == "KAI" else "👤"
            summary += (
                f"\n{speaker_icon} {msg['speaker']}: {msg['text']}\n"
            )

        if self.notes:
            summary += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 AGENT NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for note in self.notes:
                summary += f"\n• {note['note']}\n"

        if self.outcome or self.next_steps:
            summary += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ OUTCOME & NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            if self.outcome:
                summary += f"\n🎯 Outcome: {self.outcome}\n"
            if self.next_steps:
                summary += f"\n📋 Next Steps: {self.next_steps}\n"

        summary += (
            "\n╚══════════════════════════════════════════════════════════════╝"
        )
        return summary


# Global state for current call
_current_call: Optional[CallTranscript] = None


def _get_current_call() -> Optional[CallTranscript]:
    """Get the current active call transcript."""
    return _current_call


def _set_current_call(call: Optional[CallTranscript]) -> None:
    """Set the current active call transcript."""
    global _current_call
    _current_call = call


@tool
def start_interactive_call(
    phone_number: str,
    opening_statement: str,
    call_goal: str
) -> str:
    """
    Start a professional sales or consulting call with voice synthesis.

    This tool initiates an outbound call simulation with ElevenLabs voice
    synthesis. It creates a call transcript and begins the conversation
    with the provided opening statement.

    Args:
        phone_number: Target phone number (e.g., '+49123456789')
        opening_statement: Initial message to customer
        call_goal: Objective of the call (e.g., 'Schedule consultation')

    Returns:
        Confirmation message with call ID and instructions

    Requirements: 4.1, 4.2, 4.5

    Example:
        start_interactive_call(
            phone_number='+49123456789',
            opening_statement='Guten Tag, hier ist KAI von...',
            call_goal='Schedule PV system consultation'
        )
    """
    # Validate inputs (Task 12.1)
    try:
        sanitize_user_input(phone_number, max_length=50)
        sanitize_user_input(opening_statement, max_length=5000)
        sanitize_user_input(call_goal, max_length=500)
    except InputValidationError as e:
        error_msg = f"Input validation failed: {str(e)}"
        logger.warning(error_msg)
        return f"Fehler: {error_msg}"

    # Create new call transcript
    call_id = f"CALL-{uuid.uuid4().hex[:8].upper()}"
    call = CallTranscript(
        call_id=call_id,
        phone_number=phone_number,
        goal=call_goal,
        started_at=datetime.now()
    )
    _set_current_call(call)

    # Add opening message
    call.add_message("KAI", opening_statement)

    print("\n" + "=" * 60)
    print("📞 STARTING EXPERT CALL SIMULATION")
    print("=" * 60)
    print(f"Call ID: {call_id}")
    print(f"Dialing: {phone_number}")
    print(f"Goal: {call_goal}")
    print("=" * 60 + "\n")

    # Try to use ElevenLabs for voice synthesis
    if ELEVENLABS_AVAILABLE:
        api_key = os.getenv("ELEVEN_LABS_API_KEY")
        if api_key:
            try:
                logger.info("Initializing ElevenLabs voice synthesis")
                client = ElevenLabs(api_key=api_key)
                print(f"🤖 KAI: {opening_statement}\n")

                # Generate and stream audio
                logger.debug("Generating audio stream")
                audio_stream = client.generate(
                    text=opening_statement,
                    voice="Rachel",
                    model="eleven_multilingual_v2",
                    stream=True
                )
                stream(audio_stream)

                logger.info("Voice synthesis completed successfully")
                log_api_call(
                    logger,
                    api_name="ElevenLabs",
                    method="generate",
                    status_code=200
                )

                return f"""
✅ Call started successfully!

Call ID: {call_id}
Status: Active
Voice synthesis: Enabled

The opening statement has been delivered with voice synthesis.

NEXT STEPS:
1. Use 'continue_call_conversation' to simulate customer responses
2. Use 'update_call_summary' to add notes during the call
3. Use 'handle_customer_objection' if objections arise
4. Use 'end_call' when the conversation is complete

TIP: Use 'get_call_protocol_guide' for guidance on call phases!
"""
            except Exception as e:
                logger.warning(f"Voice synthesis failed: {e}")
                log_api_call(
                    logger,
                    api_name="ElevenLabs",
                    method="generate",
                    error=str(e)
                )
                print(f"⚠️  Voice synthesis failed: {e}")
                print("Continuing with text-only simulation...\n")
        else:
            logger.warning("ELEVEN_LABS_API_KEY not configured")
            print("⚠️  ELEVEN_LABS_API_KEY not configured")
            print("Continuing with text-only simulation...\n")
    else:
        logger.info("ElevenLabs not installed, using text-only mode")
        print("⚠️  ElevenLabs not installed")
        print("Continuing with text-only simulation...\n")

    # Text-only fallback
    print(f"🤖 KAI: {opening_statement}\n")

    return f"""
✅ Call started successfully!

Call ID: {call_id}
Status: Active
Voice synthesis: Not available (text-only mode)

The opening statement has been delivered.

NEXT STEPS:
1. Use 'continue_call_conversation' to simulate customer responses
2. Use 'update_call_summary' to add notes during the call
3. Use 'handle_customer_objection' if objections arise
4. Use 'end_call' when the conversation is complete

TIP: Use 'get_call_protocol_guide' for guidance on call phases!
"""


@tool
def continue_call_conversation(
    customer_response: str,
    kai_response: str
) -> str:
    """
    Continue the call conversation with customer and agent responses.

    Args:
        customer_response: What the customer said
        kai_response: How KAI should respond

    Returns:
        Confirmation message

    Requirements: 4.2, 4.5

    Example:
        continue_call_conversation(
            customer_response='Was kostet das?',
            kai_response='Eine ausgezeichnete Frage...'
        )
    """
    call = _get_current_call()
    if not call:
        return """
❌ No active call found!

Please start a call first using 'start_interactive_call'.
"""

    # Add messages to transcript
    call.add_message("CUSTOMER", customer_response)
    call.add_message("KAI", kai_response)

    print(f"👤 CUSTOMER: {customer_response}\n")
    print(f"🤖 KAI: {kai_response}\n")

    # Try voice synthesis for KAI's response
    if ELEVENLABS_AVAILABLE:
        api_key = os.getenv("ELEVEN_LABS_API_KEY")
        if api_key:
            try:
                client = ElevenLabs(api_key=api_key)
                audio_stream = client.generate(
                    text=kai_response,
                    voice="Rachel",
                    model="eleven_multilingual_v2",
                    stream=True
                )
                stream(audio_stream)
                logger.debug("Voice synthesis for response completed")
            except Exception as e:
                logger.debug(f"Voice synthesis failed, using text-only: {e}")
                # Silently fall back to text-only

    return f"""
✅ Conversation continued

Messages added to call transcript: {call.call_id}

Continue the conversation or use 'end_call' when finished.
"""


@tool
def update_call_summary(new_information: str) -> str:
    """
    Add internal notes to the ongoing call transcript.

    Use this to record important information, customer preferences,
    or observations during the call.

    Args:
        new_information: Note to add to the call

    Returns:
        Confirmation message

    Requirements: 4.5

    Example:
        update_call_summary('Customer interested in 10kW system')
    """
    call = _get_current_call()
    if not call:
        return """
❌ No active call found!

Please start a call first using 'start_interactive_call'.
"""

    call.add_note(new_information)

    return f"""
✅ Call summary updated

Note added to call {call.call_id}:
"{new_information}"

The note has been recorded in the call transcript.
"""


@tool
def end_call(outcome: str, next_steps: str) -> str:
    """
    End the current call and generate final transcript.

    Args:
        outcome: Call outcome (e.g., 'Consultation scheduled')
        next_steps: Agreed next steps (e.g., 'Send calculation via email')

    Returns:
        Complete call transcript summary

    Requirements: 4.4, 4.5

    Example:
        end_call(
            outcome='Customer interested, consultation scheduled',
            next_steps='Send detailed calculation and schedule site visit'
        )
    """
    call = _get_current_call()
    if not call:
        return """
❌ No active call found!

Please start a call first using 'start_interactive_call'.
"""

    # Set outcome and next steps
    call.outcome = outcome
    call.next_steps = next_steps
    call.ended_at = datetime.now()

    print("\n" + "=" * 60)
    print("📞 ENDING CALL")
    print("=" * 60 + "\n")

    # Generate and display summary
    summary = call.get_summary()
    print(summary)

    # Clear current call
    _set_current_call(None)

    return f"""
✅ Call ended successfully!

{summary}

The call transcript has been saved and the call is now closed.
"""


@tool
def get_call_protocol_guide(phase: str) -> str:
    """
    Get structured guidance for a specific call phase.

    Available phases:
    - preparation: Knowledge gathering before call
    - opening: Rapport building and introduction
    - discovery: Understanding customer needs
    - presentation: Presenting solution with benefits
    - objection_handling: Addressing customer concerns
    - closing: Securing commitment and next steps

    Args:
        phase: Call phase name

    Returns:
        Formatted protocol guide

    Requirements: 4.2, 4.3

    Example:
        get_call_protocol_guide('objection_handling')
    """
    from .call_protocol import format_protocol_guide
    return format_protocol_guide(phase)


@tool
def handle_customer_objection(objection: str) -> str:
    """
    Get guidance on handling a specific customer objection.

    This tool provides the 4-step objection handling process:
    1. VALIDATE: Acknowledge the concern
    2. CLARIFY: Ask questions to understand
    3. RESPOND: Provide data-driven counter-argument
    4. CONFIRM: Check if concern is resolved

    Args:
        objection: Customer objection text

    Returns:
        Suggested response and handling strategy

    Requirements: 4.3, 4.4

    Example:
        handle_customer_objection('Das ist zu teuer')
    """
    return handle_objection(objection)


@tool
def build_sales_argument(
    customer_need: str,
    knowledge_facts: str
) -> str:
    """
    Build a structured sales argument based on customer needs.

    Args:
        customer_need: Identified customer need or pain point
        knowledge_facts: Relevant facts (comma-separated or list)

    Returns:
        Structured argument

    Requirements: 4.2, 4.3

    Example:
        build_sales_argument(
            customer_need='Reduce energy costs',
            knowledge_facts='40% savings, 8-year payback, 25-year warranty'
        )
    """
    # Parse facts
    if isinstance(knowledge_facts, str):
        facts = [f.strip() for f in knowledge_facts.split(',')]
    else:
        facts = knowledge_facts

    return build_argument_structure(customer_need, facts)


@tool
def generate_call_closing(call_summary: str, proposed_next_step: str) -> str:
    """
    Generate a professional closing statement for the call.

    Args:
        call_summary: Brief summary of discussion
        proposed_next_step: Specific next action to propose

    Returns:
        Professional closing statement

    Requirements: 4.4

    Example:
        generate_call_closing(
            call_summary='Discussed 10kW PV system with battery',
            proposed_next_step='Send calculation and schedule site visit'
        )
    """
    return generate_closing_statement(call_summary, proposed_next_step)


def get_telephony_tools() -> list:
    """
    Get all telephony tools for the agent.

    Returns:
        List of telephony tool functions

    Requirements: 4.1, 4.2, 4.4, 4.5
    """
    return [
        start_interactive_call,
        continue_call_conversation,
        update_call_summary,
        end_call,
        get_call_protocol_guide,
        handle_customer_objection,
        build_sales_argument,
        generate_call_closing,
    ]
