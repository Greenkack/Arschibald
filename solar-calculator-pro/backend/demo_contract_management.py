"""
Contract Management System Demo

This script demonstrates the complete contract management workflow including
contract creation, templates, approvals, signatures, and renewals.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.services.contract_service import ContractService
from backend.models.contract_schemas import (
    ContractCreate, ContractTemplateCreate, ContractApprovalCreate,
    ContractApprovalDecision, ContractSignatureRequest, ContractSignatureSubmit,
    ContractRenewalCreate, ContractListFilters, ExpiringContractsRequest
)


def demo_basic_contract_creation():
    """Demonstrate basic contract creation."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Contract Creation")
    print("="*60)
    
    db = SessionLocal()
    service = ContractService(db)
    
    try:
        # Create a contract
        print("\n1. Creating a new contract...")
        contract_data = ContractCreate(
            title="Solar Panel Installation Contract",
            contract_type="installation",
            customer_id=123,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=365),
            value=15000.00,
            currency="EUR",
            payment_terms="50% upfront, 50% on completion",
            terms_and_conditions="Standard installation terms apply",
            auto_renew=False,
            renewal_notice_days=30
        )
        
        contract = service.create_contract(contract_data)
        print(f"    Contract created: {contract.contract_number}")
        print(f"    Status: {contract.status}")
        print(f"    Value: {contract.value} {contract.currency}")
        
        # Get contract
        print("\n2. Retrieving contract...")
        retrieved = service.get_contract(contract.id)
        print(f"    Retrieved: {retrieved.title}")
        
        # Update contract
        print("\n3. Updating contract value...")
        from backend.models.contract_schemas import ContractUpdate
        updated = service.update_contract(
            contract.id,
            ContractUpdate(value=16000.00, notes="Price adjusted for additional work")
        )
        print(f"    Updated value: {updated.value} {updated.currency}")
        
        return contract.id
        
    except Exception as e:
        print(f"    Error: {str(e)}")
        return None
    finally:
        db.close()


def demo_template_system():
    """Demonstrate contract template system."""
    print("\n" + "="*60)
    print("DEMO 2: Contract Template System")
    print("="*60)
    
    db = SessionLocal()
    service = ContractService(db)
    
    try:
        # Create template
        print("\n1. Creating contract template...")
        template_data = ContractTemplateCreate(
            name="Standard Service Contract",
            contract_type="service",
            title_template="Service Contract for {customer_name}",
            content_template="""
This Service Contract is entered into between {company_name} and {customer_name}.

Service Description: {service_description}
Duration: {duration} months
Monthly Fee: {monthly_fee} EUR

Terms and Conditions:
1. Service will be provided as described
2. Payment due on the 1st of each month
3. Either party may terminate with 30 days notice
            """,
            terms_template="Standard service terms apply",
            variables=["customer_name", "company_name", "service_description", "duration", "monthly_fee"],
            default_values={"duration": "12", "monthly_fee": "500"},
            requires_approval=True,
            requires_signature=True,
            description="Standard template for service contracts"
        )
        
        template = service.create_template(template_data)
        print(f"    Template created: {template.name}")
        print(f"    Variables: {', '.join(template.variables)}")
        
        # Generate contract from template
        print("\n2. Generating contract from template...")
        variables = {
            "customer_name": "John Doe",
            "company_name": "Solar Solutions GmbH",
            "service_description": "Monthly solar panel maintenance",
            "duration": "24",
            "monthly_fee": "750",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=730),
            "value": 18000.00  # 24 months * 750 EUR
        }
        
        contract = service.generate_contract_from_template(
            template_id=template.id,
            variables=variables,
            customer_id=456
        )
        print(f"    Contract generated: {contract.contract_number}")
        print(f"    Title: {contract.title}")
        
        return contract.id
        
    except Exception as e:
        print(f"    Error: {str(e)}")
        return None
    finally:
        db.close()


