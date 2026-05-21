"""
User and Role Management API

Provides REST API for user and role management:
- User account management
- Role-based access control (Admin, Sales)
- Permission management
- User activity logging
- User authentication system

Requirements: funktionen.txt - "Benutzer- und Rechteverwaltung"
Task: 278. User and Role Management
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib

router = APIRouter(prefix="/admin/users", tags=["User & Role Management"])


# ==================== Enums ====================

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SALES = "sales"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING = "pending"


class Permission(str, Enum):
    # User management
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_EDIT = "user:edit"
    USER_DELETE = "user:delete"
    # Project management
    PROJECT_VIEW = "project:view"
    PROJECT_CREATE = "project:create"
    PROJECT_EDIT = "project:edit"
    PROJECT_DELETE = "project:delete"
    # CRM
    CRM_VIEW = "crm:view"
    CRM_EDIT = "crm:edit"
    # PDF
    PDF_GENERATE = "pdf:generate"
    PDF_TEMPLATES = "pdf:templates"
    # Admin
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_PRICING = "admin:pricing"
    ADMIN_PRODUCTS = "admin:products"


class ActivityType(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"


# ==================== Pydantic Models ====================

class User(BaseModel):
    """User account"""
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE
    permissions: List[Permission] = []
    company_id: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    login_count: int = 0
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None


class CreateUserRequest(BaseModel):
    """Request to create user"""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    role: UserRole = UserRole.SALES
    company_id: Optional[str] = None
    phone: Optional[str] = None


class UpdateUserRequest(BaseModel):
    """Request to update user"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    status: Optional[UserStatus] = None


class RoleDefinition(BaseModel):
    """Role definition with permissions"""
    role: UserRole
    name: str
    description: str
    permissions: List[Permission]
    is_system_role: bool = True


class ActivityLog(BaseModel):
    """User activity log entry"""
    id: str
    user_id: str
    username: str
    activity_type: ActivityType
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime


class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    user: User
    token: str
    expires_at: datetime


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(min_length=8)


# ==================== Mock Data Store ====================

_users_store: Dict[str, User] = {}
_passwords_store: Dict[str, str] = {}  # user_id -> hashed password
_activity_logs: List[ActivityLog] = []


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Role definitions with default permissions
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: list(Permission),
    UserRole.ADMIN: [
        Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_EDIT,
        Permission.PROJECT_VIEW, Permission.PROJECT_CREATE, Permission.PROJECT_EDIT, Permission.PROJECT_DELETE,
        Permission.CRM_VIEW, Permission.CRM_EDIT,
        Permission.PDF_GENERATE, Permission.PDF_TEMPLATES,
        Permission.ADMIN_SETTINGS, Permission.ADMIN_PRICING, Permission.ADMIN_PRODUCTS
    ],
    UserRole.SALES: [
        Permission.PROJECT_VIEW, Permission.PROJECT_CREATE, Permission.PROJECT_EDIT,
        Permission.CRM_VIEW, Permission.CRM_EDIT,
        Permission.PDF_GENERATE
    ],
    UserRole.VIEWER: [
        Permission.PROJECT_VIEW,
        Permission.CRM_VIEW
    ]
}


def init_default_users():
    """Initialize default users"""
    now = datetime.now()
    
    # Super Admin
    admin_id = generate_id("usr")
    _users_store[admin_id] = User(
        id=admin_id,
        username="admin",
        email="admin@solar-calculator.de",
        first_name="System",
        last_name="Administrator",
        role=UserRole.SUPER_ADMIN,
        permissions=ROLE_PERMISSIONS[UserRole.SUPER_ADMIN],
        created_at=now,
        updated_at=now
    )
    _passwords_store[admin_id] = hash_password("admin123")
    
    # Sales user
    sales_id = generate_id("usr")
    _users_store[sales_id] = User(
        id=sales_id,
        username="vertrieb",
        email="vertrieb@solar-calculator.de",
        first_name="Max",
        last_name="Mustermann",
        role=UserRole.SALES,
        permissions=ROLE_PERMISSIONS[UserRole.SALES],
        created_at=now,
        updated_at=now
    )
    _passwords_store[sales_id] = hash_password("vertrieb123")


init_default_users()


def log_activity(user_id: str, username: str, activity_type: ActivityType, resource_type: str, resource_id: str = None, details: str = None):
    """Log user activity"""
    log = ActivityLog(
        id=generate_id("log"),
        user_id=user_id,
        username=username,
        activity_type=activity_type,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        timestamp=datetime.now()
    )
    _activity_logs.append(log)
    # Keep only last 1000 logs
    if len(_activity_logs) > 1000:
        _activity_logs.pop(0)


# ==================== API Endpoints ====================

@router.get("/")
async def get_users(
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    search: Optional[str] = None
):
    """Get all users."""
    users = list(_users_store.values())
    
    if role:
        users = [u for u in users if u.role == role]
    if status:
        users = [u for u in users if u.status == status]
    if search:
        search_lower = search.lower()
        users = [u for u in users if search_lower in u.username.lower() or search_lower in u.email.lower() or search_lower in f"{u.first_name} {u.last_name}".lower()]
    
    return {
        "users": users,
        "total": len(users),
        "by_role": {r.value: len([u for u in users if u.role == r]) for r in UserRole}
    }


