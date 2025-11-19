# Solar Project Management - Quick Reference

## 🚀 Quick Start

### Access the Feature
1. Navigate to **Solar Projects** in the sidebar
2. Or go to: `http://localhost:3000/solar-projects`

### Create a Project
```typescript
// Click "Neues Projekt" button
// Fill in the form:
{
  name: "Mein Solar Projekt",
  project_type: "solar" | "heatpump" | "combined"
}
// Click "Erstellen"
```

### View Project Details
```typescript
// Click on a project row or the eye icon
// Navigate to: /solar-projects/{projectId}
```

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api/v1/solar
```

### Endpoints

#### Create Project
```bash
POST /projects
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Mein Projekt",
  "customer_id": 1,
  "project_type": "solar",
  "data": {}
}

Response: 201 Created
{
  "id": 1,
  "name": "Mein Projekt",
  "customer_id": 1,
  "project_type": "solar",
  "status": "draft",
  "data": {},
  "dynamic_key": "PRJ-2024-001",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### List Projects
```bash
GET /projects?page=1&page_size=20&search=solar&project_type=solar&status=active
Authorization: Bearer {token}

Response: 200 OK
{
  "items": [...],
  "total": 50,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

#### Get Project
```bash
GET /projects/{id}
Authorization: Bearer {token}

Response: 200 OK
{
  "id": 1,
  "name": "Mein Projekt",
  ...
}
```

#### Update Project
```bash
PUT /projects/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Neuer Name",
  "status": "active",
  "data": {...}
}

Response: 200 OK
{
  "id": 1,
  "name": "Neuer Name",
  ...
}
```

#### Delete Project
```bash
DELETE /projects/{id}
Authorization: Bearer {token}

Response: 204 No Content
```

## 🎨 UI Components

### Import Components
```typescript
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { Toast } from 'primereact/toast';
import { ConfirmDialog } from 'primereact/confirmdialog';
```

### Use DataTable
```typescript
<DataTable
  value={projects}
  loading={loading}
  paginator
  rows={20}
  totalRecords={totalRecords}
  onPage={(e) => handlePageChange(e)}
>
  <Column field="name" header="Name" sortable />
  <Column field="status" header="Status" body={statusTemplate} />
</DataTable>
```

### Show Toast Notification
```typescript
toast.current?.show({
  severity: 'success',
  summary: 'Erfolg',
  detail: 'Projekt wurde erstellt',
  life: 3000
});
```

### Confirm Dialog
```typescript
confirmDialog({
  message: 'Wirklich löschen?',
  header: 'Bestätigung',
  icon: 'pi pi-exclamation-triangle',
  accept: () => handleDelete()
});
```

## 💾 Backend Service

### Import Service
```python
from backend.services.project_service import ProjectService
```

### Use Service
```python
# In API endpoint
service = ProjectService(db)

# Create
project = service.create_project(project_data, user_id)

# List
projects = service.list_projects(
    user_id=user_id,
    page=1,
    page_size=20,
    project_type='solar',
    status='active',
    search='test'
)

# Get
project = service.get_project(project_id, user_id)

# Update
project = service.update_project(project_id, update_data, user_id)