def demo_approval_workflow(contract_id):
    """Demonstrate approval workflow."""
    print("\n" + "="*60)
    print("DEMO 3: Approval Workflow")
    print("="*60)
    
    db = SessionLocal()
    service = ContractService(db)
    
    try:
        # Request approval
        print("\n1. Requesting contract approval...")
        approval_data = ContractApprovalCreate(
            contract_id=contract_id,
            approver_id=5,
            approval_level=1,
            comments="Please review and approve this contract"
        )
        
        approval = service.request_approval(approval_data)
        print(f"    Approval requested from user ID: {approval.approver_id}")
        print(f"    Approval status: {approval.status}")
        
        # Check contract status
        contract = service.get_contract(contract_id)
        print(f"    Contract status updated to: {contract.status}")
        
        # Process approval
        print("\n2. Processing approval decision...")
        decision = ContractApprovalDecision(
            status="approved",
            comments="Contract terms are acceptable. Approved."
        )
        
        processed = service.process_approval(approval.id, decision)
        print(f"    Approval processed: {processed.status}")
        print(f"    Decision date: {processed.decision_date}")
        
        # Check updated contract status
        contract = service.get_contract(contract_id)
        print(f"    Contract status: {contract.status}")
        
        # Get pending approvals
        print("\n3. Checking pending approvals...")
        pending = service.get_pending_approvals(approver_id=5)
        print(f"    Pending approvals for user 5: {len(pending)}")
        
    except Exception as e:
        print(f"    Error: {str(e)}")
    finally:
        db.close()


def demo_signature_workflow(contract_id):
    """Demonstrate e-signature workflow."""
    print("\n" + "="*60)
    print("DEMO 4: E-Signature Workflow")
    print("="*60)
    
    db = SessionLocal()
    service = ContractService(db)
    
    try:
        # Request signature
        print("\n1. Requesting e-signature...")
        signature_data = ContractSignatureRequest(
            contract_id=contract_id,
            signer_name="John Doe",
            signer_email="john.doe@example.com",
            signer_role="Customer",
            expires_in_days=7
        )
        
        signature = service.request_signature(signature_data)
        print(f"    Signature requested from: {signature.signer_name}")
        print(f"    Email sent to: {signature.signer_email}")
        print(f"    Expires at: {signature.expires_at}")
        print(f"    Verification code: {signature.verification_code}")
        
        # Submit signature
        print("\n2. Submitting signature...")
        signature_submit = ContractSignatureSubmit(
            signature_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            signature_method="drawn",
            verification_code=signature.verification_code
        )
        
        submitted = service.submit_signature(
            signature.id,
            signature_submit,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0..."
        )
        print(f"    Signature submitted: {submitted.status}")
        print(f"    Signed at: {submitted.signed_at}")
        print(f"    Verified: {submitted.is_verified}")
        
        # Check contract status
        contract = service.get_contract(contract_id)
        print(f"    Contract status: {contract.status}")
        print(f"    Signed date: {contract.signed_date}")
        
        # Get pending signatures
        print("\n3. Checking pending signatures...")
        pending = service.get_pending_signatures("john.doe@example.com")
        print(f"    Pending signatures: {len(pending)}")
        
    except Exception as e:
        print(f"    Error: {str(e)}")
    finally:
        db.close()


def demo_renewal_system():
    """Demonstrate contract renewal system."""
    print("\n" + "="*60)
    print("DEMO 5: Contract Renewal System")
    print("="*60)
    
    db = SessionLocal()
    service = ContractService(db)
    
    try:
        # Create a contract that's about to expire
        print("\n1. Creating contract near expiration...")
        contract_data = ContractCreate(
            title="Maintenance Contract - Expiring Soon",
            contract_type="maintenance",
            customer_id=789,
            start_date=datetime.utcnow() - timedelta(days=335),
            end_date=datetime.utcnow() + timedelta(days=30),
            value=5000.00,
            currency="EUR",
            auto_renew=True,
            renewal_notice_days=30
        )
        
        contract = service.create_contract(contract_data)
        # Manually set to active for demo
        contract.status = "active"
        db.commit()
        print(f"    Contract created: {contract.contract_number}")
        print(f"    Expires in: 30 days")
        print(f"    Auto-renew: {contract.auto_renew}")
        
        # Get expiring contracts
        print("\n2. Finding expiring contracts...")
        expiring = service.get_expiring_contracts(days=60)
        print(f"    Contracts expiring in 60 days: {len(expiring)}")
        for c in expiring:
            print(f"      - {c.contract_number}: {c.title}")
        
        # Manual renewal
        print("\n3. Performing manual renewal...")
        renewal_data = ContractRenewalCreate(
            contract_id=contract.id,
            new_end_date=datetime.utcnow() + timedelta(days=395),
            new_value=5500.00,
            notes="Annual renewal with 10% increase"
        )
        
        renewal = service.renew_contract(renewal_data)
        print(f"    Contract renewed: Renewal #{renewal.renewal_number}")
        print(f"    Previous value: {renewal.previous_value} EUR")
        print(f"    New value: {renewal.new_value} EUR")
        print(f"    Change: {renewal.value_change_percent:.1f}%")
        
        # Process auto-renewals
        print("\n4. Processing automatic renewals...")
        auto_renewals = service.process_auto_renewals()
        print(f"    Auto-renewals processed: {len(auto_renewals)}")
        
    except Exception as e:
        print(f"    Error: {str(e)}")
    finally:
        db.close()


