# License Management System Demo

"""
Demonstration script for the License Management System.

This script shows how to:
1. Create licenses
2. Activate licenses
3. Validate licenses
4. Check feature access
5. Renew licenses
6. Generate reports
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal, engine
from backend.models.license_models import Base
from backend.services.license_service import LicenseService
from backend.models.license_schemas import (
    LicenseCreate, LicenseValidationRequest,
    LicenseActivationRequest, LicenseRenewalRequest,
    LicenseReportRequest, LicenseFeatureCreate
)


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_license_creation(service: LicenseService):
    """Demo: Create different types of licenses"""
    print_section("1. License Creation")
    
    # Create trial license
    print("Creating Trial License...")
    trial_license = service.create_license(LicenseCreate(
        license_type="trial",
        user_email="trial@example.com",
        organization_name="Trial User"
    ))
    print(f"✓ Trial License Created: {trial_license.license_key}")
    print(f"  - Expires: {trial_license.expires_at}")
    print(f"  - Status: {trial_license.status}")
    
    # Create professional license
    print("\nCreating Professional License...")
    pro_license = service.create_license(LicenseCreate(
        license_type="professional",
        user_email="pro@example.com",
        organization_name="Pro Corp",
        max_users=5,
        max_projects=100,
        max_calculations_per_month=1000
    ))
    print(f"✓ Professional License Created: {pro_license.license_key}")
    print(f"  - Max Users: {pro_license.max_users}")
    print(f"  - Max Projects: {pro_license.max_projects}")
    print(f"  - Expires: {pro_license.expires_at}")
    
    # Create enterprise license
    print("\nCreating Enterprise License...")
    ent_license = service.create_license(LicenseCreate(
        license_type="enterprise",
        user_email="enterprise@example.com",
        organization_name="Enterprise Inc",
        enabled_features={
            "multi_pdf": True,
            "white_label": True,
            "api_access": True
        }
    ))
    print(f"✓ Enterprise License Created: {ent_license.license_key}")
    print(f"  - Enabled Features: {list(ent_license.enabled_features.keys())}")
    
    return trial_license, pro_license, ent_license


def demo_license_activation(service: LicenseService, license):
    """Demo: Activate a license"""
    print_section("2. License Activation")
    
    print(f"Activating License: {license.license_key}")
    
    result = service.activate_license(LicenseActivationRequest(
        license_key=license.license_key,
        hardware_id="DEMO-HWID-12345",
        machine_name="DEMO-PC"
    ))
    
    if result.success:
        print(f"✓ License Activated Successfully")
        print(f"  - Status: {result.license.status}")
        print(f"  - Activated At: {result.license.activated_at}")
        print(f"  - Hardware ID: {result.license.hardware_id}")
    else:
        print(f"✗ Activation Failed: {result.message}")
    
    return result.success


def demo_license_validation(service: LicenseService, license):
    """Demo: Validate a license"""
    print_section("3. License Validation")
    
    print(f"Validating License: {license.license_key}")
    
    result = service.validate_license(LicenseValidationRequest(
        license_key=license.license_key,
        hardware_id="DEMO-HWID-12345",
        features_to_check=[
            "solar_calculator",
            "3d_visualization",
            "crm",
            "multi_pdf"
        ]
    ))
    
    print(f"\nValidation Result:")
    print(f"  - Valid: {result.is_valid}")
    print(f"  - Status: {result.status}")
    print(f"  - License Type: {result.license_type}")
    print(f"  - Message: {result.message}")
    
    if result.expires_at:
        print(f"  - Expires: {result.expires_at}")
        print(f"  - Days Until Expiry: {result.days_until_expiry}")
    
    if result.warnings:
        print(f"  - Warnings: {', '.join(result.warnings)}")
    
    print(f"\nFeature Access:")
    for feature, has_access in result.feature_access.items():
        status = "✓" if has_access else "✗"
        print(f"  {status} {feature}: {has_access}")


def demo_feature_management(service: LicenseService):
    """Demo: Manage licensable features"""
    print_section("4. Feature Management")
    
    print("Getting All Features...")
    features = service.get_all_features()
    
    print(f"\nTotal Features: {len(features)}")
    print("\nFeature List:")
    
    for feature in features[:5]:  # Show first 5
        print(f"\n  {feature.feature_name} ({feature.feature_key})")
        print(f"    - Category: {feature.category}")
        print(f"    - Trial: {feature.available_in_trial}")
        print(f"    - Basic: {feature.available_in_basic}")
        print(f"    - Professional: {feature.available_in_professional}")
        print(f"    - Enterprise: {feature.available_in_enterprise}")


def demo_license_renewal(service: LicenseService, license):
    """Demo: Renew a license"""
    print_section("5. License Renewal")
    
    print(f"Renewing License: {license.license_key}")
    print(f"Current Expiry: {license.expires_at}")
    
    result = service.renew_license(LicenseRenewalRequest(
        license_key=license.license_key,
        renewal_period_days=365,
        payment_reference="DEMO-PAY-12345",
        payment_amount=99900,  # €999.00
        payment_currency="EUR"
    ))
    
    if result:
        print(f"\n✓ License Renewed Successfully")
        print(f"  - Old Expiry: {result.old_expires_at}")
        print(f"  - New Expiry: {result.new_expires_at}")
        print(f"  - Renewal Period: {result.renewal_period_days} days")
        print(f"  - Renewed At: {result.renewed_at}")
    else:
        print(f"✗ Renewal Failed")


def demo_license_report(service: LicenseService):
    """Demo: Generate license report"""
    print_section("6. License Reporting")
    
    print("Generating License Report...")
    
    report = service.get_license_report(LicenseReportRequest(
        include_validations=True,
        include_renewals=True
    ))
    
    print(f"\nLicense Statistics:")
    print(f"  - Total Licenses: {report.total_licenses}")
    print(f"  - Active: {report.active_licenses}")
    print(f"  - Expired: {report.expired_licenses}")
    print(f"  - Suspended: {report.suspended_licenses}")
    print(f"  - Revoked: {report.revoked_licenses}")
    print(f"  - Pending: {report.pending_licenses}")
    
    print(f"\nLicenses by Type:")
    for license_type, count in report.licenses_by_type.items():
        print(f"  - {license_type.capitalize()}: {count}")
    
    if report.licenses_expiring_soon:
        print(f"\nLicenses Expiring Soon ({len(report.licenses_expiring_soon)}):")
        for license in report.licenses_expiring_soon[:3]:  # Show first 3
            print(f"  - {license['license_key']}: {license['days_until_expiry']} days")
    
    if report.recent_validations:
        print(f"\nRecent Validations: {len(report.recent_validations)}")
    
    if report.recent_renewals:
        print(f"Recent Renewals: {len(report.recent_renewals)}")


def demo_hardware_id_generation():
    """Demo: Generate hardware ID"""
    print_section("7. Hardware ID Generation")
    
    import platform
    import hashlib
    import uuid
    
    print("Generating Hardware ID...")
    
    # Get MAC address
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                    for i in range(0,2*6,2)][::-1])
    
    # Get system info
    system = platform.system()
    machine = platform.machine()
    processor = platform.processor()
    
    print(f"\nSystem Information:")
    print(f"  - MAC Address: {mac}")
    print(f"  - System: {system}")
    print(f"  - Machine: {machine}")
    print(f"  - Processor: {processor}")
    
    # Generate hardware ID
    unique_string = f"{mac}:{system}:{machine}:{processor}"
    hardware_id = hashlib.sha256(unique_string.encode()).hexdigest()[:32]
    
    print(f"\nGenerated Hardware ID: {hardware_id}")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  LICENSE MANAGEMENT SYSTEM - DEMONSTRATION")
    print("=" * 80)
    
    # Create database tables
    print("\nInitializing database...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")
    
    # Create service
    db = SessionLocal()
    service = LicenseService(db)
    
    try:
        # Run demos
        trial, pro, ent = demo_license_creation(service)
        
        # Activate professional license
        if demo_license_activation(service, pro):
            demo_license_validation(service, pro)
        
        demo_feature_management(service)
        demo_license_renewal(service, pro)
        demo_license_report(service)
        demo_hardware_id_generation()
        
        print_section("Demo Complete")
        print("All demonstrations completed successfully!")
        print("\nNext Steps:")
        print("  1. Review the generated licenses in the database")
        print("  2. Test the API endpoints using the documentation")
        print("  3. Integrate license validation into your application")
        print("  4. Set up automated renewal reminders")
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
