# Results Reporting System - Complete Guide

## Overview

The Results Reporting System provides comprehensive report generation capabilities for solar calculator projects. It supports multiple report types, formats, and customization options.

## Report Types

### 1. Detailed Report
**Purpose**: Comprehensive analysis of all project aspects

**Includes**:
- Project information and system configuration
- Complete calculation results
- Energy analysis (monthly, hourly, seasonal)
- Financial analysis (costs, savings, ROI, NPV, IRR)
- Environmental impact assessment
- Technical specifications
- Recommendations
- Charts and tables

**Best For**: Technical teams, detailed project documentation, archival purposes

### 2. Executive Summary
**Purpose**: High-level overview for decision makers

**Includes**:
- Key project metrics
- System size and cost
- Annual savings and payback period
- ROI percentage
- CO₂ reduction
- Key highlights (5-7 bullet points)
- Recommendation
- Essential charts

**Best For**: Management presentations, quick decision making, stakeholder communication

### 3. Technical Report
**Purpose**: Detailed technical specifications and design

**Includes**:
- System design and configuration
- Component specifications (modules, inverters, batteries)
- Installation requirements
- Electrical design (DC/AC voltages, currents)
- Mounting system details
- Performance calculations
- Compliance standards
- Technical drawings

**Best For**: Installation teams, electrical engineers, compliance verification

### 4. Financial Report
**Purpose**: Comprehensive financial analysis

**Includes**:
- Investment summary
- Detailed cost breakdown
- Revenue projections (1, 5, 10, 25 years)
- Cash flow analysis
- ROI analysis (payback, NPV, IRR)
- Financing options comparison
- Tax benefits
- Sensitivity analysis

**Best For**: Financial planning, investment decisions, loan applications

### 5. Environmental Report
**Purpose**: Environmental impact and sustainability metrics

**Includes**:
- CO₂ emissions avoided (annual and lifetime)
- Equivalent trees planted
- Equivalent cars removed from road
- Renewable energy percentage
- Lifecycle analysis
- Environmental certifications
- Sustainability metrics

**Best For**: Sustainability reporting, green certifications, environmental compliance

### 6. Custom Report
**Purpose**: User-defined report with selected sections

**Includes**:
- User-selected sections from any report type
- Custom ordering
- Custom charts and tables
- Flexible content

**Best For**: Specific use cases, tailored presentations, specialized requirements

## Output Formats

### PDF
- Professional print-ready format
- Preserves formatting and layout
- Includes charts and tables
- Suitable for distribution

### HTML
- Web-viewable format
- Interactive elements possible
- Easy to share via email
- Browser-based preview

### JSON
- Machine-readable format
- API integration
- Data processing
- System-to-system communication

### Excel
- Spreadsheet format
- Editable data
- Custom calculations possible
- Data analysis

### CSV
- Simple data format
- Import into other systems
- Database loading
- Basic data exchange

## API Endpoints

### Generate Report
```http
POST /api/v1/reports/generate
Content-Type: application/json

{
  "project_id": 1,
  "report_type": "detailed",
  "format": "pdf",
  "template_id": null,
  "custom_sections": null,
  "include_charts": true,
  "include_tables": true,
  "include_raw_data": false,
  "language": "de",
  "branding": {
    "logo_url": "https://example.com/logo.png",
    "company_name": "Solar Solutions GmbH",
    "colors": {
      "primary": "#4CAF50",
      "secondary": "#2196F3"
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "report_id": "123e4567-e89b-12d3-a456-426614174000",
  "metadata": {
    "report_id": "123e4567-e89b-12d3-a456-426614174000",
    "project_id": 1,
    "report_type": "detailed",
    "format": "pdf",
    "generated_at": "2024-01-15T10:30:00Z",
    "generated_by": "user@example.com",
    "file_size": 1024000,
    "page_count": 15,
    "version": "1.0"
  },
  "download_url": "/api/v1/reports/123e4567-e89b-12d3-a456-426614174000/download",
  "preview_url": "/api/v1/reports/123e4567-e89b-12d3-a456-426614174000/preview",
  "message": "Report generated successfully"
}
```

### Download Report
```http
GET /api/v1/reports/{report_id}/download
```

Returns the report file for download.

### Preview Report
```http
GET /api/v1/reports/{report_id}/preview
```

Returns HTML preview of the report (HTML format only).

### Get Report History
```http
GET /api/v1/reports/history?project_id=1&report_type=detailed&page=1&page_size=20
```

**Response**:
```json
{
  "reports": [
    {
      "report_id": "123e4567-e89b-12d3-a456-426614174000",
      "project_id": 1,
      "project_name": "Sample Solar Project",
      "report_type": "detailed",
      "format": "pdf",
      "generated_at": "2024-01-15T10:30:00Z",
      "file_size": 1024000,
      "download_url": "/api/v1/reports/123e4567-e89b-12d3-a456-426614174000/download"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### Delete Report
```http
DELETE /api/v1/reports/{report_id}
```

### Get Available Report Types
```http
GET /api/v1/reports/types
```

Returns list of available report types and formats with descriptions.

## Usage Examples

### Python Example
```python
import requests

