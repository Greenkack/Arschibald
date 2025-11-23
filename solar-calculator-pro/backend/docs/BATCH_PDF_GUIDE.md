# Multi-PDF Batch Generation Guide

## Overview

The Multi-PDF Batch Generation system allows you to generate multiple PDF offers for different companies with a single request. This is the **heart of the application** - enabling you to create personalized offers for multiple companies simultaneously.

## Concept

**One Click → Multiple Company PDFs**

- **Example**: Select 8 companies → Generate 8 PDFs with one click
- **Same Data**: All offers use the same analysis data (roof area, consumption, etc.)
- **Different Details**: Each offer has:
  - Company-specific branding (logo, colors, contact info)
  - Rotated products (different PV modules, inverters, batteries)
  - Increased prices (each offer progressively more expensive)

## Key Features

### 1. Parallel Generation
- PDFs are generated in parallel using a thread pool
- Configurable number of workers (default: 4)
- Significantly faster than sequential generation

### 2. Progress Tracking
- Real-time progress updates
- Track completed vs. total PDFs
- Current company being processed
- Percentage completion

### 3. Product Rotation
- Each offer gets different products
- Avoids repeating brands across offers
- Maintains compatibility and quality

### 4. Automatic Price Increase
- Each subsequent offer is more expensive
- Configurable increase percentage (default: 7%)
- Applied on top of product-based pricing

### 5. Error Handling
- Per-company error handling
- Failed PDFs don't stop the batch
- Detailed error messages for each failure

### 6. Batch Results
- Success/failure count
- Individual PDF results
- ZIP archive with all PDFs
- Individual PDF downloads

## Usage

### Basic Batch Generation

```python
from backend.services.batch_pdf_service import BatchPDFService, BatchPDFRequest

# Create request
request = BatchPDFRequest(
    company_ids=[1, 2, 3, 4, 5],
    analysis_data={
        "roof_area": 50.0,
        "roof_type": "gable",
        "module_count": 30,
        "annual_consumption": 4500.0,
        "base_price": 16999.00,
        "products": {
            "pv_module": "Trina Solar 400W",
            "inverter": "Fronius Symo",
            "battery": "BYD Battery-Box"
        }
    },
    template_type="standard_pv",
    options={
        "price_increase_percentage": 7.0
    }
)

# Generate batch
result = await service.generate_batch(request)

# Check results
print(f"Successful: {result.successful}")
print(f"Failed: {result.failed}")
print(f"ZIP: {result.zip_path}")
```

### API Endpoints

#### Generate Batch (Synchronous)

```http
POST /api/v1/batch-pdf/generate
Content-Type: application/json

{
  "company_ids": [1, 2, 3, 4, 5],
  "analysis_data": {
    "roof_area": 50.0,
    "module_count": 30,
    "base_price": 16999.00
  },
  "template_type": "standard_pv",
  "options": {
    "price_increase_percentage": 7.0
  }
}
```

**Response:**
```json
{
  "batch_id": "batch_20240115_143022",
  "total_companies": 5,
  "successful": 5,
  "failed": 0,
  "results": [
    {
      "company_id": 1,
      "company_name": "Solar Solutions GmbH",
      "success": true,
      "pdf_path": "/output/batch_20240115_143022/Solar_Solutions_GmbH_offer_1.pdf",
      "generation_time": 1.23,
      "file_size": 245678
    }
  ],
  "total_time": 3.45,
  "zip_path": "/output/batch_20240115_143022/batch_20240115_143022_all_offers.zip",
  "zip_size": 1234567
}
```

#### Generate Batch (Asynchronous)

```http
POST /api/v1/batch-pdf/generate-async
Content-Type: application/json

{
  "company_ids": [1, 2, 3, 4, 5],
  "analysis_data": {...},
  "template_type": "standard_pv"
}
```

**Response:**
```json
{
  "batch_id": "batch_20240115_143022",
  "status": "queued",
  "total_companies": 5,
  "message": "Batch PDF generation started"
}
```

#### Get Progress

