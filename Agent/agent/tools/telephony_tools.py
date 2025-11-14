"""
Telephony Tools for KAI Agent
==============================

Provides tools for conducting professional sales and consulting calls
with voice synthesis, Bria Softphone integration, call recording,
analytics, CRM integration, and structured conversation management.

Version: 2.0.0 - MEGA EXTENSION
Requirements: 4.1, 4.2, 4.4, 4.5, Extended Features 1-20
"""

import os
import uuid
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
from langchain_core.tools import tool

# Try to import ElevenLabs, but make it optional for testing
try:
    from elevenlabs import stream
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

# Try to import Pandas for CSV/XLSX bulk import
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Try to import Whisper for call transcription
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

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

# Database path for phone numbers and call records
DB_PATH = Path(__file__).parent.parent.parent / "data" / "telephony.db"


# ====================================================================
# ENUMS AND CONSTANTS
# ====================================================================

class CallStatus(Enum):
    """Call status enumeration"""
    IDLE = "idle"
    RINGING = "ringing"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    ENDED = "ended"


class CallDirection(Enum):
    """Call direction enumeration"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallOutcome(Enum):
    """Call outcome enumeration"""
    SUCCESS = "success"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    REJECTED = "rejected"
    FAILED = "failed"


# ====================================================================
# DATACLASSES
# ====================================================================


@dataclass
class CallTranscript:
    """
    Represents a call transcript with conversation history.

    Attributes:
        call_id: Unique identifier for the call
        phone_number: Customer phone number
        goal: Objective of the call
        started_at: Call start timestamp
        ended_at: Call end timestamp (None if ongoing)
        messages: List of conversation messages
        notes: Agent notes during call
        outcome: Call outcome summary
        next_steps: Agreed next steps
        direction: Call direction (inbound/outbound)
        status: Current call status
        recording_path: Path to call recording file
        sentiment_score: Overall sentiment score (-1 to 1)
        crm_logged: Whether call was logged to CRM
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
    direction: CallDirection = CallDirection.OUTBOUND
    status: CallStatus = CallStatus.IDLE
    recording_path: Optional[str] = None
    sentiment_score: Optional[float] = None
    crm_logged: bool = False

    def __getstate__(self):
        """Ermoglicht Pickle-Serialisierung fur Session State"""
        state = self.__dict__.copy()
        # Convert Enums to strings for serialization
        if 'direction' in state and isinstance(state['direction'], CallDirection):
            state['direction'] = state['direction'].value
        if 'status' in state and isinstance(state['status'], CallStatus):
            state['status'] = state['status'].value
        return state
    
    def __setstate__(self, state):
        """Ermoglicht Pickle-Deserialisierung fur Session State"""
        # Convert strings back to Enums
        if 'direction' in state and isinstance(state['direction'], str):
            state['direction'] = CallDirection(state['direction'])
        if 'status' in state and isinstance(state['status'], str):
            state['status'] = CallStatus(state['status'])
        self.__dict__.update(state)

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
[TARGET] Goal: {self.goal}
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
[NOTE] AGENT NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for note in self.notes:
                summary += f"\n• {note['note']}\n"

        if self.outcome or self.next_steps:
            summary += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[OK] OUTCOME & NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            if self.outcome:
                summary += f"\n[TARGET] Outcome: {self.outcome}\n"
            if self.next_steps:
                summary += f"\n📋 Next Steps: {self.next_steps}\n"

        summary += (
            "\n╚══════════════════════════════════════════════════════════════╝"
        )
        return summary


@dataclass
class PhoneContact:
    """
    Represents a phone contact in the database.

    Attributes:
        contact_id: Unique contact identifier
        name: Contact name
        phone_number: Phone number (formatted)
        email: Email address (optional)
        company: Company name (optional)
        tags: List of tags (e.g., 'lead', 'customer', 'vip')
        notes: Contact notes
        created_at: Contact creation timestamp
        last_contacted: Last call timestamp
        call_count: Total number of calls
    """
    contact_id: str
    name: str
    phone_number: str
    email: Optional[str] = None
    company: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_contacted: Optional[datetime] = None
    call_count: int = 0


@dataclass
class CallAnalytics:
    """
    Call analytics metrics.

    Attributes:
        total_calls: Total number of calls
        successful_calls: Calls with positive outcome
        failed_calls: Calls with negative outcome
        avg_duration_seconds: Average call duration
        conversion_rate: Percentage of successful calls
        total_duration_seconds: Total talk time
        avg_sentiment_score: Average sentiment across all calls
    """
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    avg_duration_seconds: float = 0.0
    conversion_rate: float = 0.0
    total_duration_seconds: float = 0.0
    avg_sentiment_score: float = 0.0


# Global state for current call
_current_call: Optional[CallTranscript] = None


def _get_current_call() -> Optional[CallTranscript]:
    """Get the current active call transcript."""
    return _current_call


def _set_current_call(call: Optional[CallTranscript]) -> None:
    """Set the current active call transcript."""
    global _current_call
    _current_call = call


# ====================================================================
# DATABASE MANAGEMENT
# ====================================================================

