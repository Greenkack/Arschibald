# PDF Configuration Interface - Complete Guide

## Overview

The PDF Configuration Interface provides a comprehensive solution for customizing PDF documents before generation. It includes five main configuration areas:

1. **General Options** - Page settings, margins, and display options
2. **Logo & Branding** - Logo upload and positioning
3. **Color Scheme** - Brand color customization
4. **Content Sections** - Toggle and reorder PDF sections
5. **Custom Fields** - Add custom text and information

## Features

### ✅ Implemented Features

#### 1. PDF Options Form
- **Page Size Selection**: A4, Letter, Legal
- **Orientation**: Portrait or Landscape
- **Margins**: Customizable top, right, bottom, left margins (in mm)
- **Display Options**:
  - Show/hide page numbers
  - Show/hide generation date
  - Show/hide logo

#### 2. Logo Upload and Positioning
- **Upload**: Support for image files (PNG, JPG, SVG)
- **Preview**: Real-time logo preview
- **Position Controls**:
  - X position (0-200mm)
  - Y position (0-200mm)
  - Width (20-200mm)
  - Height (20-200mm)
- **Alignment**: Left, Center, Right

#### 3. Color Scheme Selection
- **Five Color Categories**:
  - Primary Color
  - Secondary Color
  - Accent Color
  - Text Color
  - Background Color
- **Color Picker**: Visual color selection
- **Hex Input**: Manual hex code entry
- **Live Preview**: Real-time color preview

#### 4. Content Section Toggles
- **Predefined Sections**:
  - Executive Summary
  - Calculations & Results
  - Charts & Visualizations
  - Technical Details
  - Financial Analysis
  - Recommendations
- **Toggle On/Off**: Enable or disable sections
- **Reorder**: Drag to reorder sections (UI ready)

#### 5. Custom Text Fields
- **Standard Fields**:
  - Company Name
  - Project Name
  - Customer Name
  - Additional Notes (textarea)
- **Header & Footer**:
  - Custom header text
  - Custom footer text

## Component Structure

```
PDFConfiguration/
├── PDFConfiguration.tsx       # Main configuration component
├── PDFConfiguration.css       # Styling
└── Types:
    ├── PDFConfiguration       # Main config interface
    ├── LogoPosition          # Logo positioning
    ├── ColorScheme           # Color settings
    ├── ContentSection        # Section configuration
    └── CustomTextField       # Custom field definition
```

## Usage

### Basic Usage

```typescript
import { PDFConfigurationComponent } from './components/pdf/PDFConfiguration';

<PDFConfigurationComponent
  template={selectedTemplate}
  onConfigChange={(config) => console.log('Config changed:', config)}
  onGenerate={(config) => generatePDF(config)}
  onCancel={() => setShowConfig(false)}
/>
```

### With Initial Configuration

```typescript
const initialConfig = {
  page_size: 'A4',
  orientation: 'portrait',
  color_scheme: {
    primary: '#2196F3',
    secondary: '#FFC107',
    accent: '#4CAF50',
    text: '#333333',
    background: '#FFFFFF',
  },
  // ... other settings
};

<PDFConfigurationComponent
  template={selectedTemplate}
  initialConfig={initialConfig}
  onConfigChange={handleConfigChange}
  onGenerate={handleGenerate}
  onCancel={handleCancel}
/>
```

## Configuration Object

### Complete Configuration Structure

```typescript
interface PDFConfiguration {
  // Template
  template_id: number;
  
  // Logo
  logo_url?: string;
  logo_position: {
    x: number;              // 0-200mm
    y: number;              // 0-200mm
    width: number;          // 20-200mm
    height: number;         // 20-200mm
    alignment: 'left' | 'center' | 'right';
  };
  
  // Colors
  color_scheme: {
    primary: string;        // Hex color
    secondary: string;      // Hex color
    accent: string;         // Hex color
    text: string;           // Hex color
    background: string;     // Hex color
  };
  
  // Sections
  content_sections: Array<{
    id: string;
    name: string;
    enabled: boolean;
    order: number;
  }>;
  
  // Custom Fields
  custom_fields: Array<{
    id: string;
    label: string;
    value: string;
    placeholder: string;
  }>;
  
  // Page Settings
  page_size: 'A4' | 'Letter' | 'Legal';
  orientation: 'portrait' | 'landscape';
  margins: {
    top: number;            // mm
    right: number;          // mm
    bottom: number;         // mm
    left: number;           // mm
  };
  
  // Display Options
  header_text?: string;
  footer_text?: string;
  show_page_numbers: boolean;
  show_date: boolean;
  show_logo: boolean;
}
```