# Generate detailed PDF report
response = requests.post(
    "http://localhost:8000/api/v1/reports/generate",
    json={
        "project_id": 1,
        "report_type": "detailed",
        "format": "pdf",
        "include_charts": True,
        "include_tables": True,
        "language": "de"
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

report_data = response.json()
report_id = report_data["report_id"]

# Download the report
download_response = requests.get(
    f"http://localhost:8000/api/v1/reports/{report_id}/download",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

with open("report.pdf", "wb") as f:
    f.write(download_response.content)
```

### TypeScript Example
```typescript
import axios from 'axios';

// Generate executive summary in HTML format
const generateReport = async (projectId: number) => {
  const response = await axios.post('/api/v1/reports/generate', {
    project_id: projectId,
    report_type: 'executive',
    format: 'html',
    include_charts: true,
    language: 'de'
  });
  
  return response.data;
};

// Download report
const downloadReport = async (reportId: string) => {
  const response = await axios.get(
    `/api/v1/reports/${reportId}/download`,
    { responseType: 'blob' }
  );
  
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `report-${reportId}.html`);
  document.body.appendChild(link);
  link.click();
  link.remove();
};
```

## Customization

### Custom Sections
Create custom reports with specific sections:

```json
{
  "project_id": 1,
  "report_type": "custom",
  "format": "pdf",
  "custom_sections": [
    {
      "title": "System Overview",
      "content": {
        "system_size": 10.5,
        "module_count": 30
      },
      "order": 1,
      "visible": true,
      "charts": [
        {
          "type": "bar",
          "title": "Monthly Production",
          "data": [...]
        }
      ]
    },
    {
      "title": "Financial Summary",
      "content": {
        "total_cost": 16999.00,
        "annual_savings": 1850.00
      },
      "order": 2,
      "visible": true
    }
  ]
}
```

### Branding
Apply custom branding to reports:

```json
{
  "branding": {
    "logo_url": "https://example.com/logo.png",
    "company_name": "Solar Solutions GmbH",
    "company_address": "Musterstraße 123, 10115 Berlin",
    "company_phone": "+49 30 12345678",
    "company_email": "info@solar-solutions.de",
    "colors": {
      "primary": "#4CAF50",
      "secondary": "#2196F3",
      "accent": "#FF9800"
    },
    "fonts": {
      "heading": "Helvetica-Bold",
      "body": "Helvetica"
    }
  }
}
```

## Best Practices

### 1. Choose the Right Report Type
- **Detailed**: For comprehensive documentation
- **Executive**: For quick decision making
- **Technical**: For installation and engineering
- **Financial**: For investment analysis
- **Environmental**: For sustainability reporting
- **Custom**: For specific requirements

### 2. Select Appropriate Format
- **PDF**: For distribution and printing
- **HTML**: For web viewing and sharing
- **JSON**: For API integration
- **Excel**: For data analysis
- **CSV**: For simple data exchange

### 3. Include Relevant Content
- Enable charts for visual representation
- Include tables for detailed data
- Add raw data only when needed
- Use appropriate language (de/en)

### 4. Apply Branding
- Use company logo and colors
- Maintain consistent styling
- Include contact information
- Follow brand guidelines

### 5. Manage Report History
- Keep reports organized by project
- Delete old reports regularly
- Archive important reports
- Track report generation

## Troubleshooting

### Report Generation Fails
- Check project data completeness
- Verify all required fields are present
- Ensure sufficient disk space
- Check file permissions

### Download Issues
- Verify report ID is correct
- Check user permissions
- Ensure report file exists
- Verify network connectivity

### Preview Not Available
- HTML format required for preview
- Generate HTML version if needed
- Check browser compatibility
- Verify file accessibility

## Performance Considerations

### Large Reports
- Use pagination for tables
- Optimize chart data
- Compress images
- Consider async generation

### Batch Generation
- Generate reports in background
- Use queue system
- Implement progress tracking
- Handle errors gracefully

### Storage Management
- Implement automatic cleanup
- Archive old reports
- Monitor disk usage
- Use cloud storage if needed

## Security

### Access Control
- Verify user permissions
- Check project ownership
- Validate report access
- Audit report downloads

### Data Protection
- Encrypt sensitive data
- Sanitize user inputs
- Validate file paths
- Prevent path traversal

### Compliance
- Follow data protection regulations
- Implement audit logging
- Secure file storage
- Control data retention

## Future Enhancements

### Planned Features
- Report templates library
- Scheduled report generation
- Email delivery
- Report comparison
- Version control
- Collaborative editing
- Real-time preview
- Advanced customization
- Multi-language support
- Cloud storage integration

## Support

For issues or questions:
- Check documentation
- Review API reference
- Contact support team
- Submit bug reports
- Request features

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- Six report types
- Five output formats
- Custom sections support
- Branding options
- Report history
- Download and preview
