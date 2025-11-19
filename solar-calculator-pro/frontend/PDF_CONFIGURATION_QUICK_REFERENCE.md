# PDF Configuration Interface - Quick Reference

## 🚀 Quick Start

```typescript
import { PDFConfigurationComponent } from './components/pdf/PDFConfiguration';

<PDFConfigurationComponent
  template={selectedTemplate}
  onGenerate={(config) => generatePDF(config)}
  onCancel={() => goBack()}
/>
```

## 📋 Configuration Tabs

### 1. ⚙️ General Options
- **Page Size**: A4, Letter, Legal
- **Orientation**: Portrait, Landscape
- **Margins**: Top, Right, Bottom, Left (mm)
- **Display**: Page numbers, Date, Logo

### 2. 🎨 Logo & Branding
- **Upload**: PNG, JPG, SVG (max 5MB)
- **Position**: X, Y coordinates (mm)
- **Size**: Width, Height (mm)
- **Alignment**: Left, Center, Right

### 3. 🌈 Color Scheme
- **Primary**: Main brand color
- **Secondary**: Supporting color
- **Accent**: Highlight color
- **Text**: Text color
- **Background**: Page background

### 4. 📑 Content Sections
- Executive Summary
- Calculations & Results
- Charts & Visualizations
- Technical Details
- Financial Analysis
- Recommendations

### 5. ✏️ Custom Fields
- Company Name
- Project Name
- Customer Name
- Additional Notes
- Header Text
- Footer Text

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Real-time Preview** | See changes instantly |
| **Color Picker** | Visual color selection |
| **Logo Upload** | Drag & drop support |
| **Section Toggle** | Enable/disable sections |
| **Custom Fields** | Add project information |
| **Responsive** | Works on all devices |

## 📊 Configuration Object

```typescript
{
  template_id: number,
  logo_url?: string,
  logo_position: { x, y, width, height, alignment },
  color_scheme: { primary, secondary, accent, text, background },
  content_sections: [{ id, name, enabled, order }],
  custom_fields: [{ id, label, value, placeholder }],
  page_size: 'A4' | 'Letter' | 'Legal',
  orientation: 'portrait' | 'landscape',
  margins: { top, right, bottom, left },
  header_text?: string,
  footer_text?: string,
  show_page_numbers: boolean,
  show_date: boolean,
  show_logo: boolean
}
```

## 🔧 Common Tasks

### Change Page Size
```typescript
updateConfig({ page_size: 'A4' });
```

### Update Logo Position
```typescript
updateLogoPosition({ x: 50, y: 20, width: 100, height: 50 });
```

### Change Primary Color
```typescript
updateColorScheme({ primary: '#2196F3' });
```

### Toggle Section
```typescript
toggleSection('summary');
```

### Update Custom Field
```typescript
updateCustomField('company_name', 'Acme Corp');
```

## ⚡ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` | Navigate fields |
| `Shift+Tab` | Navigate backwards |
| `Enter` | Confirm selection |
| `Esc` | Cancel configuration |
| `Ctrl+S` | Save configuration |

## 🎨 Color Presets

### Default
```typescript
{ primary: '#2196F3', secondary: '#FFC107', accent: '#4CAF50' }
```

### Professional
```typescript
{ primary: '#1E3A8A', secondary: '#F59E0B', accent: '#10B981' }
```

### Elegant
```typescript
{ primary: '#6366F1', secondary: '#EC4899', accent: '#8B5CF6' }
```

## 📏 Recommended Settings

### Standard Document
- Page Size: A4
- Orientation: Portrait
- Margins: 20mm all sides
- Logo: 100×50mm, top-left

### Presentation
- Page Size: A4
- Orientation: Landscape
- Margins: 15mm all sides
- Logo: 120×40mm, centered

### Report
- Page Size: Letter
- Orientation: Portrait
- Margins: 25mm all sides
- Logo: 80×40mm, top-right

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Logo not showing | Check file size (<5MB) and format |
| Colors not applying | Use valid hex format (#RRGGBB) |
| PDF generation fails | Verify all required fields |
| Slow performance | Optimize logo, reduce sections |

## 📱 Responsive Breakpoints

- **Desktop**: > 1024px (Full layout)
- **Tablet**: 768px - 1024px (Adapted layout)
- **Mobile**: < 768px (Stacked layout)

## 🔒 Validation Rules

- **Margins**: 0-50mm
- **Logo Size**: 20-200mm
- **Colors**: Valid hex (#RRGGBB)
- **File Size**: Max 5MB
- **Required Fields**: Template ID

## 💡 Pro Tips

1. **Save Configurations**: Save frequently used settings as presets
2. **Test First**: Preview before generating final PDF
3. **Optimize Logos**: Use web-optimized formats (WebP, optimized PNG)
4. **Brand Consistency**: Use consistent colors across all PDFs
5. **Section Order**: Arrange sections logically for better flow

## 🔗 Related Components

- `TemplateGallery` - Select PDF template
- `TemplatePreview` - Preview template
- `TemplateUpload` - Upload custom templates
- `TemplateManagement` - Manage templates

## 📚 Resources

- [Complete Guide](./PDF_CONFIGURATION_GUIDE.md)
- [API Documentation](../../backend/docs/PDF_API.md)
- [Examples](./examples/pdf-configuration-examples.tsx)

## 🆘 Support

- **Documentation**: Check the complete guide
- **Examples**: Review example configurations
- **Issues**: Submit bug reports
- **Questions**: Contact development team