def demo_analytics():
    """Demonstrate contract analytics."""
    print("\n" + "="*60)
    print("DEMO 6: Contract Analytics")
    print("="*60)
    
    db = SessionLocal()
    service = ContractService(db)
    
    try:
        # Calculate analytics
        print("\n1. Calculating contract analytics...")
        period_start = datetime(2024, 1, 1)
        period_end = datetime(2024, 12, 31)
        
        analytics = service.calculate_analytics(period_start, period_end)
        print(f"    Period: {period_start.date()} to {period_end.date()}")
        print(f"    Total contracts: {analytics.total_contracts}")
        print(f"    Active contracts: {analytics.active_contracts}")
        print(f"    Expired contracts: {analytics.expired_contracts}")
        print(f"    Renewed contracts: {analytics.renewed_contracts}")
        print(f"    Total value: {analytics.total_value:,.2f} EUR")
        print(f"    Average value: {analytics.average_value:,.2f} EUR")
        print(f"    Renewal rate: {analytics.renewal_rate:.1f}%")
        
        if analytics.metrics_by_type:
            print("\n2. Metrics by contract type:")
            for contract_type, metrics in analytics.metrics_by_type.items():
                print(f"   {contract_type}:")
                print(f"      - Count: {metrics['count']}")
                print(f"      - Total value: {metrics['total_value']:,.2f} EUR")
                print(f"      - Average value: {metrics['average_value']:,.2f} EUR")
        
    except Exception as e:
        print(f"    Error: {str(e)}")
    finally:
        db.close()


def demo_list_and_filter():
    """Demonstrate contract listing and filtering."""
    print("\n" + "="*60)
    print("DEMO 7: List and Filter Contracts")
    print("="*60)
    
    db = SessionLocal()
    service = ContractService(db)
    
    try:
        # List all contracts
        print("\n1. Listing all contracts...")
        filters = ContractListFilters(skip=0, limit=10)
        contracts, total = service.list_contracts(filters)
        print(f"    Total contracts: {total}")
        print(f"    Showing: {len(contracts)}")
        
        # Filter by type
        print("\n2. Filtering by contract type...")
        filters = ContractListFilters(contract_type="installation", skip=0, limit=10)
        contracts, total = service.list_contracts(filters)
        print(f"    Installation contracts: {total}")
        
        # Filter by status
        print("\n3. Filtering by status...")
        filters = ContractListFilters(status="active", skip=0, limit=10)
        contracts, total = service.list_contracts(filters)
        print(f"    Active contracts: {total}")
        
        # Search
        print("\n4. Searching contracts...")
        filters = ContractListFilters(search="solar", skip=0, limit=10)
        contracts, total = service.list_contracts(filters)
        print(f"    Contracts matching 'solar': {total}")
        
    except Exception as e:
        print(f"    Error: {str(e)}")
    finally:
        db.close()


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("CONTRACT MANAGEMENT SYSTEM - COMPLETE DEMO")
    print("="*60)
    
    # Demo 1: Basic contract creation
    contract_id = demo_basic_contract_creation()
    
    # Demo 2: Template system
    template_contract_id = demo_template_system()
    
    # Demo 3: Approval workflow
    if template_contract_id:
        demo_approval_workflow(template_contract_id)
    
    # Demo 4: Signature workflow
    if template_contract_id:
        demo_signature_workflow(template_contract_id)
    
    # Demo 5: Renewal system
    demo_renewal_system()
    
    # Demo 6: Analytics
    demo_analytics()
    
    # Demo 7: List and filter
    demo_list_and_filter()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nAll contract management features demonstrated successfully!")
    print("\nNext steps:")
    print("1. Review the API documentation")
    print("2. Test endpoints with Swagger UI")
    print("3. Implement frontend components")
    print("4. Add email notifications")
    print("5. Integrate with document storage")


if __name__ == "__main__":
    main()
