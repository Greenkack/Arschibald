"""
Contract Management Service

This module provides comprehensive contract management functionality including
contract creation, templates, approval workflows, e-signatures, and renewals.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib

from backend.models.contract_models import (
    Contract, ContractTemplate, ContractApproval, ContractSignature,
    ContractRenewal, ContractAnalytics, ContractStatus, ContractType,
    ApprovalStatus, SignatureStatus
)
from backend.models.contract_schemas import (
    ContractCreate, ContractUpdate, ContractTemplateCreate, ContractTemplateUpdate,
    ContractApprovalCreate, ContractApprovalDecision, ContractSignatureRequest,
    ContractSignatureSubmit, ContractRenewalCreate, ContractListFilters
)


class ContractService:
    """Service for managing contracts."""

    def __init__(self, db: Session):
        """Initialize contract service."""
        self.db = db

    # ==================== Contract CRUD ====================

    def create_contract(self, contract_data: ContractCreate, user_id: Optional[int] = None) -> Contract:
        """Create a new contract."""
        # Generate unique contract number
        contract_number = self._generate_contract_number()
        
        contract = Contract(
            contract_number=contract_number,
            **contract_data.dict(),
            status=ContractStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        
        return contract

    def get_contract(self, contract_id: int) -> Optional[Contract]:
        """Get contract by ID."""
        return self.db.query(Contract).filter(Contract.id == contract_id).first()

    def get_contract_by_number(self, contract_number: str) -> Optional[Contract]:
        """Get contract by contract number."""
        return self.db.query(Contract).filter(Contract.contract_number == contract_number).first()

    def update_contract(self, contract_id: int, contract_data: ContractUpdate, user_id: Optional[int] = None) -> Optional[Contract]:
        """Update a contract."""
        contract = self.get_contract(contract_id)
        if not contract:
            return None
        
        update_data = contract_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contract, field, value)
        
        contract.updated_by = user_id
        contract.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(contract)
        
        return contract

    def delete_contract(self, contract_id: int) -> bool:
        """Delete a contract."""
        contract = self.get_contract(contract_id)
        if not contract:
            return False
        
        self.db.delete(contract)
        self.db.commit()
        
        return True

    def list_contracts(self, filters: ContractListFilters) -> tuple[List[Contract], int]:
        """List contracts with filters."""
        query = self.db.query(Contract)
        
        # Apply filters
        if filters.customer_id:
            query = query.filter(Contract.customer_id == filters.customer_id)
        if filters.contract_type:
            query = query.filter(Contract.contract_type == filters.contract_type)
        if filters.status:
            query = query.filter(Contract.status == filters.status)
        if filters.start_date_from:
            query = query.filter(Contract.start_date >= filters.start_date_from)
        if filters.start_date_to:
            query = query.filter(Contract.start_date <= filters.start_date_to)
        if filters.end_date_from:
            query = query.filter(Contract.end_date >= filters.end_date_from)
        if filters.end_date_to:
            query = query.filter(Contract.end_date <= filters.end_date_to)
        if filters.min_value is not None:
            query = query.filter(Contract.value >= filters.min_value)
        if filters.max_value is not None:
            query = query.filter(Contract.value <= filters.max_value)
        if filters.auto_renew is not None:
            query = query.filter(Contract.auto_renew == filters.auto_renew)
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Contract.title.ilike(search_term),
                    Contract.contract_number.ilike(search_term),
                    Contract.notes.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        contracts = query.offset(filters.skip).limit(filters.limit).all()
        
        return contracts, total

    # ==================== Contract Templates ====================

    def create_template(self, template_data: ContractTemplateCreate, user_id: Optional[int] = None) -> ContractTemplate:
        """Create a contract template."""
        template = ContractTemplate(
            **template_data.dict(),
            created_by=user_id
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        return template

    def get_template(self, template_id: int) -> Optional[ContractTemplate]:
        """Get template by ID."""
        return self.db.query(ContractTemplate).filter(ContractTemplate.id == template_id).first()

    def list_templates(self, contract_type: Optional[ContractType] = None, active_only: bool = True) -> List[ContractTemplate]:
        """List contract templates."""
        query = self.db.query(ContractTemplate)
        
        if contract_type:
            query = query.filter(ContractTemplate.contract_type == contract_type)
        if active_only:
            query = query.filter(ContractTemplate.is_active == True)
        
        return query.all()

    def update_template(self, template_id: int, template_data: ContractTemplateUpdate) -> Optional[ContractTemplate]:
        """Update a contract template."""
        template = self.get_template(template_id)
        if not template:
            return None
        
        update_data = template_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(template)
        
        return template

    def generate_contract_from_template(self, template_id: int, variables: Dict[str, Any], customer_id: int, user_id: Optional[int] = None) -> Optional[Contract]:
        """Generate a contract from a template."""
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Replace variables in template
        title = self._replace_variables(template.title_template, variables)
        content = self._replace_variables(template.content_template, variables)
        terms = self._replace_variables(template.terms_template, variables) if template.terms_template else None
        
        # Create contract
        contract_data = ContractCreate(
            title=title,
            contract_type=template.contract_type,
            customer_id=customer_id,
            template_id=template_id,
            start_date=variables.get('start_date', datetime.utcnow()),
            end_date=variables.get('end_date', datetime.utcnow() + timedelta(days=365)),
            value=variables.get('value', 0.0),
            currency=variables.get('currency', 'EUR'),
            payment_terms=variables.get('payment_terms'),
            terms_and_conditions=terms,
            special_clauses=variables.get('special_clauses'),
            notes=variables.get('notes'),
            metadata=variables,
            auto_renew=variables.get('auto_renew', False),
            renewal_notice_days=variables.get('renewal_notice_days', 30)
        )
        
        return self.create_contract(contract_data, user_id)

    # ==================== Approval Workflow ====================

    def request_approval(self, approval_data: ContractApprovalCreate) -> ContractApproval:
        """Request contract approval."""
        approval = ContractApproval(**approval_data.dict())
        
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        
        # Update contract status
        contract = self.get_contract(approval_data.contract_id)
        if contract and contract.status == ContractStatus.DRAFT:
            contract.status = ContractStatus.PENDING_APPROVAL
            self.db.commit()
        
        return approval

    def process_approval(self, approval_id: int, decision: ContractApprovalDecision, user_id: Optional[int] = None) -> Optional[ContractApproval]:
        """Process an approval decision."""
        approval = self.db.query(ContractApproval).filter(ContractApproval.id == approval_id).first()
        if not approval:
            return None
        
        approval.status = decision.status
        approval.comments = decision.comments
        approval.decision_date = datetime.utcnow()
        
        self.db.commit()
        
        # Update contract status if approved
        if decision.status == ApprovalStatus.APPROVED:
            contract = self.get_contract(approval.contract_id)
            if contract:
                # Check if all approvals are complete
                all_approved = all(
                    a.status == ApprovalStatus.APPROVED
                    for a in contract.approvals
                )
                if all_approved:
                    contract.status = ContractStatus.APPROVED
                    self.db.commit()
        
        return approval

    def get_pending_approvals(self, approver_id: int) -> List[ContractApproval]:
        """Get pending approvals for an approver."""
        return self.db.query(ContractApproval).filter(
            and_(
                ContractApproval.approver_id == approver_id,
                ContractApproval.status == ApprovalStatus.PENDING
            )
        ).all()

    # ==================== E-Signature ====================

    def request_signature(self, signature_data: ContractSignatureRequest) -> ContractSignature:
        """Request an e-signature."""
        # Generate verification code
        verification_code = secrets.token_urlsafe(32)
        
        # Calculate expiration date
        expires_at = datetime.utcnow() + timedelta(days=signature_data.expires_in_days)
        
        signature = ContractSignature(
            contract_id=signature_data.contract_id,
            signer_name=signature_data.signer_name,
            signer_email=signature_data.signer_email,
            signer_role=signature_data.signer_role,
            verification_code=verification_code,
            expires_at=expires_at
        )
        
        self.db.add(signature)
        self.db.commit()
        self.db.refresh(signature)
        
        # TODO: Send email with signature request
        
        return signature

    def submit_signature(self, signature_id: int, signature_data: ContractSignatureSubmit, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Optional[ContractSignature]:
        """Submit an e-signature."""
        signature = self.db.query(ContractSignature).filter(ContractSignature.id == signature_id).first()
        if not signature:
            return None
        
        # Verify signature is still pending and not expired
        if signature.status != SignatureStatus.PENDING:
            return None
        if signature.expires_at and signature.expires_at < datetime.utcnow():
            signature.status = SignatureStatus.EXPIRED
            self.db.commit()
            return None
        
        # Verify code if provided
        if signature_data.verification_code:
            if signature.verification_code != signature_data.verification_code:
                return None
            signature.is_verified = True
        
        # Save signature
        signature.signature_data = signature_data.signature_data
        signature.signature_method = signature_data.signature_method
        signature.status = SignatureStatus.SIGNED
        signature.signed_at = datetime.utcnow()
        signature.ip_address = ip_address
        signature.user_agent = user_agent
        
        self.db.commit()
        
        # Update contract status if all signatures are complete
        contract = self.get_contract(signature.contract_id)
        if contract:
            all_signed = all(
                s.status == SignatureStatus.SIGNED
                for s in contract.signatures
            )
            if all_signed:
                contract.status = ContractStatus.ACTIVE
                contract.signed_date = datetime.utcnow()
                self.db.commit()
        
        return signature

    def get_pending_signatures(self, signer_email: str) -> List[ContractSignature]:
        """Get pending signatures for a signer."""
        return self.db.query(ContractSignature).filter(
            and_(
                ContractSignature.signer_email == signer_email,
                ContractSignature.status == SignatureStatus.PENDING,
                or_(
                    ContractSignature.expires_at == None,
                    ContractSignature.expires_at > datetime.utcnow()
                )
            )
        ).all()

    # ==================== Contract Renewal ====================

    def renew_contract(self, renewal_data: ContractRenewalCreate, user_id: Optional[int] = None) -> Optional[ContractRenewal]:
        """Renew a contract."""
        contract = self.get_contract(renewal_data.contract_id)
        if not contract:
            return None
        
        # Calculate new value if not provided
        new_value = renewal_data.new_value if renewal_data.new_value is not None else contract.value
        value_change_percent = ((new_value - contract.value) / contract.value * 100) if contract.value > 0 else 0
        
        # Create renewal record
        renewal = ContractRenewal(
            contract_id=renewal_data.contract_id,
            renewal_number=contract.renewal_count + 1,
            previous_end_date=contract.end_date,
            new_end_date=renewal_data.new_end_date,
            previous_value=contract.value,
            new_value=new_value,
            value_change_percent=value_change_percent,
            is_automatic=False,
            notes=renewal_data.notes
        )
        
        self.db.add(renewal)
        
        # Update contract
        contract.end_date = renewal_data.new_end_date
        contract.value = new_value
        contract.renewal_count += 1
        contract.renewal_date = datetime.utcnow()
        contract.status = ContractStatus.RENEWED
        contract.updated_by = user_id
        contract.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(renewal)
        
        return renewal

    def get_expiring_contracts(self, days: int = 30, include_auto_renew: bool = False) -> List[Contract]:
        """Get contracts expiring within specified days."""
        expiry_date = datetime.utcnow() + timedelta(days=days)
        
        query = self.db.query(Contract).filter(
            and_(
                Contract.end_date <= expiry_date,
                Contract.end_date >= datetime.utcnow(),
                Contract.status.in_([ContractStatus.ACTIVE, ContractStatus.APPROVED])
            )
        )
        
        if not include_auto_renew:
            query = query.filter(Contract.auto_renew == False)
        
        return query.all()

    def process_auto_renewals(self) -> List[ContractRenewal]:
        """Process automatic contract renewals."""
        # Get contracts that need auto-renewal
        contracts = self.db.query(Contract).filter(
            and_(
                Contract.auto_renew == True,
                Contract.status == ContractStatus.ACTIVE,
                Contract.end_date <= datetime.utcnow() + timedelta(days=Contract.renewal_notice_days)
            )
        ).all()
        
        renewals = []
        for contract in contracts:
            # Calculate new end date (1 year from current end date)
            new_end_date = contract.end_date + timedelta(days=365)
            
            renewal_data = ContractRenewalCreate(
                contract_id=contract.id,
                new_end_date=new_end_date,
                new_value=contract.value,
                notes="Automatic renewal"
            )
            
            renewal = self.renew_contract(renewal_data)
            if renewal:
                renewal.is_automatic = True
                self.db.commit()
                renewals.append(renewal)
        
        return renewals

    # ==================== Contract Analytics ====================

    def calculate_analytics(self, period_start: datetime, period_end: datetime) -> ContractAnalytics:
        """Calculate contract analytics for a period."""
        # Get contracts in period
        contracts = self.db.query(Contract).filter(
            or_(
                and_(Contract.start_date >= period_start, Contract.start_date <= period_end),
                and_(Contract.end_date >= period_start, Contract.end_date <= period_end),
                and_(Contract.start_date <= period_start, Contract.end_date >= period_end)
            )
        ).all()
        
        # Calculate metrics
        total_contracts = len(contracts)
        active_contracts = sum(1 for c in contracts if c.status == ContractStatus.ACTIVE)
        expired_contracts = sum(1 for c in contracts if c.status == ContractStatus.EXPIRED)
        renewed_contracts = sum(1 for c in contracts if c.status == ContractStatus.RENEWED)
        terminated_contracts = sum(1 for c in contracts if c.status == ContractStatus.TERMINATED)
        
        total_value = sum(c.value for c in contracts)
        average_value = total_value / total_contracts if total_contracts > 0 else 0
        renewal_rate = (renewed_contracts / total_contracts * 100) if total_contracts > 0 else 0
        
        # Metrics by type
        metrics_by_type = {}
        for contract_type in ContractType:
            type_contracts = [c for c in contracts if c.contract_type == contract_type]
            if type_contracts:
                metrics_by_type[contract_type.value] = {
                    'count': len(type_contracts),
                    'total_value': sum(c.value for c in type_contracts),
                    'average_value': sum(c.value for c in type_contracts) / len(type_contracts)
                }
        
        # Create or update analytics record
        analytics = ContractAnalytics(
            period_start=period_start,
            period_end=period_end,
            total_contracts=total_contracts,
            active_contracts=active_contracts,
            expired_contracts=expired_contracts,
            renewed_contracts=renewed_contracts,
            terminated_contracts=terminated_contracts,
            total_value=total_value,
            average_value=average_value,
            renewal_rate=renewal_rate,
            metrics_by_type=metrics_by_type
        )
        
        self.db.add(analytics)
        self.db.commit()
        self.db.refresh(analytics)
        
        return analytics

    def get_analytics(self, period_start: datetime, period_end: datetime) -> Optional[ContractAnalytics]:
        """Get analytics for a period."""
        return self.db.query(ContractAnalytics).filter(
            and_(
                ContractAnalytics.period_start == period_start,
                ContractAnalytics.period_end == period_end
            )
        ).first()

    # ==================== Helper Methods ====================

    def _generate_contract_number(self) -> str:
        """Generate a unique contract number."""
        # Format: CON-YYYYMMDD-XXXX
        date_part = datetime.utcnow().strftime("%Y%m%d")
        
        # Get count of contracts created today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = self.db.query(func.count(Contract.id)).filter(
            Contract.created_at >= today_start
        ).scalar()
        
        sequence = str(today_count + 1).zfill(4)
        
        return f"CON-{date_part}-{sequence}"

    def _replace_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Replace variables in template string."""
        if not template:
            return ""
        
        result = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result

    def terminate_contract(self, contract_id: int, reason: Optional[str] = None, user_id: Optional[int] = None) -> Optional[Contract]:
        """Terminate a contract."""
        contract = self.get_contract(contract_id)
        if not contract:
            return None
        
        contract.status = ContractStatus.TERMINATED
        contract.termination_date = datetime.utcnow()
        if reason:
            contract.notes = f"{contract.notes}\n\nTermination reason: {reason}" if contract.notes else f"Termination reason: {reason}"
        contract.updated_by = user_id
        contract.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(contract)
        
        return contract

    def activate_contract(self, contract_id: int, user_id: Optional[int] = None) -> Optional[Contract]:
        """Activate an approved contract."""
        contract = self.get_contract(contract_id)
        if not contract:
            return None
        
        if contract.status != ContractStatus.APPROVED:
            return None
        
        contract.status = ContractStatus.ACTIVE
        contract.updated_by = user_id
        contract.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(contract)
        
        return contract

    def get_contract_history(self, contract_id: int) -> Dict[str, Any]:
        """Get complete history of a contract."""
        contract = self.get_contract(contract_id)
        if not contract:
            return {}
        
        return {
            'contract': contract,
            'approvals': contract.approvals,
            'signatures': contract.signatures,
            'renewals': contract.renewals
        }
