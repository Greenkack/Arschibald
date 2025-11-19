/**
 * Universal Data Service Demo
 * 
 * Comprehensive demonstration of all Universal Data Service features
 * 
 * Requirements: 14.3, 14.10
 */

import React, { useState } from 'react';
import {
  useUniversalData,
  useDataByKey,
  useDataSync,
  useBulkPDF,
  useDataExport,
  useDataCache,
} from '../hooks/useUniversalData';
import { universalDataService } from '../services/UniversalDataService';

/**
 * Example 1: Fetch data with PDF bytes
 */
export const FetchWithPDFExample: React.FC = () => {
  const { data, loading, error, downloadPDF, formattedData, dynamicKey } = useUniversalData(
    '/solar/calculations/123',
    {},
    { formatNumbers: true, decimals: 2 }
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="example-card">
      <h3>Fetch with PDF Bytes</h3>
      <div className="data-display">
        <p><strong>Dynamic Key:</strong> {dynamicKey}</p>
        <pre>{JSON.stringify(formattedData, null, 2)}</pre>
      </div>
      <button onClick={() => downloadPDF('solar-calculation.pdf')}>
        Download PDF
      </button>
    </div>
  );
};

/**
 * Example 2: Fetch by dynamic key
 */
export const FetchByKeyExample: React.FC = () => {
  const [key, setKey] = useState<string>('SOL_20231116_143052_a1b2c3d4');
  const { data, loading, error, downloadPDF, formattedData } = useDataByKey(
    key,
    { formatNumbers: true }
  );

  return (
    <div className="example-card">
      <h3>Fetch by Dynamic Key</h3>
      <div className="input-group">
        <input
          type="text"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="Enter dynamic key"
        />
      </div>
      {loading && <div>Loading...</div>}
      {error && <div>Error: {error.message}</div>}
      {data && (
        <>
          <pre>{JSON.stringify(formattedData, null, 2)}</pre>
          <button onClick={() => downloadPDF()}>Download PDF</button>
        </>
      )}
    </div>
  );
};

/**
 * Example 3: Format all numbers recursively
 */
