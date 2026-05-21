"""
Contract Management API Endpoints

This module provides REST API endpoints for contract management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.database import get_db
from backend.services.contract_service import ContractService
from backend.models.contract_schemas import (
    ContractCreate, ContractUpdate, ContractResponse, ContractListResponse,
    ContractListFilters, ContractTemplateCreate, ContractTemplateUpdate,
    ContractTemplateResponse, ContractApprovalCreate, ContractApprovalDecision,
    ContractApprovalResponse, ContractSignatureRequest, ContractSignatureSubmit,
    ContractSignatureResponse, ContractRenewalCreate, ContractRenewalResponse,
    ContractAnalyticsResponse, ExpiringContractsRequest
)

router = APIRouter(prefix="/contracts", tags=["contracts"])


def get_contract_service(db: Session = Depends(get_db)) -> ContractService:
    """Get contract service instance."""
    return ContractService(db)


# ==================== Contract Endpoints ====================

@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_data: ContractCreate,
    service: ContractService = Depends(get_contract_service)
):
    """Create a new contract."""
    try:
        contract = service.create_contract(contract_data)
        return contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    service: ContractService = Depends(get_contract_service)
):
    """Get contract by ID."""
    contract = service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get("/number/{contract_number}", response_model=ContractResponse)
async def get_contract_by_number(
    contract_number: str,
    service: ContractService = Depends(get_contract_service)
):
    """Get contract by contract number."""
    contract = service.get_contract_by_number(contract_number)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    service: ContractService = Depends(get_contract_service)
):
    """Update a contract."""
    contract = service.update_contract(contract_id, contract_data)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: int,
    service: ContractService = Depends(get_contract_service)
):
    """Delete a contract."""
    success = service.delete_contract(contract_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")


@router.post("/list", response_model=ContractListResponse)
async def list_contracts(
    filters: ContractListFilters,
    service: ContractService = Depends(get_contract_service)
):
    """List contracts with filters."""
    contracts, total = service.list_contracts(filters)
    return {"total": total, "contracts": contracts}


@router.post("/{contract_id}/terminate", response_model=ContractResponse)
async def terminate_contract(
    contract_id: int,
    reason: Optional[str] = None,
    service: ContractService = Depends(get_contract_service)
):
    """Terminate a contract."""
    contract = service.terminate_contract(contract_id, reason)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.post("/{contract_id}/activate", response_model=ContractResponse)
async def activate_contract(
    contract_id: int,
    service: ContractService = Depends(get_contract_service)
):
    """Activate an approved contract."""
    contract = service.activate_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found or not approved")
    return contract


@router.get("/{contract_id}/history")
async def get_contract_history(
    contract_id: int,
    service: ContractService = Depends(get_contract_service)
):
    """Get complete history of a contract."""
    history = service.get_contract_history(contract_id)
    if not history:
        raise HTTPException(status_code=404, detail="Contract not found")
    return history


# ==================== Template Endpoints ====================

@router.post("/templates", response_model=ContractTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: ContractTemplateCreate,
    service: ContractService = Depends(get_contract_service)
):
    """Create a contract template."""
    try:
        template = service.create_template(template_data)
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}", response_model=ContractTemplateResponse)
async def get_template(
    template_id: int,
    service: ContractService = Depends(get_contract_service)
):
    """Get template by ID."""
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.get("/templates", response_model=List[ContractTemplateResponse])
async def list_templates(
    contract_type: Optional[str] = None,
    active_only: bool = True,
    service: ContractService = Depends(get_contract_service)
):
    """List contract templates."""
    templates = service.list_templates(contract_type, active_only)
    return templates


@router.put("/templates/{template_id}", response_model=ContractTemplateResponse)
async def update_template(
    template_id: int,
    template_data: ContractTemplateUpdate,
    service: ContractService = Depends(get_contract_service)
):
    """Update a contract template."""
    template = service.update_template(template_id, template_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/templates/{template_id}/generate", response_model=ContractResponse)
async def generate_from_template(
    template_id: int,
    variables: dict,
    customer_id: int,
    service: ContractService = Depends(get_contract_service)
):
    """Generate a contract from a template."""
    contract = service.generate_contract_from_template(template_id, variables, customer_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Template not found")
    return contract


# ==================== Approval Endpoints ====================

@router.post("/approvals", response_model=ContractApprovalResponse, status_code=status.HTTP_201_CREATED)
async def request_approval(
    approval_data: ContractApprovalCreate,
    service: ContractService = Depends(get_contract_service)
):
    """Request contract approval."""
    try:
        approval = service.request_approval(approval_data)
        return approval
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approvals/{approval_id}/decision", response_model=ContractApprovalResponse)
async def process_approval(
    approval_id: int,
    decision: ContractApprovalDecision,
    service: ContractService = Depends(get_contract_service)
):
    """Process an approval decision."""
    approval = service.process_approval(approval_id, decision)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@router.get("/approvals/pending/{approver_id}", response_model=List[ContractApprovalResponse])
async def get_pending_approvals(
    approver_id: int,
    service: ContractService = Depends(get_contract_service)
):
    """Get pending approvals for an approver."""
    approvals = service.get_pending_approvals(approver_id)
    return approvals


# ==================== Signature Endpoints ====================

@router.post("/signatures", response_model=ContractSignatureResponse, status_code=status.HTTP_201_CREATED)
async def request_signature(
    signature_data: ContractSignatureRequest,
    service: ContractService = Depends(get_contract_service)
):
    """Request an e-signature."""
    try:
        signature = service.request_signature(signature_data)
        return signature
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/signatures/{signature_id}/submit", response_model=ContractSignatureResponse)
async def submit_signature(
    signature_id: int,
    signature_data: ContractSignatureSubmit,
    request: Request,
    service: ContractService = Depends(get_contract_service)
):
    """Submit an e-signature."""
    # Get IP address and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    signature = service.submit_signature(signature_id, signature_data, ip_address, user_agent)
    if not signature:
        raise HTTPException(status_code=400, detail="Invalid signature request or expired")
    return signature


@router.get("/signatures/pending/{signer_email}", response_model=List[ContractSignatureResponse])
async def get_pending_signatures(
    signer_email: str,
    service: ContractService = Depends(get_contract_service)
):
    """Get pending signatures for a signer."""
    signatures = service.get_pending_signatures(signer_email)
    return signatures


# ==================== Renewal Endpoints ====================

@router.post("/renewals", response_model=ContractRenewalResponse, status_code=status.HTTP_201_CREATED)
async def renew_contract(
    renewal_data: ContractRenewalCreate,
    service: ContractService = Depends(get_contract_service)
):
    """Renew a contract."""
    renewal = service.renew_contract(renewal_data)
    if not renewal:
        raise HTTPException(status_code=404, detail="Contract not found")
    return renewal


@router.post("/renewals/expiring", response_model=List[ContractResponse])
async def get_expiring_contracts(
    request_data: ExpiringContractsRequest,
    service: ContractService = Depends(get_contract_service)
):
    """Get contracts expiring within specified days."""
    contracts = service.get_expiring_contracts(request_data.days, request_data.include_auto_renew)
    return contracts


@router.post("/renewals/process-auto")
async def process_auto_renewals(
    service: ContractService = Depends(get_contract_service)
):
    """Process automatic contract renewals."""
    renewals = service.process_auto_renewals()
    return {"processed": len(renewals), "renewals": renewals}


# ==================== Analytics Endpoints ====================

@router.post("/analytics", response_model=ContractAnalyticsResponse)
async def calculate_analytics(
    period_start: str,
    period_end: str,
    service: ContractService = Depends(get_contract_service)
):
    """Calculate contract analytics for a period."""
    from datetime import datetime
    
    try:
        start = datetime.fromisoformat(period_start)
        end = datetime.fromisoformat(period_end)
        
        analytics = service.calculate_analytics(start, end)
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{period_start}/{period_end}", response_model=ContractAnalyticsResponse)
async def get_analytics(
    period_start: str,
    period_end: str,
    service: ContractService = Depends(get_contract_service)
):
    """Get analytics for a period."""
    from datetime import datetime
    
    try:
        start = datetime.fromisoformat(period_start)
        end = datetime.fromisoformat(period_end)
        
        analytics = service.get_analytics(start, end)
        if not analytics:
            # Calculate if not exists
            analytics = service.calculate_analytics(start, end)
        
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
