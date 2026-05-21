"""
Database Setup and Configuration Demo

Demonstrates the database setup with SQLAlchemy async support,
connection pooling, session management, and Alembic migrations.

Requirements: 1.2, 1.5
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from backend.core.database import (
    engine,
    async_engine,
    SessionLocal,
    AsyncSessionLocal,
    init_db,
    init_async_db,
    check_db_connection,
    check_async_db_connection,
    get_db_stats,
    transaction,
    async_transaction,
)
from backend.core.dependencies import (
    get_pagination_params,
    BatchOperationContext,
)
from backend.models.database_models import User, Customer, Project


def demo_sync_database():
    """Demonstrate synchronous database operations"""
    print("\n" + "="*80)
    print("SYNCHRONOUS DATABASE OPERATIONS")
    print("="*80)
    
    # Check connection
    print("\n1. Checking database connection...")
    if check_db_connection():
        print("   ✓ Database connection successful")
    else:
        print("   ✗ Database connection failed")
        return
    
    # Initialize database
    print("\n2. Initializing database...")
    init_db()
    print("   ✓ Database initialized with all tables")
    
    # Get pool statistics
    print("\n3. Connection pool statistics:")
    stats = get_db_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    # Create a session
    print("\n4. Creating database session...")
    db = SessionLocal()
    try:
        # Create a user
        print("\n5. Creating a user...")
        user = User(
            username="demo_user",
            email="demo@example.com",
            hashed_password="hashed_password_here",
            full_name="Demo User",
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"   ✓ User created with ID: {user.id}")
        print(f"   - Username: {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - Dynamic Key: {user.dynamic_key}")
        
        # Query users
        print("\n6. Querying users...")
        users = db.query(User).all()
        print(f"   ✓ Found {len(users)} user(s)")
        
        # Use transaction context
        print("\n7. Using transaction context...")
        with transaction(db) as tx:
            customer = Customer(
                name="Demo Customer",
                email="customer@example.com",
                phone="+49 123 456789",
                city="Berlin",
                country="Germany"
            )
            tx.add(customer)
        print("   ✓ Customer created in transaction")
        
        # Pagination example
        print("\n8. Pagination example...")
        pagination = get_pagination_params(skip=0, limit=10)
        query = db.query(User)
        paginated_users = pagination.apply_to_query(query).all()
        print(f"   ✓ Retrieved {len(paginated_users)} users (page 1)")
        
        # Batch operations
        print("\n9. Batch operations...")
        with BatchOperationContext(db, batch_size=5) as batch_ctx:
            for i in range(12):
                project = Project(
                    name=f"Project {i+1}",
                    customer_id=1,
                    project_type="solar",
                    status="draft"
                )
                batch_ctx.add(project)
        print("   ✓ Created 12 projects in batches")
        
        # Verify batch creation
        project_count = db.query(Project).count()
        print(f"   - Total projects in database: {project_count}")
        
    finally:
        db.close()
        print("\n10. Session closed")


async def demo_async_database():
    """Demonstrate asynchronous database operations"""
    print("\n" + "="*80)
    print("ASYNCHRONOUS DATABASE OPERATIONS")
    print("="*80)
    
    # Check async connection
    print("\n1. Checking async database connection...")
    if await check_async_db_connection():
        print("   ✓ Async database connection successful")
    else:
        print("   ✗ Async database connection failed")
        return
    
    # Initialize async database
    print("\n2. Initializing async database...")
    await init_async_db()
    print("   ✓ Async database initialized")
    
    # Create async session
    print("\n3. Creating async database session...")
    async with AsyncSessionLocal() as session:
        # Create a user asynchronously
        print("\n4. Creating a user asynchronously...")
        user = User(
            username="async_user",
            email="async@example.com",
            hashed_password="hashed_password_here",
            full_name="Async User",
            role="user"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"   ✓ User created with ID: {user.id}")
        print(f"   - Username: {user.username}")
        print(f"   - Email: {user.email}")
        
        # Query users asynchronously
        print("\n5. Querying users asynchronously...")
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"   ✓ Found {len(users)} user(s)")
        
        # Use async transaction context
        print("\n6. Using async transaction context...")
        async with async_transaction(session) as tx:
            customer = Customer(
                name="Async Customer",
                email="async_customer@example.com",
                phone="+49 987 654321",
                city="Munich",
                country="Germany"
            )
            tx.add(customer)
        print("   ✓ Customer created in async transaction")
        
        # Query with filter
        print("\n7. Querying with filter...")
        result = await session.execute(
            select(User).filter(User.username == "async_user")
        )
        user = result.scalar_one_or_none()
        if user:
            print(f"   ✓ Found user: {user.username}")
        
        # Count records
        print("\n8. Counting records...")
        result = await session.execute(select(User))
        user_count = len(result.scalars().all())
        print(f"   - Total users: {user_count}")


def demo_model_features():
    """Demonstrate model features with universal data support"""
    print("\n" + "="*80)
    print("MODEL FEATURES WITH UNIVERSAL DATA SUPPORT")
    print("="*80)
    
    db = SessionLocal()
    try:
        # Create a user with dynamic key
        print("\n1. Creating user with dynamic key...")
        user = User(
            username="feature_user",
            email="features@example.com",
            hashed_password="hashed",
            full_name="Feature Demo User"
        )
        from backend.core.dynamic_keys import KeyPrefix
        user.generate_and_store_key(KeyPrefix.USER)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"   ✓ User created with dynamic key: {user.dynamic_key}")
        
        # Get formatted values
        print("\n2. Getting formatted values (German format)...")
        # Create a project with numeric values
        project = Project(
            name="Solar Installation",
            customer_id=1,
            project_type="solar",
            status="active"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        print(f"   - Project ID: {project.id}")
        print(f"   - Created at: {project.get_formatted_value('created_at', locale='de-DE')}")
        
        # Convert to dictionary
        print("\n3. Converting model to dictionary...")
        user_dict = user.to_dict(include_keys=True, formatted=False)
        print(f"   ✓ User dictionary keys: {list(user_dict.keys())[:5]}...")
        
        # JSON serializable
        print("\n4. Converting to JSON-serializable format...")
        user_json = user.to_json_serializable()
        print(f"   ✓ JSON-serializable data ready")
        print(f"   - Keys: {list(user_json.keys())[:5]}...")
        
    finally:
        db.close()


def demo_connection_pooling():
    """Demonstrate connection pooling"""
    print("\n" + "="*80)
    print("CONNECTION POOLING DEMONSTRATION")
    print("="*80)
    
    print("\n1. Initial pool statistics:")
    stats = get_db_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    print("\n2. Creating multiple sessions...")
    sessions = []
    for i in range(3):
        session = SessionLocal()
        sessions.append(session)
        print(f"   - Session {i+1} created")
    
    print("\n3. Pool statistics with active sessions:")
    stats = get_db_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    print("\n4. Closing sessions...")
    for i, session in enumerate(sessions):
        session.close()
        print(f"   - Session {i+1} closed")
    
    print("\n5. Final pool statistics:")
    stats = get_db_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")


def main():
    """Run all demonstrations"""
    print("\n" + "="*80)
    print("DATABASE SETUP AND CONFIGURATION DEMONSTRATION")
    print("="*80)
    print("\nThis demo showcases:")
    print("  • SQLAlchemy with async support")
    print("  • Database connection management")
    print("  • Session dependencies")
    print("  • Connection pooling")
    print("  • Transaction management")
    print("  • Base database models")
    print("  • Alembic migrations setup")
    
    try:
        # Run sync demos
        demo_sync_database()
        demo_model_features()
        demo_connection_pooling()
        
        # Run async demos
        print("\n" + "="*80)
        print("Running async demonstrations...")
        print("="*80)
        asyncio.run(demo_async_database())
        
        print("\n" + "="*80)
        print("DEMONSTRATION COMPLETE")
        print("="*80)
        print("\n✓ All database features demonstrated successfully!")
        print("\nNext steps:")
        print("  1. Run 'alembic revision --autogenerate -m \"Initial migration\"'")
        print("  2. Run 'alembic upgrade head' to apply migrations")
        print("  3. Use the database in your FastAPI endpoints")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
