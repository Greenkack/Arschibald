# Dashboard Quick Reference

## Overview

The Dashboard is the main landing page of Solar Calculator Pro, providing an at-a-glance view of key metrics, recent projects, and activity.

## Location

- **Component**: `src/pages/Dashboard.tsx`
- **Styles**: `src/pages/Dashboard.css`
- **Route**: `/dashboard`

## Features

### 1. Statistics Cards

Four key metrics displayed at the top:

```typescript
// Example stat card
{
  title: 'Total Projects',
  value: 42,
  icon: 'pi pi-briefcase',
  color: '#3B82F6',
  trend: { value: 12, isPositive: true }
}
```

**Available Stats**:
- Total Projects
- Active Projects
- Total Revenue
- Completed This Month

### 2. Quick Actions

Four primary action buttons:

```typescript
const quickActions = [
  { label: 'New Solar Project', icon: 'pi pi-sun', route: '/solar-calculator' },
  { label: 'New Heat Pump', icon: 'pi pi-bolt', route: '/heat-pump' },
  { label: 'Price Matrix', icon: 'pi pi-table', route: '/price-matrix' },
  { label: 'Generate PDF', icon: 'pi pi-file-pdf', route: '/solar-calculator' }
];
```

### 3. Recent Projects Table

Displays the 5 most recent projects with:
- Project Name
- Customer Name
- Project Type (Solar/Heat Pump/Combined)
- Status (Draft/Active/Completed/Archived)
- Total Value (€)
- Created Date
- Actions (View/Edit)

**Features**:
- Sortable columns
- Pagination
- Status badges
- Type icons
- Action buttons

### 4. Activity Timeline

Shows recent system activities:
- Project Created
- Project Completed
- Calculation Performed
- PDF Generated
- Customer Added

**Features**:
- Color-coded markers
- Timestamps
- Descriptive text
- Scrollable

## Usage

### Basic Usage

```typescript
import Dashboard from '@pages/Dashboard';

// In your router
<Route path="/dashboard" element={<Dashboard />} />
```

### Customizing Statistics

```typescript
const statsData: StatCard[] = [
  {
    title: 'Your Metric',
    value: 100,
    icon: 'pi pi-chart-bar',
    color: '#3B82F6',
    trend: { value: 15, isPositive: true }
  }
];
```

### Adding Quick Actions

```typescript
const newAction = {
  label: 'New Action',
  icon: 'pi pi-plus',
  command: () => navigate('/your-route'),
  className: 'p-button-primary'
};
```

### Customizing Project Table

```typescript
<Column 
  field="customField" 
  header="Custom Header" 
  body={(rowData) => <span>{rowData.customField}</span>}
  sortable 
/>
```

## Styling

### CSS Classes

```css
.dashboard              /* Main container */
.dashboard-header       /* Header section */
.quick-actions          /* Action buttons container */
.stats-grid             /* Statistics grid */
.stat-card              /* Individual stat card */
.stat-icon              /* Stat icon container */
.stat-value             /* Stat value display */
.stat-trend             /* Trend indicator */
.dashboard-content      /* Main content grid */
.recent-projects-card   /* Projects card */
.activity-card          /* Activity card */
.activity-timeline      /* Timeline container */
```

### Customizing Colors

```css
/* Stat card colors */
.stat-icon {
  background-color: #3B82F6; /* Blue */
  background-color: #10B981; /* Green */
  background-color: #F59E0B; /* Orange */
  background-color: #8B5CF6; /* Purple */
}

/* Status badge colors */
.status-badge.status-info { background-color: #DBEAFE; }
.status-badge.status-success { background-color: #D1FAE5; }
.status-badge.status-warning { background-color: #FEF3C7; }
```

## Data Structures

### StatCard Interface

```typescript
interface StatCard {
  title: string;              // Display title
  value: string | number;     // Metric value
  icon: string;               // PrimeIcons class
  color: string;              // Hex color
  trend?: {
    value: number;            // Percentage change
    isPositive: boolean;      // Up or down
  };
}
```

### Project Interface

```typescript
interface Project {
  id: number;
  name: string;
  customerName: string;
  projectType: 'solar' | 'heatpump' | 'combined';
  status: 'draft' | 'active' | 'completed' | 'archived';
  createdAt: string;          // ISO date string
  totalValue?: number;        // In cents
}
```

### Activity Interface

