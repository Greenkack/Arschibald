# User and Role Management System - Complete Guide

## Overview

The User and Role Management System provides comprehensive access control with granular permissions, custom role builder, permission inheritance, user groups, access control lists (ACL), and complete audit logging.

## Features

### 1. Granular Permissions

Permissions are defined at the resource-action level, providing fine-grained control over system access.

**Permission Structure:**
- **Resource**: The entity being accessed (user, role, project, pdf, etc.)
- **Action**: The operation being performed (create, read, update, delete, execute, etc.)
- **Conditions**: Optional dynamic conditions for context-aware permissions

**Example Permissions:**
```python
# Read all users
{
  "name": "user.read",
  "resource": "user",
  "action": "read",
  "description": "View user information"
}

# Create projects (owner only)
{
  "name": "project.create.own",
  "resource": "project",
  "action": "create",
  "description": "Create own projects",
  "conditions": {"owner_only": true}
}

# Manage price matrix
{
  "name": "price_matrix.manage",
  "resource": "price_matrix",
  "action": "manage",
  "description": "Full price matrix management"
}
```

### 2. Custom Role Builder

Create custom roles with specific permission sets tailored to your organization's needs.

**Role Features:**
- Custom role names and descriptions
- Flexible permission assignment
- Role priority levels (0-100)
- System vs. custom roles
- Active/inactive status

**Example Roles:**
```python
# Sales Manager Role
{
  "name": "Sales Manager",
  "description": "Manages sales team and customer relationships",
  "priority": 70,
  "permissions": [
    "customer.read",
    "customer.create",
    "customer.update",
    "offer.read",
    "offer.create",
    "offer.update",
    "pdf.generate",
    "report.read"
  ]
}

# Project Engineer Role
{
  "name": "Project Engineer",
  "description": "Technical project design and calculations",
  "priority": 60,
  "permissions": [
    "project.read",
    "project.create",
    "project.update",
    "calculation.execute",
    "visualization.create",
    "pdf.generate"
  ]
}
```

### 3. Permission Inheritance

Roles can inherit permissions from parent roles, creating a hierarchical permission structure.

**Inheritance Rules:**
- Child roles inherit ALL permissions from parent roles
- Child roles can add additional permissions
- Multiple inheritance levels supported
- Circular inheritance prevented

**Example Hierarchy:**
```
Super Admin (all permissions)
  ├── Admin (most permissions)
  │   ├── Department Manager (department-specific)
  │   └── Team Lead (team-specific)
  ├── Manager (management permissions)
  │   ├── Sales Manager (sales-specific)
  │   └── Technical Manager (technical-specific)
  └── User (basic permissions)
      ├── Sales Rep (sales-specific)
      └── Engineer (technical-specific)
```

### 4. User Groups

Organize users into groups for easier permission management.

**Group Features:**
- Hierarchical group structure
- Multiple roles per group
- Users can belong to multiple groups
- Group-based permission assignment
- Active/inactive status

**Example Groups:**
```python
# Sales Department
{
  "name": "Sales Department",
  "description": "All sales team members",
  "roles": ["Sales Manager", "Sales Rep"],
  "users": [user1, user2, user3]
}

# Engineering Team
{
  "name": "Engineering Team",
  "description": "Technical engineering staff",
  "parent_group": "Technical Department",
  "roles": ["Project Engineer", "Technical Manager"],
  "users": [user4, user5, user6]
}
```

### 5. Access Control Lists (ACL)

Fine-grained resource-level access control for specific users, groups, or roles.

**ACL Features:**
- Resource-specific permissions
- Allow/deny rules
- Priority-based conflict resolution
- Expiration dates
- Conditional access

