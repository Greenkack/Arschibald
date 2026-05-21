# Contract Management - Quick Reference

## Quick Start

```python
from backend.services.contract_service import ContractService
from backend.models.contract_schemas import ContractCreate

# Create contract
service = ContractService(db)
contract = service.create_contract(ContractCreate(
    title="Service Contract",
    contract_type="service",
    customer_id=123,
    start_date=datetime.utcnow(),
    end_date=datetime.utcnow() + timedelta(days=365),
    value=10000.00
))
```

## API Endpoints Cheat Sheet

| Action | Method | Endpoint |
|--------|--------|----------|
| Create Contract | POST | `/api/v1/contracts` |
| Get Contract | GET | `/api/v1/contracts/{id}` |
| Update Contract | PUT | `/api/v1/contracts/{id}` |
| Delete Contract | DELETE | `/api/v1/contracts/{id}` |
| List Contracts | POST | `/api/v1/contracts/list` |
| Terminate Contract | POST | `/api/v1/contracts/{id}/terminate` |
| Activate Contract | POST | `/api/v1/contracts/{id}/activate` |
| Create Template | POST | `/api/v1/contracts/templates` |
| Generate from Template | POST | `/api/v1/contracts/templates/{id}/generate` |
| Request Approval | POST | `/api/v1/contracts/approvals` |
| Process Approval | POST | `/api/v1/contracts/approvals/{id}/decision` |
| Request Signature | POST | `/api/v1/contracts/signatures` |
| Submit Signature | POST | `/api/v1/contracts/signatures/{id}/submit` |
| Renew Contract | POST | `/api/v1/contracts/renewals` |
| Get Expiring | POST | `/api/v1/contracts/renewals/expiring` |
| Process Auto-Renewals | POST | `/api/v1/contracts/renewals/process-auto` |
| Calculate Analytics | POST | `/api/v1/contracts/analytics` |

## Contract Types

- `service` - Service contracts
- `maintenance` - Maintenance agreements
- `installation` - Installation contracts
- `warranty` - Warranty contracts
- `lease` - Lease agreements
- `purchase` - Purchase contracts
- `subscription` - Subscription contracts

## Contract Status Flow

```
DRAFT → PENDING_APPROVAL → APPROVED → ACTIVE → EXPIRED/TERMINATED/RENEWED
```

## Common Operations

### Create Contract with Template
```python
# 1. Create template
template = service.create_template(ContractTemplateCreate(
    name="Standard Service",
    contract_type="service",
    title_template="Service Contract for {customer_name}",
    content_template="Contract between {company} and {customer_name}...",
    variables=["customer_name", "company"]
))

# 2. Generate contract
contract = service.generate_contract_from_template(
    template_id=template.id,
    variables={"customer_name": "John Doe", "company": "Solar Co"},
    customer_id=123
)
```

### Approval Workflow
```python
# 1. Request approval
approval = service.request_approval(ContractApprovalCreate(
    contract_id=1,
    approver_id=5
))

# 2. Process approval
service.process_approval(approval.id, ContractApprovalDecision(
    status="approved",
    comments="Looks good"
))
```

### E-Signature Flow
```python
# 1. Request signature
signature = service.request_signature(ContractSignatureRequest(
    contract_id=1,
    signer_name="John Doe",
    signer_email="john@example.com",
    expires_in_days=7
))

# 2. Submit signature
service.submit_signature(signature.id, ContractSignatureSubmit(
    signature_data="base64_encoded_signature",
    signature_method="drawn",
    verification_code="code_from_email"
))
```

### Contract Renewal
```python
# Manual renewal
renewal = service.renew_contract(ContractRenewalCreate(
    contract_id=1,
    new_end_date=datetime.utcnow() + timedelta(days=365),
    new_value=11000.00
))

# Auto-renewal
renewals = service.process_auto_renewals()
```

## Database Models

### Contract
- `id`, `contract_number`, `customer_id`, `template_id`
- `title`, `contract_type`, `status`
- `start_date`, `end_date`, `value`, `currency`
- `auto_renew`, `renewal_notice_days`

### ContractTemplate
- `id`, `name`, `contract_type`
- `title_template`, `content_template`
- `variables`, `requires_approval`, `requires_signature`

### ContractApproval
- `id`, `contract_id`, `approver_id`
- `status`, `decision_date`, `comments`

### ContractSignature
- `id`, `contract_id`, `signer_name`, `signer_email`
- `status`, `signature_data`, `signed_at`

### ContractRenewal
- `id`, `contract_id`, `renewal_number`
- `previous_value`, `new_value`, `is_automatic`

## Key Features

✅ Contract lifecycle management  
✅ Template system with variables  
✅ Multi-level approval workflow  
✅ E-signature integration  
✅ Automatic renewals  
✅ Expiring contract alerts  
✅ Contract analytics  
✅ Document hash verification  
✅ IP tracking for signatures  
✅ Metadata support  

## Requirements Satisfied

- ✅ 1.3 - Backend service functionality
- ✅ 6.1 - Modular service architecture
- ✅ 11.1 - Authentication and authorization
- ✅ 11.3 - Data security
- ✅ 12.1 - API documentation

## Files Created

- `backend/models/contract_models.py` - Database models
- `backend/models/contract_schemas.py` - Pydantic schemas
- `backend/services/contract_service.py` - Business logic
- `backend/api/v1/contracts.py` - API endpoints
- `backend/migrations/add_contract_tables.py` - Database migration
- `docs/CONTRACT_MANAGEMENT_GUIDE.md` - Complete guide
- `docs/CONTRACT_MANAGEMENT_QUICK_REFERENCE.md` - This file

## Next Steps

1. Run migration: `python backend/migrations/add_contract_tables.py`
2. Test API endpoints with Swagger UI
3. Implement frontend components
4. Add email notifications
5. Integrate with document storage
