"""
Controlling System Database Initialization

Handles database setup and initialization of standard criteria.

Requirements: 5.2
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.core.database import engine, Base, SessionLocal
from controlling.models import Criterion, STANDARD_CRITERIA, CalculationMethod

logger = logging.getLogger(__name__)


def init_controlling_db():
    """
    Initialize controlling database tables.
    Creates all tables defined in controlling.models.
    
    Requirements: 2.1, 4.1, 5.1
    """
    try:
        logger.info("Initializing controlling database tables...")
        # Import models to ensure they're registered with Base
        from controlling import models
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Controlling database tables created successfully")
        
        # Initialize standard criteria
        init_standard_criteria()
        
    except Exception as e:
        logger.error(f"Failed to initialize controlling database: {e}")
        raise


def init_standard_criteria():
    """
    Initialize standard criteria in the database.
    Only creates criteria that don't already exist.
    
    Requirements: 5.2
    """
    db = SessionLocal()
    try:
        logger.info("Initializing standard criteria...")
        
        for criterion_data in STANDARD_CRITERIA:
            # Check if criterion already exists
            existing = db.query(Criterion).filter(
                Criterion.name == criterion_data["name"]
            ).first()
            
            if not existing:
                criterion = Criterion(**criterion_data)
                db.add(criterion)
                logger.info(f"Created standard criterion: {criterion_data['name']}")
        
        db.commit()
        logger.info("Standard criteria initialized successfully")
        
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Some standard criteria already exist: {e}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to initialize standard criteria: {e}")
        raise
    finally:
        db.close()


def drop_controlling_db():
    """
    Drop all controlling database tables.
    WARNING: This will delete all controlling data!
    """
    try:
        logger.warning("Dropping all controlling database tables...")
        from controlling import models
        
        # Drop only controlling tables
        for table in [
            models.Report.__table__,
            models.PerformanceData.__table__,
            models.PositionCriterion.__table__,
            models.Criterion.__table__,
            models.Employee.__table__,
            models.Position.__table__,
        ]:
            table.drop(engine, checkfirst=True)
        
        logger.info("All controlling tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop controlling tables: {e}")
        raise


def check_controlling_db() -> bool:
    """
    Check if controlling database tables exist and are accessible.
    
    Returns:
        bool: True if tables exist and are accessible, False otherwise
    """
    from controlling.models import Position, Employee, PositionCriterion, PerformanceData, Report
    
    db = SessionLocal()
    try:
        # Try to query each table
        db.query(Position).first()
        db.query(Criterion).first()
        db.query(Employee).first()
        db.query(PositionCriterion).first()
        db.query(PerformanceData).first()
        db.query(Report).first()
        
        logger.info("Controlling database check successful")
        return True
    except Exception as e:
        logger.error(f"Controlling database check failed: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database
    print("Initializing Controlling Database...")
    init_controlling_db()
    
    # Check database
    if check_controlling_db():
        print("✓ Controlling database initialized and verified successfully!")
    else:
        print("✗ Controlling database verification failed!")