```typescript
interface Activity {
  id: number;
  type: 'project_created' | 'project_completed' | 'calculation' | 'pdf_generated' | 'customer_added';
  description: string;
  timestamp: string;          // ISO date string
  icon: string;               // PrimeIcons class
  color: string;              // Hex color
}
```

## API Integration

### Expected Endpoints

```typescript
// Load dashboard statistics
GET /api/v1/dashboard/stats
Response: StatCard[]

// Load recent projects
GET /api/v1/dashboard/projects/recent?limit=5
Response: Project[]

// Load activity timeline
GET /api/v1/dashboard/activities?limit=10
Response: Activity[]
```

### Integration Example

```typescript
const loadDashboardData = async () => {
  try {
    const [stats, projects, activities] = await Promise.all([
      api.get('/api/v1/dashboard/stats'),
      api.get('/api/v1/dashboard/projects/recent?limit=5'),
      api.get('/api/v1/dashboard/activities?limit=10')
    ]);
    
    setStats(stats.data);
    setRecentProjects(projects.data);
    setActivities(activities.data);
  } catch (error) {
    console.error('Error loading dashboard:', error);
  }
};
```

## Responsive Breakpoints

```css
/* Desktop: >1024px */
.dashboard-content {
  grid-template-columns: 2fr 1fr;
}

/* Tablet: 768px-1024px */
@media (max-width: 1024px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

/* Mobile: <768px */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .quick-actions .p-button {
    flex: 1;
  }
}
```

## Common Tasks

### Update Statistics

```typescript
// Update a single stat
setStats(prevStats => 
  prevStats.map(stat => 
    stat.title === 'Total Projects' 
      ? { ...stat, value: newValue }
      : stat
  )
);
```

### Refresh Data

```typescript
const handleRefresh = () => {
  setLoading(true);
  loadDashboardData();
};
```

### Navigate to Project

```typescript
const handleViewProject = (projectId: number) => {
  navigate(`/projects/${projectId}`);
};
```

### Filter Projects

```typescript
const filteredProjects = recentProjects.filter(
  project => project.status === 'active'
);
```

## Troubleshooting

### Dashboard Not Loading

1. Check if route is properly configured
2. Verify component import path
3. Check for console errors
4. Ensure PrimeReact is installed

### Statistics Not Displaying

1. Verify data structure matches interface
2. Check if `stats` state is populated
3. Inspect CSS for display issues
4. Check for JavaScript errors

### Table Not Sorting

1. Ensure `sortable` prop is set on columns
2. Verify data has proper field names
3. Check DataTable configuration

### Timeline Not Showing

1. Verify activities data structure
2. Check Timeline component import
3. Inspect custom marker/content functions
4. Check CSS for visibility issues

## Best Practices

1. **Performance**: Use `useMemo` for expensive calculations
2. **Loading States**: Always show loading indicators
3. **Error Handling**: Implement proper error boundaries
4. **Accessibility**: Ensure keyboard navigation works
5. **Responsive**: Test on multiple screen sizes
6. **Localization**: Use German number/date formats
7. **Caching**: Consider caching dashboard data
8. **Real-time**: Implement WebSocket for live updates

## Examples

### Custom Stat Card

```typescript
const CustomStatCard = ({ stat }: { stat: StatCard }) => (
  <Card className="custom-stat-card">
    <div className="stat-header">
      <i className={stat.icon} style={{ color: stat.color }} />
      <h3>{stat.title}</h3>
    </div>
    <div className="stat-body">
      <span className="stat-value">{stat.value}</span>
      {stat.trend && (
        <span className={`trend ${stat.trend.isPositive ? 'up' : 'down'}`}>
          {stat.trend.value}%
        </span>
      )}
    </div>
  </Card>
);
```

### Custom Activity Item

```typescript
const ActivityItem = ({ activity }: { activity: Activity }) => (
  <div className="activity-item">
    <div 
      className="activity-marker" 
      style={{ backgroundColor: activity.color }}
    >
      <i className={activity.icon} />
    </div>
    <div className="activity-content">
      <p>{activity.description}</p>
      <small>{new Date(activity.timestamp).toLocaleString('de-DE')}</small>
    </div>
  </div>
);
```

## Related Components

- **MainLayout**: Parent layout component
- **Sidebar**: Navigation sidebar
- **Header**: Application header
- **Card**: PrimeReact Card component
- **DataTable**: PrimeReact DataTable component
- **Timeline**: PrimeReact Timeline component

## Further Reading

- [PrimeReact Documentation](https://primereact.org/)
- [React Router Documentation](https://reactrouter.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [CSS Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
