# Contract Management System - Complete Guide

## Overview

The Contract Management System provides comprehensive functionality for managing contracts throughout their lifecycle, from creation to renewal. It includes contract templates, approval workflows, e-signatures, and analytics.

## Features

### 1. Contract Management
- Create, read, update, and delete contracts
- Multiple contract types (service, maintenance, installation, warranty, lease, purchase, subscription)
- Contract status tracking (draft, pending approval, approved, active, expired, terminated, renewed)
- Financial tracking (value, currency, payment terms)
- Document management with hash verification
- Metadata and custom fields support

### 2. Contract Templates
- Reusable contract templates
- Variable substitution system
- Template versioning
- Template activation/deactivation
- Generate contracts from templates

### 3. Approval Workflow
- Multi-level approval system
- Approval requests and tracking
- Approval decisions (approve, reject, cancel)
- Pending approvals dashboard
- Automatic contract status updates

### 4. E-Signature Integration
- Request signatures from multiple signers
- Signature verification codes
- Signature expiration dates
- IP address and user agent tracking
- Multiple signature methods (drawn, typed, uploaded)
- Signature status tracking

### 5. Contract Renewal
- Manual contract renewal
- Automatic renewal for eligible contracts
- Renewal history tracking
- Value change tracking
- Expiring contracts alerts
- Renewal notice periods

### 6. Analytics
- Contract metrics by period
- Financial analytics
- Renewal rate tracking
- Metrics by contract type
- Active/expired/terminated counts

## API Endpoints

### Contract Endpoints

#### Create Contract
```http
POST /api/v1/contracts
Content-Type: application/json

{
  "title": "Solar Installation Service Contract",
  "contract_type": "installation",
  "customer_id": 123,
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z",
  "value": 15000.00,
  "currency": "EUR",
  "payment_terms": "50% upfront, 50% on completion",
  "auto_renew": false,
  "renewal_notice_days": 30
}
```

#### Get Contract
```http
GET /api/v1/contracts/{contract_id}
```

#### Update Contract
```http
PUT /api/v1/contracts/{contract_id}
Content-Type: application/json

{
  "value": 16000.00,
  "notes": "Price updated due to additional work"
}
```

#### List Contracts
```http
POST /api/v1/contracts/list
Content-Type: application/json

{
  "customer_id": 123,
  "status": "active",
  "skip": 0,
  "limit": 100
}
```

#### Terminate Contract
```http
POST /api/v1/contracts/{contract_id}/terminate
Content-Type: application/json

{
  "reason": "Customer request"
}
```

### Template Endpoints

#### Create Template
```http
POST /api/v1/contracts/templates
Content-Type: application/json

{
  "name": "Standard Service Contract",
  "contract_type": "service",
  "title_template": "Service Contract for {customer_name}",
  "content_template": "This contract is between {company_name} and {customer_name}...",
  "variables": ["customer_name", "company_name", "service_description"],
  "requires_approval": true,
  "requires_signature": true
}
```

#### Generate from Template
```http
POST /api/v1/contracts/templates/{template_id}/generate
Content-Type: application/json

{
  "customer_id": 123,
  "variables": {
    "customer_name": "John Doe",
    "company_name": "Solar Solutions GmbH",
    "service_description": "Solar panel installation",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z",
    "value": 15000.00
  }
}
```

### Approval Endpoints

#### Request Approval
```http
POST /api/v1/contracts/approvals
Content-Type: application/json

{
  "contract_id": 1,
  "approver_id": 5,
  "approval_level": 1,
  "comments": "Please review and approve"
}
```

#### Process Approval
```http
POST /api/v1/contracts/approvals/{approval_id}/decision
Content-Type: application/json

{
  "status": "approved",
  "comments": "Approved - all terms acceptable"
}
```

### Signature Endpoints

#### Request Signature
```http
POST /api/v1/contracts/signatures
Content-Type: application/json

{
  "contract_id": 1,
  "signer_name": "John Doe",
  "signer_email": "john.doe@example.com",
  "signer_role": "Customer",
  "expires_in_days": 7
}
```

#### Submit Signature
```http
POST /api/v1/contracts/signatures/{signature_id}/submit
Content-Type: application/json

{
  "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "signature_method": "drawn",
  "verification_code": "abc123xyz789"
}
```

### Renewal Endpoints

#### Renew Contract
```http
POST /api/v1/contracts/renewals
Content-Type: application/json

{
  "contract_id": 1,
  "new_end_date": "2025-12-31T23:59:59Z",
  "new_value": 16000.00,
  "notes": "Annual renewal with 5% increase"
}
```

#### Get Expiring Contracts
```http
POST /api/v1/contracts/renewals/expiring
Content-Type: application/json

{
  "days": 30,
  "include_auto_renew": false
}
```

#### Process Auto-Renewals
```http
POST /api/v1/contracts/renewals/process-auto
```

### Analytics Endpoints

#### Calculate Analytics
```http
POST /api/v1/contracts/analytics
Content-Type: application/json

{
  "period_start": "2024-01-01T00:00:00Z",
  "period_end": "2024-12-31T23:59:59Z"
}
```

## Database Schema

