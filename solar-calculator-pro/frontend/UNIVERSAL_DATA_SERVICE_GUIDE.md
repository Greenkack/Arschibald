# Universal Data Service - Frontend Guide

Complete guide for using the Universal Data Service in the frontend application.

## Overview

The Universal Data Service provides a comprehensive solution for managing data with:
- **PDF Byte Generation**: Fetch data with PDF bytes ready for download
- **German Number Formatting**: Recursive formatting of all numbers to German format (1.234,56)
- **Dynamic Keys**: Unique key-based data access and management
- **Caching**: Intelligent caching with automatic expiration
- **Real-time Sync**: Subscribe to data changes with callbacks
- **Bulk Operations**: Generate and download multiple PDFs
- **Data Export**: Export data as JSON or CSV with formatted numbers

## Installation

The service is already included in the project. Import it in your components:

```typescript
import { universalDataService } from '../services/UniversalDataService';
import { useUniversalData, useDataByKey } from '../hooks/useUniversalData';
```

## Basic Usage

### 1. Fetch Data with PDF Bytes

```typescript
import { useUniversalData } from '../hooks/useUniversalData';

function MyComponent() {
  const { data, loading, error, downloadPDF, formattedData, dynamicKey } = useUniversalData(
    '/api/solar/calculations/123',
    {},
    { formatNumbers: true, decimals: 2 }
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h2>Dynamic Key: {dynamicKey}</h2>
      <pre>{JSON.stringify(formattedData, null, 2)}</pre>
      <button onClick={() => downloadPDF('calculation.pdf')}>
        Download PDF
      </button>
    </div>
  );
}
```

### 2. Fetch by Dynamic Key

```typescript
import { useDataByKey } from '../hooks/useUniversalData';

function KeyLookup() {
  const [key, setKey] = useState('SOL_20231116_143052_a1b2c3d4');
  const { data, loading, downloadPDF } = useDataByKey(key);

  return (
    <div>
      <input value={key} onChange={(e) => setKey(e.target.value)} />
      {data && (
        <>
          <pre>{JSON.stringify(data, null, 2)}</pre>
          <button onClick={() => downloadPDF()}>Download PDF</button>
        </>
      )}
    </div>
  );
}
```

### 3. Format All Numbers Recursively

```typescript
import { universalDataService } from '../services/UniversalDataService';

const data = {
  cost: 15000.50,
  systemSize: 10.5,
  nested: {
    value: 1234.56,
    deepNested: {
      amount: 5555.55
    }
  },
  array: [100.11, 200.22, 300.33]
};

// Format all numbers to German format
const formatted = universalDataService.formatAllNumbers(data);

console.log(formatted);
// Output:
// {
//   cost: "15.000,50",
//   systemSize: "10,50",
//   nested: {
//     value: "1.234,56",
//     deepNested: {
//       amount: "5.555,55"
//     }
//   },
//   array: ["100,11", "200,22", "300,33"]
// }
```

### 4. Download PDF

```typescript
import { universalDataService } from '../services/UniversalDataService';

// Download from data object
async function downloadFromData(data) {
  await universalDataService.downloadPDF(data, {
    filename: 'my-document.pdf',
    openInNewTab: false
  });
}

// Download by dynamic key
async function downloadByKey(key) {
  await universalDataService.downloadPDF(key, {
    filename: 'document.pdf'
  });
}

// Open in new tab instead of downloading
async function openInTab(data) {
  await universalDataService.downloadPDF(data, {
    openInNewTab: true
  });
}
```

## Advanced Features

### Real-time Data Synchronization

Subscribe to data changes for a specific key:

```typescript
import { useDataSync } from '../hooks/useUniversalData';

function SyncedComponent() {
  const [syncedData, setSyncedData] = useState(null);
  const key = 'SOL_20231116_143052_a1b2c3d4';

  useDataSync(key, (data) => {
    console.log('Data updated:', data);
    setSyncedData(data);
  });

  return <div>{syncedData && <pre>{JSON.stringify(syncedData, null, 2)}</pre>}</div>;
}
```

### Bulk PDF Generation

Generate multiple PDFs at once:

```typescript
import { useBulkPDF } from '../hooks/useUniversalData';

function BulkGenerator() {
  const { generateBulk, downloadAll, loading, results } = useBulkPDF();

  const handleGenerate = async () => {
    const dataList = [
      { id: 1, name: 'Project A', cost: 15000 },
      { id: 2, name: 'Project B', cost: 20000 },
      { id: 3, name: 'Project C', cost: 18000 }
    ];

    await generateBulk('/api/pdf/bulk-generate', dataList);
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={loading}>
        Generate Bulk PDFs
      </button>
      {results.length > 0 && (
        <button onClick={downloadAll}>Download All ({results.length})</button>
      )}
    </div>
  );
}
```

### Data Export

Export data as JSON or CSV with German formatting:

```typescript
import { useDataExport } from '../hooks/useUniversalData';

function DataExporter() {
  const { exportJSON, exportCSV, loading } = useDataExport();

  const data = [
    { id: 1, name: 'System A', cost: 15000.50, size: 10.5 },
    { id: 2, name: 'System B', cost: 20000.75, size: 15.2 }
  ];

  return (
    <div>
      <button onClick={() => exportJSON(data, 'systems.json')} disabled={loading}>
        Export JSON
      </button>
      <button onClick={() => exportCSV(data, 'systems.csv')} disabled={loading}>
        Export CSV
      </button>
    </div>
  );
}
```

### Cache Management

Manage the data cache:

