# License Service Tests

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.services.license_service import LicenseService
from backend.models.license_schemas import (
    LicenseCreate, LicenseUpdate, LicenseValidationRequest,
    LicenseRenewalRequest, LicenseActivationRequest
)
from backend.models.license_models import LicenseType, LicenseStatus


class TestLicenseService:
    """Test suite for License Service"""
    
    @pytest.fixture
    def service(self, db_session: Session):
        """Create license service instance"""
        return LicenseService(db_session)
    
    @pytest.fixture
    def sample_license_data(self):
        """Sample license creation data"""
        return LicenseCreate(
            license_type="professional",
            user_email="test@example.com",
            organization_name="Test Corp",
            max_users=5,
            max_projects=100,
            max_calculations_per_month=1000
        )
    
    def test_generate_license_key(self, service):
        """Test license key generation"""
        key1 = service.generate_license_key(LicenseType.PROFESSIONAL, "user1@example.com")
        key2 = service.generate_license_key(LicenseType.PROFESSIONAL, "user2@example.com")
        
        # Keys should be unique
        assert key1 != key2
        
        # Keys should have correct format (XXXX-XXXX-XXXX-XXXX-XXXX)
        assert len(key1) == 24  # 20 chars + 4 hyphens
        assert key1.count('-') == 4
    
    def test_create_license(self, service, sample_license_data):
        """Test license creation"""
        license = service.create_license(sample_license_data, created_by="admin")
        
        assert license.id is not None
        assert license.license_key is not None
        assert license.license_type == "professional"
        assert license.status == LicenseStatus.PENDING
        assert license.user_email == "test@example.com"
        assert license.max_users == 5
        assert license.expires_at is not None
    
    def test_create_trial_license_expiry(self, service):
        """Test trial license gets 30-day expiry"""
        license_data = LicenseCreate(
            license_type="trial",
            user_email="trial@example.com"
        )
        
        license = service.create_license(license_data)
        
        # Should expire in approximately 30 days
        days_until_expiry = (license.expires_at - datetime.utcnow()).days
        assert 29 <= days_until_expiry <= 30
    
    def test_create_lifetime_license_no_expiry(self, service):
        """Test lifetime license has no expiry"""
        license_data = LicenseCreate(
            license_type="lifetime",
            user_email="lifetime@example.com"
        )
        
        license = service.create_license(license_data)
        
        assert license.expires_at is None
    
    def test_get_license(self, service, sample_license_data):
        """Test getting license by ID"""
        created = service.create_license(sample_license_data)
        retrieved = service.get_license(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.license_key == created.license_key
    
    def test_get_license_by_key(self, service, sample_license_data):
        """Test getting license by key"""
        created = service.create_license(sample_license_data)
        retrieved = service.get_license_by_key(created.license_key)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.license_key == created.license_key
    
    def test_update_license(self, service, sample_license_data):
        """Test updating license"""
        license = service.create_license(sample_license_data)
        
        update_data = LicenseUpdate(
            status=LicenseStatus.ACTIVE,
            max_users=10,
            notes="Updated license"
        )
        
        updated = service.update_license(license.id, update_data, updated_by="admin")
        
        assert updated.status == LicenseStatus.ACTIVE
        assert updated.max_users == 10
        assert updated.notes == "Updated license"
    
    def test_activate_license_success(self, service, sample_license_data):
        """Test successful license activation"""
        license = service.create_license(sample_license_data)
        
        activation_data = LicenseActivationRequest(
            license_key=license.license_key,
            hardware_id="HWID-12345",
            machine_name="TEST-PC"
        )
        
        result = service.activate_license(activation_data)
        
        assert result.success is True
        assert result.message == "License activated successfully"
        assert result.license.status == LicenseStatus.ACTIVE
        assert result.license.hardware_id == "HWID-12345"
        assert result.license.activated_at is not None
    
    def test_activate_license_not_found(self, service):
        """Test activation with invalid license key"""
        activation_data = LicenseActivationRequest(
            license_key="INVALID-KEY",
            hardware_id="HWID-12345"
        )
        
        result = service.activate_license(activation_data)
        
        assert result.success is False
        assert "not found" in result.message.lower()
    
    def test_activate_license_already_active(self, service, sample_license_data):
        """Test activation of already active license"""
        license = service.create_license(sample_license_data)
        
        # First activation
        activation_data = LicenseActivationRequest(
            license_key=license.license_key,
            hardware_id="HWID-12345"
        )
        service.activate_license(activation_data)
        
        # Second activation attempt
        result = service.activate_license(activation_data)
        
        assert result.success is False
        assert "already" in result.message.lower()
    
    def test_validate_license_success(self, service, sample_license_data):
        """Test successful license validation"""
        license = service.create_license(sample_license_data)
        
        # Activate first
        service.activate_license(LicenseActivationRequest(
            license_key=license.license_key,
            hardware_id="HWID-12345"
        ))
        
        # Validate
        validation_data = LicenseValidationRequest(
            license_key=license.license_key,
            hardware_id="HWID-12345"
        )
        
        result = service.validate_license(validation_data)
        
        assert result.is_valid is True
        assert result.status == LicenseStatus.ACTIVE
        assert result.message == "License is valid"
    
    def test_validate_license_not_found(self, service):
        """Test validation with invalid license key"""
        validation_data = LicenseValidationRequest(
            license_key="INVALID-KEY"
        )
        
        result = service.validate_license(validation_data)
        
        assert result.is_valid is False
        assert "not found" in result.message.lower()
    
    def test_validate_license_expired(self, service):
        """Test validation of expired license"""
        # Create license that expired yesterday
        license_data = LicenseCreate(
            license_type="trial",
            user_email="expired@example.com",
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        
        license = service.create_license(license_data)
        
        # Activate
        service.activate_license(LicenseActivationRequest(
            license_key=license.license_key,
            hardware_id="HWID-12345"
        ))
        
        # Validate
        validation_data = LicenseValidationRequest(
            license_key=license.license_key
        )
        
        result = service.validate_license(validation_data)
        
        assert result.is_valid is False
        assert result.status == LicenseStatus.EXPIRED
        assert "expired" in result.message.lower()
    
    def test_validate_license_hardware_mismatch(self, service, sample_license_data):
        """Test validation with hardware ID mismatch"""
        license = service.create_license(sample_license_data)
        
        # Activate with one hardware ID
        service.activate_license(LicenseActivationRequest(
            license_key=license.license_key,
            hardware_id="HWID-12345"
        ))
        
        # Validate with different hardware ID
        validation_data = LicenseValidationRequest(
            license_key=license.license_key,
            hardware_id="HWID-DIFFERENT"
        )
        
        result = service.validate_license(validation_data)
        
        assert result.is_valid is False
        assert "mismatch" in result.message.lower()
    
    def test_validate_license_with_features(self, service, sample_license_data):
        """Test validation with feature access check"""
        license = service.create_license(sample_license_data)
        
        # Activate
        service.activate_license(LicenseActivationRequest(
            license_key=license.license_key,
            hardware_id="HWID-12345"
        ))
        
        # Validate with feature check
        validation_data = LicenseValidationRequest(
            license_key=license.license_key,
            features_to_check=["3d_visualization", "crm", "multi_pdf"]
        )
        
        result = service.validate_license(validation_data)
        
        assert result.is_valid is True
        assert "3d_visualization" in result.feature_access
        assert "crm" in result.feature_access
        assert "multi_pdf" in result.feature_access
        
        # Professional license should have 3d_visualization and crm
        assert result.feature_access["3d_visualization"] is True
        assert result.feature_access["crm"] is True
        # But not multi_pdf (enterprise only)
        assert result.feature_access["multi_pdf"] is False
    
    def test_validate_license_expiring_soon_warning(self, service):
        """Test validation shows warning for licenses expiring soon"""
        # Create license expiring in 15 days
        license_data = LicenseCreate(
            license_type="professional",
            user_email="expiring@example.com",
            expires_at=datetime.utcnow() + timedelta(days=15)
        )
        
        license = service.create_license(license_data)
        
        # Activate
        service.activate_license(LicenseActivationRequest(
            license_key=license.license_key,
            hardware_id="HWID-12345"
        ))
        
        # Validate
        validation_data = LicenseValidationRequest(
            license_key=license.license_key
        )
        
        result = service.validate_license(validation_data)
        
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "15 days" in result.warnings[0]
    
    def test_renew_license(self, service, sample_license_data):
        """Test license renewal"""
        license = service.create_license(sample_license_data)
        
        # Activate
        service.activate_license(LicenseActivationRequest(
            license_key=license.license_key,
            hardware_id="HWID-12345"
        ))
        
        old_expires_at = license.expires_at
        
        # Renew for 365 days
        renewal_data = LicenseRenewalRequest(
            license_key=license.license_key,
            renewal_period_days=365,
            payment_reference="PAY-12345"
        )
        
        result = service.renew_license(renewal_data, renewed_by="user")
        
        assert result is not None
        assert result.license_key == license.license_key
        assert result.renewal_period_days == 365
        assert result.new_expires_at > old_expires_at
        
        # Check that license was updated
        updated_license = service.get_license(license.id)
        assert updated_license.expires_at == result.new_expires_at
    
    def test_renew_expired_license(self, service):
        """Test renewing an expired license"""
        # Create expired license
        license_data = LicenseCreate(
            license_type="professional",
            user_email="expired@example.com",
            expires_at=datetime.utcnow() - timedelta(days=30)
        )
        
        license = service.create_license(license_data)
        
        # Activate
        service.activate_license(LicenseActivationRequest(
            license_key=license.license_key,
            hardware_id="HWID-12345"
        ))
        
        # Renew
        renewal_data = LicenseRenewalRequest(
            license_key=license.license_key,
            renewal_period_days=365
        )
        
        result = service.renew_license(renewal_data)
        
        assert result is not None
        # Should extend from now, not from old expiry
        assert result.new_expires_at > datetime.utcnow()
        
        # License should be active again
        updated_license = service.get_license(license.id)
        assert updated_license.status == LicenseStatus.ACTIVE
    
    def test_get_license_report(self, service):
        """Test license report generation"""
        # Create various licenses
        for i in range(5):
            service.create_license(LicenseCreate(
                license_type="professional",
                user_email=f"user{i}@example.com"
            ))
        
        # Generate report
        from backend.models.license_schemas import LicenseReportRequest
        report_request = LicenseReportRequest()
        
        report = service.get_license_report(report_request)
        
        assert report.total_licenses >= 5
        assert report.pending_licenses >= 5
        assert "professional" in report.licenses_by_type
        assert report.licenses_by_type["professional"] >= 5
    
    def test_calculate_days_until_expiry(self, service):
        """Test days until expiry calculation"""
        # Future date
        future_date = datetime.utcnow() + timedelta(days=30)
        days = service._calculate_days_until_expiry(future_date)
        assert days == 30
        
        # Past date
        past_date = datetime.utcnow() - timedelta(days=10)
        days = service._calculate_days_until_expiry(past_date)
        assert days == 0
        
        # No expiry
        days = service._calculate_days_until_expiry(None)
        assert days is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
