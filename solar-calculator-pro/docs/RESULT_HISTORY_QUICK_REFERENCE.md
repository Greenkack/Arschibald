# Result History System - Quick Reference

## Quick Start

### Save a Result
```python
POST /api/v1/result-history/
{
  "result_type": "solar",
  "result_name": "My Calculation",
  "input_data": {...},
  "output_data": {...},
  "tags": ["tag1", "tag2"]
}
```

### Search Results
```python
POST /api/v1/result-history/search
{
  "query": "search term",
  "result_type": "solar",
  "is_favorite": true,
  "page": 1,
  "page_size": 20
}
```

### Compare Results
```python
POST /api/v1/result-history/compare
{
  "result_ids": [123, 456],
  "metrics": ["system_size", "total_cost"]
}
```

### Share a Result
```python
POST /api/v1/result-history/shares
{
  "result_id": 123,
  "is_public": true,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

## Common Operations

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create result | `/result-history/` | POST |
| Get result | `/result-history/{id}` | GET |
| Update result | `/result-history/{id}` | PUT |
| Delete result | `/result-history/{id}` | DELETE |
| Search results | `/result-history/search` | POST |
| Get favorites | `/result-history/favorites/list` | GET |
| Get recent | `/result-history/recent/list` | GET |
| Create version | `/result-history/{id}/versions` | POST |
| Get versions | `/result-history/{id}/versions` | GET |
| Create comparison | `/result-history/comparisons` | POST |
| Compare (temp) | `/result-history/compare` | POST |
| Create share | `/result-history/shares` | POST |
| Get statistics | `/result-history/statistics/summary` | GET |

## Result Types

- `solar`: Solar calculator results
- `heatpump`: Heat pump calculator results
- `combined`: Combined system results

## Comparison Types

- `side-by-side`: View results next to each other
- `overlay`: Overlay results on charts
- `difference`: Highlight differences

## Search Filters

- `query`: Text search in name/description
- `result_type`: Filter by type
- `tags`: Filter by tags
- `is_favorite`: Show only favorites
- `is_archived`: Include archived results
- `date_from`: Start date
- `date_to`: End date
- `project_id`: Filter by project
- `sort_by`: Sort field (created_at, updated_at, result_name)
- `sort_order`: Sort direction (asc, desc)

## Response Codes

- `200`: Success
- `201`: Created
- `204`: No Content (delete success)
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Server Error

## Key Features

✅ Automatic result storage
✅ Version tracking
✅ Multi-result comparison
✅ Advanced search & filtering
✅ Favorites & tags
✅ Secure sharing
✅ Archive management
✅ Statistics & analytics

## Best Practices

1. Always add descriptive names
2. Use tags for organization
3. Create versions for major changes
4. Archive instead of delete
5. Set expiration on shares
6. Regular cleanup of old results

## Security

- User-isolated data
- Secure share tokens
- Expiration enforcement
- Access tracking
- Permission control
- Input validation

## Performance Tips

- Use pagination for large sets
- Filter by date range
- Use indexes (automatic)
- Archive old results
- Cache frequently accessed data