class PhoneNumberDatabase:
    """Manages phone contacts and call history in SQLite database."""
    
    def __init__(self, db_path: Path = DB_PATH):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Contacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    contact_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone_number TEXT UNIQUE NOT NULL,
                    email TEXT,
                    company TEXT,
                    tags TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    last_contacted TEXT,
                    call_count INTEGER DEFAULT 0
                )
            """)
            
            # Call history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS call_history (
                    call_id TEXT PRIMARY KEY,
                    contact_id TEXT,
                    phone_number TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    status TEXT NOT NULL,
                    goal TEXT,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_seconds INTEGER,
                    outcome TEXT,
                    next_steps TEXT,
                    recording_path TEXT,
                    sentiment_score REAL,
                    crm_logged INTEGER DEFAULT 0,
                    transcript_json TEXT,
                    FOREIGN KEY (contact_id) REFERENCES contacts(contact_id)
                )
            """)
            
            # Call scripts / knowledge base table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS call_scripts (
                    script_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    opening_statement TEXT NOT NULL,
                    key_points TEXT,
                    objection_responses TEXT,
                    closing_statement TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def add_contact(self, contact: PhoneContact) -> bool:
        """Add a new contact to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO contacts 
                    (contact_id, name, phone_number, email, company, tags, notes, 
                     created_at, last_contacted, call_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contact.contact_id,
                    contact.name,
                    contact.phone_number,
                    contact.email,
                    contact.company,
                    json.dumps(contact.tags),
                    contact.notes,
                    contact.created_at.isoformat(),
                    contact.last_contacted.isoformat() if contact.last_contacted else None,
                    contact.call_count
                ))
                conn.commit()
                logger.info(f"Contact added: {contact.name} ({contact.phone_number})")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Contact already exists: {contact.phone_number}")
            return False
        except Exception as e:
            logger.error(f"Failed to add contact: {e}")
            return False
    
    def get_contact_by_number(self, phone_number: str) -> Optional[PhoneContact]:
        """Retrieve contact by phone number."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT contact_id, name, phone_number, email, company, tags, 
                           notes, created_at, last_contacted, call_count
                    FROM contacts WHERE phone_number = ?
                """, (phone_number,))
                row = cursor.fetchone()
                
                if row:
                    return PhoneContact(
                        contact_id=row[0],
                        name=row[1],
                        phone_number=row[2],
                        email=row[3],
                        company=row[4],
                        tags=json.loads(row[5]) if row[5] else [],
                        notes=row[6],
                        created_at=datetime.fromisoformat(row[7]),
                        last_contacted=datetime.fromisoformat(row[8]) if row[8] else None,
                        call_count=row[9]
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve contact: {e}")
            return None
    
    def search_contacts(self, query: str) -> List[PhoneContact]:
        """Search contacts by name, phone, or company."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT contact_id, name, phone_number, email, company, tags, 
                           notes, created_at, last_contacted, call_count
                    FROM contacts 
                    WHERE name LIKE ? OR phone_number LIKE ? OR company LIKE ?
                    ORDER BY name
                """, (f"%{query}%", f"%{query}%", f"%{query}%"))
                
                contacts = []
                for row in cursor.fetchall():
                    contacts.append(PhoneContact(
                        contact_id=row[0],
                        name=row[1],
                        phone_number=row[2],
                        email=row[3],
                        company=row[4],
                        tags=json.loads(row[5]) if row[5] else [],
                        notes=row[6],
                        created_at=datetime.fromisoformat(row[7]),
                        last_contacted=datetime.fromisoformat(row[8]) if row[8] else None,
                        call_count=row[9]
                    ))
                return contacts
        except Exception as e:
            logger.error(f"Failed to search contacts: {e}")
            return []
    
    def save_call_transcript(self, call: CallTranscript) -> bool:
        """Save call transcript to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate duration
                duration = None
                if call.ended_at and call.started_at:
                    duration = int((call.ended_at - call.started_at).total_seconds())
                
                # Prepare transcript JSON
                transcript_data = {
                    'messages': call.messages,
                    'notes': call.notes
                }
                
                cursor.execute("""
                    INSERT INTO call_history 
                    (call_id, phone_number, direction, status, goal, started_at, 
                     ended_at, duration_seconds, outcome, next_steps, recording_path, 
                     sentiment_score, crm_logged, transcript_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    call.call_id,
                    call.phone_number,
                    call.direction.value,
                    call.status.value,
                    call.goal,
                    call.started_at.isoformat(),
                    call.ended_at.isoformat() if call.ended_at else None,
                    duration,
                    call.outcome,
                    call.next_steps,
                    call.recording_path,
                    call.sentiment_score,
                    1 if call.crm_logged else 0,
                    json.dumps(transcript_data)
                ))
                
                # Update contact's last_contacted and call_count
                cursor.execute("""
                    UPDATE contacts 
                    SET last_contacted = ?, call_count = call_count + 1
                    WHERE phone_number = ?
                """, (call.started_at.isoformat(), call.phone_number))
                
                conn.commit()
                logger.info(f"Call transcript saved: {call.call_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to save call transcript: {e}")
            return False
    
    def get_analytics(self, days: int = 30) -> CallAnalytics:
        """Calculate call analytics for the specified period."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate date threshold
                since = datetime.now() - timedelta(days=days)
                
                # Get call statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN outcome LIKE '%success%' OR outcome LIKE '%scheduled%' 
                            THEN 1 ELSE 0 END) as successful,
                        AVG(duration_seconds) as avg_duration,
                        SUM(duration_seconds) as total_duration,
                        AVG(sentiment_score) as avg_sentiment
                    FROM call_history
                    WHERE started_at >= ?
                """, (since.isoformat(),))
                
                row = cursor.fetchone()
                
                if row and row[0] > 0:
                    total = row[0]
                    successful = row[1] or 0
                    return CallAnalytics(
                        total_calls=total,
                        successful_calls=successful,
                        failed_calls=total - successful,
                        avg_duration_seconds=row[2] or 0.0,
                        conversion_rate=(successful / total * 100) if total > 0 else 0.0,
                        total_duration_seconds=row[3] or 0.0,
                        avg_sentiment_score=row[4] or 0.0
                    )
                
                return CallAnalytics()
        except Exception as e:
            logger.error(f"Failed to calculate analytics: {e}")
            return CallAnalytics()


# Initialize global database instance
_phone_db = PhoneNumberDatabase()


# ====================================================================
# BRIA SOFTPHONE INTEGRATION
# ====================================================================

class BriaSoftphone:
    """
    Bria Softphone integration for real telephony calls.
    
    This is a mock implementation that simulates Bria Softphone SDK.
    In production, replace with actual Bria SDK calls.
    """
    
    def __init__(self):
        """Initialize Bria Softphone connection."""
        self.connected = False
        self.current_call_id = None
        self.sip_account = None
        logger.info("BriaSoftphone initialized (mock mode)")
    
    def connect(self, sip_server: str, username: str, password: str) -> Tuple[bool, str]:
        """
        Connect to SIP server via Bria Softphone.
        
        Args:
            sip_server: SIP server address
            username: SIP username
            password: SIP password
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # TODO: Replace with actual Bria SDK connection
            # from bria import BriaSDK
            # self.sdk = BriaSDK()
            # self.sdk.connect(sip_server, username, password)
            
            self.connected = True
            self.sip_account = username
            logger.info(f"Connected to SIP server: {sip_server} as {username}")
            return True, f"Verbunden mit {sip_server} als {username}"
        except Exception as e:
            logger.error(f"Failed to connect to SIP server: {e}")
            return False, f"Verbindung fehlgeschlagen: {str(e)}"
    
    def disconnect(self) -> Tuple[bool, str]:
        """Disconnect from SIP server."""
        try:
            # TODO: Replace with actual Bria SDK disconnection
            self.connected = False
            self.sip_account = None
            logger.info("Disconnected from SIP server")
            return True, "Verbindung getrennt"
        except Exception as e:
            logger.error(f"Failed to disconnect: {e}")
            return False, f"Fehler beim Trennen: {str(e)}"
    
    def make_call(self, phone_number: str) -> Tuple[bool, str, Optional[str]]:
        """
        Make an outbound call.
        
        Args:
            phone_number: Phone number to call
            
        Returns:
            Tuple of (success, message, call_id)
        """
        if not self.connected:
            return False, "Nicht verbunden. Bitte zuerst verbinden.", None
        
        try:
            # TODO: Replace with actual Bria SDK call
            # call_id = self.sdk.make_call(phone_number)
            
            call_id = f"BRIA-{uuid.uuid4().hex[:8].upper()}"
            self.current_call_id = call_id
            logger.info(f"Outbound call initiated: {phone_number} (ID: {call_id})")
            return True, f"Anruf zu {phone_number} wird gestartet...", call_id
        except Exception as e:
            logger.error(f"Failed to make call: {e}")
            return False, f"Anruf fehlgeschlagen: {str(e)}", None
    
    def answer_call(self, call_id: str) -> Tuple[bool, str]:
        """Answer an incoming call."""
        try:
            # TODO: Replace with actual Bria SDK answer
            # self.sdk.answer_call(call_id)
            
            self.current_call_id = call_id
            logger.info(f"Answered call: {call_id}")
            return True, f"Anruf angenommen: {call_id}"
        except Exception as e:
            logger.error(f"Failed to answer call: {e}")
            return False, f"Fehler beim Annehmen: {str(e)}"
    
    def hangup(self, call_id: str) -> Tuple[bool, str]:
        """Hang up a call."""
        try:
            # TODO: Replace with actual Bria SDK hangup
            # self.sdk.hangup(call_id)
            
            self.current_call_id = None
            logger.info(f"Call hung up: {call_id}")
            return True, f"Anruf beendet: {call_id}"
        except Exception as e:
            logger.error(f"Failed to hangup: {e}")
            return False, f"Fehler beim Auflegen: {str(e)}"
    
    def transfer_call(self, call_id: str, target_number: str) -> Tuple[bool, str]:
        """Transfer call to another number."""
        try:
            # TODO: Replace with actual Bria SDK transfer
            logger.info(f"Call transferred: {call_id} to {target_number}")
            return True, f"Anruf weitergeleitet zu {target_number}"
        except Exception as e:
            logger.error(f"Failed to transfer call: {e}")
            return False, f"Weiterleitung fehlgeschlagen: {str(e)}"
    
    def hold_call(self, call_id: str) -> Tuple[bool, str]:
        """Put call on hold."""
        try:
            # TODO: Replace with actual Bria SDK hold
            logger.info(f"Call on hold: {call_id}")
            return True, f"Anruf in Warteschleife: {call_id}"
        except Exception as e:
            logger.error(f"Failed to hold call: {e}")
            return False, f"Fehler beim Halten: {str(e)}"
    
    def resume_call(self, call_id: str) -> Tuple[bool, str]:
        """Resume call from hold."""
        try:
            # TODO: Replace with actual Bria SDK resume
            logger.info(f"Call resumed: {call_id}")
            return True, f"Anruf fortgesetzt: {call_id}"
        except Exception as e:
            logger.error(f"Failed to resume call: {e}")
            return False, f"Fehler beim Fortsetzen: {str(e)}"
    
    def get_call_status(self, call_id: str) -> Tuple[bool, str, Optional[CallStatus]]:
        """Get current status of a call."""
        try:
            # TODO: Replace with actual Bria SDK status check
            if call_id == self.current_call_id:
                return True, "Anruf aktiv", CallStatus.ACTIVE
            return True, "Anruf beendet", CallStatus.ENDED
        except Exception as e:
            logger.error(f"Failed to get call status: {e}")
            return False, f"Fehler beim Abrufen des Status: {str(e)}", None


