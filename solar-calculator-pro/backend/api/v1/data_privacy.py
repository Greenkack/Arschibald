"""
Data Privacy System
Task 187: GDPR compliance, data anonymization, and consent management
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import re


router = APIRouter(prefix="/privacy", tags=["Data Privacy"])


class ConsentType(str, Enum):
    ESSENTIAL = "essential"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    THIRD_PARTY = "third_party"
    DATA_PROCESSING = "data_processing"
    COMMUNICATION = "communication"


class DataCategory(str, Enum):
    PERSONAL = "personal"
    CONTACT = "contact"
    FINANCIAL = "financial"
    USAGE = "usage"
    TECHNICAL = "technical"
    PREFERENCES = "preferences"


class RetentionPeriod(str, Enum):
    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    YEAR_1 = "1_year"
    YEARS_3 = "3_years"
    YEARS_7 = "7_years"
    INDEFINITE = "indefinite"


class ConsentRecord(BaseModel):
    """User consent record"""
    user_id: str
    consent_type: ConsentType
    granted: bool
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    version: str = "1.0"


class PrivacySettings(BaseModel):
    """User privacy settings"""
    user_id: str
    data_collection_enabled: bool = True
    analytics_enabled: bool = False
    marketing_enabled: bool = False
    third_party_sharing: bool = False
    profile_visibility: str = "private"
    communication_preferences: Dict[str, bool] = {}


class DataExportRequest(BaseModel):
    """Data export request (GDPR Article 20)"""
    request_id: str
    user_id: str
    requested_at: datetime
    status: str  # pending, processing, completed, failed
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class DataDeletionRequest(BaseModel):
    """Data deletion request (GDPR Article 17)"""
    request_id: str
    user_id: str
    requested_at: datetime
    status: str  # pending, processing, completed, rejected
    reason: Optional[str] = None
    completed_at: Optional[datetime] = None
    deleted_categories: List[str] = []


class RetentionPolicy(BaseModel):
    """Data retention policy"""
    policy_id: str
    data_category: DataCategory
    retention_period: RetentionPeriod
    description: str
    legal_basis: str
    auto_delete: bool = True


class AnonymizationRule(BaseModel):
    """Data anonymization rule"""
    rule_id: str
    field_name: str
    anonymization_method: str  # hash, mask, remove, generalize
    description: str


# In-memory storage
consent_records: Dict[str, List[ConsentRecord]] = {}
privacy_settings: Dict[str, PrivacySettings] = {}
export_requests: List[DataExportRequest] = []
deletion_requests: List[DataDeletionRequest] = []

# Default retention policies
retention_policies = [
    RetentionPolicy(
        policy_id="personal_data",
        data_category=DataCategory.PERSONAL,
        retention_period=RetentionPeriod.YEARS_3,
        description="Personal identification data",
        legal_basis="Contract fulfillment",
        auto_delete=True
    ),
    RetentionPolicy(
        policy_id="contact_data",
        data_category=DataCategory.CONTACT,
        retention_period=RetentionPeriod.YEARS_3,
        description="Contact information",
        legal_basis="Contract fulfillment",
        auto_delete=True
    ),
    RetentionPolicy(
        policy_id="financial_data",
        data_category=DataCategory.FINANCIAL,
        retention_period=RetentionPeriod.YEARS_7,
        description="Financial and billing data",
        legal_basis="Legal obligation (tax records)",
        auto_delete=False
    ),
    RetentionPolicy(
        policy_id="usage_data",
        data_category=DataCategory.USAGE,
        retention_period=RetentionPeriod.YEAR_1,
        description="Application usage data",
        legal_basis="Legitimate interest",
        auto_delete=True
    ),
    RetentionPolicy(
        policy_id="technical_data",
        data_category=DataCategory.TECHNICAL,
        retention_period=RetentionPeriod.DAYS_90,
        description="Technical logs and diagnostics",
        legal_basis="Legitimate interest",
        auto_delete=True
    )
]

# Anonymization rules
anonymization_rules = [
    AnonymizationRule(
        rule_id="email",
        field_name="email",
        anonymization_method="mask",
        description="Mask email address (j***@example.com)"
    ),
    AnonymizationRule(
        rule_id="phone",
        field_name="phone",
        anonymization_method="mask",
        description="Mask phone number (***-***-1234)"
    ),
    AnonymizationRule(
        rule_id="name",
        field_name="name",
        anonymization_method="hash",
        description="Hash name to pseudonym"
    ),
    AnonymizationRule(
        rule_id="address",
        field_name="address",
        anonymization_method="generalize",
        description="Generalize to city/region only"
    ),
    AnonymizationRule(
        rule_id="ip_address",
        field_name="ip_address",
        anonymization_method="mask",
        description="Mask last octet (192.168.1.xxx)"
    )
]


def generate_request_id() -> str:
    """Generate unique request ID"""
    return hashlib.sha256(f"req_{datetime.now().isoformat()}".encode()).hexdigest()[:16]


def anonymize_email(email: str) -> str:
    """Anonymize email address"""
    if "@" not in email:
        return "***@***.***"
    local, domain = email.split("@")
    if len(local) > 2:
        return f"{local[0]}***@{domain}"
    return f"***@{domain}"


def anonymize_phone(phone: str) -> str:
    """Anonymize phone number"""
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 4:
        return f"***-***-{digits[-4:]}"
    return "***-***-****"


def anonymize_name(name: str) -> str:
    """Anonymize name using hash"""
    return f"User_{hashlib.sha256(name.encode()).hexdigest()[:8]}"


def anonymize_address(address: str) -> str:
    """Generalize address to city level"""
    # Simple implementation - would use geocoding in production
    parts = address.split(",")
    if len(parts) >= 2:
        return f"[City: {parts[-2].strip()}]"
    return "[Address Anonymized]"


def anonymize_ip(ip: str) -> str:
    """Anonymize IP address"""
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.{parts[2]}.xxx"
    return "xxx.xxx.xxx.xxx"


def anonymize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Anonymize data according to rules"""
    anonymized = data.copy()
    
    for rule in anonymization_rules:
        if rule.field_name in anonymized:
            value = anonymized[rule.field_name]
            
            if rule.anonymization_method == "mask":
                if rule.field_name == "email":
                    anonymized[rule.field_name] = anonymize_email(value)
                elif rule.field_name == "phone":
                    anonymized[rule.field_name] = anonymize_phone(value)
                elif rule.field_name == "ip_address":
                    anonymized[rule.field_name] = anonymize_ip(value)
                    
            elif rule.anonymization_method == "hash":
                anonymized[rule.field_name] = anonymize_name(value)
                
            elif rule.anonymization_method == "generalize":
                anonymized[rule.field_name] = anonymize_address(value)
                
            elif rule.anonymization_method == "remove":
                del anonymized[rule.field_name]
                
    return anonymized


