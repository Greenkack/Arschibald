# CRM Advanced Service Guide

## Overview

The CRM Advanced Service provides comprehensive customer relationship management functionality by wrapping all legacy CRM modules from the Streamlit application. It offers advanced features including lead scoring, sales pipeline automation, email campaigns, customer segmentation, forecasting, contract management, warranty tracking, customer feedback, geo mapping, and knowledge base management.

## Architecture

The CRM Advanced Service follows a modular architecture that wraps existing CRM functionality:

```
CRMAdvancedService
├── Lead Scoring Engine
├── Email Manager
├── Forecasting Engine
├── Contract Manager
├── Feedback Manager
├── Geo Mapper
├── Knowledge Base
├── Offer Tracker
├── Task Manager
├── Note Manager
├── Tag Manager
├── Reporting Engine
├── Dashboard Widgets
├── Template Manager
└── Call Manager
```

## Features

### 1. Lead Scoring

Automatically score leads based on multiple factors:

- **Engagement Score**: Based on interactions and activities
- **Demographics Score**: Based on company size, industry, location
- **Behavior Score**: Based on website visits, email opens, downloads
- **Custom Weights**: Configurable scoring weights

**API Endpoints:**
- `POST /api/v1/crm-advanced/lead-scoring/calculate` - Calculate lead score
- `GET /api/v1/crm-advanced/lead-scoring/scores` - Get all lead scores
- `PUT /api/v1/crm-advanced/lead-scoring/weights` - Update scoring weights

**Example:**
```python
# Calculate lead score
result = crm_service.calculate_lead_score(lead_id=123)
# Returns: {
#     'total_score': 85,
#     'breakdown': {
#         'engagement': 30,
#         'demographics': 25,
#         'behavior': 30
#     }
# }
```

### 2. Sales Pipeline Automation

Automatically move leads through pipeline stages based on rules:

- **Stage Automation**: Auto-advance based on score thresholds
- **Assignment Rules**: Auto-assign to sales reps
- **Notification Triggers**: Alert team members
- **Custom Rules**: Define custom automation logic

**API Endpoints:**
- `POST /api/v1/crm-advanced/pipeline/automate` - Automate pipeline stage

**Example:**
```python
# Automate pipeline
rules = {
    'qualification_threshold': 70,
    'assignment_threshold': 80
}
result = crm_service.automate_pipeline_stage(lead_id=123, rules=rules)
```

### 3. Email Campaign Management

Create and manage email marketing campaigns:

- **Campaign Creation**: Design and schedule campaigns
- **Recipient Segmentation**: Target specific customer segments
- **Analytics**: Track opens, clicks, conversions
- **A/B Testing**: Test different email variations
- **Scheduling**: Schedule campaigns for optimal timing

**API Endpoints:**
- `POST /api/v1/crm-advanced/email-campaigns` - Create campaign
- `POST /api/v1/crm-advanced/email-campaigns/send` - Send campaign
- `GET /api/v1/crm-advanced/email-campaigns/{id}/analytics` - Get analytics

**Example:**
```python
# Create email campaign
campaign_data = {
    'name': 'Summer Promotion',
    'subject': 'Special Offer Inside!',
    'content': '<html>...</html>',
    'segment_id': 5
}
campaign_id = crm_service.create_email_campaign(campaign_data)

# Send campaign
result = crm_service.send_campaign_email(
    campaign_id=campaign_id,
    recipient_ids=[1, 2, 3, 4, 5]
)
```

### 4. Customer Segmentation

Segment customers based on various criteria:

- **Demographic Segmentation**: Age, location, company size
- **Behavioral Segmentation**: Purchase history, engagement
- **Value Segmentation**: Lifetime value, revenue potential
- **Custom Segments**: Define custom segmentation rules

**API Endpoints:**
- `POST /api/v1/crm-advanced/segments` - Create segment
- `GET /api/v1/crm-advanced/segments/{id}/customers` - Get segment customers
- `GET /api/v1/crm-advanced/segments/{id}/analyze` - Analyze segment