```typescript
import { useDataCache } from '../hooks/useUniversalData';

function CacheManager() {
  const { stats, clear, refresh } = useDataCache();

  return (
    <div>
      <p>Cache Size: {stats.size} entries</p>
      <p>Oldest: {stats.oldestEntry ? new Date(stats.oldestEntry).toLocaleString() : 'N/A'}</p>
      <button onClick={refresh}>Refresh Stats</button>
      <button onClick={() => clear()}>Clear All Cache</button>
      
      {stats.keys.map(key => (
        <div key={key}>
          {key}
          <button onClick={() => clear(key)}>Clear</button>
        </div>
      ))}
    </div>
  );
}
```

### Search by Key Pattern

Search for data using key patterns:

```typescript
import { universalDataService } from '../services/UniversalDataService';

async function searchData() {
  // Search for all solar calculations
  const results = await universalDataService.searchByKey('SOL_*');
  
  // Search for specific date
  const dateResults = await universalDataService.searchByKey('SOL_20231116_*');
  
  return results;
}
```

### Get by Prefix

Get all data with a specific prefix:

```typescript
import { universalDataService } from '../services/UniversalDataService';

async function getByPrefix() {
  // Get all solar calculations
  const solarData = await universalDataService.getByPrefix('SOL');
  
  // Get all heat pump calculations
  const heatPumpData = await universalDataService.getByPrefix('HP');
  
  return solarData;
}
```

## Configuration

Configure the service when creating an instance:

```typescript
import { UniversalDataService } from '../services/UniversalDataService';

const customService = new UniversalDataService({
  baseURL: 'https://api.example.com/v1',
  timeout: 60000, // 60 seconds
  enableCaching: true,
  cacheExpiration: 10 * 60 * 1000 // 10 minutes
});
```

## API Reference

### UniversalDataService Class

#### Methods

##### `fetchWithPDFBytes<T>(endpoint: string, params?: Record<string, any>): Promise<DataWithPDFBytes<T>>`
Fetch data with PDF bytes from backend.

##### `fetchByKey<T>(key: string): Promise<DataWithPDFBytes<T>>`
Fetch data by dynamic key.

##### `formatAllNumbers(data: any, decimals?: number): any`
Format all numbers in an object recursively to German format.

##### `downloadPDF(data: DataWithPDFBytes | string, options?: DownloadOptions): Promise<void>`
Download PDF from data or dynamic key.

##### `generatePDF(endpoint: string, data: Record<string, any>): Promise<DataWithPDFBytes>`
Generate PDF for data.

##### `bulkGeneratePDF(endpoint: string, dataList: Record<string, any>[]): Promise<DataWithPDFBytes[]>`
Generate multiple PDFs at once.

##### `searchByKey(pattern: string): Promise<DataWithPDFBytes[]>`
Search data by key pattern.

##### `getByPrefix(prefix: string): Promise<DataWithPDFBytes[]>`
Get all data with specific prefix.

##### `subscribeToKey(key: string, callback: (data: any) => void): () => void`
Subscribe to real-time updates for a key. Returns unsubscribe function.

##### `clearCache(key?: string): void`
Clear cache for specific key or all cache.

##### `getCacheStats(): CacheStats`
Get cache statistics.

##### `exportData(data: any, format: 'json' | 'csv', filename?: string): Promise<void>`
Export data with German formatting.

### React Hooks

#### `useUniversalData<T>(endpoint, params?, options?)`
Hook for fetching data with PDF bytes.

**Returns:**
- `data`: Fetched data
- `loading`: Loading state
- `error`: Error object
- `refetch`: Function to refetch data
- `downloadPDF`: Function to download PDF
- `formattedData`: Data with German-formatted numbers
- `dynamicKey`: Dynamic key of the data

#### `useDataByKey<T>(key, options?)`
Hook for fetching data by dynamic key.

#### `useDataSync(key, callback)`
Hook for real-time data synchronization.

#### `useBulkPDF()`
Hook for bulk PDF operations.

**Returns:**
- `generateBulk`: Function to generate bulk PDFs
- `downloadAll`: Function to download all generated PDFs
- `loading`: Loading state
- `error`: Error object
- `results`: Array of generated PDF data

#### `useDataExport()`
Hook for data export operations.

**Returns:**
- `exportJSON`: Function to export as JSON
- `exportCSV`: Function to export as CSV
- `loading`: Loading state
- `error`: Error object

#### `useDataCache()`
Hook for cache management.

**Returns:**
- `stats`: Cache statistics
- `clear`: Function to clear cache
- `refresh`: Function to refresh stats

## Types

### `DataWithPDFBytes<T>`
```typescript
interface DataWithPDFBytes<T = any> {
  data: T;
  dynamic_key: string;
  pdf_bytes?: string; // base64 encoded
  pdf_url?: string;
  key_metadata?: {
    prefix: string;
    created_at: string;
    has_timestamp: boolean;
    has_uuid: boolean;
  };
}
```

### `DownloadOptions`
```typescript
interface DownloadOptions {
  filename?: string;
  openInNewTab?: boolean;
}
```

## Best Practices

1. **Use Hooks**: Prefer React hooks over direct service calls for better state management
2. **Enable Caching**: Keep caching enabled for better performance
3. **Format Numbers**: Always format numbers for display to maintain consistency
4. **Handle Errors**: Always handle errors in your components
5. **Clean Up**: Unsubscribe from sync callbacks when component unmounts
6. **Batch Operations**: Use bulk operations for multiple PDFs
7. **Cache Management**: Clear cache periodically to free memory

## Examples

See `UniversalDataServiceDemo.tsx` for comprehensive examples of all features.

## Requirements

This implementation satisfies:
- **Requirement 14.3**: Bidirectional number conversion and formatting
- **Requirement 14.10**: Universal data access layer with dynamic keys and PDF bytes

## Support

For issues or questions, refer to the main project documentation or contact the development team.