## API Integration

### Generate PDF Endpoint

```typescript
// POST /api/v1/pdf/generate
const generatePDF = async (config: PDFConfiguration) => {
  try {
    const response = await api.post('/api/v1/pdf/generate', config);
    
    // Response contains PDF URL or base64
    const pdfUrl = response.data.pdf_url;
    
    // Download or display PDF
    window.open(pdfUrl, '_blank');
  } catch (error) {
    console.error('PDF generation failed:', error);
  }
};
```

### Save Configuration Endpoint

```typescript
// POST /api/v1/pdf/configurations
const saveConfiguration = async (config: PDFConfiguration) => {
  try {
    const response = await api.post('/api/v1/pdf/configurations', {
      name: 'My Custom Config',
      config: config,
    });
    
    return response.data.id;
  } catch (error) {
    console.error('Failed to save configuration:', error);
  }
};
```

### Load Configuration Endpoint

```typescript
// GET /api/v1/pdf/configurations/:id
const loadConfiguration = async (configId: number) => {
  try {
    const response = await api.get(`/api/v1/pdf/configurations/${configId}`);
    return response.data.config;
  } catch (error) {
    console.error('Failed to load configuration:', error);
  }
};
```

## Customization

### Adding New Color Presets

```typescript
const colorPresets = {
  default: {
    primary: '#2196F3',
    secondary: '#FFC107',
    accent: '#4CAF50',
    text: '#333333',
    background: '#FFFFFF',
  },
  dark: {
    primary: '#1976D2',
    secondary: '#FFA000',
    accent: '#388E3C',
    text: '#FFFFFF',
    background: '#121212',
  },
  // Add more presets
};
```

### Adding New Content Sections

```typescript
const additionalSections = [
  {
    id: 'warranty',
    name: 'Warranty Information',
    enabled: true,
    order: 7,
  },
  {
    id: 'maintenance',
    name: 'Maintenance Schedule',
    enabled: true,
    order: 8,
  },
];
```

### Adding New Custom Fields

```typescript
const additionalFields = [
  {
    id: 'project_location',
    label: 'Project Location',
    value: '',
    placeholder: 'Enter project location',
  },
  {
    id: 'contact_email',
    label: 'Contact Email',
    value: '',
    placeholder: 'Enter contact email',
  },
];
```

## Validation

### Client-Side Validation

```typescript
const validateConfiguration = (config: PDFConfiguration): string[] => {
  const errors: string[] = [];
  
  // Validate margins
  if (config.margins.top < 0 || config.margins.top > 50) {
    errors.push('Top margin must be between 0 and 50mm');
  }
  
  // Validate colors
  const hexPattern = /^#[0-9A-F]{6}$/i;
  if (!hexPattern.test(config.color_scheme.primary)) {
    errors.push('Invalid primary color format');
  }
  
  // Validate logo dimensions
  if (config.show_logo && config.logo_position.width < 20) {
    errors.push('Logo width must be at least 20mm');
  }
  
  return errors;
};
```

## Accessibility

### Keyboard Navigation
- All form fields are keyboard accessible
- Tab order follows logical flow
- Color pickers have keyboard support

### Screen Reader Support
- All form fields have proper labels
- ARIA labels for icon buttons
- Descriptive error messages

### Color Contrast
- Text meets WCAG AA standards
- Color picker shows contrast warnings
- High contrast mode support

## Performance

### Optimization Techniques
1. **Debounced Updates**: Config changes are debounced to prevent excessive re-renders
2. **Lazy Loading**: Color picker loaded on demand
3. **Memoization**: Complex calculations are memoized
4. **Virtual Scrolling**: For large section lists

### Best Practices
- Keep logo files under 5MB
- Use web-optimized image formats (WebP, optimized PNG)
- Limit custom fields to essential information
- Test configuration with sample data before generation

## Troubleshooting

### Common Issues

#### Logo Not Displaying
- **Cause**: File size too large or unsupported format
- **Solution**: Use PNG/JPG under 5MB, optimize images

#### Colors Not Applying
- **Cause**: Invalid hex color format
- **Solution**: Ensure colors start with # and have 6 hex digits

#### PDF Generation Fails
- **Cause**: Missing required fields or invalid configuration
- **Solution**: Check validation errors, ensure all required fields are filled

#### Slow Performance
- **Cause**: Large logo file or too many sections
- **Solution**: Optimize logo, disable unused sections

## Future Enhancements