**Example:**
```python
# Create customer segment
segment_data = {
    'name': 'High Value Customers',
    'criteria': {
        'lifetime_value': {'min': 10000},
        'engagement_score': {'min': 70}
    }
}
segment_id = crm_service.create_customer_segment(segment_data)

# Analyze segment
analysis = crm_service.analyze_segment(segment_id)
```

### 5. Sales Forecasting

Generate accurate sales forecasts:

- **Time-Based Forecasts**: Monthly, quarterly, yearly
- **Pipeline Forecasts**: Based on current pipeline
- **Accuracy Analysis**: Track forecast accuracy
- **Trend Analysis**: Identify sales trends

**API Endpoints:**
- `POST /api/v1/crm-advanced/forecasting/sales` - Generate forecast
- `GET /api/v1/crm-advanced/forecasting/pipeline` - Get pipeline forecast
- `GET /api/v1/crm-advanced/forecasting/accuracy/{period}` - Analyze accuracy

**Example:**
```python
# Generate sales forecast
forecast = crm_service.generate_sales_forecast(
    period='quarter',
    parameters={'confidence_level': 0.95}
)
```

### 6. Contract Management

Manage customer contracts:

- **Contract Creation**: Create and store contracts
- **Status Tracking**: Track contract status
- **Renewal Alerts**: Alert for expiring contracts
- **Version Control**: Track contract versions
- **E-Signature Integration**: Digital signatures

**API Endpoints:**
- `POST /api/v1/crm-advanced/contracts` - Create contract
- `GET /api/v1/crm-advanced/contracts/{id}` - Get contract
- `GET /api/v1/crm-advanced/contracts/expiring` - Get expiring contracts

**Example:**
```python
# Create contract
contract_data = {
    'customer_id': 123,
    'contract_type': 'service',
    'start_date': datetime.now(),
    'end_date': datetime.now() + timedelta(days=365),
    'value': 50000.0,
    'terms': {...}
}
contract_id = crm_service.create_contract(contract_data)

# Get expiring contracts
expiring = crm_service.get_expiring_contracts(days=30)
```

### 7. Warranty Tracking

Track product warranties:

- **Warranty Registration**: Register new warranties
- **Status Tracking**: Track warranty status
- **Expiration Alerts**: Alert for expiring warranties
- **Claim Management**: Manage warranty claims
- **History Tracking**: Track warranty history

**API Endpoints:**
- `POST /api/v1/crm-advanced/warranties` - Register warranty
- `GET /api/v1/crm-advanced/warranties/{id}` - Get warranty status
- `GET /api/v1/crm-advanced/warranties/active` - Get active warranties

**Example:**
```python
# Register warranty
warranty_data = {
    'product_id': 456,
    'customer_id': 123,
    'purchase_date': datetime.now(),
    'warranty_period_months': 24
}
warranty_id = crm_service.register_warranty(warranty_data)
```

### 8. Customer Feedback System

Collect and analyze customer feedback:

- **Feedback Collection**: Multiple feedback channels
- **Rating System**: 1-5 star ratings
- **Sentiment Analysis**: Analyze feedback sentiment
- **Trend Tracking**: Track feedback trends
- **Action Items**: Generate action items from feedback

**API Endpoints:**
- `POST /api/v1/crm-advanced/feedback` - Submit feedback
- `GET /api/v1/crm-advanced/feedback/{id}` - Get feedback
- `GET /api/v1/crm-advanced/feedback/analyze` - Analyze feedback
- `GET /api/v1/crm-advanced/feedback/trends` - Get trends

**Example:**
```python
# Submit feedback
feedback_data = {
    'customer_id': 123,
    'rating': 5,
    'category': 'service',
    'comment': 'Excellent service and support!'
}
feedback_id = crm_service.submit_feedback(feedback_data)

# Analyze feedback
analysis = crm_service.analyze_feedback(
    filters={'category': 'service'}
)
```

### 9. Geo Mapping

Geographic analysis and mapping:

- **Geocoding**: Convert addresses to coordinates
- **Proximity Search**: Find customers in area
- **Territory Mapping**: Define sales territories
- **Route Optimization**: Optimize visit routes
- **Heat Maps**: Visualize customer distribution