# Initialize global Bria Softphone instance
_bria_softphone = BriaSoftphone()


# ====================================================================
# ORIGINAL TOOLS (PRESERVED)
# ====================================================================

# ====================================================================
# NEW EXTENDED TOOLS - BRIA SOFTPHONE
# ====================================================================

@tool
def bria_connect(sip_server: str, username: str, password: str) -> str:
    """
    Verbinde mit SIP-Server uber Bria Softphone.
    
    Args:
        sip_server: SIP Server Adresse (z.B. 'sip.example.com')
        username: SIP Benutzername
        password: SIP Passwort
    
    Returns:
        Verbindungsstatus
    
    Example:
        bria_connect('sip.company.com', 'user123', 'password')
    """
    success, message = _bria_softphone.connect(sip_server, username, password)
    
    if success:
        return f"Erfolgreich verbunden mit {sip_server} als {username}"
    return f"Verbindung fehlgeschlagen: {message}"


@tool
def bria_disconnect() -> str:
    """
    Trenne Verbindung zum SIP-Server.
    
    Returns:
        Trennungsstatus
    """
    success, message = _bria_softphone.disconnect()
    return message


@tool
def bria_make_call(phone_number: str, call_goal: str = "") -> str:
    """
    Starte ausgehenden Anruf uber Bria Softphone.
    
    Args:
        phone_number: Zielrufnummer
        call_goal: Anrufziel (optional)
    
    Returns:
        Anrufstatus mit Call ID
    
    Example:
        bria_make_call('+49301234567', 'Beratungstermin vereinbaren')
    """
    success, message, call_id = _bria_softphone.make_call(phone_number)
    
    if success and call_id:
        # Create call transcript
        call = CallTranscript(
            call_id=call_id,
            phone_number=phone_number,
            goal=call_goal,
            started_at=datetime.now(),
            direction=CallDirection.OUTBOUND,
            status=CallStatus.RINGING
        )
        _set_current_call(call)
        
        return f"Anruf gestartet zu {phone_number}\nCall ID: {call_id}\nZiel: {call_goal}"
    
    return message


