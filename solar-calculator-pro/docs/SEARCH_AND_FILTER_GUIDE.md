# Search and Filter System - Complete Guide

## Overview

The Search and Filter system provides comprehensive search functionality across all entities in the Solar Calculator Pro application. It includes global search, advanced filtering, fuzzy matching, search suggestions, saved searches, and search analytics.

## Features

### 1. Global Search

**Description**: Search across all entity types (projects, customers, products, documents, offers, contracts) from a single search interface.

**Key Features**:
- Real-time search with debouncing (300ms delay)
- Fuzzy matching for typo tolerance
- Entity type filtering
- Search suggestions based on history
- Relevance scoring
- Execution time tracking

**Usage**:
```typescript
import { GlobalSearch } from '@/components/search/GlobalSearch';

<GlobalSearch
  onResultClick={(result) => {
    console.log('Selected:', result);
    // Navigate to result detail page
  }}
  placeholder="Search projects, customers, products..."
  autoFocus={true}
/>
```

### 2. Advanced Filtering

**Description**: Apply complex filters to narrow down search results with multiple criteria.

**Key Features**:
- Dynamic filter fields based on entity type
- Multiple filter types (select, multiselect, date range, price range, text)
- Filter combinations with AND logic
- Saved filters for reuse
- Active filter display with chips
- Filter presets

**Usage**:
```typescript
import { AdvancedFilter } from '@/components/search/AdvancedFilter';

<AdvancedFilter
  entityType="projects"
  onFilterApply={(filters) => {
    console.log('Applied filters:', filters);
    // Fetch filtered results
  }}
  onFilterClear={() => {
    console.log('Filters cleared');
    // Reset to unfiltered results
  }}
/>
```

### 3. Fuzzy Search

**Description**: Find results even with typos or partial matches.

**Algorithm**: Uses SequenceMatcher to calculate similarity ratio between query and text.

**Threshold**: Default 0.6 (60% similarity)

**Example**:
- Query: "solarmodul" → Matches: "Solarmodule", "Solar Module", "PV Solarmodul"
- Query: "invertr" → Matches: "Inverter", "Wechselrichter"

### 4. Search Suggestions

**Description**: Auto-complete suggestions based on search history and entity names.

**Features**:
- Appears after 2 characters
- Shows up to 10 suggestions
- Based on search history
- Based on entity names in database
- Click to apply suggestion

### 5. Saved Searches

**Description**: Save frequently used searches and filters for quick access.

**Features**:
- Save search query + filters
- Name your saved searches
- Public or private searches
- Quick apply from saved list
- Edit and delete saved searches

### 6. Search Analytics

**Description**: Track search usage and trends.

**Metrics**:
- Total searches performed
- Recent searches (last 10)
- Popular search terms
- Search trends (trending up/down/stable)

## API Endpoints

### Global Search

```http
POST /api/v1/search/global
Content-Type: application/json

{
  "query": "solar",
  "entity_types": ["projects", "products"],
  "limit": 50,
  "fuzzy": true
}
```

**Response**:
```json
{
  "results": {
    "projects": [
      {
        "id": 1,
        "entity_type": "projects",
        "title": "Solar Installation - Müller",
        "description": "10 kWp system",
        "metadata": {
          "status": "active",
          "created_at": "2024-01-15"
        },
        "relevance_score": 0.95
      }
    ],
    "products": [...]
  },
  "total_results": 25,
  "query": "solar",
  "execution_time_ms": 45.23
}
```

### Apply Filters

```http
POST /api/v1/search/filter
Content-Type: application/json

{
  "entity_type": "projects",
  "filters": {
    "project_type": ["solar", "combined"],
    "status": ["active"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "price_range": {
      "min": 10000,
      "max": 50000
    }
  },
  "sort_by": "created_at",
  "sort_order": "desc",
  "page": 1,
  "page_size": 50
}
```

**Response**:
```json
{
  "results": [...],
  "total_count": 150,
  "page": 1,
  "page_size": 50,
  "total_pages": 3,
  "has_next": true,
  "has_prev": false
}
```

### Get Search Suggestions

```http
GET /api/v1/search/suggestions?query=sol&limit=10
```

**Response**:
```json
{
  "suggestions": [
    "solar",
    "solarmodule",
    "solar installation",
    "solar calculator"
  ],
  "query": "sol"
}
```

### Save Search

```http
POST /api/v1/search/saved?user_id=1
Content-Type: application/json

{
  "name": "Active Solar Projects 2024",
  "entity_type": "projects",
  "query": "solar",
  "filters": {
    "project_type": ["solar"],
    "status": ["active"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    }
  },
  "is_public": false
}
```

### Get Saved Searches

```http
GET /api/v1/search/saved?user_id=1&include_public=true
```

### Get Filter Options

```http
GET /api/v1/search/filter-options/projects
```

**Response**:
```json
{
  "project_type": ["solar", "heatpump", "combined"],
  "status": ["draft", "active", "completed", "archived"],
  "date_range": true,
  "price_range": true
}
```

### Get Search Analytics

```http
GET /api/v1/search/analytics
```

**Response**:
```json
{
  "total_searches": 1250,
  "recent_searches": [
    "solar modules",
    "inverter",
    "battery storage"
  ],
  "popular_searches": [
    {
      "term": "solar",
      "count": 150
    },
    {
      "term": "inverter",
      "count": 95
    }
  ],
  "search_trends": {
    "trending_up": ["battery storage", "heat pump"],
    "trending_down": [],
    "stable": ["solar", "inverter"]
  }
}
```