@router.post("/")
async def create_user(request: CreateUserRequest):
    """Create new user."""
    # Check username uniqueness
    if any(u.username == request.username for u in _users_store.values()):
        raise HTTPException(status_code=400, detail="Benutzername bereits vergeben")
    
    # Check email uniqueness
    if any(u.email == request.email for u in _users_store.values()):
        raise HTTPException(status_code=400, detail="E-Mail bereits registriert")
    
    user_id = generate_id("usr")
    now = datetime.now()
    
    user = User(
        id=user_id,
        username=request.username,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        role=request.role,
        permissions=ROLE_PERMISSIONS.get(request.role, []),
        company_id=request.company_id,
        phone=request.phone,
        status=UserStatus.ACTIVE,
        created_at=now,
        updated_at=now
    )
    
    _users_store[user_id] = user
    _passwords_store[user_id] = hash_password(request.password)
    
    log_activity("system", "system", ActivityType.CREATE, "user", user_id, f"User {request.username} created")
    
    return {"user": user, "created": True}


@router.get("/{user_id}")
async def get_user(user_id: str):
    """Get specific user."""
    if user_id not in _users_store:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    
    return {"user": _users_store[user_id]}


@router.put("/{user_id}")
async def update_user(user_id: str, request: UpdateUserRequest):
    """Update user."""
    if user_id not in _users_store:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    
    user = _users_store[user_id]
    
    if request.email:
        user.email = request.email
    if request.first_name:
        user.first_name = request.first_name
    if request.last_name:
        user.last_name = request.last_name
    if request.role:
        user.role = request.role
        user.permissions = ROLE_PERMISSIONS.get(request.role, [])
    if request.phone:
        user.phone = request.phone
    if request.status:
        user.status = request.status
    
    user.updated_at = datetime.now()
    
    return {"user": user, "updated": True}


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete user."""
    if user_id not in _users_store:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    
    user = _users_store[user_id]
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super-Admin kann nicht gelöscht werden")
    
    del _users_store[user_id]
    if user_id in _passwords_store:
        del _passwords_store[user_id]
    
    return {"deleted": True, "user_id": user_id}


@router.put("/{user_id}/status")
async def update_user_status(user_id: str, status: UserStatus):
    """Update user status."""
    if user_id not in _users_store:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    
    user = _users_store[user_id]
    user.status = status
    user.updated_at = datetime.now()
    
    return {"user": user, "updated": True}


@router.post("/login")
async def login(request: LoginRequest):
    """User login."""
    user = None
    for u in _users_store.values():
        if u.username == request.username:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Konto ist deaktiviert")
    
    if _passwords_store.get(user.id) != hash_password(request.password):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    
    user.last_login = datetime.now()
    user.login_count += 1
    
    log_activity(user.id, user.username, ActivityType.LOGIN, "session")
    
    return LoginResponse(
        user=user,
        token=f"token_{uuid.uuid4().hex}",
        expires_at=datetime.now() + timedelta(hours=8)
    )


@router.post("/{user_id}/change-password")
async def change_password(user_id: str, request: PasswordChangeRequest):
    """Change user password."""
    if user_id not in _users_store:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    
    if _passwords_store.get(user_id) != hash_password(request.current_password):
        raise HTTPException(status_code=401, detail="Aktuelles Passwort ist falsch")
    
    _passwords_store[user_id] = hash_password(request.new_password)
    
    return {"changed": True, "message": "Passwort erfolgreich geändert"}


@router.get("/roles/definitions")
async def get_role_definitions():
    """Get role definitions with permissions."""
    return {
        "roles": [
            RoleDefinition(
                role=UserRole.SUPER_ADMIN,
                name="Super Administrator",
                description="Vollzugriff auf alle Funktionen",
                permissions=ROLE_PERMISSIONS[UserRole.SUPER_ADMIN]
            ),
            RoleDefinition(
                role=UserRole.ADMIN,
                name="Administrator",
                description="Verwaltung von Benutzern, Produkten und Einstellungen",
                permissions=ROLE_PERMISSIONS[UserRole.ADMIN]
            ),
            RoleDefinition(
                role=UserRole.SALES,
                name="Vertrieb",
                description="Projekte erstellen und bearbeiten, PDFs generieren",
                permissions=ROLE_PERMISSIONS[UserRole.SALES]
            ),
            RoleDefinition(
                role=UserRole.VIEWER,
                name="Betrachter",
                description="Nur Lesezugriff auf Projekte und CRM",
                permissions=ROLE_PERMISSIONS[UserRole.VIEWER]
            )
        ]
    }


@router.get("/permissions/all")
async def get_all_permissions():
    """Get all available permissions."""
    return {
        "permissions": [
            {"id": p.value, "name": p.value.replace(":", " - ").replace("_", " ").title()}
            for p in Permission
        ]
    }


@router.get("/activity-logs")
async def get_activity_logs(
    user_id: Optional[str] = None,
    activity_type: Optional[ActivityType] = None,
    limit: int = Query(default=50, le=200)
):
    """Get user activity logs."""
    logs = _activity_logs.copy()
    
    if user_id:
        logs = [l for l in logs if l.user_id == user_id]
    if activity_type:
        logs = [l for l in logs if l.activity_type == activity_type]
    
    logs.sort(key=lambda l: l.timestamp, reverse=True)
    
    return {"logs": logs[:limit], "total": len(logs)}


@router.get("/health/check")
async def health_check():
    """Health check for user management service."""
    return {
        "status": "healthy",
        "service": "user-role-management",
        "users_count": len(_users_store),
        "active_users": len([u for u in _users_store.values() if u.status == UserStatus.ACTIVE]),
        "timestamp": datetime.now().isoformat()
    }