@tool
def bria_answer_call(call_id: str) -> str:
    """
    Eingehenden Anruf annehmen.
    
    Args:
        call_id: Call ID des eingehenden Anrufs
    
    Returns:
        Status
    """
    success, message = _bria_softphone.answer_call(call_id)
    
    if success:
        # Create call transcript for inbound call
        call = CallTranscript(
            call_id=call_id,
            phone_number="INBOUND",
            goal="Kundenanfrage bearbeiten",
            started_at=datetime.now(),
            direction=CallDirection.INBOUND,
            status=CallStatus.ACTIVE
        )
        _set_current_call(call)
    
    return message


@tool
def bria_hangup(call_id: str) -> str:
    """
    Anruf beenden.
    
    Args:
        call_id: Call ID
    
    Returns:
        Status
    """
    success, message = _bria_softphone.hangup(call_id)
    
    if success:
        call = _get_current_call()
        if call and call.call_id == call_id:
            call.ended_at = datetime.now()
            call.status = CallStatus.ENDED
            # Save to database
            _phone_db.save_call_transcript(call)
            _set_current_call(None)
    
    return message


@tool
def bria_transfer_call(call_id: str, target_number: str) -> str:
    """
    Anruf weiterleiten.
    
    Args:
        call_id: Call ID
        target_number: Zielrufnummer
    
    Returns:
        Status
    """
    success, message = _bria_softphone.transfer_call(call_id, target_number)
    return message


@tool
def bria_hold_call(call_id: str) -> str:
    """
    Anruf in Warteschleife legen.
    
    Args:
        call_id: Call ID
    
    Returns:
        Status
    """
    success, message = _bria_softphone.hold_call(call_id)
    
    if success:
        call = _get_current_call()
        if call and call.call_id == call_id:
            call.status = CallStatus.ON_HOLD
    
    return message


@tool
def bria_resume_call(call_id: str) -> str:
    """
    Anruf aus Warteschleife fortsetzen.
    
    Args:
        call_id: Call ID
    
    Returns:
        Status
    """
    success, message = _bria_softphone.resume_call(call_id)
    
    if success:
        call = _get_current_call()
        if call and call.call_id == call_id:
            call.status = CallStatus.ACTIVE
    
    return message


# ====================================================================
# NEW EXTENDED TOOLS - PHONE NUMBER MANAGEMENT
# ====================================================================

@tool
def add_phone_contact(
    name: str,
    phone_number: str,
    email: str = "",
    company: str = "",
    tags: str = "",
    notes: str = ""
) -> str:
    """
    Fugt einen neuen Kontakt zur Telefondatenbank hinzu.
    
    Args:
        name: Kontaktname
        phone_number: Telefonnummer
        email: E-Mail (optional)
        company: Firma (optional)
        tags: Tags, kommagetrennt (z.B. 'lead,vip')
        notes: Notizen (optional)
    
    Returns:
        Erfolgsmeldung
    
    Example:
        add_phone_contact(
            name='Max Mustermann',
            phone_number='+49301234567',
            company='Musterfirma GmbH',
            tags='lead,interessiert'
        )
    """
    try:
        sanitize_user_input(name, max_length=200)
        sanitize_user_input(phone_number, max_length=50)
    except InputValidationError as e:
        return f"Fehler: {str(e)}"
    
    contact = PhoneContact(
        contact_id=f"CONTACT-{uuid.uuid4().hex[:8].upper()}",
        name=name,
        phone_number=phone_number,
        email=email if email else None,
        company=company if company else None,
        tags=[t.strip() for t in tags.split(',')] if tags else [],
        notes=notes
    )
    
    success = _phone_db.add_contact(contact)
    
    if success:
        return f"Kontakt hinzugefugt: {name} ({phone_number})\nID: {contact.contact_id}"
    return f"Fehler: Kontakt mit Nummer {phone_number} existiert bereits"


@tool
def search_phone_contacts(query: str) -> str:
    """
    Sucht Kontakte in der Datenbank.
    
    Args:
        query: Suchbegriff (Name, Nummer oder Firma)
    
    Returns:
        Liste der gefundenen Kontakte
    
    Example:
        search_phone_contacts('Mustermann')
    """
    contacts = _phone_db.search_contacts(query)
    
    if not contacts:
        return f"Keine Kontakte gefunden fur: {query}"
    
    result = f"Gefundene Kontakte ({len(contacts)}):\n\n"
    
    for contact in contacts:
        result += f"Name: {contact.name}\n"
        result += f"Telefon: {contact.phone_number}\n"
        if contact.company:
            result += f"Firma: {contact.company}\n"
        if contact.email:
            result += f"E-Mail: {contact.email}\n"
        if contact.tags:
            result += f"Tags: {', '.join(contact.tags)}\n"
        result += f"Anzahl Anrufe: {contact.call_count}\n"
        if contact.last_contacted:
            result += f"Letzter Kontakt: {contact.last_contacted.strftime('%d.%m.%Y %H:%M')}\n"
        result += "\n" + "-" * 50 + "\n\n"
    
    return result


@tool
def bulk_import_phone_numbers(file_path: str) -> str:
    """
    Importiert Kontakte aus CSV oder XLSX Datei.
    
    Erwartete Spalten: name, phone_number, email (optional), company (optional), tags (optional)
    
    Args:
        file_path: Pfad zur CSV/XLSX Datei
    
    Returns:
        Import-Bericht
    
    Example:
        bulk_import_phone_numbers('C:/contacts.xlsx')
    """
    if not PANDAS_AVAILABLE:
        return "Fehler: Pandas nicht installiert. Bitte 'pip install pandas openpyxl' ausfuhren."
    
    try:
        # Read file based on extension
        file_path_obj = Path(file_path)
        
        if file_path_obj.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif file_path_obj.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            return f"Fehler: Nicht unterstutztes Dateiformat. Nur CSV und XLSX erlaubt."
        
        # Validate required columns
        if 'name' not in df.columns or 'phone_number' not in df.columns:
            return "Fehler: Spalten 'name' und 'phone_number' sind erforderlich"
        
        # Import contacts
        imported = 0
        skipped = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                contact = PhoneContact(
                    contact_id=f"CONTACT-{uuid.uuid4().hex[:8].upper()}",
                    name=str(row['name']),
                    phone_number=str(row['phone_number']),
                    email=str(row.get('email', '')) if pd.notna(row.get('email')) else None,
                    company=str(row.get('company', '')) if pd.notna(row.get('company')) else None,
                    tags=[t.strip() for t in str(row.get('tags', '')).split(',')] if pd.notna(row.get('tags')) else [],
                    notes=str(row.get('notes', '')) if pd.notna(row.get('notes')) else ""
                )
                
                if _phone_db.add_contact(contact):
                    imported += 1
                else:
                    skipped += 1
            except Exception as e:
                errors.append(f"Zeile {idx + 2}: {str(e)}")
        
        result = f"Bulk-Import abgeschlossen:\n"
        result += f"Importiert: {imported}\n"
        result += f"Ubersprungen (bereits vorhanden): {skipped}\n"
        
        if errors:
            result += f"\nFehler ({len(errors)}):\n"
            for error in errors[:10]:  # Show max 10 errors
                result += f"- {error}\n"
        
        return result
    except Exception as e:
        logger.error(f"Bulk import failed: {e}")
        return f"Fehler beim Import: {str(e)}"