```http
GET /api/v1/batch-pdf/progress/{batch_id}
```

**Response:**
```json
{
  "batch_id": "batch_20240115_143022",
  "total": 5,
  "completed": 3,
  "current_company": "Green Energy AG",
  "percentage": 60.0,
  "status": "processing"
}
```

#### Download ZIP

```http
GET /api/v1/batch-pdf/download/zip/{batch_id}
```

Returns ZIP file with all generated PDFs.

#### Download Single PDF

```http
GET /api/v1/batch-pdf/download/single/{batch_id}/{company_id}
```

Returns individual PDF for specified company.

## Product Rotation

### How It Works

Each offer in the batch gets different products to avoid repetition:

**Offer 1:**
- PV Module: Trina Solar 400W
- Inverter: Fronius Symo
- Battery: BYD Battery-Box

**Offer 2:**
- PV Module: JA Solar 410W (different brand!)
- Inverter: SMA Sunny Tripower (different brand!)
- Battery: Tesla Powerwall (different brand!)

**Offer 3:**
- PV Module: Longi 420W (different brand!)
- Inverter: Huawei SUN2000 (different brand!)
- Battery: Sonnen Batterie (different brand!)

### Implementation

```python
class ProductRotationService:
    def rotate_products(self, original_products, offer_index):
        """
        Rotate products for each offer
        
        Args:
            original_products: Original product selection
            offer_index: Index of current offer (0-based)
            
        Returns:
            Dict with rotated products
        """
        # Get available products from database
        available_modules = self.get_available_modules()
        available_inverters = self.get_available_inverters()
        available_batteries = self.get_available_batteries()
        
        # Rotate based on index
        return {
            "pv_module": available_modules[offer_index % len(available_modules)],
            "inverter": available_inverters[offer_index % len(available_inverters)],
            "battery": available_batteries[offer_index % len(available_batteries)]
        }
```

## Price Increase

### How It Works

Each subsequent offer is more expensive than the previous one:

**Base Price:** 16.999,00 €

**With 7% Increase:**
- Offer 1: 16.999,00 € (base price)
- Offer 2: 18.188,93 € (+7%)
- Offer 3: 19.462,15 € (+14.5%)
- Offer 4: 20.824,50 € (+22.5%)
- Offer 5: 22.282,22 € (+31%)

### Formula

```
price = base_price × (1 + (increase_percentage / 100) × offer_index)
```

### Implementation

```python
class PriceIncreaseService:
    def apply_increase(self, base_price, offer_index, increase_percentage):
        """
        Apply price increase for each offer
        
        Args:
            base_price: Base price from calculator
            offer_index: Index of current offer (0-based)
            increase_percentage: Percentage increase per offer
            
        Returns:
            Increased price
        """
        multiplier = 1 + (increase_percentage / 100) * offer_index
        return base_price * multiplier
```

## Performance

### Parallel vs Sequential

**Sequential (1 worker):**
- 8 PDFs × 2 seconds each = 16 seconds total

**Parallel (4 workers):**
- 8 PDFs ÷ 4 workers × 2 seconds = 4 seconds total
- **4x faster!**

### Optimization Tips

1. **Adjust Worker Count**
   ```python
   service = BatchPDFService(
       ...,
       max_workers=8  # More workers = faster
   )
   ```

2. **Batch Size**
   - Optimal: 5-10 companies per batch
   - Maximum: 50 companies per batch

3. **Caching**
   - Cache company data
   - Cache product data
   - Cache templates

## Error Handling

### Per-Company Errors

If one company fails, others continue:

```json
{
  "total_companies": 5,
  "successful": 4,
  "failed": 1,
  "results": [
    {
      "company_id": 3,
      "company_name": "Eco Power Systems",
      "success": false,
      "error_message": "Company logo not found"
    }
  ]
}
```

### Common Errors

1. **Company Not Found**
   - Error: "Company {id} not found"
   - Solution: Verify company exists in database

2. **Template Missing**
   - Error: "Template {type} not found"
   - Solution: Ensure template files exist

