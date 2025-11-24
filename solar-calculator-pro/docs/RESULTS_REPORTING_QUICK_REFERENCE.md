# Results Reporting - Quick Reference

## Report Types

| Type | Purpose | Best For |
|------|---------|----------|
| **Detailed** | Comprehensive analysis | Technical teams, documentation |
| **Executive** | High-level summary | Management, decision makers |
| **Technical** | Technical specifications | Installation teams, engineers |
| **Financial** | Financial analysis | Investment decisions, planning |
| **Environmental** | Sustainability metrics | Green certifications, compliance |
| **Custom** | User-defined sections | Specific requirements |

## Output Formats

| Format | Use Case | Features |
|--------|----------|----------|
| **PDF** | Distribution, printing | Professional, formatted |
| **HTML** | Web viewing | Interactive, shareable |
| **JSON** | API integration | Machine-readable |
| **Excel** | Data analysis | Editable, calculations |
| **CSV** | Data exchange | Simple, universal |

## Quick Start

### Generate Report
```bash
curl -X POST http://localhost:8000/api/v1/reports/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "project_id": 1,
    "report_type": "detailed",
    "format": "pdf",
    "include_charts": true,
    "include_tables": true,
    "language": "de"
  }'
```

### Download Report
```bash
curl -X GET http://localhost:8000/api/v1/reports/{report_id}/download \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o report.pdf
```

### Get History
```bash
curl -X GET "http://localhost:8000/api/v1/reports/history?project_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Report Content

### Detailed Report
- ✅ Project info & system config
- ✅ Calculation results
- ✅ Energy analysis
- ✅ Financial analysis
- ✅ Environmental impact
- ✅ Technical specs
- ✅ Recommendations
- ✅ Charts & tables

### Executive Summary
- ✅ Key metrics
- ✅ System size & cost
- ✅ Annual savings
- ✅ Payback period
- ✅ ROI percentage
- ✅ CO₂ reduction
- ✅ Highlights
- ✅ Recommendation

### Technical Report
- ✅ System design
- ✅ Component specs
- ✅ Installation requirements
- ✅ Electrical design
- ✅ Mounting system
- ✅ Performance calculations
- ✅ Compliance standards
- ✅ Technical drawings

### Financial Report
- ✅ Investment summary
- ✅ Cost breakdown
- ✅ Revenue projections
- ✅ Cash flow analysis
- ✅ ROI analysis
- ✅ Financing options
- ✅ Tax benefits
- ✅ Sensitivity analysis

### Environmental Report
- ✅ CO₂ emissions avoided
- ✅ Trees equivalent
- ✅ Cars equivalent
- ✅ Renewable energy %
- ✅ Lifecycle analysis
- ✅ Certifications
- ✅ Sustainability metrics

## Common Options

```json
{
  "include_charts": true,      // Include visual charts
  "include_tables": true,      // Include data tables
  "include_raw_data": false,   // Include raw calculation data
  "language": "de",            // Report language (de/en)
  "branding": {                // Custom branding
    "logo_url": "...",
    "company_name": "...",
    "colors": {...}
  }
}
```

## Response Structure

```json
{
  "success": true,
  "report_id": "uuid",
  "metadata": {
    "report_type": "detailed",
    "format": "pdf",
    "generated_at": "2024-01-15T10:30:00Z",
    "file_size": 1024000
  },
  "download_url": "/api/v1/reports/{id}/download",
  "preview_url": "/api/v1/reports/{id}/preview"
}
```

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Verify authentication |
| 404 | Not Found | Check report/project ID |
| 500 | Server Error | Contact support |

## Tips

### Performance
- Use JSON for fastest generation
- PDF takes longer but looks better
- Enable charts only when needed
- Limit table data for large datasets

### Quality
- Use PDF for professional reports
- Include charts for visual impact
- Add branding for consistency
- Choose appropriate report type

### Storage
- Delete old reports regularly
- Archive important reports
- Monitor disk usage
- Use cloud storage for scale

## Keyboard Shortcuts (UI)

| Action | Shortcut |
|--------|----------|
| Generate Report | `Ctrl+G` |
| Download | `Ctrl+D` |
| Preview | `Ctrl+P` |
| Delete | `Del` |
| Refresh History | `F5` |

## Common Workflows

### 1. Quick Executive Summary
```
1. Select project
2. Choose "Executive" type
3. Select PDF format
4. Click Generate
5. Download report
```

### 2. Detailed Technical Documentation
```
1. Select project
2. Choose "Technical" type
3. Enable all charts and tables
4. Add custom branding
5. Generate PDF
6. Archive for records
```

### 3. Financial Analysis for Investor
```
1. Select project
2. Choose "Financial" type
3. Include sensitivity analysis
4. Generate Excel format
5. Share with stakeholders
```

### 4. Environmental Certification
```
1. Select project
2. Choose "Environmental" type
3. Include all metrics
4. Generate PDF
5. Submit for certification
```

## Integration Examples

### React Component
```typescript
const generateReport = async () => {
  const response = await api.post('/reports/generate', {
    project_id: projectId,
    report_type: 'detailed',
    format: 'pdf'
  });
  
  window.open(response.data.download_url);
};
```

### Python Script
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/reports/generate',
    json={'project_id': 1, 'report_type': 'detailed', 'format': 'pdf'},
    headers={'Authorization': f'Bearer {token}'}
)

report_id = response.json()['report_id']
```

## Troubleshooting

### Report Won't Generate
1. Check project data completeness
2. Verify user permissions
3. Check disk space
4. Review error logs

### Download Fails
1. Verify report ID
2. Check file exists
3. Verify permissions
4. Try different browser

### Preview Not Working
1. Ensure HTML format
2. Check browser compatibility
3. Disable popup blockers
4. Clear browser cache

## Support

- 📖 Full Guide: `/docs/RESULTS_REPORTING_GUIDE.md`
- 🔧 API Reference: `/api/v1/docs`
- 💬 Support: support@example.com
- 🐛 Bug Reports: github.com/project/issues