**Example ACL Entries:**
```python
# Grant user access to specific project
{
  "user_id": 123,
  "resource_type": "project",
  "resource_id": 456,
  "permission": "project.update",
  "allow": true,
  "priority": 10
}

# Deny group access to sensitive data
{
  "group_id": 789,
  "resource_type": "customer",
  "resource_id": 101,
  "permission": "customer.read",
  "allow": false,
  "priority": 20
}

# Temporary access with expiration
{
  "user_id": 234,
  "resource_type": "report",
  "resource_id": 567,
  "permission": "report.export",
  "allow": true,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### 6. Permission Audit Log

Complete audit trail of all permission-related activities and access attempts.

**Logged Events:**
- Permission checks (allowed/denied)
- Role assignments/removals
- Permission grants/revokes
- Group membership changes
- ACL modifications
- Failed access attempts

**Audit Log Fields:**
- User ID
- Action performed
- Resource accessed
- Permission checked
- Result (allowed/denied)
- Reason for decision
- IP address
- User agent
- Timestamp

## API Endpoints

### Permissions

```
POST   /api/v1/permissions              Create permission
GET    /api/v1/permissions              List permissions
GET    /api/v1/permissions/{id}         Get permission
PUT    /api/v1/permissions/{id}         Update permission
DELETE /api/v1/permissions/{id}         Delete permission
```

### Roles

```
POST   /api/v1/permissions/roles                    Create role
GET    /api/v1/permissions/roles                    List roles
GET    /api/v1/permissions/roles/{id}               Get role
GET    /api/v1/permissions/roles/{id}/inheritance   Get role with inheritance
PUT    /api/v1/permissions/roles/{id}               Update role
DELETE /api/v1/permissions/roles/{id}               Delete role
```

### Groups

```
POST   /api/v1/permissions/groups           Create group
GET    /api/v1/permissions/groups           List groups
GET    /api/v1/permissions/groups/{id}      Get group
PUT    /api/v1/permissions/groups/{id}      Update group
DELETE /api/v1/permissions/groups/{id}      Delete group
```

### User Role Assignments

```
POST   /api/v1/permissions/user-roles       Assign role to user
GET    /api/v1/permissions/user-roles       List user role assignments
DELETE /api/v1/permissions/user-roles/{id}  Remove role assignment
```

### Access Control Lists

```
POST   /api/v1/permissions/acl              Create ACL entry
GET    /api/v1/permissions/acl              List ACL entries
GET    /api/v1/permissions/acl/{id}         Get ACL entry
PUT    /api/v1/permissions/acl/{id}         Update ACL entry
DELETE /api/v1/permissions/acl/{id}         Delete ACL entry
```

### Permission Checks

```
POST   /api/v1/permissions/check            Check user permission
GET    /api/v1/permissions/users/{id}/summary   Get user permission summary
```

### Audit Logs

```
GET    /api/v1/permissions/audit-logs       List audit logs
GET    /api/v1/permissions/audit-logs/{id}  Get audit log entry
```

## Usage Examples

### Creating a Custom Role

```python
# Create a custom "Content Manager" role
role_data = {
    "name": "Content Manager",
    "description": "Manages content and documentation",
    "priority": 50,
    "permission_ids": [1, 2, 3, 5, 8]  # Specific permission IDs
}

response = requests.post(
    "http://localhost:8000/api/v1/permissions/roles",
    json=role_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Assigning Role to User

```python
# Assign "Sales Manager" role to user
assignment_data = {
    "user_id": 123,
    "role_id": 5,
    "expires_at": "2025-12-31T23:59:59Z"  # Optional expiration
}

response = requests.post(
    "http://localhost:8000/api/v1/permissions/user-roles",
    json=assignment_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Creating User Group

```python
# Create "Marketing Team" group
group_data = {
    "name": "Marketing Team",
    "description": "Marketing department members",
    "role_ids": [3, 7]  # Assign multiple roles
}

response = requests.post(
    "http://localhost:8000/api/v1/permissions/groups",
    json=group_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Checking User Permission

```python
# Check if user can update a specific project
check_data = {
    "user_id": 123,
    "resource": "project",
    "action": "update",
    "resource_id": 456
}

response = requests.post(
    "http://localhost:8000/api/v1/permissions/check",
    json=check_data,
    headers={"Authorization": f"Bearer {token}"}
)

result = response.json()
if result["allowed"]:
    print("Access granted")
else:
    print(f"Access denied: {result['reason']}")
```

## Best Practices

1. **Use Role Inheritance**: Create base roles and extend them for specific needs
2. **Group by Function**: Organize users into functional groups (departments, teams)
3. **Principle of Least Privilege**: Grant only necessary permissions
4. **Regular Audits**: Review audit logs regularly for security
5. **Expiration Dates**: Use temporary permissions for contractors/guests
6. **Priority Levels**: Use ACL priorities to handle permission conflicts
7. **System Roles**: Protect system roles from modification
8. **Permission Naming**: Use consistent naming convention (resource.action)

## Security Considerations

- All permission changes are logged in audit trail
- System roles cannot be modified or deleted
- Permission cache is automatically cleared on changes
- Failed access attempts are logged
- IP addresses and user agents are tracked
- Expired permissions are automatically enforced

## Requirements Satisfied

- ✅ 7.1: Admin panel functionality
- ✅ 11.1: Authentication and authorization
- ✅ Granular permissions implemented
- ✅ Custom role builder created
- ✅ Permission inheritance built
- ✅ User groups implemented
- ✅ Access control lists created
- ✅ Permission audit log added