### Planned Features
- [ ] Drag-and-drop section reordering (backend support needed)
- [ ] Configuration templates/presets
- [ ] Real-time PDF preview
- [ ] Multi-language support
- [ ] Advanced typography settings
- [ ] Custom CSS injection
- [ ] Batch PDF generation
- [ ] Configuration sharing/export

### API Requirements
- [ ] PDF generation endpoint
- [ ] Configuration save/load endpoints
- [ ] Template customization endpoint
- [ ] Logo upload endpoint with processing
- [ ] Preview generation endpoint

## Examples

### Example 1: Simple Configuration

```typescript
const simpleConfig: PDFConfiguration = {
  template_id: 1,
  page_size: 'A4',
  orientation: 'portrait',
  margins: { top: 20, right: 20, bottom: 20, left: 20 },
  color_scheme: {
    primary: '#2196F3',
    secondary: '#FFC107',
    accent: '#4CAF50',
    text: '#333333',
    background: '#FFFFFF',
  },
  content_sections: [
    { id: 'summary', name: 'Summary', enabled: true, order: 1 },
    { id: 'calculations', name: 'Calculations', enabled: true, order: 2 },
  ],
  custom_fields: [
    { id: 'company_name', label: 'Company', value: 'Acme Corp', placeholder: '' },
  ],
  logo_position: { x: 50, y: 20, width: 100, height: 50, alignment: 'left' },
  show_page_numbers: true,
  show_date: true,
  show_logo: false,
};
```

### Example 2: Branded Configuration

```typescript
const brandedConfig: PDFConfiguration = {
  template_id: 2,
  logo_url: 'data:image/png;base64,...',
  page_size: 'A4',
  orientation: 'portrait',
  margins: { top: 30, right: 25, bottom: 30, left: 25 },
  color_scheme: {
    primary: '#1E3A8A',      // Brand blue
    secondary: '#F59E0B',    // Brand orange
    accent: '#10B981',       // Brand green
    text: '#1F2937',         // Dark gray
    background: '#FFFFFF',   // White
  },
  content_sections: [
    { id: 'summary', name: 'Executive Summary', enabled: true, order: 1 },
    { id: 'calculations', name: 'Calculations', enabled: true, order: 2 },
    { id: 'charts', name: 'Charts', enabled: true, order: 3 },
    { id: 'technical', name: 'Technical Details', enabled: true, order: 4 },
    { id: 'financial', name: 'Financial Analysis', enabled: true, order: 5 },
    { id: 'recommendations', name: 'Recommendations', enabled: true, order: 6 },
  ],
  custom_fields: [
    { id: 'company_name', label: 'Company', value: 'Solar Solutions Inc.', placeholder: '' },
    { id: 'project_name', label: 'Project', value: 'Residential Solar Installation', placeholder: '' },
    { id: 'customer_name', label: 'Customer', value: 'John Doe', placeholder: '' },
    { id: 'notes', label: 'Notes', value: 'Premium installation package', placeholder: '' },
  ],
  logo_position: { x: 150, y: 15, width: 120, height: 40, alignment: 'center' },
  header_text: 'Solar Solutions Inc. - Professional Solar Analysis',
  footer_text: 'Confidential - For Internal Use Only',
  show_page_numbers: true,
  show_date: true,
  show_logo: true,
};
```

## Testing

### Unit Tests

```typescript
describe('PDFConfiguration', () => {
  it('should render with default configuration', () => {
    const { getByText } = render(
      <PDFConfigurationComponent template={mockTemplate} />
    );
    expect(getByText('Configure PDF')).toBeInTheDocument();
  });

  it('should update color scheme', () => {
    const handleChange = jest.fn();
    const { getByLabelText } = render(
      <PDFConfigurationComponent
        template={mockTemplate}
        onConfigChange={handleChange}
      />
    );
    
    const primaryColorInput = getByLabelText('Primary Color');
    fireEvent.change(primaryColorInput, { target: { value: '#FF0000' } });
    
    expect(handleChange).toHaveBeenCalledWith(
      expect.objectContaining({
        color_scheme: expect.objectContaining({
          primary: '#FF0000',
        }),
      })
    );
  });

  it('should toggle content sections', () => {
    const handleChange = jest.fn();
    const { getByLabelText } = render(
      <PDFConfigurationComponent
        template={mockTemplate}
        onConfigChange={handleChange}
      />
    );
    
    const summaryCheckbox = getByLabelText('Executive Summary');
    fireEvent.click(summaryCheckbox);
    
    expect(handleChange).toHaveBeenCalled();
  });
});
```

## Support

For issues or questions:
- Check the troubleshooting section
- Review the examples
- Contact the development team
- Submit a bug report

## License

This component is part of the Solar Calculator Pro application.
