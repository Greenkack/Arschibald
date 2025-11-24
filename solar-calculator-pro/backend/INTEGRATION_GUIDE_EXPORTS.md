# Results Export System - Integration Guide

## Quick Integration

### 1. Add to Main Application

```python
# backend/main.py

from fastapi import FastAPI
from api.v1 import exports

app = FastAPI()

# Include export router
app.include_router(
    exports.router,
    prefix="/api/v1",
    tags=["exports"]
)
```

### 2. Frontend Integration

```typescript
// frontend/src/services/exportService.ts

export class ExportService {
  private baseUrl = '/api/v1/exports';

  async createExport(
    resultId: number,
    format: 'pdf' | 'excel' | 'csv' | 'json' | 'xml',
    options: Record<string, any> = {}
  ) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ result_id: resultId, format, options })
    });
    return response.json();
  }

  async downloadExport(exportId: string) {
    window.open(`${this.baseUrl}/${exportId}/download`, '_blank');
  }

  async batchExport(
    resultIds: number[],
    format: string,
    options: Record<string, any> = {}
  ) {
    const response = await fetch(`${this.baseUrl}/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ result_ids: resultIds, format, options })
    });
    return response.json();
  }
}

export const exportService = new ExportService();
```

### 3. React Component Example

```typescript
// frontend/src/components/ExportButton.tsx

import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { exportService } from '../services/exportService';

interface ExportButtonProps {
  resultId: number;
}

export const ExportButton: React.FC<ExportButtonProps> = ({ resultId }) => {
  const [format, setFormat] = useState('pdf');
  const [loading, setLoading] = useState(false);

  const formats = [
    { label: 'PDF', value: 'pdf' },
    { label: 'Excel', value: 'excel' },
    { label: 'CSV', value: 'csv' },
    { label: 'JSON', value: 'json' },
    { label: 'XML', value: 'xml' }
  ];

  const handleExport = async () => {
    setLoading(true);
    try {
      const response = await exportService.createExport(resultId, format);
      await exportService.downloadExport(response.export_id);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="export-controls">
      <Dropdown
        value={format}
        options={formats}
        onChange={(e) => setFormat(e.value)}
        placeholder="Select Format"
      />
      <Button
        label="Export"
        icon="pi pi-download"
        onClick={handleExport}
        loading={loading}
      />
    </div>
  );
};
```

### 4. Advanced Export Dialog

```typescript
// frontend/src/components/ExportDialog.tsx

import React, { useState } from 'react';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { Checkbox } from 'primereact/checkbox';
import { RadioButton } from 'primereact/radiobutton';

interface ExportDialogProps {
  visible: boolean;
  onHide: () => void;
  resultId: number;
}

export const ExportDialog: React.FC<ExportDialogProps> = ({
  visible,
  onHide,
  resultId
}) => {
  const [format, setFormat] = useState('pdf');
  const [options, setOptions] = useState({
    include_charts: true,
    include_tables: true,
    include_summary: true,
    page_size: 'A4',
    orientation: 'portrait'
  });

  const handleExport = async () => {
    const response = await exportService.createExport(
      resultId,
      format,
      options
    );
    await exportService.downloadExport(response.export_id);
    onHide();
  };

  return (
    <Dialog
      header="Export Result"
      visible={visible}
      onHide={onHide}
      style={{ width: '500px' }}
    >
      <div className="export-options">
        <h3>Format</h3>
        <div className="format-options">
          {['pdf', 'excel', 'csv', 'json', 'xml'].map(fmt => (
            <div key={fmt}>
              <RadioButton
                inputId={fmt}
                value={fmt}
                onChange={(e) => setFormat(e.value)}
                checked={format === fmt}
              />
              <label htmlFor={fmt}>{fmt.toUpperCase()}</label>
            </div>
          ))}
        </div>

        {format === 'pdf' && (
          <>
            <h3>PDF Options</h3>
            <div className="checkbox-group">
              <Checkbox
                inputId="charts"
                checked={options.include_charts}
                onChange={(e) => setOptions({
                  ...options,
                  include_charts: e.checked
                })}
              />
              <label htmlFor="charts">Include Charts</label>
            </div>
            <div className="checkbox-group">
              <Checkbox
                inputId="tables"
                checked={options.include_tables}
                onChange={(e) => setOptions({
                  ...options,
                  include_tables: e.checked
                })}
              />
              <label htmlFor="tables">Include Tables</label>
            </div>
          </>
        )}

        <div className="dialog-footer">
          <Button
            label="Cancel"
            icon="pi pi-times"
            onClick={onHide}
            className="p-button-text"
          />
          <Button
            label="Export"
            icon="pi pi-download"
            onClick={handleExport}
          />
        </div>
      </div>
    </Dialog>
  );
};
```

## Database Integration

### Add Export History Table

```python
# backend/models/database_models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class ExportHistory(Base):
    __tablename__ = "export_history"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("results.id"))
    format = Column(String)
    file_name = Column(String)
    file_size = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    downloaded_at = Column(DateTime, nullable=True)
    download_count = Column(Integer, default=0)

    result = relationship("Result", back_populates="exports")
    user = relationship("User", back_populates="exports")