# Consent Management Endpoints

@router.post("/consent")
async def record_consent(
    user_id: str,
    consent_type: ConsentType,
    granted: bool,
    ip_address: Optional[str] = None
):
    """Record user consent"""
    record = ConsentRecord(
        user_id=user_id,
        consent_type=consent_type,
        granted=granted,
        granted_at=datetime.now() if granted else None,
        revoked_at=datetime.now() if not granted else None,
        ip_address=ip_address
    )
    
    if user_id not in consent_records:
        consent_records[user_id] = []
    consent_records[user_id].append(record)
    
    return {"status": "recorded", "consent": record}


@router.get("/consent/{user_id}")
async def get_user_consents(user_id: str):
    """Get all consents for a user"""
    if user_id not in consent_records:
        return {"user_id": user_id, "consents": []}
        
    # Get latest consent for each type
    latest_consents = {}
    for record in consent_records[user_id]:
        consent_type = record.consent_type.value
        if consent_type not in latest_consents:
            latest_consents[consent_type] = record
        elif record.granted_at and latest_consents[consent_type].granted_at:
            if record.granted_at > latest_consents[consent_type].granted_at:
                latest_consents[consent_type] = record
                
    return {
        "user_id": user_id,
        "consents": list(latest_consents.values())
    }


@router.post("/consent/{user_id}/revoke-all")
async def revoke_all_consents(user_id: str):
    """Revoke all non-essential consents"""
    revoked = []
    for consent_type in ConsentType:
        if consent_type != ConsentType.ESSENTIAL:
            record = ConsentRecord(
                user_id=user_id,
                consent_type=consent_type,
                granted=False,
                revoked_at=datetime.now()
            )
            if user_id not in consent_records:
                consent_records[user_id] = []
            consent_records[user_id].append(record)
            revoked.append(consent_type.value)
            
    return {"status": "revoked", "revoked_consents": revoked}


# Privacy Settings Endpoints

@router.get("/settings/{user_id}", response_model=PrivacySettings)
async def get_privacy_settings(user_id: str):
    """Get user privacy settings"""
    if user_id in privacy_settings:
        return privacy_settings[user_id]
        
    # Return default settings
    return PrivacySettings(user_id=user_id)


@router.put("/settings/{user_id}", response_model=PrivacySettings)
async def update_privacy_settings(user_id: str, settings: PrivacySettings):
    """Update user privacy settings"""
    settings.user_id = user_id
    privacy_settings[user_id] = settings
    return settings


# Data Export (GDPR Article 20)

@router.post("/export-request")
async def request_data_export(user_id: str):
    """Request data export (Right to Data Portability)"""
    request = DataExportRequest(
        request_id=generate_request_id(),
        user_id=user_id,
        requested_at=datetime.now(),
        status="pending"
    )
    export_requests.append(request)
    
    return {
        "status": "accepted",
        "request_id": request.request_id,
        "message": "Your data export request has been received. You will be notified when ready."
    }


@router.get("/export-request/{request_id}")
async def get_export_status(request_id: str):
    """Get data export request status"""
    for request in export_requests:
        if request.request_id == request_id:
            return request
            
    raise HTTPException(status_code=404, detail="Export request not found")