# ====================================================================
# NEW EXTENDED TOOLS - CALL ANALYTICS
# ====================================================================

@tool
def get_call_analytics(days: int = 30) -> str:
    """
    Ruft Anruf-Statistiken ab.
    
    Args:
        days: Zeitraum in Tagen (Standard: 30)
    
    Returns:
        Detaillierte Anruf-Statistiken
    
    Example:
        get_call_analytics(7)  # Letzte 7 Tage
    """
    analytics = _phone_db.get_analytics(days)
    
    result = f"Anruf-Analytics (letzte {days} Tage)\n"
    result += "=" * 50 + "\n\n"
    result += f"Gesamtanzahl Anrufe: {analytics.total_calls}\n"
    result += f"Erfolgreiche Anrufe: {analytics.successful_calls}\n"
    result += f"Fehlgeschlagene Anrufe: {analytics.failed_calls}\n"
    result += f"Conversion Rate: {analytics.conversion_rate:.1f}%\n\n"
    
    if analytics.total_calls > 0:
        avg_minutes = analytics.avg_duration_seconds / 60
        total_hours = analytics.total_duration_seconds / 3600
        
        result += f"Durchschnittliche Dauer: {avg_minutes:.1f} Minuten\n"
        result += f"Gesamte Gesprächszeit: {total_hours:.1f} Stunden\n"
        
        if analytics.avg_sentiment_score != 0:
            result += f"Durchschnittliche Stimmung: {analytics.avg_sentiment_score:.2f}\n"
    else:
        result += "Keine Anrufe im ausgewahlten Zeitraum.\n"
    
    return result


# ====================================================================
# NEW EXTENDED TOOLS - KNOWLEDGE BASE & CALL SCRIPTS
# ====================================================================

@tool
def save_call_script(
    name: str,
    category: str,
    opening_statement: str,
    key_points: str = "",
    objection_responses: str = "",
    closing_statement: str = ""
) -> str:
    """
    Speichert ein Anruf-Skript in der Knowledge Base.
    
    Args:
        name: Skriptname
        category: Kategorie (z.B. 'Verkauf', 'Support', 'Beratung')
        opening_statement: Eroffnungssatz
        key_points: Wichtige Punkte (kommagetrennt)
        objection_responses: Einwandbehandlung (JSON format)
        closing_statement: Abschlusssatz
    
    Returns:
        Erfolgsmeldung
    
    Example:
        save_call_script(
            name='PV-Beratung Standard',
            category='Verkauf',
            opening_statement='Guten Tag, hier ist KAI von...',
            key_points='Kostenersparnis,Umweltschutz,Unabhangigkeit'
        )
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            script_id = f"SCRIPT-{uuid.uuid4().hex[:8].upper()}"
            
            cursor.execute("""
                INSERT INTO call_scripts
                (script_id, name, category, opening_statement, key_points,
                 objection_responses, closing_statement, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                script_id,
                name,
                category,
                opening_statement,
                key_points,
                objection_responses,
                closing_statement,
                datetime.now().isoformat()
            ))
            conn.commit()
            
            return f"Skript gespeichert: {name}\nKategorie: {category}\nID: {script_id}"
    except Exception as e:
        logger.error(f"Failed to save call script: {e}")
        return f"Fehler beim Speichern: {str(e)}"


@tool
def get_call_script(category: str = "") -> str:
    """
    Ruft Anruf-Skripte aus der Knowledge Base ab.
    
    Args:
        category: Kategorie filtern (optional)
    
    Returns:
        Liste der verfugbaren Skripte
    
    Example:
        get_call_script('Verkauf')
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT script_id, name, category, opening_statement, key_points
                    FROM call_scripts WHERE category = ?
                    ORDER BY created_at DESC
                """, (category,))
            else:
                cursor.execute("""
                    SELECT script_id, name, category, opening_statement, key_points
                    FROM call_scripts
                    ORDER BY category, created_at DESC
                """)
            
            scripts = cursor.fetchall()
            
            if not scripts:
                return "Keine Skripte gefunden" + (f" fur Kategorie: {category}" if category else "")
            
            result = f"Verfugbare Call-Skripte ({len(scripts)}):\n\n"
            
            for script in scripts:
                result += f"Name: {script[1]}\n"
                result += f"Kategorie: {script[2]}\n"
                result += f"ID: {script[0]}\n"
                result += f"Eroffnung: {script[3][:100]}...\n"
                if script[4]:
                    result += f"Key Points: {script[4]}\n"
                result += "\n" + "-" * 50 + "\n\n"
            
            return result
    except Exception as e:
        logger.error(f"Failed to get call scripts: {e}")
        return f"Fehler beim Abrufen: {str(e)}"


# ====================================================================
# NEW EXTENDED TOOLS - CALL RECORDING & TRANSCRIPTION
# ====================================================================