# Delete
service.delete_project(project_id, user_id)
```

## 🗄️ Database Model

### Project Model
```python
class Project(UniversalDatabaseModel):
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False)
    customer_id = Column(Integer, nullable=False)
    project_type = Column(String(50))  # 'solar', 'heatpump', 'combined'
    status = Column(String(50), default='draft')  # 'draft', 'active', 'completed', 'archived'
    data = Column(Text)  # JSON data
    dynamic_key = Column(String(255), unique=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

### Query Examples
```python
# Get all projects
projects = db.query(Project).all()

# Filter by type
solar_projects = db.query(Project).filter(
    Project.project_type == 'solar'
).all()

# Search by name
results = db.query(Project).filter(
    Project.name.ilike(f'%{search}%')
).all()

# Pagination
projects = db.query(Project).offset(offset).limit(page_size).all()
```

## 🎯 Common Tasks

### Add a New Filter
```typescript
// 1. Add state
const [newFilter, setNewFilter] = useState<string | null>(null);

// 2. Add to API params
if (newFilter) {
  params.new_filter = newFilter;
}

// 3. Add dropdown
<Dropdown
  value={newFilter}
  options={filterOptions}
  onChange={(e) => setNewFilter(e.value)}
/>
```

### Add a New Column
```typescript
// 1. Add to DataTable
<Column 
  field="new_field" 
  header="New Field" 
  body={newFieldTemplate}
  sortable 
/>

// 2. Create template
const newFieldTemplate = (rowData: Project) => {
  return <span>{rowData.new_field}</span>;
};
```

### Add a New Action
```typescript
// 1. Add button
<Button
  icon="pi pi-star"
  onClick={() => handleNewAction(rowData)}
  tooltip="New Action"
/>

// 2. Implement handler
const handleNewAction = async (project: Project) => {
  try {
    await api.post(`/api/v1/solar/projects/${project.id}/action`);
    toast.current?.show({
      severity: 'success',
      summary: 'Success',
      detail: 'Action completed'
    });
  } catch (error) {
    // Handle error
  }
};
```

## 🔧 Customization

### Change Page Size Options
```typescript
<DataTable
  rowsPerPageOptions={[10, 20, 50, 100]}
  rows={20}
/>
```

### Customize Status Colors
```typescript
const statusConfig: Record<string, { label: string; severity: any }> = {
  draft: { label: 'Entwurf', severity: 'info' },
  active: { label: 'Aktiv', severity: 'success' },
  completed: { label: 'Fertig', severity: 'warning' },
  archived: { label: 'Archiviert', severity: 'secondary' }
};
```

### Add Custom Validation
```typescript
const handleCreateProject = async () => {
  // Custom validation
  if (!newProjectName.trim()) {
    toast.current?.show({
      severity: 'warn',
      summary: 'Warnung',
      detail: 'Name ist erforderlich'
    });
    return;
  }
  
  if (newProjectName.length < 3) {
    toast.current?.show({
      severity: 'warn',
      summary: 'Warnung',
      detail: 'Name muss mindestens 3 Zeichen lang sein'
    });
    return;
  }
  
  // Create project
  await api.post('/api/v1/solar/projects', {...});
};
```

## 🐛 Troubleshooting

### Projects Not Loading
```typescript
// Check:
1. Backend is running (http://localhost:8000)
2. Authentication token is valid
3. Database has projects
4. Check browser console for errors
5. Check network tab for API response
```

### Create Dialog Not Opening
```typescript
// Check:
1. showCreateDialog state is updating
2. Dialog component is rendered
3. Button onClick is connected
4. No JavaScript errors in console
```

### Delete Not Working
```typescript
// Check:
1. ConfirmDialog is imported and rendered
2. confirmDialog function is called
3. API endpoint is correct
4. User has permission to delete
5. Project ID is valid
```

## 📚 Related Documentation

- [PrimeReact DataTable](https://primereact.org/datatable/)
- [PrimeReact Dialog](https://primereact.org/dialog/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [React Router](https://reactrouter.com/)

## 🎓 Best Practices

### Frontend
- ✅ Use TypeScript for type safety
- ✅ Handle loading states
- ✅ Show error messages
- ✅ Validate user input
- ✅ Use toast notifications
- ✅ Implement confirmation dialogs
- ✅ Make UI responsive
- ✅ Use semantic HTML

### Backend
- ✅ Use service layer pattern
- ✅ Validate input with Pydantic
- ✅ Handle errors gracefully
- ✅ Use transactions for data integrity
- ✅ Return proper HTTP status codes
- ✅ Document API endpoints
- ✅ Use dependency injection
- ✅ Log important operations

### Database
- ✅ Use indexes for frequently queried columns
- ✅ Use transactions for multiple operations
- ✅ Validate foreign keys
- ✅ Use proper data types
- ✅ Add timestamps (created_at, updated_at)
- ✅ Use soft deletes when appropriate
- ✅ Normalize data structure

## 🔗 Quick Links

- **Frontend Code**: `solar-calculator-pro/frontend/src/pages/SolarProjects.tsx`
- **Backend Service**: `backend/services/project_service.py`
- **API Endpoints**: `backend/api/v1/solar.py`
- **Database Model**: `backend/models/database_models.py`
- **Routes**: `solar-calculator-pro/frontend/src/routes/index.tsx`

---

**Last Updated**: January 2024
**Version**: 1.0.0