@router.post("/export-request/{request_id}/complete")
async def complete_export_request(request_id: str, download_url: str):
    """Mark export request as complete (admin)"""
    for request in export_requests:
        if request.request_id == request_id:
            request.status = "completed"
            request.completed_at = datetime.now()
            request.download_url = download_url
            request.expires_at = datetime.now() + timedelta(days=7)
            return request
            
    raise HTTPException(status_code=404, detail="Export request not found")


# Data Deletion (GDPR Article 17)

@router.post("/deletion-request")
async def request_data_deletion(user_id: str, reason: Optional[str] = None):
    """Request data deletion (Right to be Forgotten)"""
    request = DataDeletionRequest(
        request_id=generate_request_id(),
        user_id=user_id,
        requested_at=datetime.now(),
        status="pending",
        reason=reason
    )
    deletion_requests.append(request)
    
    return {
        "status": "accepted",
        "request_id": request.request_id,
        "message": "Your data deletion request has been received. Processing may take up to 30 days."
    }


@router.get("/deletion-request/{request_id}")
async def get_deletion_status(request_id: str):
    """Get data deletion request status"""
    for request in deletion_requests:
        if request.request_id == request_id:
            return request
            
    raise HTTPException(status_code=404, detail="Deletion request not found")


@router.post("/deletion-request/{request_id}/complete")
async def complete_deletion_request(request_id: str, deleted_categories: List[str]):
    """Mark deletion request as complete (admin)"""
    for request in deletion_requests:
        if request.request_id == request_id:
            request.status = "completed"
            request.completed_at = datetime.now()
            request.deleted_categories = deleted_categories
            return request
            
    raise HTTPException(status_code=404, detail="Deletion request not found")


# Retention Policies

@router.get("/retention-policies", response_model=List[RetentionPolicy])
async def get_retention_policies():
    """Get all data retention policies"""
    return retention_policies


@router.get("/retention-policies/{category}")
async def get_retention_policy(category: DataCategory):
    """Get retention policy for a data category"""
    for policy in retention_policies:
        if policy.data_category == category:
            return policy
            
    raise HTTPException(status_code=404, detail="Policy not found")


# Anonymization

@router.post("/anonymize")
async def anonymize_user_data(data: Dict[str, Any]):
    """Anonymize user data according to rules"""
    return {
        "original_fields": list(data.keys()),
        "anonymized_data": anonymize_data(data)
    }


@router.get("/anonymization-rules", response_model=List[AnonymizationRule])
async def get_anonymization_rules():
    """Get all anonymization rules"""
    return anonymization_rules


# GDPR Compliance Dashboard

@router.get("/gdpr-dashboard")
async def get_gdpr_dashboard():
    """Get GDPR compliance dashboard"""
    pending_exports = sum(1 for r in export_requests if r.status == "pending")
    pending_deletions = sum(1 for r in deletion_requests if r.status == "pending")
    
    return {
        "compliance_status": "compliant",
        "pending_requests": {
            "data_exports": pending_exports,
            "data_deletions": pending_deletions
        },
        "retention_policies_active": len(retention_policies),
        "anonymization_rules_active": len(anonymization_rules),
        "consent_types_tracked": len(ConsentType),
        "recent_activity": {
            "exports_last_30_days": sum(
                1 for r in export_requests
                if r.requested_at >= datetime.now() - timedelta(days=30)
            ),
            "deletions_last_30_days": sum(
                1 for r in deletion_requests
                if r.requested_at >= datetime.now() - timedelta(days=30)
            )
        },
        "gdpr_articles_implemented": [
            "Article 6 - Lawful Processing (Consent Management)",
            "Article 7 - Conditions for Consent",
            "Article 13/14 - Information to Data Subject",
            "Article 15 - Right of Access",
            "Article 17 - Right to Erasure",
            "Article 20 - Right to Data Portability",
            "Article 25 - Data Protection by Design"
        ]
    }


@router.get("/privacy-policy")
async def get_privacy_policy_info():
    """Get privacy policy information"""
    return {
        "version": "1.0",
        "last_updated": "2025-11-29",
        "data_controller": {
            "name": "Solar Calculator Pro",
            "contact": "privacy@solarcalculator.example.com"
        },
        "data_categories_collected": [
            {"category": "Personal Data", "examples": ["Name", "Email", "Phone"]},
            {"category": "Contact Data", "examples": ["Address", "City", "Postal Code"]},
            {"category": "Financial Data", "examples": ["Offers", "Invoices"]},
            {"category": "Usage Data", "examples": ["Calculations", "Projects"]},
            {"category": "Technical Data", "examples": ["IP Address", "Browser Info"]}
        ],
        "purposes": [
            "Providing solar calculation services",
            "Generating offers and proposals",
            "Customer relationship management",
            "Service improvement and analytics"
        ],
        "legal_bases": [
            "Contract fulfillment",
            "Consent",
            "Legitimate interest",
            "Legal obligation"
        ],
        "data_subject_rights": [
            "Right to access your data",
            "Right to rectification",
            "Right to erasure (right to be forgotten)",
            "Right to data portability",
            "Right to object to processing",
            "Right to withdraw consent"
        ]
    }