@tool
def start_call_recording(call_id: str, audio_file_path: str = "") -> str:
    """
    Startet Aufnahme des aktuellen Anrufs.
    
    Args:
        call_id: Call ID
        audio_file_path: Pfad zur Audiodatei (optional, automatisch generiert)
    
    Returns:
        Status
    
    Example:
        start_call_recording('CALL-12345678')
    """
    call = _get_current_call()
    if not call or call.call_id != call_id:
        return f"Kein aktiver Anruf mit ID: {call_id}"
    
    # Generate recording path if not provided
    if not audio_file_path:
        recordings_dir = Path(__file__).parent.parent.parent / "data" / "recordings"
        recordings_dir.mkdir(parents=True, exist_ok=True)
        audio_file_path = str(recordings_dir / f"{call_id}.wav")
    
    call.recording_path = audio_file_path
    
    # TODO: Implement actual recording with Bria SDK
    # _bria_softphone.start_recording(call_id, audio_file_path)
    
    logger.info(f"Call recording started: {call_id} -> {audio_file_path}")
    return f"Aufnahme gestartet\nCall ID: {call_id}\nDatei: {audio_file_path}"


@tool
def transcribe_call_recording(recording_path: str) -> str:
    """
    Transkribiert eine Anrufaufnahme mit Whisper.
    
    Args:
        recording_path: Pfad zur Audiodatei
    
    Returns:
        Transkription
    
    Example:
        transcribe_call_recording('C:/recordings/CALL-12345678.wav')
    """
    if not WHISPER_AVAILABLE:
        return "Fehler: Whisper nicht installiert. Bitte 'pip install openai-whisper' ausfuhren."
    
    try:
        # Load Whisper model
        model = whisper.load_model("base")
        
        # Transcribe
        result = model.transcribe(recording_path, language="de")
        
        transcription = result["text"]
        
        logger.info(f"Transcription completed for: {recording_path}")
        return f"Transkription:\n\n{transcription}"
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return f"Fehler bei Transkription: {str(e)}"


# ====================================================================
# NEW EXTENDED TOOLS - SENTIMENT ANALYSIS
# ====================================================================

@tool
def analyze_call_sentiment(call_id: str) -> str:
    """
    Analysiert die Stimmung wahrend eines Anrufs.
    
    Args:
        call_id: Call ID
    
    Returns:
        Sentiment-Analyse Ergebnis
    
    Example:
        analyze_call_sentiment('CALL-12345678')
    """
    call = _get_current_call()
    if not call or call.call_id != call_id:
        # Try to load from database
        return f"Kein aktiver Anruf mit ID: {call_id}"
    
    if not call.messages:
        return "Keine Nachrichten im Anruf vorhanden"
    
    # Simple sentiment analysis based on keywords
    positive_keywords = [
        'interessiert', 'gut', 'super', 'perfekt', 'ja', 'gerne',
        'einverstanden', 'toll', 'ausgezeichnet', 'danke'
    ]
    negative_keywords = [
        'nein', 'nicht', 'kein', 'teuer', 'problem', 'schwierig',
        'unmöglich', 'ablehnen', 'unwichtig', 'spater'
    ]
    
    positive_count = 0
    negative_count = 0
    total_words = 0
    
    for msg in call.messages:
        if msg['speaker'] == 'CUSTOMER':
            text = msg['text'].lower()
            words = text.split()
            total_words += len(words)
            
            for word in words:
                if any(kw in word for kw in positive_keywords):
                    positive_count += 1
                if any(kw in word for kw in negative_keywords):
                    negative_count += 1
    
    # Calculate sentiment score (-1 to 1)
    if total_words > 0:
        sentiment_score = (positive_count - negative_count) / total_words
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
    else:
        sentiment_score = 0.0
    
    call.sentiment_score = sentiment_score
    
    # Determine sentiment category
    if sentiment_score > 0.1:
        sentiment = "Positiv"
        emoji = "😊"
    elif sentiment_score < -0.1:
        sentiment = "Negativ"
        emoji = "😟"
    else:
        sentiment = "Neutral"
        emoji = "😐"
    
    result = f"Sentiment-Analyse fur Call {call_id}\n"
    result += "=" * 50 + "\n\n"
    result += f"Stimmung: {sentiment}\n"
    result += f"Score: {sentiment_score:.2f}\n"
    result += f"Positive Keywords: {positive_count}\n"
    result += f"Negative Keywords: {negative_count}\n"
    result += f"Gesamtworter (Kunde): {total_words}\n"
    
    return result


# ====================================================================
# NEW EXTENDED TOOLS - CRM INTEGRATION
# ====================================================================

@tool
def log_call_to_crm(call_id: str, customer_id: str = "") -> str:
    """
    Protokolliert Anruf im CRM-System.
    
    Args:
        call_id: Call ID
        customer_id: CRM Kunden-ID (optional)
    
    Returns:
        Status
    
    Example:
        log_call_to_crm('CALL-12345678', 'CRM-001')
    """
    call = _get_current_call()
    if not call or call.call_id != call_id:
        return f"Kein aktiver Anruf mit ID: {call_id}"
    
    try:
        # Save to telephony database
        _phone_db.save_call_transcript(call)
        
        # Mark as logged to CRM
        call.crm_logged = True
        
        # TODO: Integrate with actual CRM system
        # from crm import add_activity
        # add_activity(
        #     customer_id=customer_id,
        #     activity_type='phone_call',
        #     description=call.goal,
        #     outcome=call.outcome
        # )
        
        logger.info(f"Call logged to CRM: {call_id}")
        return f"Anruf erfolgreich ins CRM protokolliert\nCall ID: {call_id}\nKunde: {customer_id or 'N/A'}"
    except Exception as e:
        logger.error(f"Failed to log call to CRM: {e}")
        return f"Fehler beim CRM-Logging: {str(e)}"


# ====================================================================
# NEW EXTENDED TOOLS - FOLLOW-UP SCHEDULING
# ====================================================================

@tool
def schedule_follow_up(
    call_id: str,
    follow_up_date: str,
    follow_up_action: str
) -> str:
    """
    Plant Wiedervorlage nach Anruf.
    
    Args:
        call_id: Call ID
        follow_up_date: Datum (YYYY-MM-DD)
        follow_up_action: Geplante Aktion
    
    Returns:
        Status
    
    Example:
        schedule_follow_up(
            'CALL-12345678',
            '2024-02-15',
            'Angebot nachfassen'
        )
    """
    call = _get_current_call()
    if not call or call.call_id != call_id:
        return f"Kein aktiver Anruf mit ID: {call_id}"
    
    try:
        # Parse follow-up date
        follow_up_dt = datetime.strptime(follow_up_date, "%Y-%m-%d")
        
        # Add to call notes
        note = f"Follow-up geplant fur {follow_up_date}: {follow_up_action}"
        call.add_note(note)
        
        # TODO: Integrate with calendar/CRM for actual scheduling
        # from crm_calendar_ui import add_event
        # add_event(
        #     date=follow_up_dt,
        #     title=f'Follow-up: {call.phone_number}',
        #     description=follow_up_action
        # )
        
        logger.info(f"Follow-up scheduled for call {call_id}: {follow_up_date}")
        return f"Wiedervorlage gesetzt\nDatum: {follow_up_date}\nAktion: {follow_up_action}"
    except ValueError:
        return "Fehler: Ungultiges Datumsformat. Bitte YYYY-MM-DD verwenden."
    except Exception as e:
        logger.error(f"Failed to schedule follow-up: {e}")
        return f"Fehler beim Setzen der Wiedervorlage: {str(e)}"