export const FormatNumbersExample: React.FC = () => {
  const sampleData = {
    cost: 15000.50,
    systemSize: 10.5,
    production: 12500.75,
    nested: {
      value1: 1234.56,
      value2: 9876.54,
      deepNested: {
        amount: 5555.55,
      },
    },
    array: [100.11, 200.22, 300.33],
  };

  const formatted = universalDataService.formatAllNumbers(sampleData);

  return (
    <div className="example-card">
      <h3>Format All Numbers (German Format)</h3>
      <div className="comparison">
        <div>
          <h4>Original:</h4>
          <pre>{JSON.stringify(sampleData, null, 2)}</pre>
        </div>
        <div>
          <h4>Formatted:</h4>
          <pre>{JSON.stringify(formatted, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
};

/**
 * Example 4: Real-time data synchronization
 */
export const DataSyncExample: React.FC = () => {
  const [key] = useState<string>('SOL_20231116_143052_a1b2c3d4');
  const [syncedData, setSyncedData] = useState<any>(null);
  const [updateCount, setUpdateCount] = useState<number>(0);

  useDataSync(key, (data) => {
    setSyncedData(data);
    setUpdateCount((prev) => prev + 1);
  });

  return (
    <div className="example-card">
      <h3>Real-time Data Sync</h3>
      <p><strong>Watching Key:</strong> {key}</p>
      <p><strong>Updates Received:</strong> {updateCount}</p>
      {syncedData && (
        <pre>{JSON.stringify(syncedData, null, 2)}</pre>
      )}
    </div>
  );
};

/**
 * Example 5: Bulk PDF generation
 */
export const BulkPDFExample: React.FC = () => {
  const { generateBulk, downloadAll, loading, error, results } = useBulkPDF();

  const handleGenerate = async () => {
    const dataList = [
      { id: 1, name: 'Project A', cost: 15000 },
      { id: 2, name: 'Project B', cost: 20000 },
      { id: 3, name: 'Project C', cost: 18000 },
    ];

    await generateBulk('/pdf/bulk-generate', dataList);
  };

  return (
    <div className="example-card">
      <h3>Bulk PDF Generation</h3>
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Bulk PDFs'}
      </button>
      {error && <div className="error">Error: {error.message}</div>}
      {results.length > 0 && (
        <>
          <p>Generated {results.length} PDFs</p>
          <button onClick={downloadAll}>Download All</button>
        </>
      )}
    </div>
  );
};

/**
 * Example 6: Data export
 */
export const DataExportExample: React.FC = () => {
  const { exportJSON, exportCSV, loading, error } = useDataExport();

  const sampleData = [
    { id: 1, name: 'Solar System A', cost: 15000.50, size: 10.5 },
    { id: 2, name: 'Solar System B', cost: 20000.75, size: 15.2 },
    { id: 3, name: 'Solar System C', cost: 18000.25, size: 12.8 },
  ];

  return (
    <div className="example-card">
      <h3>Data Export</h3>
      <div className="button-group">
        <button
          onClick={() => exportJSON(sampleData, 'solar-systems.json')}
          disabled={loading}
        >
          Export as JSON
        </button>
        <button
          onClick={() => exportCSV(sampleData, 'solar-systems.csv')}
          disabled={loading}
        >
          Export as CSV
        </button>
      </div>
      {error && <div className="error">Error: {error.message}</div>}
      <pre>{JSON.stringify(sampleData, null, 2)}</pre>
    </div>
  );
};

/**
 * Example 7: Cache management
 */
export const CacheManagementExample: React.FC = () => {
  const { stats, clear, refresh } = useDataCache();

  return (
    <div className="example-card">
      <h3>Cache Management</h3>
      <div className="stats">
        <p><strong>Cache Size:</strong> {stats.size} entries</p>
        <p><strong>Oldest Entry:</strong> {stats.oldestEntry ? new Date(stats.oldestEntry).toLocaleString() : 'N/A'}</p>
        <p><strong>Newest Entry:</strong> {stats.newestEntry ? new Date(stats.newestEntry).toLocaleString() : 'N/A'}</p>
      </div>
      <div className="button-group">
        <button onClick={refresh}>Refresh Stats</button>
        <button onClick={() => clear()}>Clear All Cache</button>
      </div>
      {stats.keys.length > 0 && (
        <div className="cache-keys">
          <h4>Cached Keys:</h4>
          <ul>
            {stats.keys.map((key) => (
              <li key={key}>
                {key}
                <button onClick={() => clear(key)}>Clear</button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

/**
 * Example 8: Search by key pattern
 */
export const SearchByKeyExample: React.FC = () => {
  const [pattern, setPattern] = useState<string>('SOL_*');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const data = await universalDataService.searchByKey(pattern);
      setResults(data);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="example-card">
      <h3>Search by Key Pattern</h3>
      <div className="input-group">
        <input
          type="text"
          value={pattern}
          onChange={(e) => setPattern(e.target.value)}
          placeholder="Enter pattern (e.g., SOL_*)"
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
      {results.length > 0 && (
        <div className="results">
          <p>Found {results.length} results</p>
          <ul>
            {results.map((result, index) => (
              <li key={index}>
                <strong>{result.dynamic_key}</strong>
                <pre>{JSON.stringify(result.data, null, 2)}</pre>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

/**
 * Main demo component
 */
export const UniversalDataServiceDemo: React.FC = () => {
  const [activeExample, setActiveExample] = useState<string>('fetch');

  const examples = [
    { id: 'fetch', label: 'Fetch with PDF', component: FetchWithPDFExample },
    { id: 'key', label: 'Fetch by Key', component: FetchByKeyExample },
    { id: 'format', label: 'Format Numbers', component: FormatNumbersExample },
    { id: 'sync', label: 'Real-time Sync', component: DataSyncExample },
    { id: 'bulk', label: 'Bulk PDF', component: BulkPDFExample },
    { id: 'export', label: 'Data Export', component: DataExportExample },
    { id: 'cache', label: 'Cache Management', component: CacheManagementExample },
    { id: 'search', label: 'Search by Key', component: SearchByKeyExample },
  ];

  const ActiveComponent = examples.find((ex) => ex.id === activeExample)?.component || FetchWithPDFExample;

  return (
    <div className="universal-data-demo">
      <h1>Universal Data Service Demo</h1>
      <p className="description">
        Comprehensive demonstration of all Universal Data Service features including
        PDF generation, German number formatting, caching, and real-time synchronization.
      </p>

      <div className="demo-container">
        <nav className="example-nav">
          <h3>Examples</h3>
          <ul>
            {examples.map((example) => (
              <li key={example.id}>
                <button
                  className={activeExample === example.id ? 'active' : ''}
                  onClick={() => setActiveExample(example.id)}
                >
                  {example.label}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        <main className="example-content">
          <ActiveComponent />
        </main>
      </div>

      <style>{`
        .universal-data-demo {
          padding: 2rem;
          max-width: 1400px;
          margin: 0 auto;
        }

        .description {
          color: #666;
          margin-bottom: 2rem;
        }

        .demo-container {
          display: grid;
          grid-template-columns: 250px 1fr;
          gap: 2rem;
        }

        .example-nav {
          background: #f5f5f5;
          padding: 1rem;
          border-radius: 8px;
        }

        .example-nav h3 {
          margin-top: 0;
        }

        .example-nav ul {
          list-style: none;
          padding: 0;
        }

        .example-nav button {
          width: 100%;
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          border: none;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          text-align: left;
          transition: all 0.2s;
        }

        .example-nav button:hover {
          background: #e0e0e0;
        }

        .example-nav button.active {
          background: #007bff;
          color: white;
        }

        .example-card {
          background: white;
          padding: 2rem;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .example-card h3 {
          margin-top: 0;
          color: #333;
        }

        .input-group {
          margin: 1rem 0;
        }

        .input-group input {
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          width: 100%;
          max-width: 400px;
        }

        .button-group {
          display: flex;
          gap: 1rem;
          margin: 1rem 0;
        }

        button {
          padding: 0.75rem 1.5rem;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          transition: background 0.2s;
        }

        button:hover:not(:disabled) {
          background: #0056b3;
        }

        button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        pre {
          background: #f5f5f5;
          padding: 1rem;
          border-radius: 4px;
          overflow-x: auto;
          font-size: 0.875rem;
        }

        .comparison {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .error {
          color: #dc3545;
          padding: 0.5rem;
          background: #f8d7da;
          border-radius: 4px;
          margin: 1rem 0;
        }

        .stats {
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 4px;
          margin: 1rem 0;
        }

        .cache-keys ul {
          list-style: none;
          padding: 0;
        }

        .cache-keys li {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.5rem;
          background: #f8f9fa;
          margin-bottom: 0.5rem;
          border-radius: 4px;
        }

        .cache-keys button {
          padding: 0.25rem 0.75rem;
          font-size: 0.875rem;
        }

        .results ul {
          list-style: none;
          padding: 0;
        }

        .results li {
          margin-bottom: 1rem;
          padding: 1rem;
          background: #f8f9fa;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
};

export default UniversalDataServiceDemo;
