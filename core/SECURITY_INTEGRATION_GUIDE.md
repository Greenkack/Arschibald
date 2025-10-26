# Security System Integration Guide

Quick guide to integrate the Security & Access Control System into your Streamlit application.

## Prerequisites

```bash
pip install bcrypt pyotp streamlit
```

## Step 1: Initialize Database (One-time setup)

```python
# setup_security.py
from core.security import init_all_security_tables, create_default_roles_and_permissions

# Initialize tables
init_all_security_tables()

# Create default roles and permissions
create_default_roles_and_permissions()

print("✓ Security system initialized!")
```

Run once:
```bash
python setup_security.py
```

## Step 2: Add Authentication to Your Streamlit App

```python
# app.py
import streamlit as st
from core.security import AuthenticationManager, get_authentication_manager

# Initialize
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = get_authentication_manager()

auth_manager = st.session_state.auth_manager

# Check if user is logged in
if 'session_token' not in st.session_state:
    # Show login page
    st.title("Login")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        result = auth_manager.authenticate(
            email=email,
            password=password,
            ip_address=st.session_state.get('client_ip', '127.0.0.1')
        )
        
        if result.status.value == "success":
            st.session_state.session_token = result.session_token
            st.session_state.user = result.user
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error(f"Login failed: {result.message}")
else:
    # User is logged in - show main app
    user = st.session_state.user
    
    st.title(f"Welcome, {user.full_name or user.email}!")
    
    # Your app content here
    st.write("Your protected content goes here")
    
    # Logout button
    if st.button("Logout"):
        auth_manager.logout(st.session_state.session_token)
        del st.session_state.session_token
        del st.session_state.user
        st.rerun()
```

## Step 3: Add Authorization Checks

```python
# app.py (continued)
from core.security import get_authorization_manager

authz_manager = get_authorization_manager()

# Check if user has permission
if authz_manager.has_permission(user.id, "users:delete"):
    if st.button("Delete User"):
        # Delete user logic
        pass
else:
    st.info("You don't have permission to delete users")

# Check if user has role
if authz_manager.has_role(user.id, "admin"):
    st.sidebar.write("Admin Panel")
    # Admin-only features
```

## Step 4: Protect Sensitive Data

```python
from core.security import get_data_protection_manager

data_protection = get_data_protection_manager()

# Display user data with PII masked
user_data = {
    "email": user.email,
    "phone": user.phone,
    "name": user.full_name
}

# Mask for display
masked_data = data_protection.mask_dict(user_data)
st.json(masked_data)

# Log data access
from core.security import log_data_access

log_data_access(
    user_id=user.id,
    resource_type="user_profile",
    resource_id=user.id,
    action="READ",
    pii_fields=["email", "phone"],
    ip_address=st.session_state.get('client_ip')
)
```

## Step 5: Monitor Security

```python
from core.security import get_security_monitor

security_monitor = get_security_monitor()

# Validate user input
user_comment = st.text_area("Comment")

if st.button("Submit"):
    if security_monitor.validate_input(user_comment, "comment_field"):
        # Process comment
        st.success("Comment submitted!")
    else:
        st.error("Invalid input detected. Please check your comment.")

# Show security stats (admin only)
if authz_manager.has_role(user.id, "admin"):
    st.sidebar.subheader("Security Stats")
    stats = security_monitor.get_security_stats(days=7)
    st.sidebar.metric("Security Events", stats['total_events'])
    st.sidebar.metric("Failed Logins", stats['failed_logins'])
```

## Complete Example