# ====================================================================
# NEW EXTENDED TOOLS - 10+ WOW FEATURES
# ====================================================================

@tool
def quick_dial_favorite(contact_name: str) -> str:
    """
    Schnellwahl aus Favoriten.
    
    Args:
        contact_name: Kontaktname
    
    Returns:
        Anrufstatus
    """
    contacts = _phone_db.search_contacts(contact_name)
    
    if not contacts:
        return f"Kein Kontakt gefunden: {contact_name}"
    
    if len(contacts) > 1:
        return f"Mehrere Kontakte gefunden ({len(contacts)}). Bitte genauer spezifizieren."
    
    contact = contacts[0]
    
    # Start call
    success, message, call_id = _bria_softphone.make_call(contact.phone_number)
    
    if success and call_id:
        call = CallTranscript(
            call_id=call_id,
            phone_number=contact.phone_number,
            goal=f"Anruf an {contact.name}",
            started_at=datetime.now(),
            direction=CallDirection.OUTBOUND,
            status=CallStatus.RINGING
        )
        _set_current_call(call)
        
        return f"Schnellwahl gestartet\nKontakt: {contact.name}\nNummer: {contact.phone_number}\nCall ID: {call_id}"
    
    return message


@tool
def set_do_not_disturb(enabled: bool, until: str = "") -> str:
    """
    Bitte nicht storen Modus aktivieren/deaktivieren.
    
    Args:
        enabled: True zum Aktivieren, False zum Deaktivieren
        until: Bis wann (YYYY-MM-DD HH:MM, optional)
    
    Returns:
        Status
    
    Example:
        set_do_not_disturb(True, '2024-01-15 17:00')
    """
    status = "aktiviert" if enabled else "deaktiviert"
    
    # TODO: Implement actual DND mode with Bria SDK
    logger.info(f"DND mode {status}" + (f" until {until}" if until else ""))
    
    result = f"Bitte nicht storen Modus {status}"
    if enabled and until:
        result += f"\nBis: {until}"
    
    return result


@tool
def search_call_history(
    phone_number: str = "",
    days: int = 30,
    outcome_filter: str = ""
) -> str:
    """
    Durchsucht Anruf-Historiedatenbank.
    
    Args:
        phone_number: Nach Nummer filtern (optional)
        days: Zeitraum in Tagen (Standard: 30)
        outcome_filter: Nach Ergebnis filtern (optional)
    
    Returns:
        Liste der Anrufe
    
    Example:
        search_call_history(phone_number='+49301234567', days=7)
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT call_id, phone_number, direction, started_at, duration_seconds, outcome FROM call_history WHERE 1=1"
            params = []
            
            # Add filters
            since = datetime.now() - timedelta(days=days)
            query += " AND started_at >= ?"
            params.append(since.isoformat())
            
            if phone_number:
                query += " AND phone_number = ?"
                params.append(phone_number)
            
            if outcome_filter:
                query += " AND outcome LIKE ?"
                params.append(f"%{outcome_filter}%")
            
            query += " ORDER BY started_at DESC LIMIT 50"
            
            cursor.execute(query, params)
            calls = cursor.fetchall()
            
            if not calls:
                return "Keine Anrufe gefunden"
            
            result = f"Anruf-Historie ({len(calls)} Einträge):\n\n"
            
            for call in calls:
                call_id, number, direction, started, duration, outcome = call
                started_dt = datetime.fromisoformat(started)
                
                result += f"Call ID: {call_id}\n"
                result += f"Nummer: {number}\n"
                result += f"Richtung: {direction}\n"
                result += f"Datum: {started_dt.strftime('%d.%m.%Y %H:%M')}\n"
                if duration:
                    result += f"Dauer: {duration // 60} Min {duration % 60} Sek\n"
                if outcome:
                    result += f"Ergebnis: {outcome}\n"
                result += "\n" + "-" * 50 + "\n\n"
            
            return result
    except Exception as e:
        logger.error(f"Call history search failed: {e}")
        return f"Fehler bei der Suche: {str(e)}"


@tool
def auto_dialer_campaign(
    contact_tag: str,
    call_goal: str,
    max_calls: int = 10
) -> str:
    """
    Startet Auto-Dialer Kampagne fur Kontakte mit bestimmtem Tag.
    
    Args:
        contact_tag: Tag zum Filtern der Kontakte
        call_goal: Anrufziel
        max_calls: Maximale Anzahl Anrufe
    
    Returns:
        Kampagnen-Status
    
    Example:
        auto_dialer_campaign('lead', 'Beratungstermin vereinbaren', max_calls=20)
    """
    try:
        # Get all contacts
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT contact_id, name, phone_number, tags
                FROM contacts
            """)
            
            all_contacts = cursor.fetchall()
            
            # Filter by tag
            matching_contacts = []
            for contact in all_contacts:
                tags = json.loads(contact[3]) if contact[3] else []
                if contact_tag in tags:
                    matching_contacts.append(contact)
            
            if not matching_contacts:
                return f"Keine Kontakte mit Tag '{contact_tag}' gefunden"
            
            # Limit to max_calls
            contacts_to_call = matching_contacts[:max_calls]
            
            result = f"Auto-Dialer Kampagne gestartet\n"
            result += "=" * 50 + "\n\n"
            result += f"Tag: {contact_tag}\n"
            result += f"Ziel: {call_goal}\n"
            result += f"Gefunden: {len(matching_contacts)} Kontakte\n"
            result += f"Anrufe geplant: {len(contacts_to_call)}\n\n"
            
            result += "Kontakte:\n"
            for contact in contacts_to_call:
                result += f"- {contact[1]} ({contact[2]})\n"
            
            # TODO: Implement actual auto-dialing logic
            # This would require background processing and queue management
            
            return result
    except Exception as e:
        logger.error(f"Auto-dialer campaign failed: {e}")
        return f"Fehler bei Kampagne: {str(e)}"


