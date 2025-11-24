# Result History and Comparison System - Complete Guide

## Overview

The Result History and Comparison System provides comprehensive functionality for storing, versioning, comparing, and sharing calculation results across the Solar Calculator Pro application.

## Features

### 1. Calculation History
- **Automatic Storage**: All calculations are automatically saved to history
- **Manual Save**: Users can explicitly save important calculations
- **Rich Metadata**: Store input parameters, output results, and custom descriptions
- **Project Association**: Link results to specific projects for organization

### 2. Result Versioning
- **Version Tracking**: Create multiple versions of the same calculation
- **Version Tree**: Navigate through parent-child relationships
- **Version Comparison**: Compare different versions to see changes
- **Version History**: View complete history of all versions

### 3. Result Comparison
- **Multi-Result Comparison**: Compare up to 10 results simultaneously
- **Comparison Types**:
  - **Side-by-Side**: View results next to each other
  - **Overlay**: Overlay results on charts
  - **Difference**: Highlight differences between results
- **Metric Selection**: Choose specific metrics to compare
- **Statistical Analysis**: Automatic calculation of min, max, avg, range
- **Saved Comparisons**: Save comparison configurations for reuse

### 4. Result Search and Filtering
- **Full-Text Search**: Search by name and description
- **Type Filtering**: Filter by result type (solar, heatpump, combined)
- **Tag Filtering**: Filter by custom tags
- **Date Range**: Filter by creation date
- **Favorite Filter**: Show only favorite results
- **Archive Filter**: Include or exclude archived results
- **Project Filter**: Filter by associated project
- **Sorting**: Sort by date, name, or update time
- **Pagination**: Efficient handling of large result sets

### 5. Result Organization
- **Favorites**: Mark important results as favorites
- **Tags**: Add custom tags for categorization
- **Archive**: Archive old results without deleting
- **Projects**: Associate results with projects

### 6. Result Sharing
- **Share Links**: Generate secure share links
- **Public Sharing**: Make results publicly accessible
- **Private Sharing**: Share with specific users
- **Edit Permissions**: Control whether recipients can edit
- **Expiration**: Set expiration dates for shares
- **Access Tracking**: Monitor share access and usage

## API Endpoints

### Result History CRUD

#### Create Result
```http
POST /api/v1/result-history/
Content-Type: application/json

{
  "result_type": "solar",
  "result_name": "Residential Solar System - 10kW",
  "description": "Initial calculation for Smith residence",
  "input_data": {
    "roof_area": 50,
    "roof_type": "flat",
    "annual_consumption": 4000
  },
  "output_data": {
    "system_size": 10.5,
    "module_count": 30,
    "annual_production": 12000
  },
  "project_id": 123,
  "tags": ["residential", "10kw", "smith"]
}
```

#### Get Result
```http
GET /api/v1/result-history/{result_id}
```

#### Update Result
```http
PUT /api/v1/result-history/{result_id}
Content-Type: application/json

{
  "result_name": "Updated Name",
  "is_favorite": true,
  "tags": ["residential", "10kw", "smith", "approved"]
}
```

#### Delete Result
```http
DELETE /api/v1/result-history/{result_id}
```

### Result Search

#### Search Results
```http
POST /api/v1/result-history/search
Content-Type: application/json

{
  "query": "residential",
  "result_type": "solar",
  "tags": ["10kw"],
  "is_favorite": true,
  "date_from": "2024-01-01T00:00:00Z",
  "date_to": "2024-12-31T23:59:59Z",
  "page": 1,
  "page_size": 20,
  "sort_by": "created_at",
  "sort_order": "desc"
}
```

#### Get Favorites
```http
GET /api/v1/result-history/favorites/list?limit=20
```

#### Get Recent Results
```http
GET /api/v1/result-history/recent/list?limit=10
```

### Result Versioning

#### Get Version Tree
```http
GET /api/v1/result-history/{result_id}/versions
```

#### Create New Version
```http
POST /api/v1/result-history/{result_id}/versions
Content-Type: application/json

{
  "result_type": "solar",
  "result_name": "Residential Solar System - 10kW (v2)",
  "description": "Updated calculation with new modules",
  "input_data": {...},
  "output_data": {...}
}
```

### Result Comparison

#### Create Comparison
```http
POST /api/v1/result-history/comparisons
Content-Type: application/json

{
  "comparison_name": "10kW vs 15kW Systems",
  "description": "Comparing different system sizes",
  "result_ids": [123, 456],
  "comparison_type": "side-by-side",
  "metrics_to_compare": ["system_size", "total_cost", "payback_period"]
}
```

#### Get Comparison
```http
GET /api/v1/result-history/comparisons/{comparison_id}
```

#### Compare Results (Temporary)
```http
POST /api/v1/result-history/compare
Content-Type: application/json

{
  "result_ids": [123, 456, 789],
  "metrics": ["system_size", "total_cost"]
}
```

#### Get All Comparisons
```http
GET /api/v1/result-history/comparisons/list/all
```

#### Delete Comparison
```http
DELETE /api/v1/result-history/comparisons/{comparison_id}
```

### Result Sharing