**API Endpoints:**
- `POST /api/v1/crm-advanced/geo/geocode` - Geocode address
- `POST /api/v1/crm-advanced/geo/customers-in-area` - Get customers in area

**Example:**
```python
# Geocode address
location = crm_service.geocode_address(
    "Hauptstraße 123, 10115 Berlin, Germany"
)

# Find customers in area
center = {'lat': 52.5200, 'lon': 13.4050}
customers = crm_service.get_customers_in_area(
    center=center,
    radius_km=10.0
)
```

### 10. Knowledge Base

Manage internal knowledge base:

- **Article Management**: Create and manage articles
- **Search**: Full-text search
- **Categories**: Organize by categories
- **Tags**: Tag articles for easy discovery
- **Analytics**: Track article views and popularity

**API Endpoints:**
- `POST /api/v1/crm-advanced/knowledge-base/articles` - Create article
- `GET /api/v1/crm-advanced/knowledge-base/search` - Search articles
- `GET /api/v1/crm-advanced/knowledge-base/articles/{id}` - Get article
- `GET /api/v1/crm-advanced/knowledge-base/popular` - Get popular articles

**Example:**
```python
# Create KB article
article_data = {
    'title': 'How to Install Solar Panels',
    'content': '...',
    'category': 'installation',
    'tags': ['solar', 'installation', 'guide'],
    'author_id': 1
}
article_id = crm_service.create_kb_article(article_data)

# Search KB
results = crm_service.search_kb(
    query='solar panel installation',
    filters={'category': 'installation'}
)
```

## Integration with Legacy Modules

The CRM Advanced Service integrates with the following legacy modules:

1. **crm/features/lead_scoring.py** - Lead scoring algorithms
2. **crm/features/email_manager.py** - Email campaign management
3. **crm/features/forecasting_engine.py** - Sales forecasting
4. **crm/features/contract_manager.py** - Contract management
5. **crm/features/feedback_manager.py** - Customer feedback
6. **crm/features/geo_mapper.py** - Geographic mapping
7. **crm/features/knowledge_base.py** - Knowledge base
8. **crm/features/offer_tracker.py** - Offer tracking
9. **crm/features/task_manager.py** - Task management
10. **crm/features/note_manager.py** - Note management
11. **crm/features/tag_manager.py** - Tag management
12. **crm/features/reporting_engine.py** - Reporting
13. **crm/features/dashboard_widgets.py** - Dashboard widgets
14. **crm/features/template_manager.py** - Template management
15. **crm/features/call_manager.py** - Call logging

## Error Handling

The service implements comprehensive error handling:

```python
try:
    result = crm_service.calculate_lead_score(lead_id)
except Exception as e:
    logger.error(f"Error calculating lead score: {e}")
    # Handle error appropriately
```

## Health Check

Monitor the health of all CRM modules:

```python
health_status = crm_service.health_check()
# Returns:
# {
#     'overall': 'healthy',
#     'modules': {
#         'lead_scoring': 'ok',
#         'email_manager': 'ok',
#         'forecasting': 'ok',
#         ...
#     }
# }
```

## Best Practices

1. **Use Dependency Injection**: Always use FastAPI's dependency injection for service instances
2. **Handle Errors Gracefully**: Wrap service calls in try-except blocks
3. **Validate Input**: Use Pydantic models for request validation
4. **Monitor Performance**: Use health checks to monitor module performance
5. **Log Operations**: Log all important operations for debugging
6. **Cache Results**: Cache frequently accessed data
7. **Batch Operations**: Use batch operations for bulk updates

## Requirements

- Python 3.10+
- FastAPI 0.100+
- SQLAlchemy (async)
- All legacy CRM modules

## See Also

- [API Documentation](./API_DOCUMENTATION.md)
- [CRM System Deep Analysis](../../docs/CRM_SYSTEM_DEEP_ANALYSIS.md)
- [Legacy Wrapper Guide](./LEGACY_WRAPPER_GUIDE.md)
