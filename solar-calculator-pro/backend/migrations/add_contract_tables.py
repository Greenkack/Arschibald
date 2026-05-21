"""
Database Migration: Add Contract Management Tables

This migration adds all tables required for contract management including
contracts, templates, approvals, signatures, renewals, and analytics.
"""

from sqlalchemy import create_engine, MetaData
from backend.models.contract_models import (
    Contract, ContractTemplate, ContractApproval, ContractSignature,
    ContractRenewal, ContractAnalytics
)
from backend.core.database import Base, engine


def upgrade():
    """Create contract management tables."""
    print("Creating contract management tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine, tables=[
        Contract.__table__,
        ContractTemplate.__table__,
        ContractApproval.__table__,
        ContractSignature.__table__,
        ContractRenewal.__table__,
        ContractAnalytics.__table__
    ])
    
    print("✓ Contract management tables created successfully")


def downgrade():
    """Drop contract management tables."""
    print("Dropping contract management tables...")
    
    # Drop all tables in reverse order
    Base.metadata.drop_all(bind=engine, tables=[
        ContractAnalytics.__table__,
        ContractRenewal.__table__,
        ContractSignature.__table__,
        ContractApproval.__table__,
        ContractTemplate.__table__,
        Contract.__table__
    ])
    
    print("✓ Contract management tables dropped successfully")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