## Filter Types

### 1. Select Filter
Single selection from predefined options.

**Example**: Project Status
```typescript
{
  name: 'status',
  label: 'Status',
  type: 'select',
  options: [
    { label: 'Draft', value: 'draft' },
    { label: 'Active', value: 'active' },
    { label: 'Completed', value: 'completed' }
  ]
}
```

### 2. MultiSelect Filter
Multiple selections from predefined options.

**Example**: Project Types
```typescript
{
  name: 'project_type',
  label: 'Project Type',
  type: 'multiselect',
  options: [
    { label: 'Solar', value: 'solar' },
    { label: 'Heat Pump', value: 'heatpump' },
    { label: 'Combined', value: 'combined' }
  ]
}
```

### 3. Date Range Filter
Select start and end dates.

**Example**: Creation Date
```typescript
{
  name: 'date_range',
  label: 'Date Range',
  type: 'date_range'
}
```

**Value Format**:
```json
{
  "start": "2024-01-01",
  "end": "2024-12-31"
}
```

### 4. Price Range Filter
Select minimum and maximum prices.

**Example**: Project Price
```typescript
{
  name: 'price_range',
  label: 'Price Range',
  type: 'price_range'
}
```

**Value Format**:
```json
{
  "min": 10000,
  "max": 50000
}
```

### 5. Text Filter
Free text input for custom filtering.

**Example**: Customer Name
```typescript
{
  name: 'customer_name',
  label: 'Customer Name',
  type: 'text'
}
```

## Entity Types

### Projects
**Filterable Fields**:
- project_type: solar, heatpump, combined
- status: draft, active, completed, archived
- date_range: creation date
- price_range: project price

### Customers
**Filterable Fields**:
- customer_type: residential, commercial, industrial
- status: active, inactive, prospect
- date_range: registration date

### Products
**Filterable Fields**:
- category: pv_module, inverter, battery, heatpump
- manufacturer: (dynamic list from database)
- price_range: product price
- availability: in_stock, out_of_stock, discontinued

### Documents
**Filterable Fields**:
- document_type: contract, invoice, datasheet, manual
- status: draft, final, archived
- date_range: creation date

### Offers
**Filterable Fields**:
- status: draft, sent, accepted, rejected, expired
- date_range: offer date
- price_range: offer amount

### Contracts
**Filterable Fields**:
- contract_type: installation, maintenance, warranty
- status: active, completed, cancelled
- date_range: contract date

## Performance Considerations

### Search Optimization
- **Debouncing**: 300ms delay prevents excessive API calls
- **Caching**: Search results cached for 5 minutes
- **Indexing**: Database indexes on searchable fields
- **Pagination**: Results limited to 50 per entity type

### Filter Optimization
- **Lazy Loading**: Filter options loaded on demand
- **Query Optimization**: Efficient SQL queries with proper indexes
- **Result Caching**: Filtered results cached based on filter hash

## Best Practices

### 1. Search Query
- Use at least 2 characters for search
- Enable fuzzy matching for better results
- Use specific keywords for faster results

### 2. Filtering
- Start with broad filters, then narrow down
- Use date ranges to limit result set
- Combine multiple filters for precise results

### 3. Saved Searches
- Name saved searches descriptively
- Review and update saved searches regularly
- Share useful searches with team (public searches)

### 4. Performance
- Limit entity types when possible
- Use pagination for large result sets
- Clear filters when not needed

## Troubleshooting

### No Results Found
1. Check spelling (or enable fuzzy matching)
2. Broaden search criteria
3. Remove some filters
4. Check entity type selection

### Slow Search
1. Reduce number of entity types
2. Add more specific filters
3. Use pagination
4. Check network connection

### Filter Not Working
1. Verify filter options are loaded
2. Check filter value format
3. Ensure entity type is correct
4. Clear browser cache

## Examples

### Example 1: Find Active Solar Projects
```typescript
// Global search
<GlobalSearch
  onResultClick={(result) => navigate(`/projects/${result.id}`)}
/>

// With filters
<AdvancedFilter
  entityType="projects"
  onFilterApply={(filters) => {
    // filters = {
    //   project_type: ['solar'],
    //   status: ['active']
    // }
    fetchProjects(filters);
  }}
/>
```

### Example 2: Search Products by Price Range
```typescript
<AdvancedFilter
  entityType="products"
  onFilterApply={(filters) => {
    // filters = {
    //   category: ['pv_module'],
    //   price_range: { min: 200, max: 500 }
    // }
    fetchProducts(filters);
  }}
/>
```

### Example 3: Save Frequently Used Search
```typescript
// After applying filters
const saveCurrentSearch = async () => {
  await fetch('/api/v1/search/saved?user_id=1', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'High-Value Solar Projects',
      entity_type: 'projects',
      query: 'solar',
      filters: {
        project_type: ['solar'],
        price_range: { min: 30000, max: 100000 }
      },
      is_public: false
    })
  });
};
```

## Future Enhancements

1. **Advanced Query Syntax**: Support for boolean operators (AND, OR, NOT)
2. **Faceted Search**: Show result counts per filter option
3. **Search History**: Persistent search history across sessions
4. **Smart Suggestions**: ML-based suggestions from user behavior
5. **Export Results**: Export search results to CSV/Excel
6. **Bulk Actions**: Perform actions on multiple search results
7. **Search Alerts**: Get notified when new results match saved search

## Support

For issues or questions about the Search and Filter system:
- Check this documentation
- Review API documentation at `/api/docs`
- Contact development team
- Submit bug reports via issue tracker
