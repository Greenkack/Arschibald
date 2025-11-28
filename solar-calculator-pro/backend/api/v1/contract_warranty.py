"""
Contract and Warranty Management API

Provides REST API for contract and warranty management:
- Contract creation and management
- Warranty tracking system
- Maintenance contract management
- Contract renewal reminders
- Contract document generation

Requirements: funktionen.txt - "ContractManager"
Task: 264. Contract and Warranty Management
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import uuid

router = APIRouter(prefix="/contracts", tags=["Contract & Warranty"])


# ==================== Enums ====================

class ContractType(str, Enum):
    PURCHASE = "purchase"
    INSTALLATION = "installation"
    MAINTENANCE = "maintenance"
    SERVICE = "service"
    LEASE = "lease"
    WARRANTY_EXTENSION = "warranty_extension"


class ContractStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    RENEWED = "renewed"


class WarrantyType(str, Enum):
    MANUFACTURER = "manufacturer"
    INSTALLER = "installer"
    EXTENDED = "extended"
    PERFORMANCE = "performance"


class WarrantyStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CLAIMED = "claimed"
    VOID = "void"


class ReminderType(str, Enum):
    RENEWAL = "renewal"
    EXPIRY = "expiry"
    MAINTENANCE_DUE = "maintenance_due"
    WARRANTY_EXPIRY = "warranty_expiry"


# ==================== Pydantic Models ====================

class ContractParty(BaseModel):
    """Contract party (customer or company)"""
    name: str
    address: str
    email: Optional[str] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None


class ContractItem(BaseModel):
    """Item covered by contract"""
    product_id: str
    product_name: str
    serial_number: Optional[str] = None
    quantity: int = 1
    unit_price_eur: float


class Contract(BaseModel):
    """Contract"""
    id: str
    contract_number: str
    contract_type: ContractType
    status: ContractStatus = ContractStatus.DRAFT
    customer: ContractParty
    company: ContractParty
    project_id: Optional[str] = None
    items: List[ContractItem] = []
    total_value_eur: float
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool = False
    renewal_period_months: int = 12
    payment_terms: str = "30 Tage netto"
    notes: Optional[str] = None
    document_url: Optional[str] = None
    signed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class CreateContractRequest(BaseModel):
    """Request to create contract"""
    contract_type: ContractType
    customer: ContractParty
    project_id: Optional[str] = None
    items: List[ContractItem] = []
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool = False
    renewal_period_months: int = 12
    payment_terms: str = "30 Tage netto"
    notes: Optional[str] = None


class Warranty(BaseModel):
    """Warranty"""
    id: str
    warranty_type: WarrantyType
    status: WarrantyStatus = WarrantyStatus.ACTIVE
    contract_id: Optional[str] = None
    customer_id: str
    product_id: str
    product_name: str
    serial_number: Optional[str] = None
    manufacturer: str
    start_date: datetime
    end_date: datetime
    coverage_details: str
    terms_url: Optional[str] = None
    claim_count: int = 0
    created_at: datetime
    updated_at: datetime


class CreateWarrantyRequest(BaseModel):
    """Request to create warranty"""
    warranty_type: WarrantyType
    contract_id: Optional[str] = None
    customer_id: str
    product_id: str
    product_name: str
    serial_number: Optional[str] = None
    manufacturer: str
    start_date: datetime
    duration_years: int = 2
    coverage_details: str


class WarrantyClaim(BaseModel):
    """Warranty claim"""
    id: str
    warranty_id: str
    claim_date: datetime
    issue_description: str
    resolution: Optional[str] = None
    status: str = "pending"
    resolved_at: Optional[datetime] = None


class MaintenanceSchedule(BaseModel):
    """Maintenance schedule"""
    id: str
    contract_id: str
    customer_id: str
    system_type: str
    last_maintenance: Optional[datetime] = None
    next_maintenance: datetime
    interval_months: int = 12
    tasks: List[str]
    estimated_duration_hours: float
    estimated_cost_eur: float


class ContractReminder(BaseModel):
    """Contract reminder"""
    id: str
    contract_id: Optional[str] = None
    warranty_id: Optional[str] = None
    reminder_type: ReminderType
    due_date: datetime
    message: str
    sent: bool = False
    sent_at: Optional[datetime] = None


# ==================== Mock Data Store ====================

_contracts_store: Dict[str, Contract] = {}
_warranties_store: Dict[str, Warranty] = {}
_claims_store: Dict[str, WarrantyClaim] = {}
_maintenance_store: Dict[str, MaintenanceSchedule] = {}
_reminders_store: Dict[str, ContractReminder] = {}

_contract_counter = 1000


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def generate_contract_number() -> str:
    global _contract_counter
    _contract_counter += 1
    return f"VTR-{datetime.now().year}-{_contract_counter:05d}"


def get_company_info() -> ContractParty:
    return ContractParty(
        name="Solar Calculator Pro GmbH",
        address="Solarstraße 1, 12345 Sonnenstadt",
        email="vertraege@solar-calculator-pro.de",
        phone="+49 123 456789",
        tax_id="DE123456789"
    )


def create_mock_data():
    """Create mock contracts and warranties"""
    now = datetime.now()
    
    # Mock contract
    contract_id = generate_id("ctr")
    contract = Contract(
        id=contract_id,
        contract_number=generate_contract_number(),
        contract_type=ContractType.INSTALLATION,
        status=ContractStatus.ACTIVE,
        customer=ContractParty(
            name="Familie Müller",
            address="Musterstraße 123, 12345 Musterstadt",
            email="mueller@example.com"
        ),
        company=get_company_info(),
        project_id="proj_001",
        items=[
            ContractItem(product_id="mod_001", product_name="PV-Modul 400W", quantity=20, unit_price_eur=180),
            ContractItem(product_id="inv_001", product_name="Wechselrichter 8kW", quantity=1, unit_price_eur=1800),
            ContractItem(product_id="bat_001", product_name="Batteriespeicher 10kWh", quantity=1, unit_price_eur=6500)
        ],
        total_value_eur=11900,
        start_date=now - timedelta(days=30),
        end_date=now + timedelta(days=335),
        signed_at=now - timedelta(days=30),
        created_at=now - timedelta(days=35),
        updated_at=now - timedelta(days=30)
    )
    _contracts_store[contract_id] = contract
    
    # Mock warranty
    warranty_id = generate_id("war")
    warranty = Warranty(
        id=warranty_id,
        warranty_type=WarrantyType.MANUFACTURER,
        status=WarrantyStatus.ACTIVE,
        contract_id=contract_id,
        customer_id="cust_001",
        product_id="mod_001",
        product_name="PV-Module 400W (20 Stück)",
        manufacturer="SolarTech GmbH",
        start_date=now - timedelta(days=30),
        end_date=now + timedelta(days=365*25),
        coverage_details="25 Jahre Leistungsgarantie, 12 Jahre Produktgarantie",
        created_at=now - timedelta(days=30),
        updated_at=now - timedelta(days=30)
    )
    _warranties_store[warranty_id] = warranty


create_mock_data()


# ==================== Contract Endpoints ====================

@router.get("/")
async def get_contracts(
    contract_type: Optional[ContractType] = None,
    status: Optional[ContractStatus] = None,
    customer_name: Optional[str] = None,
    limit: int = Query(default=50, le=100)
):
    """Get all contracts with optional filters."""
    contracts = list(_contracts_store.values())
    
    if contract_type:
        contracts = [c for c in contracts if c.contract_type == contract_type]
    if status:
        contracts = [c for c in contracts if c.status == status]
    if customer_name:
        contracts = [c for c in contracts if customer_name.lower() in c.customer.name.lower()]
    
    contracts.sort(key=lambda c: c.created_at, reverse=True)
    
    return {
        "contracts": contracts[:limit],
        "total": len(contracts),
        "by_status": {s.value: len([c for c in contracts if c.status == s]) for s in ContractStatus}
    }


@router.post("/")
async def create_contract(request: CreateContractRequest):
    """Create a new contract."""
    contract_id = generate_id("ctr")
    now = datetime.now()
    
    total_value = sum(item.quantity * item.unit_price_eur for item in request.items)
    
    contract = Contract(
        id=contract_id,
        contract_number=generate_contract_number(),
        contract_type=request.contract_type,
        status=ContractStatus.DRAFT,
        customer=request.customer,
        company=get_company_info(),
        project_id=request.project_id,
        items=request.items,
        total_value_eur=total_value,
        start_date=request.start_date,
        end_date=request.end_date,
        auto_renew=request.auto_renew,
        renewal_period_months=request.renewal_period_months,
        payment_terms=request.payment_terms,
        notes=request.notes,
        created_at=now,
        updated_at=now
    )
    
    _contracts_store[contract_id] = contract
    
    return {"contract": contract, "message": "Vertrag erfolgreich erstellt"}


@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    """Get a specific contract."""
    if contract_id not in _contracts_store:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    
    contract = _contracts_store[contract_id]
    warranties = [w for w in _warranties_store.values() if w.contract_id == contract_id]
    
    return {
        "contract": contract,
        "warranties": warranties,
        "warranty_count": len(warranties)
    }


@router.put("/{contract_id}")
async def update_contract(contract_id: str, request: CreateContractRequest):
    """Update a contract."""
    if contract_id not in _contracts_store:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    
    existing = _contracts_store[contract_id]
    total_value = sum(item.quantity * item.unit_price_eur for item in request.items)
    
    updated = Contract(
        id=contract_id,
        contract_number=existing.contract_number,
        contract_type=request.contract_type,
        status=existing.status,
        customer=request.customer,
        company=existing.company,
        project_id=request.project_id,
        items=request.items,
        total_value_eur=total_value,
        start_date=request.start_date,
        end_date=request.end_date,
        auto_renew=request.auto_renew,
        renewal_period_months=request.renewal_period_months,
        payment_terms=request.payment_terms,
        notes=request.notes,
        document_url=existing.document_url,
        signed_at=existing.signed_at,
        created_at=existing.created_at,
        updated_at=datetime.now()
    )
    
    _contracts_store[contract_id] = updated
    
    return {"contract": updated, "updated": True}


@router.put("/{contract_id}/status")
async def update_contract_status(contract_id: str, status: ContractStatus):
    """Update contract status."""
    if contract_id not in _contracts_store:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    
    contract = _contracts_store[contract_id]
    contract.status = status
    contract.updated_at = datetime.now()
    
    if status == ContractStatus.ACTIVE and not contract.signed_at:
        contract.signed_at = datetime.now()
    
    return {"contract": contract, "updated": True}


@router.post("/{contract_id}/renew")
async def renew_contract(contract_id: str):
    """Renew a contract."""
    if contract_id not in _contracts_store:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    
    old_contract = _contracts_store[contract_id]
    old_contract.status = ContractStatus.RENEWED
    
    new_id = generate_id("ctr")
    now = datetime.now()
    new_start = old_contract.end_date or now
    new_end = new_start + timedelta(days=old_contract.renewal_period_months * 30)
    
    new_contract = Contract(
        id=new_id,
        contract_number=generate_contract_number(),
        contract_type=old_contract.contract_type,
        status=ContractStatus.ACTIVE,
        customer=old_contract.customer,
        company=old_contract.company,
        project_id=old_contract.project_id,
        items=old_contract.items,
        total_value_eur=old_contract.total_value_eur,
        start_date=new_start,
        end_date=new_end,
        auto_renew=old_contract.auto_renew,
        renewal_period_months=old_contract.renewal_period_months,
        payment_terms=old_contract.payment_terms,
        notes=f"Verlängerung von {old_contract.contract_number}",
        created_at=now,
        updated_at=now
    )
    
    _contracts_store[new_id] = new_contract
    
    return {
        "old_contract": old_contract,
        "new_contract": new_contract,
        "message": "Vertrag erfolgreich verlängert"
    }


@router.post("/{contract_id}/generate-document")
async def generate_contract_document(contract_id: str):
    """Generate contract document (PDF)."""
    if contract_id not in _contracts_store:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    
    contract = _contracts_store[contract_id]
    doc_url = f"/documents/contracts/{contract.contract_number}.pdf"
    contract.document_url = doc_url
    contract.updated_at = datetime.now()
    
    return {
        "contract": contract,
        "document_url": doc_url,
        "message": "Vertragsdokument erstellt"
    }


# ==================== Warranty Endpoints ====================

@router.get("/warranties")
async def get_warranties(
    warranty_type: Optional[WarrantyType] = None,
    status: Optional[WarrantyStatus] = None,
    customer_id: Optional[str] = None,
    expiring_within_days: Optional[int] = None
):
    """Get all warranties with optional filters."""
    warranties = list(_warranties_store.values())
    
    if warranty_type:
        warranties = [w for w in warranties if w.warranty_type == warranty_type]
    if status:
        warranties = [w for w in warranties if w.status == status]
    if customer_id:
        warranties = [w for w in warranties if w.customer_id == customer_id]
    if expiring_within_days:
        cutoff = datetime.now() + timedelta(days=expiring_within_days)
        warranties = [w for w in warranties if w.end_date <= cutoff]
    
    return {
        "warranties": warranties,
        "total": len(warranties),
        "expiring_soon": len([w for w in warranties if w.end_date <= datetime.now() + timedelta(days=90)])
    }


@router.post("/warranties")
async def create_warranty(request: CreateWarrantyRequest):
    """Create a new warranty."""
    warranty_id = generate_id("war")
    now = datetime.now()
    
    warranty = Warranty(
        id=warranty_id,
        warranty_type=request.warranty_type,
        status=WarrantyStatus.ACTIVE,
        contract_id=request.contract_id,
        customer_id=request.customer_id,
        product_id=request.product_id,
        product_name=request.product_name,
        serial_number=request.serial_number,
        manufacturer=request.manufacturer,
        start_date=request.start_date,
        end_date=request.start_date + timedelta(days=365 * request.duration_years),
        coverage_details=request.coverage_details,
        created_at=now,
        updated_at=now
    )
    
    _warranties_store[warranty_id] = warranty
    
    return {"warranty": warranty, "message": "Garantie erfolgreich erstellt"}


@router.get("/warranties/{warranty_id}")
async def get_warranty(warranty_id: str):
    """Get a specific warranty."""
    if warranty_id not in _warranties_store:
        raise HTTPException(status_code=404, detail="Garantie nicht gefunden")
    
    warranty = _warranties_store[warranty_id]
    claims = [c for c in _claims_store.values() if c.warranty_id == warranty_id]
    
    days_remaining = (warranty.end_date - datetime.now()).days
    
    return {
        "warranty": warranty,
        "claims": claims,
        "days_remaining": max(0, days_remaining),
        "is_valid": warranty.status == WarrantyStatus.ACTIVE and days_remaining > 0
    }


@router.post("/warranties/{warranty_id}/claim")
async def create_warranty_claim(warranty_id: str, issue_description: str):
    """Create a warranty claim."""
    if warranty_id not in _warranties_store:
        raise HTTPException(status_code=404, detail="Garantie nicht gefunden")
    
    warranty = _warranties_store[warranty_id]
    
    if warranty.status != WarrantyStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Garantie ist nicht aktiv")
    
    if warranty.end_date < datetime.now():
        raise HTTPException(status_code=400, detail="Garantie ist abgelaufen")
    
    claim_id = generate_id("clm")
    claim = WarrantyClaim(
        id=claim_id,
        warranty_id=warranty_id,
        claim_date=datetime.now(),
        issue_description=issue_description
    )
    
    _claims_store[claim_id] = claim
    warranty.claim_count += 1
    
    return {"claim": claim, "message": "Garantieanspruch eingereicht"}


# ==================== Maintenance Endpoints ====================

@router.get("/maintenance")
async def get_maintenance_schedules(
    customer_id: Optional[str] = None,
    due_within_days: Optional[int] = None
):
    """Get maintenance schedules."""
    schedules = list(_maintenance_store.values())
    
    if customer_id:
        schedules = [s for s in schedules if s.customer_id == customer_id]
    if due_within_days:
        cutoff = datetime.now() + timedelta(days=due_within_days)
        schedules = [s for s in schedules if s.next_maintenance <= cutoff]
    
    return {
        "schedules": schedules,
        "total": len(schedules),
        "due_soon": len([s for s in schedules if s.next_maintenance <= datetime.now() + timedelta(days=30)])
    }


@router.get("/reminders")
async def get_reminders(
    reminder_type: Optional[ReminderType] = None,
    pending_only: bool = True
):
    """Get contract and warranty reminders."""
    reminders = list(_reminders_store.values())
    
    if reminder_type:
        reminders = [r for r in reminders if r.reminder_type == reminder_type]
    if pending_only:
        reminders = [r for r in reminders if not r.sent]
    
    reminders.sort(key=lambda r: r.due_date)
    
    return {
        "reminders": reminders,
        "total": len(reminders),
        "pending": len([r for r in reminders if not r.sent])
    }


@router.get("/dashboard")
async def get_contracts_dashboard():
    """Get contracts and warranties dashboard."""
    contracts = list(_contracts_store.values())
    warranties = list(_warranties_store.values())
    now = datetime.now()
    
    return {
        "contracts": {
            "total": len(contracts),
            "active": len([c for c in contracts if c.status == ContractStatus.ACTIVE]),
            "expiring_soon": len([c for c in contracts if c.end_date and c.end_date <= now + timedelta(days=30)]),
            "total_value_eur": sum(c.total_value_eur for c in contracts)
        },
        "warranties": {
            "total": len(warranties),
            "active": len([w for w in warranties if w.status == WarrantyStatus.ACTIVE]),
            "expiring_soon": len([w for w in warranties if w.end_date <= now + timedelta(days=90)]),
            "claims_pending": len([c for c in _claims_store.values() if c.status == "pending"])
        },
        "maintenance": {
            "scheduled": len(_maintenance_store),
            "due_this_month": len([m for m in _maintenance_store.values() if m.next_maintenance <= now + timedelta(days=30)])
        }
    }


@router.get("/health/check")
async def health_check():
    """Health check for contract and warranty service."""
    return {
        "status": "healthy",
        "service": "contract-warranty",
        "contracts_count": len(_contracts_store),
        "warranties_count": len(_warranties_store),
        "timestamp": datetime.now().isoformat()
    }