```python
# secure_app.py
import streamlit as st
from core.security import (
    get_authentication_manager,
    get_authorization_manager,
    get_data_protection_manager,
    get_security_monitor,
    init_all_security_tables,
)

# Initialize (first run only)
try:
    init_all_security_tables()
except:
    pass  # Tables already exist

# Get managers
auth_manager = get_authentication_manager()
authz_manager = get_authorization_manager()
data_protection = get_data_protection_manager()
security_monitor = get_security_monitor()

# Page config
st.set_page_config(page_title="Secure App", page_icon="🔒")

# Authentication
if 'session_token' not in st.session_state:
    # Login page
    st.title("🔒 Secure Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            result = auth_manager.authenticate(
                email=email,
                password=password,
                ip_address="127.0.0.1"
            )
            
            if result.status.value == "success":
                st.session_state.session_token = result.session_token
                st.session_state.user = result.user
                st.success("✓ Logged in!")
                st.rerun()
            else:
                st.error(f"✗ {result.message}")
    
    with tab2:
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_name = st.text_input("Full Name", key="reg_name")
        
        if st.button("Register"):
            try:
                user = auth_manager.register_user(
                    email=reg_email,
                    password=reg_password,
                    full_name=reg_name
                )
                st.success("✓ Registered! Please login.")
            except Exception as e:
                st.error(f"✗ Registration failed: {e}")

else:
    # Main app
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        st.write(f"👤 {user.full_name or user.email}")
        
        # Show permissions
        permissions = authz_manager.get_user_permissions(user.id)
        with st.expander("My Permissions"):
            for perm in permissions:
                st.write(f"• {perm}")
        
        # Security stats (admin only)
        if authz_manager.has_role(user.id, "admin"):
            st.divider()
            st.subheader("🛡️ Security")
            stats = security_monitor.get_security_stats(days=7)
            st.metric("Events (7d)", stats['total_events'])
            st.metric("Failed Logins", stats['failed_logins'])
        
        st.divider()
        if st.button("Logout"):
            auth_manager.logout(st.session_state.session_token)
            del st.session_state.session_token
            del st.session_state.user
            st.rerun()
    
    # Main content
    st.title("🏠 Dashboard")
    
    # User info (masked)
    st.subheader("Profile")
    user_data = {
        "email": user.email,
        "name": user.full_name,
    }
    masked_data = data_protection.mask_dict(user_data)
    st.json(masked_data)
    
    # Protected feature
    st.subheader("Protected Features")
    
    if authz_manager.has_permission(user.id, "data:write"):
        st.success("✓ You can write data")
        
        # Example: Comment with validation
        comment = st.text_area("Add Comment")
        if st.button("Submit Comment"):
            if security_monitor.validate_input(comment, "comment"):
                st.success("✓ Comment submitted!")
            else:
                st.error("✗ Invalid input detected!")
    else:
        st.info("ℹ️ You don't have write permission")
    
    # Admin panel
    if authz_manager.has_role(user.id, "admin"):
        st.divider()
        st.subheader("⚙️ Admin Panel")
        
        # Security report
        if st.button("Generate Security Report"):
            report = security_monitor.generate_security_report(days=30)
            st.json(report)
```

## Configuration

Create `.env` file:

```bash
# Security
SECRET_KEY=your-secret-key-change-in-production
SESSION_TIMEOUT=86400
BCRYPT_ROUNDS=12

# Database
DATABASE_URL=sqlite:///app.db
```

## Running the App

```bash
streamlit run secure_app.py
```

## Default Credentials

After running `create_default_roles_and_permissions()`, you can create an admin user:

```python
from core.security import get_authentication_manager, get_authorization_manager
from core.security import Role
from core.database import get_db_manager

auth_manager = get_authentication_manager()
authz_manager = get_authorization_manager()

# Create admin user
admin = auth_manager.register_user(
    email="admin@example.com",
    password="AdminPass123!",
    full_name="Admin User"
)

# Assign admin role
with get_db_manager().session_scope() as session:
    admin_role = session.query(Role).filter(Role.name == "admin").first()
    if admin_role:
        authz_manager.assign_role_to_user(admin.id, admin_role.id)

print("✓ Admin user created!")
print("Email: admin@example.com")
print("Password: AdminPass123!")
```

## Best Practices

1. **Always validate sessions**: Check session validity on each page load
2. **Use HTTPS**: Enable TLS in production
3. **Rotate secrets**: Change SECRET_KEY regularly
4. **Monitor security**: Review security logs regularly
5. **Update dependencies**: Keep bcrypt and pyotp up to date
6. **Test permissions**: Verify permission checks work correctly
7. **Mask PII**: Always mask sensitive data in logs and displays
8. **Validate input**: Check all user input for security threats

## Troubleshooting

### Session expires too quickly
Increase `SESSION_TIMEOUT` in `.env`

### Password too weak error
Ensure password has:
- At least 8 characters
- One uppercase letter
- One lowercase letter
- One digit

### Permission denied
Check user has required role/permission:
```python
permissions = authz_manager.get_user_permissions(user.id)
print(permissions)
```

### MFA not working
Install pyotp:
```bash
pip install pyotp
```

## Next Steps

1. Customize roles and permissions for your app
2. Add more security monitoring
3. Set up alert handlers
4. Configure data retention policies
5. Add custom authentication providers

## Support

- Documentation: `core/SECURITY_README.md`
- Quick Start: `core/SECURITY_QUICK_START.md`
- Examples: `core/example_security_usage.py`
- Tests: `core/test_security.py`