#### Create Share
```http
POST /api/v1/result-history/shares
Content-Type: application/json

{
  "result_id": 123,
  "shared_with_user_id": 456,
  "is_public": false,
  "can_edit": false,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

#### Get Shared Result
```http
GET /api/v1/result-history/shares/token/{share_token}
```

#### Get Shares for Result
```http
GET /api/v1/result-history/{result_id}/shares
```

#### Delete Share
```http
DELETE /api/v1/result-history/shares/{share_id}
```

### Statistics

#### Get Statistics
```http
GET /api/v1/result-history/statistics/summary
```

Response:
```json
{
  "total_results": 150,
  "results_by_type": {
    "solar": 100,
    "heatpump": 30,
    "combined": 20
  },
  "favorite_count": 25,
  "archived_count": 10,
  "recent_results": [...],
  "most_compared": [...],
  "tags_usage": {
    "residential": 80,
    "commercial": 40,
    "10kw": 30
  }
}
```

## Database Schema

### result_history Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `project_id`: Foreign key to projects table (optional)
- `result_type`: Type of calculation (solar, heatpump, combined)
- `result_name`: User-friendly name
- `description`: Optional description
- `input_data`: JSON field storing input parameters
- `output_data`: JSON field storing calculation results
- `version`: Version number
- `parent_id`: Foreign key to parent result (for versioning)
- `is_favorite`: Boolean flag
- `is_archived`: Boolean flag
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### result_tags Table
- `id`: Primary key
- `result_id`: Foreign key to result_history
- `tag_name`: Tag name
- `created_at`: Creation timestamp

### result_shares Table
- `id`: Primary key
- `result_id`: Foreign key to result_history
- `shared_by_user_id`: User who created the share
- `shared_with_user_id`: User who receives the share (optional)
- `share_token`: Unique token for accessing shared result
- `is_public`: Public share flag
- `can_edit`: Edit permission flag
- `expires_at`: Expiration timestamp (optional)
- `created_at`: Creation timestamp
- `accessed_at`: Last access timestamp
- `access_count`: Number of times accessed

### result_comparisons Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `comparison_name`: User-friendly name
- `description`: Optional description
- `result_ids`: JSON array of result IDs
- `comparison_type`: Type of comparison
- `metrics_to_compare`: JSON array of metric names
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Usage Examples

### Example 1: Save Calculation Result
```python
from backend.services.result_history_service import ResultHistoryService
from backend.models.result_history_schemas import ResultHistoryCreate, ResultType

service = ResultHistoryService(db)

data = ResultHistoryCreate(
    result_type=ResultType.SOLAR,
    result_name="10kW Residential System",
    description="Initial calculation",
    input_data={
        "roof_area": 50,
        "module_type": "premium"
    },
    output_data={
        "system_size": 10.5,
        "total_cost": 25000
    },
    tags=["residential", "10kw"]
)

result = service.create_result(user_id=1, data=data)
```

### Example 2: Search Results
```python
from backend.models.result_history_schemas import ResultSearchRequest

search = ResultSearchRequest(
    query="residential",
    result_type=ResultType.SOLAR,
    is_favorite=True,
    page=1,
    page_size=20
)

results, total = service.search_results(user_id=1, search=search)
```

### Example 3: Compare Results
```python
comparison_data = service.compare_results(
    result_ids=[123, 456, 789],
    user_id=1,
    metrics=["system_size", "total_cost", "payback_period"]
)

print(f"Comparing {len(comparison_data['results'])} results")
print(f"Differences: {comparison_data['differences']}")
print(f"Summary: {comparison_data['summary']}")
```

### Example 4: Create Version
```python
new_version = service.create_version(
    parent_id=123,
    user_id=1,
    data=ResultHistoryCreate(
        result_type=ResultType.SOLAR,
        result_name="10kW Residential System (v2)",
        description="Updated with new modules",
        input_data={...},
        output_data={...}
    )
)
```

### Example 5: Share Result
```python
from backend.models.result_history_schemas import ResultShareCreate

share = service.create_share(
    user_id=1,
    data=ResultShareCreate(
        result_id=123,
        is_public=True,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
)

share_url = f"https://app.example.com/shared/{share.share_token}"
```

## Best Practices

1. **Always Add Tags**: Use tags for better organization and searchability
2. **Use Descriptive Names**: Make result names clear and descriptive
3. **Version Important Changes**: Create versions when making significant changes
4. **Archive Old Results**: Archive instead of delete to maintain history
5. **Set Share Expiration**: Always set expiration dates for shared results
6. **Regular Cleanup**: Periodically review and archive old results
7. **Use Favorites**: Mark important results as favorites for quick access
8. **Associate with Projects**: Link results to projects for better organization

## Security Considerations

1. **User Isolation**: Results are isolated by user_id
2. **Share Token Security**: Share tokens are cryptographically secure
3. **Expiration Enforcement**: Expired shares are automatically rejected
4. **Access Tracking**: All share access is logged
5. **Permission Control**: Edit permissions are enforced
6. **Data Validation**: All inputs are validated before storage

## Performance Optimization

1. **Indexed Queries**: All common queries use database indexes
2. **Pagination**: Large result sets are paginated
3. **Selective Loading**: Only load required data
4. **Caching**: Consider caching frequently accessed results
5. **Batch Operations**: Use batch operations for multiple results
6. **Archive Strategy**: Archive old results to improve query performance

## Troubleshooting

### Result Not Found
- Verify result_id is correct
- Check if result is archived (use include_archived=True)
- Verify user has access to the result

### Share Token Invalid
- Check if share has expired
- Verify token is correct
- Check if share was deleted

### Comparison Fails
- Verify all result_ids exist
- Check if user has access to all results
- Ensure results are compatible for comparison

### Search Returns No Results
- Check filter criteria
- Verify results exist for the user
- Check if results are archived

## Future Enhancements

1. **Export Formats**: Export results to PDF, Excel, CSV
2. **Bulk Operations**: Bulk tag, archive, delete operations
3. **Advanced Analytics**: Trend analysis, pattern detection
4. **Collaboration**: Real-time collaboration on shared results
5. **Notifications**: Notify users of share access
6. **Templates**: Save result configurations as templates
7. **AI Insights**: AI-powered result recommendations
8. **Integration**: Integration with external systems
