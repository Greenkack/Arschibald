# License Management Service

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.models.license_models import (
    License, LicenseValidation, LicenseFeature, LicenseRenewal,
    LicenseType, LicenseStatus
)
from backend.models.license_schemas import (
    LicenseCreate, LicenseUpdate, LicenseResponse,
    LicenseValidationRequest, LicenseValidationResponse,
    LicenseRenewalRequest, LicenseRenewalResponse,
    LicenseFeatureCreate, LicenseFeatureResponse,
    LicenseReportRequest, LicenseReportResponse,
    LicenseActivationRequest, LicenseActivationResponse
)


class LicenseService:
    """Service for managing licenses"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_license_key(self, license_type: LicenseType, user_email: str) -> str:
        """Generate a unique license key"""
        # Create a unique string from type, email, and random data
        unique_string = f"{license_type.value}:{user_email}:{secrets.token_hex(16)}"
        
        # Hash it
        hash_obj = hashlib.sha256(unique_string.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Format as XXXX-XXXX-XXXX-XXXX-XXXX
        key_parts = [hash_hex[i:i+4].upper() for i in range(0, 20, 4)]
        return "-".join(key_parts)
    
    def create_license(self, license_data: LicenseCreate, created_by: Optional[str] = None) -> LicenseResponse:
        """Create a new license"""
        # Generate license key
        license_key = self.generate_license_key(
            LicenseType(license_data.license_type),
            license_data.user_email
        )
        
        # Set default expiry based on license type
        if license_data.expires_at is None:
            if license_data.license_type == "trial":
                license_data.expires_at = datetime.utcnow() + timedelta(days=30)
            elif license_data.license_type == "lifetime":
                license_data.expires_at = None
            else:
                license_data.expires_at = datetime.utcnow() + timedelta(days=365)
        
        # Create license
        license = License(
            license_key=license_key,
            license_type=LicenseType(license_data.license_type),
            status=LicenseStatus.PENDING,
            user_email=license_data.user_email,
            organization_name=license_data.organization_name,
            expires_at=license_data.expires_at,
            enabled_features=license_data.enabled_features,
            max_users=license_data.max_users,
            max_projects=license_data.max_projects,
            max_calculations_per_month=license_data.max_calculations_per_month,
            hardware_id=license_data.hardware_id,
            machine_name=license_data.machine_name,
            notes=license_data.notes,
            metadata=license_data.metadata,
            created_by=created_by
        )
        
        self.db.add(license)
        self.db.commit()
        self.db.refresh(license)
        
        return self._to_response(license)
    
    def get_license(self, license_id: int) -> Optional[LicenseResponse]:
        """Get license by ID"""
        license = self.db.query(License).filter(License.id == license_id).first()
        return self._to_response(license) if license else None
    
    def get_license_by_key(self, license_key: str) -> Optional[LicenseResponse]:
        """Get license by key"""
        license = self.db.query(License).filter(License.license_key == license_key).first()
        return self._to_response(license) if license else None
    
    def update_license(self, license_id: int, license_data: LicenseUpdate, updated_by: Optional[str] = None) -> Optional[LicenseResponse]:
        """Update a license"""
        license = self.db.query(License).filter(License.id == license_id).first()
        
        if not license:
            return None
        
        # Update fields
        update_data = license_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(license, field, value)
        
        license.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(license)
        
        return self._to_response(license)
    
    def activate_license(self, activation_data: LicenseActivationRequest) -> LicenseActivationResponse:
        """Activate a license"""
        license = self.db.query(License).filter(
            License.license_key == activation_data.license_key
        ).first()
        
        if not license:
            return LicenseActivationResponse(
                success=False,
                message="License key not found"
            )
        
        if license.status != LicenseStatus.PENDING:
            return LicenseActivationResponse(
                success=False,
                message=f"License is already {license.status.value}"
            )
        
        # Check if hardware binding is required
        if license.hardware_id and license.hardware_id != activation_data.hardware_id:
            return LicenseActivationResponse(
                success=False,
                message="Hardware ID mismatch"
            )
        
        # Activate license
        license.status = LicenseStatus.ACTIVE
        license.activated_at = datetime.utcnow()
        license.hardware_id = activation_data.hardware_id
        license.machine_name = activation_data.machine_name
        
        self.db.commit()
        self.db.refresh(license)
        
        return LicenseActivationResponse(
            success=True,
            message="License activated successfully",
            license=self._to_response(license)
        )
    
    def validate_license(
        self,
        validation_data: LicenseValidationRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> LicenseValidationResponse:
        """Validate a license"""
        license = self.db.query(License).filter(
            License.license_key == validation_data.license_key
        ).first()
        
        if not license:
            self._log_validation(
                license_key=validation_data.license_key,
                is_valid=False,
                message="License key not found",
                hardware_id=validation_data.hardware_id,
                machine_name=validation_data.machine_name,
                ip_address=ip_address,
                user_agent=user_agent
            )
            return LicenseValidationResponse(
                is_valid=False,
                license_key=validation_data.license_key,
                status=LicenseStatus.REVOKED,
                license_type=LicenseType.TRIAL,
                message="License key not found",
                expires_at=None,
                days_until_expiry=None,
                enabled_features={},
                feature_access={},
                warnings=[]
            )
        
        # Check status
        if license.status != LicenseStatus.ACTIVE:
            self._log_validation(
                license_id=license.id,
                license_key=license.license_key,
                is_valid=False,
                message=f"License is {license.status.value}",
                hardware_id=validation_data.hardware_id,
                machine_name=validation_data.machine_name,
                ip_address=ip_address,
                user_agent=user_agent
            )
            return LicenseValidationResponse(
                is_valid=False,
                license_key=license.license_key,
                status=license.status,
                license_type=license.license_type,
                message=f"License is {license.status.value}",
                expires_at=license.expires_at,
                days_until_expiry=self._calculate_days_until_expiry(license.expires_at),
                enabled_features=license.enabled_features,
                feature_access={},
                warnings=[]
            )
        
        # Check expiry
        warnings = []
        if license.expires_at and license.expires_at < datetime.utcnow():
            license.status = LicenseStatus.EXPIRED
            self.db.commit()
            
            self._log_validation(
                license_id=license.id,
                license_key=license.license_key,
                is_valid=False,
                message="License has expired",
                hardware_id=validation_data.hardware_id,
                machine_name=validation_data.machine_name,
                ip_address=ip_address,
                user_agent=user_agent
            )
            return LicenseValidationResponse(
                is_valid=False,
                license_key=license.license_key,
                status=LicenseStatus.EXPIRED,
                license_type=license.license_type,
                message="License has expired",
                expires_at=license.expires_at,
                days_until_expiry=self._calculate_days_until_expiry(license.expires_at),
                enabled_features=license.enabled_features,
                feature_access={},
                warnings=[]
            )
        
        # Check if expiring soon
        days_until_expiry = self._calculate_days_until_expiry(license.expires_at)
        if days_until_expiry is not None and days_until_expiry <= 30:
            warnings.append(f"License expires in {days_until_expiry} days")
        
        # Check hardware binding
        if validation_data.hardware_id:
            if license.hardware_id and license.hardware_id != validation_data.hardware_id:
                self._log_validation(
                    license_id=license.id,
                    license_key=license.license_key,
                    is_valid=False,
                    message="Hardware ID mismatch",
                    hardware_id=validation_data.hardware_id,
                    machine_name=validation_data.machine_name,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return LicenseValidationResponse(
                    is_valid=False,
                    license_key=license.license_key,
                    status=license.status,
                    license_type=license.license_type,
                    message="Hardware ID mismatch",
                    expires_at=license.expires_at,
                    days_until_expiry=days_until_expiry,
                    enabled_features=license.enabled_features,
                    feature_access={},
                    warnings=warnings
                )
        
        # Check feature access
        feature_access = {}
        if validation_data.features_to_check:
            feature_access = self._check_feature_access(
                license.license_type,
                license.enabled_features,
                validation_data.features_to_check
            )
        
        # Update last validated timestamp
        license.last_validated_at = datetime.utcnow()
        self.db.commit()
        
        # Log successful validation
        self._log_validation(
            license_id=license.id,
            license_key=license.license_key,
            is_valid=True,
            message="License is valid",
            hardware_id=validation_data.hardware_id,
            machine_name=validation_data.machine_name,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return LicenseValidationResponse(
            is_valid=True,
            license_key=license.license_key,
            status=license.status,
            license_type=license.license_type,
            message="License is valid",
            expires_at=license.expires_at,
            days_until_expiry=days_until_expiry,
            enabled_features=license.enabled_features,
            feature_access=feature_access,
            warnings=warnings
        )
    
    def renew_license(self, renewal_data: LicenseRenewalRequest, renewed_by: Optional[str] = None) -> Optional[LicenseRenewalResponse]:
        """Renew a license"""
        license = self.db.query(License).filter(
            License.license_key == renewal_data.license_key
        ).first()
        
        if not license:
            return None
        
        old_expires_at = license.expires_at
        
        # Calculate new expiry date
        if license.expires_at and license.expires_at > datetime.utcnow():
            # Extend from current expiry
            new_expires_at = license.expires_at + timedelta(days=renewal_data.renewal_period_days)
        else:
            # Extend from now
            new_expires_at = datetime.utcnow() + timedelta(days=renewal_data.renewal_period_days)
        
        # Update license
        license.expires_at = new_expires_at
        if license.status == LicenseStatus.EXPIRED:
            license.status = LicenseStatus.ACTIVE
        
        # Log renewal
        renewal = LicenseRenewal(
            license_id=license.id,
            license_key=license.license_key,
            old_expires_at=old_expires_at,
            new_expires_at=new_expires_at,
            renewal_period_days=renewal_data.renewal_period_days,
            payment_reference=renewal_data.payment_reference,
            payment_amount=renewal_data.payment_amount,
            payment_currency=renewal_data.payment_currency,
            renewed_by=renewed_by
        )
        
        self.db.add(renewal)
        self.db.commit()
        self.db.refresh(renewal)
        
        return LicenseRenewalResponse(
            license_id=license.id,
            license_key=license.license_key,
            old_expires_at=old_expires_at,
            new_expires_at=new_expires_at,
            renewal_period_days=renewal_data.renewal_period_days,
            renewed_at=renewal.renewed_at,
            message="License renewed successfully"
        )
    
    def get_license_report(self, report_request: LicenseReportRequest) -> LicenseReportResponse:
        """Generate license report"""
        query = self.db.query(License)
        
        # Apply filters
        if report_request.start_date:
            query = query.filter(License.created_at >= report_request.start_date)
        if report_request.end_date:
            query = query.filter(License.created_at <= report_request.end_date)
        if report_request.license_types:
            query = query.filter(License.license_type.in_(report_request.license_types))
        if report_request.statuses:
            query = query.filter(License.status.in_(report_request.statuses))
        
        licenses = query.all()
        
        # Calculate statistics
        total_licenses = len(licenses)
        active_licenses = sum(1 for l in licenses if l.status == LicenseStatus.ACTIVE)
        expired_licenses = sum(1 for l in licenses if l.status == LicenseStatus.EXPIRED)
        suspended_licenses = sum(1 for l in licenses if l.status == LicenseStatus.SUSPENDED)
        revoked_licenses = sum(1 for l in licenses if l.status == LicenseStatus.REVOKED)
        pending_licenses = sum(1 for l in licenses if l.status == LicenseStatus.PENDING)
        
        # Licenses by type
        licenses_by_type = {}
        for license_type in LicenseType:
            licenses_by_type[license_type.value] = sum(
                1 for l in licenses if l.license_type == license_type
            )
        
        # Licenses expiring soon (within 30 days)
        expiring_soon = []
        for license in licenses:
            if license.status == LicenseStatus.ACTIVE and license.expires_at:
                days_until_expiry = (license.expires_at - datetime.utcnow()).days
                if 0 <= days_until_expiry <= 30:
                    expiring_soon.append({
                        "license_key": license.license_key,
                        "user_email": license.user_email,
                        "expires_at": license.expires_at.isoformat(),
                        "days_until_expiry": days_until_expiry
                    })
        
        # Recent validations
        recent_validations = None
        if report_request.include_validations:
            validations = self.db.query(LicenseValidation).order_by(
                LicenseValidation.validated_at.desc()
            ).limit(100).all()
            recent_validations = [
                {
                    "license_key": v.license_key,
                    "is_valid": v.is_valid,
                    "validated_at": v.validated_at.isoformat(),
                    "message": v.validation_message
                }
                for v in validations
            ]
        
        # Recent renewals
        recent_renewals = None
        if report_request.include_renewals:
            renewals = self.db.query(LicenseRenewal).order_by(
                LicenseRenewal.renewed_at.desc()
            ).limit(100).all()
            recent_renewals = [
                {
                    "license_key": r.license_key,
                    "renewed_at": r.renewed_at.isoformat(),
                    "renewal_period_days": r.renewal_period_days,
                    "new_expires_at": r.new_expires_at.isoformat()
                }
                for r in renewals
            ]
        
        return LicenseReportResponse(
            total_licenses=total_licenses,
            active_licenses=active_licenses,
            expired_licenses=expired_licenses,
            suspended_licenses=suspended_licenses,
            revoked_licenses=revoked_licenses,
            pending_licenses=pending_licenses,
            licenses_by_type=licenses_by_type,
            licenses_expiring_soon=expiring_soon,
            recent_validations=recent_validations,
            recent_renewals=recent_renewals,
            generated_at=datetime.utcnow()
        )
    
    # Feature management
    
    def create_feature(self, feature_data: LicenseFeatureCreate) -> LicenseFeatureResponse:
        """Create a new licensable feature"""
        feature = LicenseFeature(**feature_data.dict())
        self.db.add(feature)
        self.db.commit()
        self.db.refresh(feature)
        return LicenseFeatureResponse.from_orm(feature)
    
    def get_all_features(self) -> List[LicenseFeatureResponse]:
        """Get all licensable features"""
        features = self.db.query(LicenseFeature).filter(
            LicenseFeature.is_active == True
        ).all()
        return [LicenseFeatureResponse.from_orm(f) for f in features]
    
    def _check_feature_access(
        self,
        license_type: LicenseType,
        enabled_features: Dict[str, bool],
        features_to_check: List[str]
    ) -> Dict[str, bool]:
        """Check if features are accessible for a license"""
        feature_access = {}
        
        for feature_key in features_to_check:
            # Check if explicitly enabled/disabled
            if feature_key in enabled_features:
                feature_access[feature_key] = enabled_features[feature_key]
                continue
            
            # Check default availability by license type
            feature = self.db.query(LicenseFeature).filter(
                LicenseFeature.feature_key == feature_key,
                LicenseFeature.is_active == True
            ).first()
            
            if not feature:
                feature_access[feature_key] = False
                continue
            
            # Check availability based on license type
            if license_type == LicenseType.TRIAL:
                feature_access[feature_key] = feature.available_in_trial
            elif license_type == LicenseType.BASIC:
                feature_access[feature_key] = feature.available_in_basic
            elif license_type == LicenseType.PROFESSIONAL:
                feature_access[feature_key] = feature.available_in_professional
            elif license_type == LicenseType.ENTERPRISE:
                feature_access[feature_key] = feature.available_in_enterprise
            elif license_type == LicenseType.LIFETIME:
                feature_access[feature_key] = feature.available_in_lifetime
            else:
                feature_access[feature_key] = False
        
        return feature_access
    
    def _log_validation(
        self,
        license_key: str,
        is_valid: bool,
        message: str,
        license_id: Optional[int] = None,
        hardware_id: Optional[str] = None,
        machine_name: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log license validation"""
        validation = LicenseValidation(
            license_id=license_id,
            license_key=license_key,
            is_valid=is_valid,
            validation_message=message,
            hardware_id=hardware_id,
            machine_name=machine_name,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(validation)
        self.db.commit()
    
    def _calculate_days_until_expiry(self, expires_at: Optional[datetime]) -> Optional[int]:
        """Calculate days until license expiry"""
        if not expires_at:
            return None
        delta = expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    def _to_response(self, license: License) -> LicenseResponse:
        """Convert license model to response schema"""
        is_expired = False
        if license.expires_at and license.expires_at < datetime.utcnow():
            is_expired = True
        
        days_until_expiry = self._calculate_days_until_expiry(license.expires_at)
        is_active = license.status == LicenseStatus.ACTIVE and not is_expired
        
        return LicenseResponse(
            id=license.id,
            license_key=license.license_key,
            license_type=license.license_type,
            status=license.status,
            user_email=license.user_email,
            organization_name=license.organization_name,
            issued_at=license.issued_at,
            expires_at=license.expires_at,
            activated_at=license.activated_at,
            last_validated_at=license.last_validated_at,
            enabled_features=license.enabled_features,
            max_users=license.max_users,
            max_projects=license.max_projects,
            max_calculations_per_month=license.max_calculations_per_month,
            hardware_id=license.hardware_id,
            machine_name=license.machine_name,
            metadata=license.metadata,
            notes=license.notes,
            created_at=license.created_at,
            updated_at=license.updated_at,
            is_expired=is_expired,
            days_until_expiry=days_until_expiry,
            is_active=is_active
        )