3. **Product Unavailable**
   - Error: "No products available for rotation"
   - Solution: Add more products to database

4. **Disk Space**
   - Error: "No space left on device"
   - Solution: Clean up old batches

## Best Practices

### 1. Cleanup Old Batches

```python
# Cleanup after 24 hours
service.cleanup_batch(batch_id, keep_zip=True)
```

### 2. Monitor Progress

```python
# Poll progress every second
while True:
    progress = service.get_progress(batch_id)
    if progress.status == "completed":
        break
    await asyncio.sleep(1)
```

### 3. Handle Failures

```python
result = await service.generate_batch(request)

if result.failed > 0:
    # Log failures
    for r in result.results:
        if not r.success:
            logger.error(f"Failed: {r.company_name} - {r.error_message}")
    
    # Retry failed companies
    failed_ids = [r.company_id for r in result.results if not r.success]
    retry_request = BatchPDFRequest(
        company_ids=failed_ids,
        analysis_data=request.analysis_data,
        template_type=request.template_type
    )
    retry_result = await service.generate_batch(retry_request)
```

### 4. Validate Input

```python
# Validate before generation
if not request.company_ids:
    raise ValueError("No companies selected")

if len(request.company_ids) > 50:
    raise ValueError("Maximum 50 companies per batch")

if not request.analysis_data.get("base_price"):
    raise ValueError("Base price required")
```

## Frontend Integration

### React Component

```typescript
import { useState } from 'react';
import { Button } from 'primereact/button';
import { ProgressBar } from 'primereact/progressbar';

export const BatchPDFGenerator = () => {
  const [progress, setProgress] = useState(0);
  const [batchId, setBatchId] = useState(null);
  
  const generateBatch = async () => {
    // Start generation
    const response = await fetch('/api/v1/batch-pdf/generate-async', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_ids: [1, 2, 3, 4, 5],
        analysis_data: {...},
        template_type: 'standard_pv'
      })
    });
    
    const { batch_id } = await response.json();
    setBatchId(batch_id);
    
    // Poll progress
    const interval = setInterval(async () => {
      const progressResponse = await fetch(
        `/api/v1/batch-pdf/progress/${batch_id}`
      );
      const progressData = await progressResponse.json();
      
      setProgress(progressData.percentage);
      
      if (progressData.status === 'completed') {
        clearInterval(interval);
        // Download ZIP
        window.location.href = `/api/v1/batch-pdf/download/zip/${batch_id}`;
      }
    }, 1000);
  };
  
  return (
    <div>
      <Button 
        label="Generate PDFs" 
        onClick={generateBatch}
        icon="pi pi-file-pdf"
      />
      
      {progress > 0 && (
        <ProgressBar value={progress} />
      )}
    </div>
  );
};
```

## Troubleshooting

### Issue: Slow Generation

**Symptoms:**
- Batch takes too long
- Progress stalls

**Solutions:**
1. Increase worker count
2. Optimize PDF templates
3. Cache company/product data
4. Use faster storage (SSD)

### Issue: Memory Usage

**Symptoms:**
- High memory consumption
- Out of memory errors

**Solutions:**
1. Reduce worker count
2. Process smaller batches
3. Clean up completed batches
4. Stream PDF generation

### Issue: Failed PDFs

**Symptoms:**
- Some PDFs fail to generate
- Error messages in results

**Solutions:**
1. Check error messages
2. Verify company data
3. Validate templates
4. Check disk space
5. Review logs

## Examples

See `demo_batch_pdf.py` for complete examples:

```bash
python backend/demo_batch_pdf.py
```

## API Reference

See `BATCH_PDF_QUICK_REFERENCE.md` for quick API reference.

## Related Documentation

- [Product Rotation Guide](PRODUCT_ROTATION_GUIDE.md)
- [Price Increase Guide](PRICE_INCREASE_GUIDE.md)
- [Company Database Guide](COMPANY_DATABASE_GUIDE.md)
- [PDF Generation Guide](PDF_GENERATION_GUIDE.md)
