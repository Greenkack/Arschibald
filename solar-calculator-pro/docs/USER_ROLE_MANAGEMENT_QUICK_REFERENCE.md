# User and Role Management - Quick Reference

## Key Concepts

### Permissions
- **Granular**: Resource + Action level control
- **Conditional**: Dynamic evaluation based on context
- **System vs Custom**: Protected system permissions

### Roles
- **Hierarchical**: Parent-child inheritance
- **Priority**: 0-100 (higher = more permissions)
- **Flexible**: Custom permission sets

### Groups
- **Organizational**: Department/team structure
- **Multi-role**: Assign multiple roles to group
- **Hierarchical**: Parent-child relationships

### ACL (Access Control Lists)
- **Resource-specific**: Fine-grained access
- **Allow/Deny**: Explicit permission control
- **Priority-based**: Conflict resolution

## Quick Commands

### Create Permission
```bash
curl -X POST http://localhost:8000/api/v1/permissions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "project.create",
    "description": "Create projects",
    "resource": "project",
    "action": "create"
  }'
```

### Create Role
```bash
curl -X POST http://localhost:8000/api/v1/permissions/roles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Manager",
    "description": "Manages projects",
    "priority": 60,
    "permission_ids": [1, 2, 3, 5]
  }'
```

### Create Group
```bash
curl -X POST http://localhost:8000/api/v1/permissions/groups \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Engineering Team",
    "description": "Technical staff",
    "role_ids": [2, 5]
  }'
```

### Assign Role to User
```bash
curl -X POST http://localhost:8000/api/v1/permissions/user-roles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "role_id": 5
  }'
```

### Check Permission
```bash
curl -X POST http://localhost:8000/api/v1/permissions/check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "resource": "project",
    "action": "update",
    "resource_id": 456
  }'
```

## Common Permission Patterns

### Resource Permissions
```
user.create, user.read, user.update, user.delete
role.create, role.read, role.update, role.delete
group.create, group.read, group.update, group.delete
project.create, project.read, project.update, project.delete
```

### Action Permissions
```
*.read          - View resources
*.create        - Create new resources
*.update        - Modify existing resources
*.delete        - Remove resources
*.execute       - Run operations
*.manage        - Full control
*.export        - Export data
*.import        - Import data
```

## Role Hierarchy Example

```
Super Admin (all permissions)
  └── Admin
      ├── Department Manager
      │   ├── Sales Manager
      │   └── Technical Manager
      └── Team Lead
          ├── Senior Engineer
          └── Senior Sales Rep
```

## Permission Evaluation Order

1. **ACL Deny Rules** (highest priority)
2. **ACL Allow Rules**
3. **Direct Role Permissions**
4. **Inherited Role Permissions**
5. **Group Role Permissions**
6. **Default Deny** (if no match)

## Audit Log Events

- `create_permission` - Permission created
- `update_permission` - Permission modified
- `delete_permission` - Permission removed
- `create_role` - Role created
- `update_role` - Role modified
- `delete_role` - Role removed
- `assign_role` - Role assigned to user
- `revoke_role` - Role removed from user
- `create_group` - Group created
- `update_group` - Group modified
- `add_user_to_group` - User added to group
- `remove_user_from_group` - User removed from group
- `create_acl` - ACL entry created
- `update_acl` - ACL entry modified
- `delete_acl` - ACL entry removed
- `check_permission` - Permission checked
- `access_denied` - Access attempt denied

## Database Tables

- `permissions` - Permission definitions
- `enhanced_roles` - Role definitions with hierarchy
- `groups` - User group definitions
- `user_groups` - User-group associations
- `role_permissions` - Role-permission associations
- `group_roles` - Group-role associations
- `user_role_assignments` - User-role assignments
- `access_control_lists` - ACL entries
- `permission_audit_logs` - Audit trail

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Deleted successfully
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - No permission
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate resource

## Tips

1. **Cache Clearing**: Permission cache auto-clears on changes
2. **System Protection**: System roles/permissions cannot be modified
3. **Inheritance**: Child roles inherit ALL parent permissions
4. **Priority**: Higher priority wins in conflicts
5. **Expiration**: Set expiration dates for temporary access
6. **Conditions**: Use conditions for dynamic permissions
7. **Audit**: All changes are logged automatically
8. **Groups**: Use groups for bulk user management

## Requirements

- ✅ Granular permissions
- ✅ Custom role builder
- ✅ Permission inheritance
- ✅ User groups
- ✅ Access control lists
- ✅ Permission audit log
