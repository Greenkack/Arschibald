# Data API Endpoints Documentation

## Overview

This document describes the REST API endpoints for managing universal data with dynamic keys and PDF byte generation capabilities.

**Task:** 231 - API Endpoints for Dynamic Keys and PDF  
**Requirements:** 14.4, 14.5, 14.10

## Base URL

```
http://localhost:8000/api/v1/data
```

## Endpoints

### 1. Get PDF by Dynamic Key

Retrieve PDF bytes for a record using its dynamic key.

**Endpoint:** `GET /api/v1/data/pdf/{dynamic_key}`

**Parameters:**
- `dynamic_key` (path, required): The dynamic key of the record

**Response:**
- Content-Type: `application/pdf`
- Binary PDF data

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/data/pdf/SOL_20231116_143052_a1b2c3d4" \
  --output report.pdf
```

**Status Codes:**
- `200 OK`: PDF retrieved successfully
- `400 Bad Request`: Invalid key format
- `404 Not Found`: Record or PDF not found

---

### 2. Generate PDF

Generate PDF bytes for a specific record.

**Endpoint:** `POST /api/v1/data/generate-pdf`

**Query Parameters:**
- `record_id` (required): ID of the record to generate PDF for

**Request Body:**
```json
{
  "title": "Solar Calculation Report",
  "author": "Solar Calculator Pro",
  "subject": "PV System Analysis",
  "keywords": ["solar", "pv", "calculation"],
  "include_base64": false
}
```

**Response:**
```json
{
  "success": true,
  "size_bytes": 52428,
  "message": "PDF generated successfully",
  "pdf_base64": "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAwIG9iago8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+PgplbmRvYmoKMyAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3hbMCAwIDU5NSA4NDJdL1BhcmVudCAyIDAgUi9SZXNvdXJjZXM8PC9Gb250PDwvRjEgNCAwIFI+Pj4+L0NvbnRlbnRzIDUgMCBSPj4KZW5kb2JqCjQgMCBvYmoKPDwvVHlwZS9Gb250L1N1YnR5cGUvVHlwZTEvQmFzZUZvbnQvSGVsdmV0aWNhPj4KZW5kb2JqCjUgMCBvYmoKPDwvTGVuZ3RoIDQ0Pj4Kc3RyZWFtCkJUCi9GMSA0OCBUZgoxMDAgNzAwIFRkCihIZWxsbyBXb3JsZCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwMDA2NiAwMDAwMCBuIAowMDAwMDAwMTI1IDAwMDAwIG4gCjAwMDAwMDAyNDQgMDAwMDAgbiAKMDAwMDAwMDMxNyAwMDAwMCBuIAp0cmFpbGVyCjw8L1NpemUgNi9Sb290IDEgMCBSPj4Kc3RhcnR4cmVmCjQxMAolJUVPRgo="
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/data/generate-pdf?record_id=123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Report",
    "author": "Test User",
    "include_base64": true
  }'