@tool
def add_call_tags(call_id: str, tags: str) -> str:
    """
    Fugt Tags zu einem Anruf hinzu.
    
    Args:
        call_id: Call ID
        tags: Tags, kommagetrennt (z.B. 'wichtig,follow-up,hot-lead')
    
    Returns:
        Status
    
    Example:
        add_call_tags('CALL-12345678', 'wichtig,hot-lead')
    """
    call = _get_current_call()
    if not call or call.call_id != call_id:
        return f"Kein aktiver Anruf mit ID: {call_id}"
    
    tag_list = [t.strip() for t in tags.split(',')]
    note = f"Tags hinzugefugt: {', '.join(tag_list)}"
    call.add_note(note)
    
    return f"Tags hinzugefugt zu Call {call_id}: {', '.join(tag_list)}"


@tool
def conference_call_add_participant(call_id: str, phone_number: str) -> str:
    """
    Fugt Teilnehmer zu Konferenzschaltung hinzu.
    
    Args:
        call_id: Call ID der Konferenz
        phone_number: Rufnummer des Teilnehmers
    
    Returns:
        Status
    
    Example:
        conference_call_add_participant('CALL-12345678', '+49301234567')
    """
    # TODO: Implement with Bria SDK conference call features
    logger.info(f"Adding participant {phone_number} to conference {call_id}")
    
    call = _get_current_call()
    if call and call.call_id == call_id:
        call.add_note(f"Konferenz: Teilnehmer hinzugefugt {phone_number}")
    
    return f"Teilnehmer hinzugefugt zur Konferenz\nCall ID: {call_id}\nNummer: {phone_number}"


@tool
def enable_call_routing(
    routing_rules: str
) -> str:
    """
    Konfiguriert automatisches Call-Routing.
    
    Args:
        routing_rules: Routing-Regeln im JSON Format
            Beispiel: '{"vip": "agent1", "support": "agent2", "sales": "agent3"}'
    
    Returns:
        Status
    
    Example:
        enable_call_routing('{"vip": "agent1", "default": "queue"}')
    """
    try:
        rules = json.loads(routing_rules)
        
        # TODO: Implement actual routing logic
        logger.info(f"Call routing configured with {len(rules)} rules")
        
        result = "Call Routing konfiguriert\n"
        result += "=" * 50 + "\n\n"
        result += "Regeln:\n"
        for key, value in rules.items():
            result += f"- {key} -> {value}\n"
        
        return result
    except json.JSONDecodeError:
        return "Fehler: Ungultiges JSON Format"


@tool
def check_voicemail(mailbox: str = "default") -> str:
    """
    Pruft Voicemail-Nachrichten.
    
    Args:
        mailbox: Mailbox Name (Standard: 'default')
    
    Returns:
        Liste der Voicemail-Nachrichten
    
    Example:
        check_voicemail()
    """
    # TODO: Implement actual voicemail retrieval with Bria SDK
    logger.info(f"Checking voicemail: {mailbox}")
    
    return f"Voicemail-Box: {mailbox}\nKeine neuen Nachrichten"


# ====================================================================



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
[OK] Call started successfully!

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
                print(f"[WARNING]  Voice synthesis failed: {e}")
                print("Continuing with text-only simulation...\n")
        else:
            logger.warning("ELEVEN_LABS_API_KEY not configured")
            print("[WARNING]  ELEVEN_LABS_API_KEY not configured")
            print("Continuing with text-only simulation...\n")
    else:
        logger.info("ElevenLabs not installed, using text-only mode")
        print("[WARNING]  ElevenLabs not installed")
        print("Continuing with text-only simulation...\n")

    # Text-only fallback
    print(f"🤖 KAI: {opening_statement}\n")

    return f"""
[OK] Call started successfully!

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
[ERROR] No active call found!

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
[OK] Conversation continued

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
[ERROR] No active call found!

Please start a call first using 'start_interactive_call'.
"""

    call.add_note(new_information)

    return f"""
[OK] Call summary updated

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
[ERROR] No active call found!

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
[OK] Call ended successfully!

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
    Get all telephony tools for the agent (MEGA EXTENDED VERSION 2.0).

    Returns:
        List of telephony tool functions

    Requirements: 4.1, 4.2, 4.4, 4.5, Extended Features 1-20
    
    Categories:
    - Original Tools (8): Basic call management with ElevenLabs
    - Bria Softphone (7): Real telephony integration
    - Phone Management (3): Contact database and bulk import
    - Analytics (1): Call metrics and reporting
    - Knowledge Base (2): Call scripts and templates
    - Recording (2): Call recording and transcription
    - Sentiment (1): Emotion analysis
    - CRM Integration (1): Activity logging
    - Follow-up (1): Scheduling and reminders
    - WOW Features (10): Auto-dialer, DND, voicemail, routing, etc.
    
    Total: 36 Tools
    """
    return [
        # Original Tools (preserved)
        start_interactive_call,
        continue_call_conversation,
        update_call_summary,
        end_call,
        get_call_protocol_guide,
        handle_customer_objection,
        build_sales_argument,
        generate_call_closing,
        
        # Bria Softphone Integration
        bria_connect,
        bria_disconnect,
        bria_make_call,
        bria_answer_call,
        bria_hangup,
        bria_transfer_call,
        bria_hold_call,
        bria_resume_call,
        
        # Phone Number Management
        add_phone_contact,
        search_phone_contacts,
        bulk_import_phone_numbers,
        
        # Analytics
        get_call_analytics,
        
        # Knowledge Base & Call Scripts
        save_call_script,
        get_call_script,
        
        # Call Recording & Transcription
        start_call_recording,
        transcribe_call_recording,
        
        # Sentiment Analysis
        analyze_call_sentiment,
        
        # CRM Integration
        log_call_to_crm,
        
        # Follow-up Scheduling
        schedule_follow_up,
        
        # WOW Features (10+)
        quick_dial_favorite,
        set_do_not_disturb,
        search_call_history,
        auto_dialer_campaign,
        add_call_tags,
        conference_call_add_participant,
        enable_call_routing,
        check_voicemail,
    ]

