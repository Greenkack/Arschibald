"""
Beta Tester Service

Manages beta testers, invitations, and access control
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import secrets
import hashlib

from ..models.beta_schemas import (
    BetaTesterCreate,
    BetaTesterUpdate,
    BetaTesterResponse,
    BetaInvitationCreate,
    BetaInvitationResponse,
)
from ..core.exceptions import APIError


class BetaTesterService:
    """Service for managing beta testers"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_beta_tester(
        self,
        tester_data: BetaTesterCreate
    ) -> BetaTesterResponse:
        """
        Create a new beta tester
        
        Args:
            tester_data: Beta tester creation data
            
        Returns:
            Created beta tester
        """
        # Check if email already exists
        existing = self.db.query(BetaTester).filter(
            BetaTester.email == tester_data.email
        ).first()
        
        if existing:
            raise APIError(
                status_code=400,
                message="Beta tester with this email already exists"
            )
        
        # Create beta tester
        tester = BetaTester(
            email=tester_data.email,
            name=tester_data.name,
            company=tester_data.company,
            role=tester_data.role,
            experience_level=tester_data.experience_level,
            areas_of_interest=tester_data.areas_of_interest,
            platform=tester_data.platform,
            status='pending',
            invited_at=datetime.utcnow(),
        )
        
        self.db.add(tester)
        self.db.commit()
        self.db.refresh(tester)
        
        return BetaTesterResponse.from_orm(tester)
    
    def get_beta_tester(self, tester_id: int) -> Optional[BetaTesterResponse]:
        """Get beta tester by ID"""
        tester = self.db.query(BetaTester).filter(
            BetaTester.id == tester_id
        ).first()
        
        if not tester:
            return None
        
        return BetaTesterResponse.from_orm(tester)
    
    def get_beta_tester_by_email(
        self,
        email: str
    ) -> Optional[BetaTesterResponse]:
        """Get beta tester by email"""
        tester = self.db.query(BetaTester).filter(
            BetaTester.email == email
        ).first()
        
        if not tester:
            return None
        
        return BetaTesterResponse.from_orm(tester)
    
    def list_beta_testers(
        self,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BetaTesterResponse]:
        """List beta testers with filters"""
        query = self.db.query(BetaTester)
        
        if status:
            query = query.filter(BetaTester.status == status)
        
        if platform:
            query = query.filter(BetaTester.platform == platform)
        
        testers = query.offset(skip).limit(limit).all()
        
        return [BetaTesterResponse.from_orm(t) for t in testers]
    
    def update_beta_tester(
        self,
        tester_id: int,
        tester_data: BetaTesterUpdate
    ) -> BetaTesterResponse:
        """Update beta tester"""
        tester = self.db.query(BetaTester).filter(
            BetaTester.id == tester_id
        ).first()
        
        if not tester:
            raise APIError(
                status_code=404,
                message="Beta tester not found"
            )
        
        # Update fields
        update_data = tester_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tester, field, value)
        
        tester.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(tester)
        
        return BetaTesterResponse.from_orm(tester)
    
    def activate_beta_tester(self, tester_id: int) -> BetaTesterResponse:
        """Activate a beta tester"""
        tester = self.db.query(BetaTester).filter(
            BetaTester.id == tester_id
        ).first()
        
        if not tester:
            raise APIError(
                status_code=404,
                message="Beta tester not found"
            )
        
        tester.status = 'active'
        tester.activated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(tester)
        
        return BetaTesterResponse.from_orm(tester)
    
    def deactivate_beta_tester(self, tester_id: int) -> BetaTesterResponse:
        """Deactivate a beta tester"""
        tester = self.db.query(BetaTester).filter(
            BetaTester.id == tester_id
        ).first()
        
        if not tester:
            raise APIError(
                status_code=404,
                message="Beta tester not found"
            )
        
        tester.status = 'inactive'
        
        self.db.commit()
        self.db.refresh(tester)
        
        return BetaTesterResponse.from_orm(tester)
    
    def create_invitation(
        self,
        tester_id: int,
        invitation_data: BetaInvitationCreate
    ) -> BetaInvitationResponse:
        """Create a beta invitation"""
        tester = self.db.query(BetaTester).filter(
            BetaTester.id == tester_id
        ).first()
        
        if not tester:
            raise APIError(
                status_code=404,
                message="Beta tester not found"
            )
        
        # Generate invitation code
        invitation_code = self.generate_invitation_code()
        
        # Create invitation
        invitation = BetaInvitation(
            tester_id=tester_id,
            code=invitation_code,
            expires_at=datetime.utcnow() + timedelta(days=invitation_data.valid_days),
            max_uses=invitation_data.max_uses,
            uses=0,
            status='active',
        )
        
        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)
        
        return BetaInvitationResponse.from_orm(invitation)
    
    def validate_invitation(self, code: str) -> Dict[str, Any]:
        """Validate an invitation code"""
        invitation = self.db.query(BetaInvitation).filter(
            BetaInvitation.code == code
        ).first()
        
        if not invitation:
            return {
                'valid': False,
                'reason': 'Invalid invitation code'
            }
        
        if invitation.status != 'active':
            return {
                'valid': False,
                'reason': 'Invitation is not active'
            }
        
        if invitation.expires_at < datetime.utcnow():
            return {
                'valid': False,
                'reason': 'Invitation has expired'
            }
        
        if invitation.max_uses and invitation.uses >= invitation.max_uses:
            return {
                'valid': False,
                'reason': 'Invitation has reached maximum uses'
            }
        
        return {
            'valid': True,
            'invitation': BetaInvitationResponse.from_orm(invitation)
        }
    
    def use_invitation(self, code: str) -> BetaInvitationResponse:
        """Use an invitation code"""
        validation = self.validate_invitation(code)
        
        if not validation['valid']:
            raise APIError(
                status_code=400,
                message=validation['reason']
            )
        
        invitation = self.db.query(BetaInvitation).filter(
            BetaInvitation.code == code
        ).first()
        
        invitation.uses += 1
        invitation.last_used_at = datetime.utcnow()
        
        # Deactivate if max uses reached
        if invitation.max_uses and invitation.uses >= invitation.max_uses:
            invitation.status = 'exhausted'
        
        self.db.commit()
        self.db.refresh(invitation)
        
        return BetaInvitationResponse.from_orm(invitation)
    
    def get_tester_statistics(self) -> Dict[str, Any]:
        """Get beta tester statistics"""
        total = self.db.query(BetaTester).count()
        active = self.db.query(BetaTester).filter(
            BetaTester.status == 'active'
        ).count()
        pending = self.db.query(BetaTester).filter(
            BetaTester.status == 'pending'
        ).count()
        inactive = self.db.query(BetaTester).filter(
            BetaTester.status == 'inactive'
        ).count()
        
        # Platform distribution
        platforms = self.db.query(
            BetaTester.platform,
            func.count(BetaTester.id)
        ).group_by(BetaTester.platform).all()
        
        return {
            'total': total,
            'active': active,
            'pending': pending,
            'inactive': inactive,
            'platforms': {p[0]: p[1] for p in platforms},
        }
    
    @staticmethod
    def generate_invitation_code() -> str:
        """Generate a unique invitation code"""
        # Generate random bytes
        random_bytes = secrets.token_bytes(16)
        
        # Create hash
        hash_obj = hashlib.sha256(random_bytes)
        hash_hex = hash_obj.hexdigest()
        
        # Take first 16 characters and format
        code = hash_hex[:16].upper()
        
        # Format as XXXX-XXXX-XXXX-XXXX
        return f"{code[:4]}-{code[4:8]}-{code[8:12]}-{code[12:16]}"


# Database models (would be in models/database_models.py)
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class BetaTester(Base):
    """Beta tester model"""
    __tablename__ = "beta_testers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    company = Column(String)
    role = Column(String)
    experience_level = Column(String)  # beginner, intermediate, advanced, expert
    areas_of_interest = Column(Text)  # JSON array
    platform = Column(String)  # windows, macos, linux
    status = Column(String, default='pending')  # pending, active, inactive
    invited_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime)
    last_active_at = Column(DateTime)
    feedback_count = Column(Integer, default=0)
    crash_reports_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invitations = relationship("BetaInvitation", back_populates="tester")
    feedback = relationship("BetaFeedback", back_populates="tester")


class BetaInvitation(Base):
    """Beta invitation model"""
    __tablename__ = "beta_invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    tester_id = Column(Integer, ForeignKey("beta_testers.id"))
    code = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    max_uses = Column(Integer)
    uses = Column(Integer, default=0)
    status = Column(String, default='active')  # active, exhausted, revoked
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tester = relationship("BetaTester", back_populates="invitations")
