# Sales Pipeline System - Complete Guide

## Overview

The Sales Pipeline system provides comprehensive opportunity management with customizable stages, drag-and-drop interface, automation, analytics, and forecasting capabilities.

## Features

### 1. Customizable Pipeline Stages

- **Default Stages**: Lead, Qualified, Proposal, Negotiation, Closed Won, Closed Lost
- **Custom Stages**: Create unlimited custom stages
- **Stage Configuration**:
  - Name and description
  - Win probability percentage
  - Color coding
  - Icons
  - Time limits
  - Required fields
  - Automated actions

### 2. Drag-and-Drop Pipeline Board

- **Kanban-Style Interface**: Visual pipeline with drag-and-drop
- **Stage Columns**: Each stage displayed as a column
- **Opportunity Cards**: Compact cards showing key information
- **Quick Actions**: Click to view/edit, drag to move stages
- **Real-Time Updates**: Instant synchronization

### 3. Opportunity Management

#### Create/Edit Opportunities
- Name and description
- Contact information
- Estimated value and currency
- Win probability
- Expected close date
- Owner assignment
- Source tracking
- Custom fields and tags

#### Opportunity Actions
- Move between stages
- Mark as won/lost
- Add activities
- Attach products
- View history

### 4. Stage Automation

Configure automated actions when opportunities enter a stage:

- **Send Email**: Automated email notifications
- **Create Task**: Auto-create follow-up tasks
- **Update Fields**: Automatically update opportunity fields
- **Trigger Webhooks**: Integrate with external systems

### 5. Pipeline Analytics

#### Overview Metrics
- Total opportunities
- Total pipeline value
- Weighted value (probability-adjusted)
- Average deal size
- Win rate
- Average sales cycle

#### Breakdown Analysis
- By stage
- By owner
- By source
- By time period

#### Visualizations
- Bar charts
- Pie charts
- Trend lines
- Heat maps

### 6. Win/Loss Analysis

#### Metrics
- Total won/lost opportunities
- Win rate percentage
- Won/lost value
- Average deal sizes

#### Analysis
- Win reasons
- Loss reasons
- Competitor analysis
- Stage-by-stage breakdown

### 7. Pipeline Forecasting

#### Forecast Generation
- Period-based forecasting (monthly, quarterly)
- Expected wins and revenue
- Confidence levels
- Breakdown by stage and owner

#### Forecast Accuracy
- Based on historical data
- Probability-weighted calculations
- Data quality indicators

## API Endpoints

### Pipeline Stages

```
GET    /api/v1/pipeline/stages
POST   /api/v1/pipeline/stages
GET    /api/v1/pipeline/stages/{id}
PUT    /api/v1/pipeline/stages/{id}
DELETE /api/v1/pipeline/stages/{id}
POST   /api/v1/pipeline/stages/reorder
```

### Opportunities

```
GET    /api/v1/pipeline/opportunities
POST   /api/v1/pipeline/opportunities
GET    /api/v1/pipeline/opportunities/{id}
PUT    /api/v1/pipeline/opportunities/{id}
DELETE /api/v1/pipeline/opportunities/{id}
POST   /api/v1/pipeline/opportunities/{id}/change-stage
POST   /api/v1/pipeline/opportunities/{id}/win
POST   /api/v1/pipeline/opportunities/{id}/lose
```

### Analytics

```
GET    /api/v1/pipeline/analytics
GET    /api/v1/pipeline/analytics/win-loss
POST   /api/v1/pipeline/forecast
```

### Automation

```
GET    /api/v1/pipeline/automations
POST   /api/v1/pipeline/automations
PUT    /api/v1/pipeline/automations/{id}
DELETE /api/v1/pipeline/automations/{id}
```

## Database Schema

### Tables

1. **pipeline_stages**: Stage configuration
2. **opportunities**: Opportunity records
3. **opportunity_activities**: Activity log
4. **opportunity_stage_history**: Stage change tracking
5. **opportunity_products**: Products per opportunity
6. **pipeline_forecasts**: Forecast data
7. **pipeline_automations**: Automation rules

## Usage Examples

### Creating a Pipeline Stage

```typescript
const stage = await api.post('/api/v1/pipeline/stages', {
  name: 'Demo Scheduled',
  stage_type: 'qualified',
  order_index: 3,
  probability: 40.0,
  color: '#3B82F6',
  icon: 'pi pi-calendar',
  time_limit_days: 7,
  auto_actions: {
    actions: [
      {
        type: 'send_email',
        template: 'demo_scheduled',
        to: 'owner'
      }
    ]
  }
});
```

