# Solar Project Details Page - Quick Reference

## Overview

The Solar Project Details Page provides a comprehensive view of individual solar projects with calculation results, 3D visualization, and management actions.

## Page Structure

### Three Main Tabs

1. **📋 Projektinformationen** (Project Information)
   - Project metadata (ID, type, status, dates)
   - Customer information
   - Input data summary (roof dimensions, consumption, location)

2. **📊 Berechnungsergebnisse** (Calculation Results)
   - System sizing and module count
   - Energy production and consumption
   - Economic analysis and savings
   - Environmental impact
   - Interactive charts and visualizations

3. **📦 3D-Visualisierung** (3D Visualization)
   - Interactive 3D roof model
   - Solar module placement
   - Camera controls and viewing options
   - Export capabilities

## Key Features

### Header Actions

```typescript
// Available actions in header
- 3D-Ansicht: Switch to 3D visualization tab
- PDF erstellen: Generate and download PDF report
- Bearbeiten: Edit project in calculator
- Löschen: Delete project (with confirmation)
```

### Data Display

```typescript
// Project information displayed
{
  id: number,
  name: string,
  type: 'solar' | 'heatpump' | 'combined',
  status: 'draft' | 'active' | 'completed' | 'archived',
  customer_id: number,
  dynamic_key: string,
  created_at: Date,
  updated_at: Date
}
```

### Calculation Results

When available, displays:
- ⚡ System size (kWp) and module count
- ☀️ Annual energy production
- 🏠 Self-consumption rate and autarky degree
- 💰 Annual savings and payback period
- 🌱 CO2 savings and environmental impact
- 📈 Interactive charts (monthly production, energy distribution, payback curve)

### 3D Visualization

Interactive features:
- **Rotate**: Left mouse + drag
- **Zoom**: Mouse wheel or pinch
- **Pan**: Right mouse + drag
- **Controls**: Grid, sky, auto-rotate toggles
- **Camera**: Adjustable distance (5-50m)
- **Export**: Multiple 3D format options

## Usage Examples

### Loading a Project

```typescript
// Navigate to project details
navigate(`/solar-projects/${projectId}`);

// Or from project list
<Button onClick={() => handleViewProject(project)} />
```

### Generating PDF

```typescript
// PDF generation with options
const response = await api.post('/api/v1/pdf/generate', {
  project_id: projectId,
  template: 'solar_offer',
  options: {
    include_3d: true,
    include_charts: true,
    language: 'de'
  }
}, {
  responseType: 'blob'
});

// Automatic download
const blob = new Blob([response.data], { type: 'application/pdf' });
const url = window.URL.createObjectURL(blob);
// ... download logic
```

### Editing Project

```typescript
// Navigate to calculator with project context
navigate('/solar-calculator', { 
  state: { 
    projectId, 
    projectData: project?.data 
  } 
});
```

### Deleting Project

```typescript
// Confirmation dialog before deletion
confirmDialog({
  message: `Möchten Sie das Projekt "${project.name}" wirklich löschen?`,
  accept: async () => {
    await api.delete(`/api/v1/solar/projects/${projectId}`);
    navigate('/solar-projects');
  }
});
```

## Empty States

### No Calculation Results

```
┌─────────────────────────────────────┐
│  📊                                  │
│  Keine Berechnungsergebnisse        │
│  vorhanden                           │
│                                      │
│  Führen Sie eine Berechnung durch,  │
│  um Ergebnisse anzuzeigen.          │
│                                      │
│  [Neue Berechnung starten]          │
└─────────────────────────────────────┘
```

### No 3D Visualization

```
┌─────────────────────────────────────┐
│  📦                                  │
│  Keine 3D-Visualisierung            │
│  verfügbar                           │
│                                      │
│  Führen Sie zuerst eine Berechnung  │
│  durch.                              │
│                                      │
│  [Berechnung starten]               │
└─────────────────────────────────────┘
```

## API Endpoints

### Get Project Details
```http
GET /api/v1/solar/projects/{projectId}
Response: Project object with data
```

### Generate PDF
```http
POST /api/v1/pdf/generate
Body: {
  project_id: number,
  template: string,
  options: object
}
Response: PDF blob
```

### Delete Project
```http
DELETE /api/v1/solar/projects/{projectId}
Response: Success message
```

## Component Props

### SolarCalculationResults

```typescript
interface SolarCalculationResultsProps {
  results: SolarCalculationResponse;
  onEdit?: () => void;
  onSave?: () => void;
  onGeneratePDF?: () => void;
  onView3D?: () => void;
}
```

### Viewer3D

```typescript
interface Viewer3DProps {
  roofType: 'flat' | 'gable' | 'hip';
  roofWidth: number;
  roofLength: number;
  roofHeight?: number;
  roofAngle: number;
  moduleCount: number;
}
```

## Styling Classes

### Main Container
```css
.solar-project-details-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}
```

### Header
```css
.page-header {
  display: flex;
  justify-content: space-between;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

### Tabs
```css
.p-tabview {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

## Responsive Behavior

### Desktop (>992px)
- Full three-column layout
- All features visible
- Large buttons and text

### Tablet (768px - 992px)
- Two-column layout
- Adjusted tab padding
- Medium buttons

### Mobile (<768px)
- Single column layout
- Stacked header
- Full-width buttons
- Compact spacing

## Error Handling

### Common Errors

1. **Project Not Found (404)**
   - Shows error message
   - Auto-redirects to project list after 2 seconds

2. **Network Error**
   - Toast notification with error details
   - Retry option available

3. **PDF Generation Failed**
   - Error toast with details
   - Button returns to normal state

4. **Missing Data**
   - Empty state cards with helpful messages
   - Call-to-action buttons to resolve

## Performance Tips

1. **Lazy Loading**: Calculation results component loads on demand
2. **Caching**: Project data cached in component state
3. **Debouncing**: Tab switches debounced to prevent rapid changes
4. **Memoization**: Expensive calculations memoized
5. **Code Splitting**: Route-level code splitting enabled

## Accessibility

- Keyboard navigation supported
- ARIA labels on interactive elements
- Focus management in dialogs
- Screen reader friendly
- High contrast mode compatible

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Full support
- IE11: ❌ Not supported

## Related Components

- `SolarProjects.tsx`: Project list page
- `SolarCalculator.tsx`: Calculator page
- `SolarCalculationResults.tsx`: Results display
- `Viewer3D.tsx`: 3D visualization
- `Scene3D.tsx`: 3D scene rendering

## Common Tasks

### Add New Tab

```typescript
<TabPanel header="New Tab" leftIcon="pi pi-icon">
  <YourComponent />
</TabPanel>
```

### Customize PDF Options

```typescript
const pdfOptions = {
  include_3d: true,
  include_charts: true,
  include_tables: true,
  language: 'de',
  template: 'custom_template'
};
```

### Add Custom Action

```typescript
const handleCustomAction = async () => {
  try {
    await api.post('/api/v1/custom-endpoint', data);
    toast.current?.show({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Aktion erfolgreich'
    });
  } catch (error) {
    // Error handling
  }
};
```

## Troubleshooting

### Issue: 3D Visualization Not Loading
**Solution**: Check if calculation results contain required roof dimensions

### Issue: PDF Generation Fails
**Solution**: Verify project has complete calculation results

### Issue: Empty State Always Shows
**Solution**: Check project.data.calculation_results structure

### Issue: Tabs Not Switching
**Solution**: Verify activeTab state is being updated correctly

---

**Last Updated**: 2025-01-19  
**Version**: 1.0.0  
**Component**: SolarProjectDetails
