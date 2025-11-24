/**
 * Search and Filter Demo
 * 
 * Demonstrates the complete search and filter functionality
 */

import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { GlobalSearch } from '../components/search/GlobalSearch';
import { AdvancedFilter } from '../components/search/AdvancedFilter';
import './SearchAndFilterDemo.css';

interface SearchResult {
  id: number;
  entity_type: string;
  title: string;
  description?: string;
  metadata: Record<string, any>;
  relevance_score: number;
}

export const SearchAndFilterDemo: React.FC = () => {
  const [selectedResult, setSelectedResult] = useState<SearchResult | null>(null);
  const [filteredData, setFilteredData] = useState<any[]>([]);
  const [activeEntityType, setActiveEntityType] = useState('projects');

  // Sample data for demonstration
  const sampleProjects = [
    {
      id: 1,
      name: 'Solar Installation - Müller',
      customer: 'Hans Müller',
      type: 'solar',
      status: 'active',
      price: 25000,
      created_at: '2024-01-15'
    },
    {
      id: 2,
      name: 'Heat Pump System - Schmidt',
      customer: 'Anna Schmidt',
      type: 'heatpump',
      status: 'completed',
      price: 18000,
      created_at: '2024-02-20'
    },
    {
      id: 3,
      name: 'Combined System - Weber',
      customer: 'Peter Weber',
      type: 'combined',
      status: 'active',
      price: 45000,
      created_at: '2024-03-10'
    }
  ];

  const handleSearchResultClick = (result: SearchResult) => {
    setSelectedResult(result);
    console.log('Selected result:', result);
  };

  const handleFilterApply = (filters: Record<string, any>) => {
    console.log('Applied filters:', filters);
    
    // Simulate filtering
    let filtered = [...sampleProjects];
    
    if (filters.project_type && filters.project_type.length > 0) {
      filtered = filtered.filter(p => filters.project_type.includes(p.type));
    }
    
    if (filters.status && filters.status.length > 0) {
      filtered = filtered.filter(p => filters.status.includes(p.status));
    }
    
    if (filters.price_range) {
      if (filters.price_range.min) {
        filtered = filtered.filter(p => p.price >= filters.price_range.min);
      }
      if (filters.price_range.max) {
        filtered = filtered.filter(p => p.price <= filters.price_range.max);
      }
    }
    
    setFilteredData(filtered);
  };

  const handleFilterClear = () => {
    console.log('Filters cleared');
    setFilteredData(sampleProjects);
  };

  const formatPrice = (value: number) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(value);
  };

  return (
    <div className="search-filter-demo">
      <h1>Search and Filter System Demo</h1>
      <p className="demo-description">
        Comprehensive demonstration of the search and filter functionality
      </p>

      <TabView>
        {/* Global Search Tab */}
        <TabPanel header="Global Search" leftIcon="pi pi-search">
          <Card title="Global Search Across All Entities">
            <p className="mb-4">
              Search across projects, customers, products, documents, offers, and contracts.
              Features real-time search, fuzzy matching, and search suggestions.
            </p>

            <GlobalSearch
              onResultClick={handleSearchResultClick}
              placeholder="Search across all entities..."
              autoFocus={false}
            />

            {selectedResult && (
              <Card title="Selected Result" className="mt-4">
                <div className="result-details">
                  <p><strong>ID:</strong> {selectedResult.id}</p>
                  <p><strong>Type:</strong> {selectedResult.entity_type}</p>
                  <p><strong>Title:</strong> {selectedResult.title}</p>
                  {selectedResult.description && (
                    <p><strong>Description:</strong> {selectedResult.description}</p>
                  )}
                  <p><strong>Relevance Score:</strong> {selectedResult.relevance_score}</p>
                  <div className="metadata">
                    <strong>Metadata:</strong>
                    <pre>{JSON.stringify(selectedResult.metadata, null, 2)}</pre>
                  </div>
                </div>
              </Card>
            )}
          </Card>
        </TabPanel>

        {/* Advanced Filter Tab */}
        <TabPanel header="Advanced Filters" leftIcon="pi pi-filter">
          <Card title="Advanced Filtering">
            <p className="mb-4">
              Apply complex filters with multiple criteria. Supports date ranges,
              price ranges, multi-select options, and more.
            </p>

            <AdvancedFilter
              entityType={activeEntityType}
              onFilterApply={handleFilterApply}
              onFilterClear={handleFilterClear}
            />

            <Card title="Filtered Results" className="mt-4">
              <DataTable
                value={filteredData.length > 0 ? filteredData : sampleProjects}
                paginator
                rows={10}
                emptyMessage="No results found"
              >
                <Column field="id" header="ID" sortable />
                <Column field="name" header="Name" sortable />
                <Column field="customer" header="Customer" sortable />
                <Column field="type" header="Type" sortable />
                <Column field="status" header="Status" sortable />
                <Column
                  field="price"
                  header="Price"
                  sortable
                  body={(rowData) => formatPrice(rowData.price)}
                />
                <Column field="created_at" header="Created" sortable />
              </DataTable>
            </Card>
          </Card>
        </TabPanel>

        {/* Features Tab */}
        <TabPanel header="Features" leftIcon="pi pi-star">
          <Card title="Search and Filter Features">
            <div className="features-grid">
              <div className="feature-card">
                <i className="pi pi-search feature-icon" />
                <h3>Global Search</h3>
                <p>Search across all entity types from a single interface</p>
                <ul>
                  <li>Real-time search with debouncing</li>
                  <li>Multi-entity support</li>
                  <li>Relevance scoring</li>
                  <li>Execution time tracking</li>
                </ul>
              </div>

              <div className="feature-card">
                <i className="pi pi-filter feature-icon" />
                <h3>Advanced Filtering</h3>
                <p>Apply complex filters with multiple criteria</p>
                <ul>
                  <li>Dynamic filter fields</li>
                  <li>Date range filtering</li>
                  <li>Price range filtering</li>
                  <li>Multi-select options</li>
                </ul>
              </div>

              <div className="feature-card">
                <i className="pi pi-bolt feature-icon" />
                <h3>Fuzzy Matching</h3>
                <p>Find results even with typos or partial matches</p>
                <ul>
                  <li>Typo tolerance</li>
                  <li>Partial word matching</li>
                  <li>Configurable threshold</li>
                  <li>Better user experience</li>
                </ul>
              </div>

              <div className="feature-card">
                <i className="pi pi-lightbulb feature-icon" />
                <h3>Search Suggestions</h3>
                <p>Auto-complete based on history and entity names</p>
                <ul>
                  <li>Search history</li>
                  <li>Entity name suggestions</li>
                  <li>Quick selection</li>
                  <li>Improved efficiency</li>
                </ul>
              </div>

              <div className="feature-card">
                <i className="pi pi-save feature-icon" />
                <h3>Saved Searches</h3>
                <p>Save frequently used searches for quick access</p>
                <ul>
                  <li>Save query + filters</li>
                  <li>Named searches</li>
                  <li>Public/private options</li>
                  <li>Quick apply</li>
                </ul>
              </div>

              <div className="feature-card">
                <i className="pi pi-chart-line feature-icon" />
                <h3>Search Analytics</h3>
                <p>Track search usage and trends</p>
                <ul>
                  <li>Total searches</li>
                  <li>Popular terms</li>
                  <li>Search trends</li>
                  <li>Usage insights</li>
                </ul>
              </div>
            </div>
          </Card>
        </TabPanel>

        {/* API Examples Tab */}
        <TabPanel header="API Examples" leftIcon="pi pi-code">
          <Card title="API Usage Examples">
            <div className="api-examples">
              <h3>Global Search</h3>
              <pre className="code-block">
{`POST /api/v1/search/global
Content-Type: application/json

{
  "query": "solar",
  "entity_types": ["projects", "products"],
  "limit": 50,
  "fuzzy": true
}`}
              </pre>

              <h3>Apply Filters</h3>
              <pre className="code-block">
{`POST /api/v1/search/filter
Content-Type: application/json

{
  "entity_type": "projects",
  "filters": {
    "project_type": ["solar"],
    "status": ["active"],
    "price_range": {
      "min": 10000,
      "max": 50000
    }
  },
  "sort_by": "created_at",
  "sort_order": "desc",
  "page": 1,
  "page_size": 50
}`}
              </pre>

              <h3>Get Suggestions</h3>
              <pre className="code-block">
{`GET /api/v1/search/suggestions?query=sol&limit=10`}
              </pre>

              <h3>Save Search</h3>
              <pre className="code-block">
{`POST /api/v1/search/saved?user_id=1
Content-Type: application/json

{
  "name": "Active Solar Projects",
  "entity_type": "projects",
  "query": "solar",
  "filters": {
    "status": ["active"]
  },
  "is_public": false
}`}
              </pre>
            </div>
          </Card>
        </TabPanel>
      </TabView>
    </div>
  );
};

export default SearchAndFilterDemo;
