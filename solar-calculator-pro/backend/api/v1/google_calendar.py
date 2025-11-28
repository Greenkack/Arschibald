"""
Google Calendar Integration API

Provides REST API for Google Calendar integration:
- Google Calendar API connection
- Bidirectional appointment sync
- Appointment creation from CRM
- Appointment reminders
- Calendar view in CRM

Requirements: funktionen.txt - "Google Calendar Integration"
Task: 261. Google Calendar Integration
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import uuid

router = APIRouter(prefix="/calendar", tags=["Google Calendar"])


# ==================== Enums ====================

class EventStatus(str, Enum):
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class ReminderMethod(str, Enum):
    EMAIL = "email"
    POPUP = "popup"
    SMS = "sms"


class SyncDirection(str, Enum):
    TO_GOOGLE = "to_google"
    FROM_GOOGLE = "from_google"
    BIDIRECTIONAL = "bidirectional"


# ==================== Pydantic Models ====================

class CalendarCredentials(BaseModel):
    """Google Calendar OAuth credentials"""
    client_id: str
    client_secret: str
    redirect_uri: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None


class EventAttendee(BaseModel):
    """Event attendee"""
    email: str
    name: Optional[str] = None
    response_status: str = "needsAction"


class EventReminder(BaseModel):
    """Event reminder"""
    method: ReminderMethod = ReminderMethod.POPUP
    minutes_before: int = Field(default=30, ge=0, le=40320)


class CalendarEvent(BaseModel):
    """Calendar event"""
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    status: EventStatus = EventStatus.CONFIRMED
    attendees: List[EventAttendee] = []
    reminders: List[EventReminder] = []
    crm_lead_id: Optional[str] = None
    crm_customer_id: Optional[str] = None
    google_event_id: Optional[str] = None
    color_id: Optional[str] = None


class CreateEventRequest(BaseModel):
    """Request to create calendar event"""
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    attendees: List[EventAttendee] = []
    reminders: List[EventReminder] = [EventReminder()]
    crm_lead_id: Optional[str] = None
    crm_customer_id: Optional[str] = None
    send_notifications: bool = True


class SyncRequest(BaseModel):
    """Request for calendar sync"""
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_cancelled: bool = False


class SyncResult(BaseModel):
    """Result of calendar sync"""
    synced_to_google: int
    synced_from_google: int
    conflicts: int
    errors: List[str]
    last_sync: datetime


class CalendarSettings(BaseModel):
    """Calendar integration settings"""
    enabled: bool = True
    default_calendar_id: str = "primary"
    sync_interval_minutes: int = 15
    auto_create_events: bool = True
    default_reminder_minutes: int = 30
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL


# ==================== Mock Data Store ====================

_events_store: Dict[str, CalendarEvent] = {}
_settings: CalendarSettings = CalendarSettings()
_connected: bool = False


# ==================== Helper Functions ====================

def generate_event_id() -> str:
    """Generate unique event ID"""
    return f"evt_{uuid.uuid4().hex[:12]}"


def create_mock_events() -> List[CalendarEvent]:
    """Create mock calendar events"""
    now = datetime.now()
    return [
        CalendarEvent(
            id=generate_event_id(),
            title="Kundenbesuch - Familie Müller",
            description="Vor-Ort-Begehung für PV-Anlage",
            location="Musterstraße 123, 12345 Musterstadt",
            start_time=now + timedelta(days=1, hours=10),
            end_time=now + timedelta(days=1, hours=11, minutes=30),
            crm_customer_id="cust_001",
            attendees=[EventAttendee(email="mueller@example.com", name="Hans Müller")]
        ),
        CalendarEvent(
            id=generate_event_id(),
            title="Angebotspräsentation - Firma Schmidt",
            description="Präsentation des PV+Wärmepumpen-Angebots",
            location="Online Meeting",
            start_time=now + timedelta(days=2, hours=14),
            end_time=now + timedelta(days=2, hours=15),
            crm_lead_id="lead_002"
        ),
        CalendarEvent(
            id=generate_event_id(),
            title="Installation - Projekt Weber",
            description="Beginn der PV-Installation",
            location="Sonnenweg 45, 54321 Solarstadt",
            start_time=now + timedelta(days=5, hours=8),
            end_time=now + timedelta(days=5, hours=17),
            all_day=False,
            crm_customer_id="cust_003"
        )
    ]


# ==================== API Endpoints ====================

@router.get("/auth/status")
async def get_auth_status():
    """Get Google Calendar authentication status."""
    return {
        "connected": _connected,
        "account_email": "user@example.com" if _connected else None,
        "last_sync": datetime.now().isoformat() if _connected else None,
        "permissions": ["calendar.events", "calendar.readonly"] if _connected else []
    }


@router.post("/auth/connect")
async def connect_google_calendar(credentials: CalendarCredentials):
    """Connect to Google Calendar with OAuth credentials."""
    global _connected
    
    # Mock OAuth flow
    if not credentials.client_id or not credentials.client_secret:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    _connected = True
    
    # Initialize mock events
    for event in create_mock_events():
        _events_store[event.id] = event
    
    return {
        "status": "connected",
        "message": "Google Calendar erfolgreich verbunden",
        "account_email": "user@example.com",
        "calendars": [
            {"id": "primary", "name": "Hauptkalender", "primary": True},
            {"id": "work", "name": "Arbeit", "primary": False}
        ]
    }


@router.post("/auth/disconnect")
async def disconnect_google_calendar():
    """Disconnect from Google Calendar."""
    global _connected
    _connected = False
    _events_store.clear()
    
    return {
        "status": "disconnected",
        "message": "Google Calendar Verbindung getrennt"
    }


@router.get("/events")
async def get_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    crm_customer_id: Optional[str] = None,
    crm_lead_id: Optional[str] = None,
    limit: int = Query(default=50, le=100)
):
    """Get calendar events with optional filters."""
    events = list(_events_store.values())
    
    # Apply filters
    if start_date:
        events = [e for e in events if e.start_time >= start_date]
    if end_date:
        events = [e for e in events if e.end_time <= end_date]
    if crm_customer_id:
        events = [e for e in events if e.crm_customer_id == crm_customer_id]
    if crm_lead_id:
        events = [e for e in events if e.crm_lead_id == crm_lead_id]
    
    # Sort by start time
    events.sort(key=lambda e: e.start_time)
    
    return {
        "events": events[:limit],
        "total": len(events),
        "has_more": len(events) > limit
    }


@router.post("/events")
async def create_event(request: CreateEventRequest):
    """Create a new calendar event."""
    event_id = generate_event_id()
    
    event = CalendarEvent(
        id=event_id,
        title=request.title,
        description=request.description,
        location=request.location,
        start_time=request.start_time,
        end_time=request.end_time,
        all_day=request.all_day,
        attendees=request.attendees,
        reminders=request.reminders,
        crm_lead_id=request.crm_lead_id,
        crm_customer_id=request.crm_customer_id,
        google_event_id=f"google_{event_id}" if _connected else None
    )
    
    _events_store[event_id] = event
    
    return {
        "event": event,
        "synced_to_google": _connected,
        "notifications_sent": request.send_notifications and len(request.attendees) > 0
    }


@router.get("/events/{event_id}")
async def get_event(event_id: str):
    """Get a specific calendar event."""
    if event_id not in _events_store:
        raise HTTPException(status_code=404, detail="Event nicht gefunden")
    
    return {"event": _events_store[event_id]}


@router.put("/events/{event_id}")
async def update_event(event_id: str, request: CreateEventRequest):
    """Update a calendar event."""
    if event_id not in _events_store:
        raise HTTPException(status_code=404, detail="Event nicht gefunden")
    
    existing = _events_store[event_id]
    
    updated = CalendarEvent(
        id=event_id,
        title=request.title,
        description=request.description,
        location=request.location,
        start_time=request.start_time,
        end_time=request.end_time,
        all_day=request.all_day,
        attendees=request.attendees,
        reminders=request.reminders,
        crm_lead_id=request.crm_lead_id or existing.crm_lead_id,
        crm_customer_id=request.crm_customer_id or existing.crm_customer_id,
        google_event_id=existing.google_event_id
    )
    
    _events_store[event_id] = updated
    
    return {
        "event": updated,
        "synced_to_google": _connected
    }


@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """Delete a calendar event."""
    if event_id not in _events_store:
        raise HTTPException(status_code=404, detail="Event nicht gefunden")
    
    del _events_store[event_id]
    
    return {
        "deleted": True,
        "event_id": event_id,
        "synced_to_google": _connected
    }


@router.post("/sync")
async def sync_calendar(request: SyncRequest):
    """Sync calendar with Google Calendar."""
    if not _connected:
        raise HTTPException(status_code=400, detail="Google Calendar nicht verbunden")
    
    # Mock sync operation
    result = SyncResult(
        synced_to_google=len(_events_store),
        synced_from_google=3,
        conflicts=0,
        errors=[],
        last_sync=datetime.now()
    )
    
    return {
        "result": result,
        "message": "Synchronisation erfolgreich"
    }


@router.post("/events/from-crm")
async def create_event_from_crm(
    crm_type: str,
    crm_id: str,
    event_type: str = "appointment"
):
    """Create calendar event from CRM entity (lead or customer)."""
    # Mock CRM data lookup
    crm_data = {
        "name": "Max Mustermann",
        "email": "max@example.com",
        "address": "Musterstraße 1, 12345 Musterstadt",
        "phone": "+49 123 456789"
    }
    
    event_templates = {
        "appointment": {
            "title": f"Termin - {crm_data['name']}",
            "duration_hours": 1.5
        },
        "site_visit": {
            "title": f"Vor-Ort-Begehung - {crm_data['name']}",
            "duration_hours": 2
        },
        "presentation": {
            "title": f"Angebotspräsentation - {crm_data['name']}",
            "duration_hours": 1
        },
        "installation": {
            "title": f"Installation - {crm_data['name']}",
            "duration_hours": 8
        }
    }
    
    template = event_templates.get(event_type, event_templates["appointment"])
    start_time = datetime.now() + timedelta(days=1, hours=10)
    
    event_id = generate_event_id()
    event = CalendarEvent(
        id=event_id,
        title=template["title"],
        description=f"Automatisch erstellt aus CRM ({crm_type}: {crm_id})",
        location=crm_data["address"],
        start_time=start_time,
        end_time=start_time + timedelta(hours=template["duration_hours"]),
        attendees=[EventAttendee(email=crm_data["email"], name=crm_data["name"])],
        crm_lead_id=crm_id if crm_type == "lead" else None,
        crm_customer_id=crm_id if crm_type == "customer" else None
    )
    
    _events_store[event_id] = event
    
    return {
        "event": event,
        "crm_linked": True,
        "message": f"Termin für {crm_data['name']} erstellt"
    }


@router.get("/settings")
async def get_calendar_settings():
    """Get calendar integration settings."""
    return {"settings": _settings}


@router.put("/settings")
async def update_calendar_settings(settings: CalendarSettings):
    """Update calendar integration settings."""
    global _settings
    _settings = settings
    return {"settings": _settings, "updated": True}


@router.get("/upcoming")
async def get_upcoming_events(days: int = Query(default=7, le=30)):
    """Get upcoming events for the next N days."""
    now = datetime.now()
    end_date = now + timedelta(days=days)
    
    events = [
        e for e in _events_store.values()
        if now <= e.start_time <= end_date
    ]
    events.sort(key=lambda e: e.start_time)
    
    # Group by day
    grouped = {}
    for event in events:
        day_key = event.start_time.strftime("%Y-%m-%d")
        if day_key not in grouped:
            grouped[day_key] = []
        grouped[day_key].append(event)
    
    return {
        "events": events,
        "grouped_by_day": grouped,
        "total": len(events),
        "period_days": days
    }


@router.get("/health/check")
async def health_check():
    """Health check for Google Calendar service."""
    return {
        "status": "healthy",
        "service": "google-calendar",
        "connected": _connected,
        "events_count": len(_events_store),
        "timestamp": datetime.now().isoformat()
    }
