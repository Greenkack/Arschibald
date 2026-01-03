"""
Authentication System Tests

Tests for authentication endpoints, security utilities, and user management.

Requirements: 1.7, 11.1, 11.2
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir.parent) not in sys.path:
    sys.path.insert(0, str(backend_dir.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from backend.main import app
from backend.core.database import Base, get_db
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    verify_refresh_token
)
from backend.models.database_models import User


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("TestPassword123"),
        full_name="Test User",
        role="user",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def admin_user(test_db):
    """Create an admin user"""
    db = TestingSessionLocal()
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("AdminPassword123"),
        full_name="Admin User",
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def auth_token(test_user):
    """Generate auth token for test user"""
    token = create_access_token(data={"sub": test_user.username, "role": test_user.role})
    return token


@pytest.fixture
def admin_token(admin_user):
    """Generate auth token for admin user"""
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    return token


# Security utilities tests

def test_password_hashing():
    """Test password hashing and verification"""
    password = "TestPassword123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_jwt_token_creation_and_validation():
    """Test JWT token creation and validation"""
    data = {"sub": "testuser", "role": "user"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode token
    payload = decode_access_token(token)
    assert payload["sub"] == "testuser"
    assert payload["role"] == "user"
    assert "exp" in payload


def test_refresh_token():
    """Test refresh token creation and validation"""
    data = {"sub": "testuser"}
    refresh_token = create_refresh_token(data)
    
    assert refresh_token is not None
    
    # Verify refresh token
    payload = verify_refresh_token(refresh_token)
    assert payload["sub"] == "testuser"
    assert payload["type"] == "refresh"


# Registration tests

def test_register_user_success(test_db):
    """Test successful user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "full_name": "New User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_username(test_user):
    """Test registration with duplicate username"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",  # Already exists
            "email": "different@example.com",
            "password": "Password123"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_duplicate_email(test_user):
    """Test registration with duplicate email"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "differentuser",
            "email": "test@example.com",  # Already exists
            "password": "Password123"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_weak_password(test_db):
    """Test registration with weak password"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "weak"  # Too short, no uppercase, no digit
        }
    )
    
    assert response.status_code == 422  # Validation error


# Login tests

def test_login_success(test_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "TestPassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


def test_login_wrong_password(test_user):
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "WrongPassword"
        }
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user(test_db):
    """Test login with nonexistent user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "Password123"
        }
    )
    
    assert response.status_code == 401


def test_login_inactive_user(test_db):
    """Test login with inactive user"""
    db = TestingSessionLocal()
    user = User(
        username="inactive",
        email="inactive@example.com",
        hashed_password=hash_password("Password123"),
        is_active=False
    )
    db.add(user)
    db.commit()
    db.close()
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "inactive",
            "password": "Password123"
        }
    )
    
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


# Token refresh tests

def test_refresh_token_success(test_user):
    """Test successful token refresh"""
    # Login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "TestPassword123"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_with_invalid_token(test_db):
    """Test refresh with invalid token"""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )
    
    assert response.status_code == 401


# Current user tests

def test_get_current_user(test_user, auth_token):
    """Test getting current user info"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_current_user_without_token(test_db):
    """Test getting current user without token"""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


def test_get_current_user_with_invalid_token(test_db):
    """Test getting current user with invalid token"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401


# Update user tests

def test_update_current_user(test_user, auth_token):
    """Test updating current user info"""
    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "full_name": "Updated Name",
            "email": "updated@example.com"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == "updated@example.com"


def test_user_cannot_change_own_role(test_user, auth_token):
    """Test that regular user cannot change their own role"""
    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"role": "admin"}
    )
    
    assert response.status_code == 403


# Password change tests

def test_change_password_success(test_user, auth_token):
    """Test successful password change"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "current_password": "TestPassword123",
            "new_password": "NewPassword456"
        }
    )
    
    assert response.status_code == 200
    assert "success" in response.json()["message"].lower()
    
    # Verify can login with new password
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "NewPassword456"
        }
    )
    assert login_response.status_code == 200


def test_change_password_wrong_current(test_user, auth_token):
    """Test password change with wrong current password"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "current_password": "WrongPassword",
            "new_password": "NewPassword456"
        }
    )
    
    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"].lower()


# Admin endpoints tests

def test_admin_list_users(admin_user, admin_token):
    """Test admin can list all users"""
    response = client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_non_admin_cannot_list_users(test_user, auth_token):
    """Test non-admin cannot list users"""
    response = client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 403


def test_admin_get_user(admin_user, test_user, admin_token):
    """Test admin can get specific user"""
    response = client.get(
        f"/api/v1/auth/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_admin_update_user(admin_user, test_user, admin_token):
    """Test admin can update user"""
    response = client.put(
        f"/api/v1/auth/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "moderator"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "moderator"


def test_admin_deactivate_user(admin_user, test_user, admin_token):
    """Test admin can deactivate user"""
    response = client.post(
        f"/api/v1/auth/users/{test_user.id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    
    # Verify user cannot login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "TestPassword123"
        }
    )
    assert login_response.status_code == 403


def test_admin_cannot_deactivate_self(admin_user, admin_token):
    """Test admin cannot deactivate their own account"""
    response = client.post(
        f"/api/v1/auth/users/{admin_user.id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400


def test_logout(test_user, auth_token):
    """Test logout endpoint"""
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    assert "logged out" in response.json()["message"].lower()


def test_session_info(test_user, auth_token):
    """Test getting session info"""
    response = client.get(
        "/api/v1/auth/session",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "user"
    assert "login_time" in data
