# Search and Filter - Quick Reference

## Quick Start

### Global Search
```typescript
import { GlobalSearch } from '@/components/search/GlobalSearch';

<GlobalSearch
  onResultClick={(result) => console.log(result)}
  placeholder="Search..."
  autoFocus={true}
/>
```

### Advanced Filter
```typescript
import { AdvancedFilter } from '@/components/search/AdvancedFilter';

<AdvancedFilter
  entityType="projects"
  onFilterApply={(filters) => fetchData(filters)}
  onFilterClear={() => fetchData({})}
/>
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/search/global` | POST | Global search across entities |
| `/api/v1/search/filter` | POST | Apply advanced filters |
| `/api/v1/search/suggestions` | GET | Get search suggestions |
| `/api/v1/search/analytics` | GET | Get search analytics |
| `/api/v1/search/filter-options/{type}` | GET | Get filter options |
| `/api/v1/search/saved` | POST | Save search |
| `/api/v1/search/saved` | GET | Get saved searches |
| `/api/v1/search/saved/{id}` | PUT | Update saved search |
| `/api/v1/search/saved/{id}` | DELETE | Delete saved search |

## Entity Types

- `projects` - Solar/Heat Pump projects
- `customers` - Customer records
- `products` - Product catalog
- `documents` - Documents and files
- `offers` - Sales offers
- `contracts` - Contracts

## Filter Types

| Type | Description | Example |
|------|-------------|---------|
| `select` | Single selection | Status: Active |
| `multiselect` | Multiple selections | Types: Solar, Heat Pump |
| `date_range` | Date range | 2024-01-01 to 2024-12-31 |
| `price_range` | Price range | €10,000 to €50,000 |
| `text` | Free text | Customer name |

## Common Filters

### Projects
```json
{
  "project_type": ["solar", "heatpump"],
  "status": ["active"],
  "date_range": { "start": "2024-01-01", "end": "2024-12-31" },
  "price_range": { "min": 10000, "max": 50000 }
}
```

### Products
```json
{
  "category": ["pv_module", "inverter"],
  "manufacturer": ["Manufacturer A"],
  "price_range": { "min": 200, "max": 1000 },
  "availability": ["in_stock"]
}
```

### Customers
```json
{
  "customer_type": ["residential"],
  "status": ["active"],
  "date_range": { "start": "2024-01-01", "end": "2024-12-31" }
}
```

## Features

✅ Real-time search with debouncing  
✅ Fuzzy matching for typo tolerance  
✅ Search suggestions  
✅ Advanced filtering  
✅ Saved searches  
✅ Search analytics  
✅ Multi-entity search  
✅ Pagination support  
✅ Sort options  
✅ German number formatting  

## Performance Tips

1. **Use specific keywords** - More specific = faster results
2. **Limit entity types** - Search fewer types when possible
3. **Enable fuzzy matching** - Better results with typos
4. **Use filters** - Narrow down results efficiently
5. **Save frequent searches** - Quick access to common queries

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + K` | Open global search |
| `Esc` | Close search results |
| `Enter` | Apply filters |
| `Ctrl/Cmd + Enter` | Save search |

## Troubleshooting

**No results?**
- Check spelling or enable fuzzy matching
- Broaden search criteria
- Remove some filters

**Slow search?**
- Reduce entity types
- Add more specific filters
- Use pagination

**Filter not working?**
- Verify filter options loaded
- Check filter value format
- Clear browser cache

## Examples

### Search for Active Projects
```typescript
// Query: "solar"
// Entity Types: ["projects"]
// Filters: { status: ["active"] }
```

### Find Products in Price Range
```typescript
// Entity Type: "products"
// Filters: {
//   category: ["pv_module"],
//   price_range: { min: 200, max: 500 }
// }
```

### Save Search for Later
```typescript
POST /api/v1/search/saved?user_id=1
{
  "name": "Active Solar Projects",
  "entity_type": "projects",
  "query": "solar",
  "filters": { "status": ["active"] }
}
```

## Support

📖 Full Documentation: `SEARCH_AND_FILTER_GUIDE.md`  
🔧 API Docs: `/api/docs`  
💬 Support: Contact development team