### Creating an Opportunity

```typescript
const opportunity = await api.post('/api/v1/pipeline/opportunities', {
  name: 'Solar Installation - ABC Corp',
  description: '50kW commercial installation',
  contact_name: 'John Doe',
  contact_email: 'john@abccorp.com',
  contact_phone: '+49 123 456789',
  stage_id: 1,
  estimated_value: 75000,
  currency: 'EUR',
  expected_close_date: '2024-12-31',
  owner_id: 1,
  source: 'Website',
  tags: ['commercial', 'high-value']
});
```

### Moving an Opportunity

```typescript
await api.post(`/api/v1/pipeline/opportunities/${oppId}/change-stage`, {
  stage_id: 3,
  reason: 'Proposal sent and accepted'
});
```

### Marking as Won

```typescript
await api.post(`/api/v1/pipeline/opportunities/${oppId}/win`, {
  actual_value: 78000,
  actual_close_date: '2024-11-15',
  win_reason: 'Best price and service package'
});
```

### Getting Analytics

```typescript
const analytics = await api.get('/api/v1/pipeline/analytics', {
  params: {
    start_date: '2024-01-01',
    end_date: '2024-12-31'
  }
});

console.log('Total Value:', analytics.total_value);
console.log('Win Rate:', analytics.win_rate);
console.log('Avg Deal Size:', analytics.average_deal_size);
```

### Generating Forecast

```typescript
const forecast = await api.post('/api/v1/pipeline/forecast', {
  period_start: '2024-12-01',
  period_end: '2025-02-28'
});

console.log('Expected Revenue:', forecast.expected_revenue);
console.log('Confidence:', forecast.confidence_level);
```

## Best Practices

### Stage Configuration

1. **Keep it Simple**: 4-6 stages is optimal
2. **Clear Definitions**: Each stage should have clear entry/exit criteria
3. **Realistic Probabilities**: Base on historical data
4. **Time Limits**: Set expected time in each stage
5. **Required Fields**: Enforce data quality

### Opportunity Management

1. **Regular Updates**: Keep opportunities current
2. **Accurate Values**: Update estimates as you learn more
3. **Close Dates**: Set realistic expected close dates
4. **Activities**: Log all interactions
5. **Win/Loss Reasons**: Always document outcomes

### Analytics Usage

1. **Regular Review**: Weekly pipeline reviews
2. **Trend Analysis**: Monitor changes over time
3. **Stage Velocity**: Track time in each stage
4. **Conversion Rates**: Monitor stage-to-stage conversion
5. **Forecast Accuracy**: Compare forecasts to actuals

### Automation

1. **Start Simple**: Begin with basic automations
2. **Test Thoroughly**: Verify automation behavior
3. **Monitor Results**: Track automation effectiveness
4. **Iterate**: Refine based on results
5. **Document**: Keep automation rules documented

## Troubleshooting

### Common Issues

**Opportunities Not Moving**
- Check stage permissions
- Verify required fields are filled
- Check automation rules

**Analytics Not Updating**
- Refresh the page
- Check date range filters
- Verify data exists for period

**Forecast Inaccurate**
- Ensure opportunities have close dates
- Set realistic probabilities
- Update opportunities regularly

## Integration

### CRM Integration

The pipeline system integrates with:
- Customer management
- Contact tracking
- Communication history
- Document management

### Product Integration

- Link products to opportunities
- Calculate total opportunity value
- Track product performance

### Reporting Integration

- Export pipeline data
- Custom reports
- Dashboard widgets

## Performance

### Optimization

- Pagination for large datasets
- Caching for analytics
- Lazy loading for stage columns
- Debounced drag-and-drop

### Scalability

- Handles 10,000+ opportunities
- Real-time updates via WebSocket
- Efficient database queries
- Indexed fields for fast search

## Security

### Access Control

- Role-based permissions
- Owner-based visibility
- Team-based access
- Admin controls

### Data Protection

- Encrypted sensitive data
- Audit logging
- Backup and recovery
- GDPR compliance

## Future Enhancements

- AI-powered win probability
- Predictive analytics
- Advanced automation workflows
- Mobile app
- Email integration
- Calendar sync
- Voice notes
- Document OCR

## Support

For issues or questions:
- Check documentation
- Review API reference
- Contact support team
- Submit feature requests