```

### Migration Script

```python
# backend/migrations/add_export_history.py

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'export_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('result_id', sa.Integer(), nullable=False),
        sa.Column('format', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('downloaded_at', sa.DateTime(), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['result_id'], ['results.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_export_history_result_id', 'export_history', ['result_id'])
    op.create_index('ix_export_history_user_id', 'export_history', ['user_id'])

def downgrade():
    op.drop_index('ix_export_history_user_id')
    op.drop_index('ix_export_history_result_id')
    op.drop_table('export_history')
```

## Background Tasks

### Scheduled Cleanup

```python
# backend/tasks/export_cleanup.py

from apscheduler.schedulers.background import BackgroundScheduler
from services.export_service import ExportService

def setup_export_cleanup():
    scheduler = BackgroundScheduler()
    export_service = ExportService()
    
    # Run cleanup every hour
    scheduler.add_job(
        func=export_service.cleanup_expired_exports,
        trigger='interval',
        hours=1
    )
    
    scheduler.start()
    return scheduler
```

### Async Export Generation

```python
# backend/api/v1/exports.py

from fastapi import BackgroundTasks

@router.post("/async")
async def create_async_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create export asynchronously"""
    
    # Queue export generation
    background_tasks.add_task(
        generate_export_async,
        request,
        db
    )
    
    return {
        "message": "Export queued",
        "status": "processing"
    }

async def generate_export_async(request: ExportRequest, db: Session):
    """Generate export in background"""
    result_data = await fetch_result_data(request.result_id, db)
    export_response = await export_service.export_result(request, result_data)
    
    # Optionally send notification
    await notify_user(export_response)
```

## Monitoring

### Export Metrics

```python
# backend/services/export_metrics.py

from prometheus_client import Counter, Histogram

export_counter = Counter(
    'exports_total',
    'Total number of exports',
    ['format', 'status']
)

export_duration = Histogram(
    'export_duration_seconds',
    'Export generation duration',
    ['format']
)

def track_export(format: str, duration: float, success: bool):
    status = 'success' if success else 'failure'
    export_counter.labels(format=format, status=status).inc()
    export_duration.labels(format=format).observe(duration)
```

## Testing

### Unit Tests

```python
# backend/tests/test_export_service.py

import pytest
from services.export_service import ExportService
from models.export_schemas import ExportRequest

@pytest.fixture
def export_service():
    return ExportService()

@pytest.fixture
def sample_data():
    return {
        "id": 123,
        "title": "Test Result",
        "summary": {"key": "value"}
    }

@pytest.mark.asyncio
async def test_pdf_export(export_service, sample_data):
    request = ExportRequest(
        result_id=123,
        format='pdf',
        options={}
    )
    response = await export_service.export_result(request, sample_data)
    
    assert response.format == 'pdf'
    assert response.file_name.endswith('.pdf')
    assert response.file_size > 0

@pytest.mark.asyncio
async def test_german_formatting(export_service, sample_data):
    request = ExportRequest(
        result_id=123,
        format='csv',
        options={
            'decimal_separator': ',',
            'thousands_separator': '.'
        }
    )
    response = await export_service.export_result(request, sample_data)
    
    # Verify German formatting in file
    file_path = export_service.get_export_file(response.export_id)
    with open(file_path, 'r') as f:
        content = f.read()
        assert ',' in content  # Decimal separator
        assert '.' in content  # Thousands separator
```

### Integration Tests

```python
# backend/tests/test_export_api.py

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_export():
    response = client.post(
        "/api/v1/exports/",
        json={
            "result_id": 123,
            "format": "pdf",
            "options": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert 'export_id' in data
    assert 'download_url' in data

def test_download_export():
    # Create export first
    create_response = client.post(
        "/api/v1/exports/",
        json={"result_id": 123, "format": "pdf", "options": {}}
    )
    export_id = create_response.json()['export_id']
    
    # Download
    download_response = client.get(f"/api/v1/exports/{export_id}/download")
    assert download_response.status_code == 200
    assert download_response.headers['content-type'] == 'application/octet-stream'
```

## Deployment

### Environment Variables

```bash
# .env

# Export settings
EXPORT_DIR=exports
EXPORT_TTL_HOURS=24
MAX_EXPORT_SIZE_MB=50

# Cleanup schedule
CLEANUP_INTERVAL_HOURS=1
```

### Docker Configuration

```dockerfile
# Dockerfile

FROM python:3.10

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Create export directory
RUN mkdir -p exports

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Best Practices

1. **Always validate result_id** before export
2. **Use appropriate format** for use case
3. **Enable German formatting** for all exports
4. **Handle expired exports** gracefully
5. **Monitor export metrics** for performance
6. **Implement rate limiting** for API
7. **Use batch export** for multiple results
8. **Clean up old exports** regularly

## Troubleshooting

### Common Issues

1. **Export not found (404)**
   - Check if export has expired (24h)
   - Verify export_id is correct

2. **Large file sizes**
   - Disable charts in PDF/Excel
   - Use CSV for simple data

3. **Formatting issues**
   - Verify German options are set
   - Check decimal/thousands separators

4. **Performance issues**
   - Use batch export
   - Reduce included data
   - Implement caching

## Support

- Full Guide: `docs/RESULTS_EXPORT_GUIDE.md`
- Quick Reference: `docs/RESULTS_EXPORT_QUICK_REFERENCE.md`
- Demo: `python backend/demo_results_export.py`
- API Docs: `/api/v1/docs`
