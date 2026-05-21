# CRM Advanced Service - Quick Reference

## Service Initialization

```python
from services.crm_advanced_service import CRMAdvancedService

crm_service = CRMAdvancedService(database_path="crm_database.db")
```

## Lead Scoring

```python
# Calculate lead score
score = crm_service.calculate_lead_score(lead_id=123)

# Get all lead scores
scores = crm_service.get_lead_scores(filters={'min_score': 70})

# Update scoring weights
weights = {'engagement': 0.3, 'demographics': 0.2, 'behavior': 0.5}
crm_service.update_lead_score_weights(weights)
```

## Pipeline Automation

```python
# Automate pipeline stage
rules = {'qualification_threshold': 70, 'assignment_threshold': 80}
result = crm_service.automate_pipeline_stage(lead_id=123, rules=rules)
```

## Email Campaigns

```python
# Create campaign
campaign_data = {
    'name': 'Summer Sale',
    'subject': 'Special Offer',
    'content': '<html>...</html>'
}
campaign_id = crm_service.create_email_campaign(campaign_data)

# Send campaign
crm_service.send_campaign_email(campaign_id, recipient_ids=[1, 2, 3])

# Get analytics
analytics = crm_service.get_campaign_analytics(campaign_id)
```

## Customer Segmentation

```python
# Create segment
segment_data = {
    'name': 'High Value',
    'criteria': {'lifetime_value': {'min': 10000}}
}
segment_id = crm_service.create_customer_segment(segment_data)

# Get segment customers
customers = crm_service.get_segment_customers(segment_id)

# Analyze segment
analysis = crm_service.analyze_segment(segment_id)
```

## Forecasting

```python
# Generate sales forecast
forecast = crm_service.generate_sales_forecast('quarter')

# Get pipeline forecast
pipeline_forecast = crm_service.get_pipeline_forecast()

# Analyze accuracy
accuracy = crm_service.analyze_forecast_accuracy('month')
```

## Contract Management

```python
# Create contract
contract_data = {
    'customer_id': 123,
    'contract_type': 'service',
    'start_date': datetime.now(),
    'end_date': datetime.now() + timedelta(days=365),
    'value': 50000.0
}
contract_id = crm_service.create_contract(contract_data)

# Get contract
contract = crm_service.get_contract(contract_id)

# Get expiring contracts
expiring = crm_service.get_expiring_contracts(days=30)
```

## Warranty Tracking

```python
# Register warranty
warranty_data = {
    'product_id': 456,
    'customer_id': 123,
    'purchase_date': datetime.now(),
    'warranty_period_months': 24
}
warranty_id = crm_service.register_warranty(warranty_data)

# Get warranty status
status = crm_service.get_warranty_status(warranty_id)

# Get active warranties
active = crm_service.get_active_warranties(customer_id=123)
```

## Customer Feedback

```python
# Submit feedback
feedback_data = {
    'customer_id': 123,
    'rating': 5,
    'category': 'service',
    'comment': 'Excellent!'
}
feedback_id = crm_service.submit_feedback(feedback_data)

# Get feedback
feedback = crm_service.get_feedback(feedback_id)

# Analyze feedback
analysis = crm_service.analyze_feedback(filters={'category': 'service'})

# Get trends
trends = crm_service.get_feedback_trends('month')
```

## Geo Mapping

```python
# Geocode address
location = crm_service.geocode_address("Hauptstraße 123, Berlin")

# Get customers in area
center = {'lat': 52.5200, 'lon': 13.4050}
customers = crm_service.get_customers_in_area(center, radius_km=10.0)

# Optimize route
locations = [{'lat': 52.52, 'lon': 13.40}, {'lat': 52.53, 'lon': 13.41}]
route = crm_service.optimize_route(locations)
```

## Knowledge Base

```python
# Create article
article_data = {
    'title': 'Installation Guide',
    'content': '...',
    'category': 'support',
    'tags': ['installation'],
    'author_id': 1
}
article_id = crm_service.create_kb_article(article_data)

# Search KB
results = crm_service.search_kb('installation guide')

# Get article
article = crm_service.get_kb_article(article_id)

# Get popular articles
popular = crm_service.get_popular_kb_articles(limit=10)
```

## Additional Features

```python
# Create offer
offer_id = crm_service.create_offer(offer_data)

# Track offer status
status = crm_service.track_offer_status(offer_id)

# Create task
task_id = crm_service.create_task(task_data)

# Get tasks
tasks = crm_service.get_tasks(filters={'status': 'open'})

# Create note
note_id = crm_service.create_note(note_data)

# Log call
call_id = crm_service.log_call(call_data)

# Get call history
history = crm_service.get_call_history(customer_id=123)

# Generate report
report = crm_service.generate_report('sales', parameters={})

# Get dashboard data
dashboard = crm_service.get_dashboard_data(user_id=1)
```

## Health Check

```python
# Check health of all modules
health = crm_service.health_check()
# Returns: {'overall': 'healthy', 'modules': {...}}
```

## API Endpoints

### Lead Scoring
- `POST /api/v1/crm-advanced/lead-scoring/calculate`
- `GET /api/v1/crm-advanced/lead-scoring/scores`
- `PUT /api/v1/crm-advanced/lead-scoring/weights`

### Pipeline
- `POST /api/v1/crm-advanced/pipeline/automate`

### Email Campaigns
- `POST /api/v1/crm-advanced/email-campaigns`
- `POST /api/v1/crm-advanced/email-campaigns/send`
- `GET /api/v1/crm-advanced/email-campaigns/{id}/analytics`

### Segmentation
- `POST /api/v1/crm-advanced/segments`
- `GET /api/v1/crm-advanced/segments/{id}/customers`
- `GET /api/v1/crm-advanced/segments/{id}/analyze`

### Forecasting
- `POST /api/v1/crm-advanced/forecasting/sales`
- `GET /api/v1/crm-advanced/forecasting/pipeline`
- `GET /api/v1/crm-advanced/forecasting/accuracy/{period}`

### Contracts
- `POST /api/v1/crm-advanced/contracts`
- `GET /api/v1/crm-advanced/contracts/{id}`
- `GET /api/v1/crm-advanced/contracts/expiring`

### Warranties
- `POST /api/v1/crm-advanced/warranties`
- `GET /api/v1/crm-advanced/warranties/{id}`
- `GET /api/v1/crm-advanced/warranties/active`

### Feedback
- `POST /api/v1/crm-advanced/feedback`
- `GET /api/v1/crm-advanced/feedback/{id}`
- `GET /api/v1/crm-advanced/feedback/analyze`
- `GET /api/v1/crm-advanced/feedback/trends`

### Geo Mapping
- `POST /api/v1/crm-advanced/geo/geocode`
- `POST /api/v1/crm-advanced/geo/customers-in-area`

### Knowledge Base
- `POST /api/v1/crm-advanced/knowledge-base/articles`
- `GET /api/v1/crm-advanced/knowledge-base/search`
- `GET /api/v1/crm-advanced/knowledge-base/articles/{id}`
- `GET /api/v1/crm-advanced/knowledge-base/popular`

### Health
- `GET /api/v1/crm-advanced/health`

## Error Handling

All methods raise exceptions on error. Always wrap in try-except:

```python
try:
    result = crm_service.calculate_lead_score(lead_id)
except Exception as e:
    logger.error(f"Error: {e}")
    # Handle error
```

## Requirements

- Requirements: 1.3, 6.1
- Python 3.10+
- FastAPI 0.100+
- All legacy CRM modules
