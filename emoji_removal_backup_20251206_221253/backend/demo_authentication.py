"""
Authentication System Demo

Demonstrates the authentication system functionality including:
- User registration
- Login and token generation
- Token validation
- Password management
- Role-based access control

Requirements: 1.7, 11.1, 11.2
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from backend.core.database import Base
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    verify_refresh_token
)
from backend.models.database_models import User
from backend.models.auth_schemas import UserCreate, LoginRequest, PasswordChangeRequest
from backend.services.auth_service import AuthService


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_success(message: str):
    """Print success message"""
    print(f"[SUCCESS] {message}")


def print_info(message: str):
    """Print info message"""
    print(f"[INFO] {message}")


def print_error(message: str):
    """Print error message"""
    print(f"[ERROR] {message}")


def demo_password_hashing():
    """Demonstrate password hashing"""
    print_section("1. Password Hashing with bcrypt")
    
    password = "SecurePassword123"
    print_info(f"Original password: {password}")
    
    # Hash password
    hashed = hash_password(password)
    print_success(f"Hashed password: {hashed[:50]}...")
    
    # Verify correct password
    is_valid = verify_password(password, hashed)
    print_success(f"Verify correct password: {is_valid}")
    
    # Verify wrong password
    is_valid = verify_password("WrongPassword", hashed)
    print_info(f"Verify wrong password: {is_valid}")


def demo_jwt_tokens():
    """Demonstrate JWT token creation and validation"""
    print_section("2. JWT Token Generation and Validation")
    
    # Create access token
    user_data = {"sub": "johndoe", "role": "user"}
    access_token = create_access_token(user_data)
    print_success(f"Access token created: {access_token[:50]}...")
    
    # Decode token
    payload = decode_access_token(access_token)
    print_success(f"Decoded payload: {payload}")
    
    # Create refresh token
    refresh_token = create_refresh_token({"sub": "johndoe"})
    print_success(f"Refresh token created: {refresh_token[:50]}...")
    
    # Verify refresh token
    refresh_payload = verify_refresh_token(refresh_token)
    print_success(f"Refresh token payload: {refresh_payload}")


def demo_user_registration(db_session):
    """Demonstrate user registration"""
    print_section("3. User Registration")
    
    auth_service = AuthService(db_session)
    
    # Register new user
    user_data = UserCreate(
        username="demo_user",
        email="demo@example.com",
        password="DemoPassword123",
        full_name="Demo User",
        role="user"
    )
    
    try:
        user = auth_service.register_user(user_data)
        print_success(f"User registered: {user.username}")
        print_info(f"  - ID: {user.id}")
        print_info(f"  - Email: {user.email}")
        print_info(f"  - Role: {user.role}")
        print_info(f"  - Active: {user.is_active}")
        print_info(f"  - Dynamic Key: {user.dynamic_key}")
        return user
    except Exception as e:
        print_error(f"Registration failed: {e}")
        # User might already exist, get existing user
        return auth_service.get_user_by_username("demo_user")


def demo_user_login(db_session):
    """Demonstrate user login"""
    print_section("4. User Login and Token Generation")
    
    auth_service = AuthService(db_session)
    
    # Login
    login_data = LoginRequest(
        username="demo_user",
        password="DemoPassword123"
    )
    
    try:
        token_response = auth_service.authenticate_user(login_data)
        print_success("Login successful!")
        print_info(f"  - Access Token: {token_response.access_token[:50]}...")
        print_info(f"  - Refresh Token: {token_response.refresh_token[:50]}...")
        print_info(f"  - Token Type: {token_response.token_type}")
        print_info(f"  - Expires In: {token_response.expires_in} seconds")
        return token_response
    except Exception as e:
        print_error(f"Login failed: {e}")
        return None


def demo_token_refresh(db_session, refresh_token: str):
    """Demonstrate token refresh"""
    print_section("5. Token Refresh")
    
    auth_service = AuthService(db_session)
    
    try:
        new_tokens = auth_service.refresh_access_token(refresh_token)
        print_success("Token refreshed successfully!")
        print_info(f"  - New Access Token: {new_tokens.access_token[:50]}...")
        print_info(f"  - New Refresh Token: {new_tokens.refresh_token[:50]}...")
        return new_tokens
    except Exception as e:
        print_error(f"Token refresh failed: {e}")
        return None


def demo_password_change(db_session, user: User):
    """Demonstrate password change"""
    print_section("6. Password Change")
    
    auth_service = AuthService(db_session)
    
    password_data = PasswordChangeRequest(
        current_password="DemoPassword123",
        new_password="NewDemoPassword456"
    )
    
    try:
        result = auth_service.change_password(user, password_data)
        print_success(result["message"])
        
        # Verify can login with new password
        login_data = LoginRequest(
            username="demo_user",
            password="NewDemoPassword456"
        )
        token_response = auth_service.authenticate_user(login_data)
        print_success("Login with new password successful!")
        
        # Change back to original password for other demos
        password_data = PasswordChangeRequest(
            current_password="NewDemoPassword456",
            new_password="DemoPassword123"
        )
        auth_service.change_password(user, password_data)
        print_info("Password changed back to original for demo purposes")
        
    except Exception as e:
        print_error(f"Password change failed: {e}")


def demo_admin_operations(db_session):
    """Demonstrate admin operations"""
    print_section("7. Admin Operations")
    
    auth_service = AuthService(db_session)
    
    # Create admin user if doesn't exist
    admin_data = UserCreate(
        username="admin_user",
        email="admin@example.com",
        password="AdminPassword123",
        full_name="Admin User",
        role="admin"
    )
    
    try:
        admin = auth_service.register_user(admin_data)
        print_success(f"Admin user created: {admin.username}")
    except:
        admin = auth_service.get_user_by_username("admin_user")
        print_info(f"Using existing admin user: {admin.username}")
    
    # List all users
    users = db_session.query(User).all()
    print_success(f"Total users in system: {len(users)}")
    for user in users:
        print_info(f"  - {user.username} ({user.role}) - Active: {user.is_active}")
    
    # Get specific user
    demo_user = auth_service.get_user_by_username("demo_user")
    if demo_user:
        print_success(f"Retrieved user: {demo_user.username}")
        print_info(f"  - Email: {demo_user.email}")
        print_info(f"  - Role: {demo_user.role}")
        print_info(f"  - Created: {demo_user.created_at}")


def demo_role_based_access():
    """Demonstrate role-based access control"""
    print_section("8. Role-Based Access Control")
    
    print_info("Available roles:")
    print_info("  - user: Regular user with basic access")
    print_info("  - moderator: Can moderate content")
    print_info("  - admin: Full system access")
    
    print_success("\nRole-based dependencies available:")
    print_info("  - get_current_user: Any authenticated user")
    print_info("  - get_current_active_user: Active users only")
    print_info("  - get_current_admin_user: Admin users only")
    print_info("  - require_role('role_name'): Specific role required")
    print_info("  - require_any_role('role1', 'role2'): Any of specified roles")


def demo_security_features():
    """Demonstrate security features"""
    print_section("9. Security Features")
    
    print_success("Password Security:")
    print_info("  ✓ bcrypt hashing with automatic salt")
    print_info("  ✓ Minimum 8 characters")
    print_info("  ✓ Must include uppercase, lowercase, and digit")
    print_info("  ✓ Password strength validation")
    
    print_success("\nToken Security:")
    print_info("  ✓ JWT with HS256 algorithm")
    print_info("  ✓ Access token expires in 30 minutes")
    print_info("  ✓ Refresh token expires in 7 days")
    print_info("  ✓ Token type validation")
    print_info("  ✓ Automatic expiration checking")
    
    print_success("\nAccess Control:")
    print_info("  ✓ Role-based access control (RBAC)")
    print_info("  ✓ Active user verification")
    print_info("  ✓ Permission-based endpoints")
    print_info("  ✓ Admin-only operations")


def main():
    """Run all authentication demos"""
    print("\n" + "=" * 80)
    print("  AUTHENTICATION SYSTEM DEMONSTRATION")
    print("  Requirements: 1.7, 11.1, 11.2")
    print("=" * 80)
    
    # Setup database
    engine = create_engine("sqlite:///./demo_auth.db")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Run demos
        demo_password_hashing()
        demo_jwt_tokens()
        user = demo_user_registration(db)
        token_response = demo_user_login(db)
        
        if token_response:
            demo_token_refresh(db, token_response.refresh_token)
        
        if user:
            demo_password_change(db, user)
        
        demo_admin_operations(db)
        demo_role_based_access()
        demo_security_features()
        
        # Summary
        print_section("Summary")
        print_success("Authentication system demonstration completed!")
        print_info("\nKey Features Demonstrated:")
        print_info("  ✓ Password hashing with bcrypt")
        print_info("  ✓ JWT token generation and validation")
        print_info("  ✓ User registration and login")
        print_info("  ✓ Token refresh mechanism")
        print_info("  ✓ Password change functionality")
        print_info("  ✓ Admin operations")
        print_info("  ✓ Role-based access control")
        print_info("  ✓ Security features")
        
        print_info("\nNext Steps:")
        print_info("  1. Review API documentation: backend/docs/AUTHENTICATION_GUIDE.md")
        print_info("  2. Run tests: pytest backend/tests/test_auth.py -v")
        print_info("  3. Try API endpoints: http://localhost:8000/api/docs")
        print_info("  4. Integrate with frontend application")
        
    finally:
        db.close()
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
