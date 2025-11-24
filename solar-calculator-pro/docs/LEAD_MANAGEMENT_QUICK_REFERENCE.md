# Lead Management - Quick Reference

## Quick Start

### Create a Lead

```bash
curl -X POST http://localhost:8000/api/v1/leads/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Max",
    "last_name": "Mustermann",
    "email": "max@example.com",
    "phone": "+49 30 12345678",
    "company": "Example GmbH",
    "source": "website",
    "priority": "high",
    "estimated_value": 75000.00
  }'
```

### Get All Leads

```bash
curl http://localhost:8000/api/v1/leads/?limit=50
```

### Get Lead by ID

```bash
curl http://localhost:8000/api/v1/leads/123
```

### Update Lead

```bash
curl -X PUT http://localhost:8000/api/v1/leads/123 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "qualified",
    "priority": "urgent"
  }'
```

### Assign Lead

```bash
curl -X POST http://localhost:8000/api/v1/leads/123/assign \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 123,
    "assign_to_user_id": 5
  }'
```

## Lead Statuses

| Status | Description |
|--------|-------------|
| `new` | Freshly captured, not contacted |
| `contacted` | Initial contact made |
| `qualified` | Meets qualification criteria |
| `proposal` | Proposal sent |
| `negotiation` | In negotiation |
| `won` | Converted to customer |
| `lost` | Did not convert |
| `nurturing` | In nurturing campaign |

## Lead Sources

| Source | Description |
|--------|-------------|
| `website` | Website form submission |
| `referral` | Customer referral |
| `social_media` | Social media channels |
| `email_campaign` | Email marketing |
| `phone` | Phone inquiry |
| `event` | Trade show/event |
| `partner` | Partner referral |
| `advertisement` | Paid advertising |
| `organic_search` | Organic search |
| `paid_search` | Paid search |
| `other` | Other sources |

## Lead Priorities

| Priority | Description |
|----------|-------------|
| `low` | Low priority |
| `medium` | Medium priority (default) |
| `high` | High priority |
| `urgent` | Urgent attention needed |

## Scoring Rules

### Create Scoring Rule

```bash
curl -X POST http://localhost:8000/api/v1/leads/scoring-rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Value Lead",
    "category": "demographic",
    "field": "estimated_value",
    "operator": "greater_than",
    "value": "50000",
    "points": 25,
    "active": true
  }'
```

### Operators

- `equals` - Exact match
- `not_equals` - Not equal
- `contains` - Contains substring
- `not_contains` - Does not contain
- `greater_than` - Greater than (numeric)
- `less_than` - Less than (numeric)
- `is_empty` - Field is empty
- `is_not_empty` - Field has value

### Categories

- `demographic` - Company, location, industry
- `behavioral` - Website activity, downloads
- `engagement` - Responses, meetings, calls

## Assignment Rules

### Create Assignment Rule

```bash
curl -X POST http://localhost:8000/api/v1/leads/assignment-rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Value to Senior Rep",
    "conditions": {
      "priority": "urgent",
      "estimated_value": ">50000"
    },
    "assign_to_user_id": 5,
    "assignment_method": "direct",
    "active": true
  }'
```

## Activities

### Create Activity

```bash
curl -X POST http://localhost:8000/api/v1/leads/123/activities \
  -H "Content-Type: application/json" \
  -d '{
    "activity_type": "call",
    "subject": "Initial consultation",
    "description": "Discussed requirements",
    "outcome": "interested",
    "duration_minutes": 30
  }'
```

### Activity Types

- `call` - Phone call
- `email` - Email communication
- `meeting` - In-person/virtual meeting
- `note` - General note
- `task` - Task/to-do
- `demo` - Product demonstration

## Nurturing Campaigns

### Create Campaign

```bash
curl -X POST http://localhost:8000/api/v1/leads/123/nurturing \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Solar Education Series",
    "campaign_type": "educational",
    "total_steps": 5
  }'
```

## Conversion

### Convert Lead to Customer

```bash
curl -X POST http://localhost:8000/api/v1/leads/123/convert?customer_id=456
```

## Analytics

### Dashboard Metrics

```bash
curl http://localhost:8000/api/v1/leads/analytics/dashboard
```

### Source Analytics

```bash
curl "http://localhost:8000/api/v1/leads/analytics/sources?start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z"
```

### Conversion Tracking

```bash
curl "http://localhost:8000/api/v1/leads/conversion/tracking?start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z"
```

## Filtering

### Filter by Status

```bash
curl "http://localhost:8000/api/v1/leads/?status=qualified"
```

### Filter by Source

```bash
curl "http://localhost:8000/api/v1/leads/?source=website"
```

### Filter by Score

```bash
curl "http://localhost:8000/api/v1/leads/?min_score=70"
```

### Filter by Assignment

```bash
curl "http://localhost:8000/api/v1/leads/?assigned_to_id=5"
```

### Search

```bash
curl "http://localhost:8000/api/v1/leads/?search=example"
```

### Combined Filters

```bash
curl "http://localhost:8000/api/v1/leads/?status=qualified&min_score=50&source=website&limit=20"
```

## Common Workflows

### New Lead Workflow

1. Create lead
2. System auto-scores lead
3. System auto-assigns based on rules
4. Sales rep contacts lead
5. Create activity record
6. Update lead status
7. Continue nurturing or convert

### Lead Qualification

1. Review lead score
2. Check contact history
3. Verify interest level
4. Update status to "qualified"
5. Assign to appropriate rep
6. Schedule follow-up

### Lead Conversion

1. Verify qualification
2. Create customer record
3. Convert lead
4. Update analytics
5. Close nurturing campaigns

## Best Practices

### Scoring

- Review rules quarterly
- Balance point distribution
- Test before activating
- Monitor score distribution

### Assignment

- Define clear criteria
- Ensure fair distribution
- Match skills to leads
- Balance workload

### Activities

- Record all interactions
- Be specific in descriptions
- Set follow-up dates
- Track outcomes

### Data Quality

- Remove duplicates
- Validate email addresses
- Keep information current
- Enrich missing data

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (deleted) |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

## Support

- API Documentation: `/docs`
- Full Guide: `LEAD_MANAGEMENT_GUIDE.md`
- System Admin: Contact IT support