### contracts
- id (PK)
- contract_number (unique)
- customer_id (FK)
- template_id (FK, nullable)
- title
- contract_type (enum)
- status (enum)
- start_date
- end_date
- signed_date
- renewal_date
- termination_date
- value
- currency
- payment_terms
- terms_and_conditions
- special_clauses
- notes
- metadata (JSON)
- auto_renew
- renewal_notice_days
- renewal_count
- document_url
- document_hash
- created_at
- updated_at
- created_by (FK)
- updated_by (FK)

### contract_templates
- id (PK)
- name
- contract_type (enum)
- title_template
- content_template
- terms_template
- variables (JSON)
- default_values (JSON)
- is_active
- requires_approval
- requires_signature
- description
- version
- created_at
- updated_at
- created_by (FK)

### contract_approvals
- id (PK)
- contract_id (FK)
- approver_id (FK)
- approval_level
- status (enum)
- decision_date
- comments
- requested_at

### contract_signatures
- id (PK)
- contract_id (FK)
- signer_name
- signer_email
- signer_role
- status (enum)
- signature_data
- signature_method
- ip_address
- user_agent
- requested_at
- signed_at
- expires_at
- verification_code
- is_verified

### contract_renewals
- id (PK)
- contract_id (FK)
- renewal_number
- previous_end_date
- new_end_date
- previous_value
- new_value
- value_change_percent
- is_automatic
- renewal_date
- notes

### contract_analytics
- id (PK)
- period_start
- period_end
- total_contracts
- active_contracts
- expired_contracts
- renewed_contracts
- terminated_contracts
- total_value
- average_value
- renewal_rate
- metrics_by_type (JSON)
- calculated_at

## Usage Examples

### Python Service Usage

```python
from backend.services.contract_service import ContractService
from backend.models.contract_schemas import ContractCreate
from datetime import datetime, timedelta

# Initialize service
service = ContractService(db_session)

# Create a contract
contract_data = ContractCreate(
    title="Solar Installation Contract",
    contract_type="installation",
    customer_id=123,
    start_date=datetime.utcnow(),
    end_date=datetime.utcnow() + timedelta(days=365),
    value=15000.00,
    currency="EUR",
    auto_renew=False
)
contract = service.create_contract(contract_data)

# Request approval
approval_data = ContractApprovalCreate(
    contract_id=contract.id,
    approver_id=5,
    approval_level=1
)
approval = service.request_approval(approval_data)

# Request signature
signature_data = ContractSignatureRequest(
    contract_id=contract.id,
    signer_name="John Doe",
    signer_email="john.doe@example.com",
    expires_in_days=7
)
signature = service.request_signature(signature_data)

# Get expiring contracts
expiring = service.get_expiring_contracts(days=30)

# Calculate analytics
analytics = service.calculate_analytics(
    period_start=datetime(2024, 1, 1),
    period_end=datetime(2024, 12, 31)
)
```

## Best Practices

1. **Contract Numbers**: Always use the auto-generated contract numbers for tracking
2. **Approvals**: Implement multi-level approvals for high-value contracts
3. **Signatures**: Always verify signatures with verification codes
4. **Renewals**: Set up automatic renewals for recurring contracts
5. **Analytics**: Calculate analytics regularly for business insights
6. **Templates**: Use templates for standardized contracts
7. **Metadata**: Store additional contract information in the metadata field
8. **Document Hash**: Always generate and verify document hashes for integrity

## Security Considerations

1. All signatures are tracked with IP address and user agent
2. Verification codes are required for signature submission
3. Signatures expire after the specified period
4. Contract modifications are tracked with user IDs
5. All sensitive data should be encrypted at rest
6. API endpoints should require authentication
7. Implement rate limiting for signature requests

## Integration with CRM

The contract management system integrates seamlessly with the CRM system:

- Contracts are linked to customers via customer_id
- Contract status updates trigger CRM notifications
- Expiring contracts appear in CRM dashboards
- Contract analytics feed into CRM reports
- Signatures and approvals are tracked in customer history

## Troubleshooting

### Common Issues

1. **Contract not activating after approval**
   - Ensure all required approvals are complete
   - Check that all required signatures are submitted
   - Verify contract status is "approved"

2. **Signature request expired**
   - Signatures expire after the specified period
   - Request a new signature if expired
   - Consider extending expiration period for complex contracts

3. **Auto-renewal not working**
   - Verify auto_renew flag is set to true
   - Check renewal_notice_days is configured
   - Ensure process_auto_renewals is called regularly

4. **Template variables not replacing**
   - Use correct variable format: {variable_name}
   - Ensure all variables are provided in the variables dict
   - Check for typos in variable names

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 1.3**: Backend service exposes contract management functionality
- **Requirement 6.1**: Modular service architecture with clear interfaces
- **Requirement 11.1**: User authentication and authorization
- **Requirement 11.3**: Data encryption and security
- **Requirement 12.1**: Comprehensive API documentation

## Next Steps

1. Implement frontend UI components for contract management
2. Add email notifications for approvals and signatures
3. Integrate with document storage system
4. Add contract comparison functionality
5. Implement contract search with full-text indexing
6. Add contract export to PDF
7. Implement contract versioning
8. Add contract amendment tracking