```

**Status Codes:**
- `200 OK`: PDF generated successfully
- `404 Not Found`: Record not found
- `500 Internal Server Error`: PDF generation failed

---

### 3. Get Data by Key

Retrieve record data using its dynamic key.

**Endpoint:** `GET /api/v1/data/by-key/{key}`

**Parameters:**
- `key` (path, required): Dynamic key to lookup

**Query Parameters:**
- `include_pdf` (optional, default: false): Include PDF bytes in response
- `formatted` (optional, default: true): Return formatted data
- `locale` (optional, default: "de-DE"): Locale for formatting

**Response:**
```json
{
  "id": 123,
  "data_type": "solar_calculation",
  "content": {
    "system_size": "10,50",
    "annual_production": "12.000,00",
    "cost": "15.000,00"
  },
  "dynamic_key": "SOL_20231116_143052_a1b2c3d4",
  "created_at": "2023-11-16T14:30:52",
  "pdf_bytes": "JVBERi0xLjQK...",
  "pdf_size_bytes": 52428
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/data/by-key/SOL_20231116_143052_a1b2c3d4?include_pdf=true&formatted=true"
```

**Status Codes:**
- `200 OK`: Data retrieved successfully
- `400 Bad Request`: Invalid key format
- `404 Not Found`: Record not found

---

### 4. Bulk Generate PDF

Generate PDF bytes for multiple records in bulk.

**Endpoint:** `POST /api/v1/data/bulk-pdf`

**Request Body:**
```json
{
  "record_ids": [1, 2, 3, 4, 5],
  "batch_size": 100,
  "metadata": {
    "title": "Bulk Report",
    "author": "Solar Calculator Pro",
    "subject": "Bulk Generation",
    "keywords": ["bulk", "report"]
  }
}
```

**Response:**
```json
{
  "total_records": 5,
  "generated": 5,
  "failed": 0,
  "success_rate": 100.0,
  "errors": []
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/data/bulk-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "record_ids": [1, 2, 3, 4, 5],
    "batch_size": 2,
    "metadata": {
      "title": "Bulk Test Report"
    }
  }'
```

**Status Codes:**
- `200 OK`: Bulk generation completed
- `404 Not Found`: No records found
- `500 Internal Server Error`: Bulk generation failed

---

### 5. Search Keys

Search for dynamic keys with filtering and pagination.

**Endpoint:** `GET /api/v1/data/keys/search`

**Query Parameters:**
- `prefix` (optional): Filter by key prefix (e.g., 'SOL', 'PRJ', 'CUS')
- `pattern` (optional): Search pattern (supports SQL LIKE wildcards)
- `limit` (optional, default: 100): Maximum number of results (1-1000)
- `offset` (optional, default: 0): Offset for pagination

**Response:**
```json
{
  "keys": [
    "SOL_20231116_143052_a1b2c3d4",
    "SOL_20231116_144523_b2c3d4e5",
    "SOL_20231116_145612_c3d4e5f6"
  ],
  "total": 150,
  "limit": 100,
  "offset": 0
}
```

**Examples:**
```bash
# Search all keys
curl -X GET "http://localhost:8000/api/v1/data/keys/search"

# Search by prefix
curl -X GET "http://localhost:8000/api/v1/data/keys/search?prefix=SOL&limit=50"

# Search with pattern
curl -X GET "http://localhost:8000/api/v1/data/keys/search?pattern=%2023%&limit=100"

# Pagination
curl -X GET "http://localhost:8000/api/v1/data/keys/search?limit=50&offset=50"
```

**Status Codes:**
- `200 OK`: Search completed successfully
- `400 Bad Request`: Invalid prefix or parameters

---

### 6. Get Key Statistics

Get statistics about dynamic key usage.

**Endpoint:** `GET /api/v1/data/keys/statistics`

**Response:**
```json
{
  "model": "UniversalDatabaseModel",
  "total_records": 1300,
  "records_with_keys": 1250,
  "records_without_keys": 50,
  "key_coverage_percent": 96.15,
  "keys_by_prefix": {
    "SOL": 450,
    "PRJ": 300,
    "CUS": 200,
    "HP": 150,
    "PDF": 150
  }
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/data/keys/statistics"
```

**Status Codes:**
- `200 OK`: Statistics retrieved successfully

---

### 7. Get PDF Statistics

Get statistics about PDF generation.

**Endpoint:** `GET /api/v1/data/pdf/statistics`

**Response:**
```json
{
  "total_records": 1300,
  "records_with_pdfs": 1100,
  "records_without_pdfs": 200,
  "pdf_coverage_percent": 84.6,
  "total_pdf_size_bytes": 52428800,
  "average_pdf_size_bytes": 47662
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/data/pdf/statistics"
```

**Status Codes:**
- `200 OK`: Statistics retrieved successfully

---

### 8. Delete PDF

Delete PDF bytes for a record by its dynamic key.

**Endpoint:** `DELETE /api/v1/data/pdf/{dynamic_key}`

**Parameters:**
- `dynamic_key` (path, required): Dynamic key of the record

**Response:**
```json
{
  "success": true,
  "message": "PDF deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/data/pdf/SOL_20231116_143052_a1b2c3d4"
```

**Status Codes:**
- `200 OK`: Deletion completed (check success field)
- `400 Bad Request`: Invalid key format
- `404 Not Found`: Record not found

---

### 9. Regenerate PDF

Regenerate PDF bytes for a record by its dynamic key.

**Endpoint:** `POST /api/v1/data/pdf/{dynamic_key}/regenerate`

**Parameters:**
- `dynamic_key` (path, required): Dynamic key of the record

**Request Body:**
```json
{
  "title": "Regenerated Report",
  "author": "Solar Calculator Pro",
  "subject": "Updated Analysis",
  "keywords": ["regenerated", "updated"],
  "include_base64": false
}
```

**Response:**
```json
{
  "success": true,
  "size_bytes": 54321,
  "message": "PDF regenerated successfully",
  "pdf_base64": "JVBERi0xLjQK..."
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/data/pdf/SOL_20231116_143052_a1b2c3d4/regenerate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Report",
    "include_base64": true
  }'
```

**Status Codes:**
- `200 OK`: PDF regenerated successfully
- `400 Bad Request`: Invalid key format
- `404 Not Found`: Record not found
- `500 Internal Server Error`: Regeneration failed

---

## Key Prefixes

The following key prefixes are supported:

| Prefix | Description |
|--------|-------------|
| `USR` | User |
| `PRJ` | Project |
| `CUS` | Customer |
| `SOL` | Solar Calculation |
| `MOD` | Solar Module |
| `INV` | Solar Inverter |
| `BAT` | Solar Battery |
| `HP` | Heat Pump Calculation |
| `HPP` | Heat Pump Product |
| `PMX` | Price Matrix |
| `PRC` | Price Calculation |
| `PRD` | Product |
| `PDF` | PDF Document |
| `TPL` | PDF Template |
| `VIS` | 3D Visualization |
| `PLC` | Module Placement |
| `OFF` | Offer |
| `TSK` | Task |
| `NOT` | Note |
| `EML` | Email |
| `CNT` | Contract |
| `CFG` | Configuration |
| `SET` | Setting |
| `IMG` | Image |
| `DOC` | Document |
| `CHT` | Chart |
| `DAT` | Generic Data |
| `TMP` | Temporary |

## Error Responses

All endpoints return errors in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error codes:
- `400 Bad Request`: Invalid input or parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Rate Limiting

Currently, no rate limiting is applied. This may be added in future versions.

## Authentication

Currently, no authentication is required. Authentication will be added in subsequent tasks.

## Examples

### Complete Workflow Example

```bash
# 1. Create a record (assume ID 123 is returned)

# 2. Generate PDF for the record
curl -X POST "http://localhost:8000/api/v1/data/generate-pdf?record_id=123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Solar Analysis Report",
    "author": "John Doe",
    "subject": "PV System Calculation",
    "keywords": ["solar", "pv", "analysis"],
    "include_base64": false
  }'

# 3. Get the record data with its dynamic key
curl -X GET "http://localhost:8000/api/v1/data/by-key/SOL_20231116_143052_a1b2c3d4?include_pdf=false"

# 4. Download the PDF
curl -X GET "http://localhost:8000/api/v1/data/pdf/SOL_20231116_143052_a1b2c3d4" \
  --output solar_report.pdf

# 5. Search for all solar calculation keys
curl -X GET "http://localhost:8000/api/v1/data/keys/search?prefix=SOL&limit=50"

# 6. Get statistics
curl -X GET "http://localhost:8000/api/v1/data/keys/statistics"
curl -X GET "http://localhost:8000/api/v1/data/pdf/statistics"

# 7. Regenerate PDF with new metadata
curl -X POST "http://localhost:8000/api/v1/data/pdf/SOL_20231116_143052_a1b2c3d4/regenerate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Solar Analysis Report",
    "author": "Jane Smith",
    "include_base64": false
  }'

# 8. Delete PDF if needed
curl -X DELETE "http://localhost:8000/api/v1/data/pdf/SOL_20231116_143052_a1b2c3d4"
```

## Integration with Frontend

### TypeScript Example

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1/data';

// Get PDF by key
async function getPDF(dynamicKey: string): Promise<Blob> {
  const response = await axios.get(`${API_BASE_URL}/pdf/${dynamicKey}`, {
    responseType: 'blob'
  });
  return response.data;
}

// Generate PDF
async function generatePDF(recordId: number, metadata: any): Promise<any> {
  const response = await axios.post(
    `${API_BASE_URL}/generate-pdf?record_id=${recordId}`,
    metadata
  );
  return response.data;
}

// Get data by key
async function getDataByKey(key: string, includePDF: boolean = false): Promise<any> {
  const response = await axios.get(`${API_BASE_URL}/by-key/${key}`, {
    params: { include_pdf: includePDF, formatted: true }
  });
  return response.data;
}

// Search keys
async function searchKeys(prefix?: string, limit: number = 100): Promise<any> {
  const response = await axios.get(`${API_BASE_URL}/keys/search`, {
    params: { prefix, limit }
  });
  return response.data;
}

// Bulk generate PDFs
async function bulkGeneratePDFs(recordIds: number[], batchSize: number = 100): Promise<any> {
  const response = await axios.post(`${API_BASE_URL}/bulk-pdf`, {
    record_ids: recordIds,
    batch_size: batchSize
  });
  return response.data;
}
```

## See Also

- [Dynamic Key System Documentation](DYNAMIC_KEY_SYSTEM.md)
- [PDF Byte Generation Documentation](PDF_BYTE_GENERATION.md)
- [Universal Data Model Documentation](UNIVERSAL_DATA_MODEL.md)
