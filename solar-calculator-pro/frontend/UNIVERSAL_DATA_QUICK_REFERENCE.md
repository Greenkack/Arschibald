# Universal Data Service - Quick Reference

Quick reference for common operations with the Universal Data Service.

## Import

```typescript
import { universalDataService } from '../services/UniversalDataService';
import { useUniversalData, useDataByKey } from '../hooks/useUniversalData';
```

## Common Operations

### Fetch Data with PDF

```typescript
const { data, downloadPDF, formattedData } = useUniversalData('/api/endpoint');
```

### Fetch by Key

```typescript
const { data, downloadPDF } = useDataByKey('SOL_20231116_143052_a1b2c3d4');
```

### Format Numbers

```typescript
const formatted = universalDataService.formatAllNumbers(data);
// 15000.50 → "15.000,50"
```

### Download PDF

```typescript
await universalDataService.downloadPDF(data, { filename: 'doc.pdf' });
```

### Real-time Sync

```typescript
useDataSync(key, (data) => console.log('Updated:', data));
```

### Bulk PDF

```typescript
const { generateBulk, downloadAll } = useBulkPDF();
await generateBulk('/api/bulk', dataList);
await downloadAll();
```

### Export Data

```typescript
const { exportJSON, exportCSV } = useDataExport();
await exportJSON(data, 'data.json');
await exportCSV(data, 'data.csv');
```

### Cache Management

```typescript
const { stats, clear } = useDataCache();
clear(); // Clear all
clear(key); // Clear specific key
```

### Search

```typescript
const results = await universalDataService.searchByKey('SOL_*');
const byPrefix = await universalDataService.getByPrefix('SOL');
```

## Hook Returns

### useUniversalData
- `data` - Fetched data
- `loading` - Loading state
- `error` - Error object
- `refetch` - Refetch function
- `downloadPDF` - Download function
- `formattedData` - German-formatted data
- `dynamicKey` - Dynamic key

### useBulkPDF
- `generateBulk` - Generate function
- `downloadAll` - Download all function
- `loading` - Loading state
- `error` - Error object
- `results` - Generated PDFs

### useDataExport
- `exportJSON` - Export as JSON
- `exportCSV` - Export as CSV
- `loading` - Loading state
- `error` - Error object

### useDataCache
- `stats` - Cache statistics
- `clear` - Clear function
- `refresh` - Refresh stats

## Configuration

```typescript
new UniversalDataService({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
  enableCaching: true,
  cacheExpiration: 5 * 60 * 1000
});
```

## German Number Format

Input: `1234.56`
Output: `"1.234,56"`

Works recursively on:
- Numbers
- Arrays
- Nested objects
- All data types

## Dynamic Keys

Format: `PREFIX_TIMESTAMP_UUID_ID`

Examples:
- `SOL_20231116_143052_a1b2c3d4` - Solar calculation
- `HP_20231116_143052_b2c3d4e5` - Heat pump
- `PDF_20231116_143052_c3d4e5f6` - PDF document

## Requirements

✅ **14.3**: German formatting and bidirectional conversion
✅ **14.10**: Universal data access with keys and PDF bytes
