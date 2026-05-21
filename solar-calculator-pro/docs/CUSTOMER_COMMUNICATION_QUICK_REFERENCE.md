# Customer Communication System - Quick Reference

## Overview

Comprehensive customer communication system with email, SMS, templates, scheduling, tracking, and analytics.

## Key Features

### 📧 Email Integration
- SMTP configuration with TLS/SSL support
- HTML email support with attachments
- CC/BCC support
- Reply-to configuration
- Rate limiting (daily/hourly)
- Error handling and retry logic

### 📱 SMS Integration
- Twilio provider support
- Nexmo/Vonage provider support
- Multiple recipient support
- Rate limiting
- Provider-agnostic interface

### 📝 Communication Templates
- Email and SMS templates
- Variable substitution ({{variable}})
- Template categories
- Usage tracking
- Default templates

### ⏰ Communication Scheduling
- One-time scheduled communications
- Recurring schedules (daily, weekly, monthly, yearly)
- Custom recurrence patterns
- Time-of-day scheduling
- Recipient criteria filtering

### 📊 Communication Tracking
- Status tracking (draft → sent → delivered → opened → clicked → replied)
- Timestamp tracking for all events
- Error message logging
- Retry count tracking
- Delivery confirmation

### 📈 Communication Analytics
- Engagement metrics (opens, clicks, replies, forwards)
- Timing metrics (time to open, click, reply)
- Device and browser tracking
- Location tracking
- Link click tracking
- Campaign statistics
- Delivery/open/click/reply rates

## Quick Start

### 1. Configure Email
```python
from backend.services.communication_service import CommunicationService
from backend.models.communication_schemas import EmailConfigCreate

email_config = EmailConfigCreate(
    name="Primary SMTP",
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_username="your-email@gmail.com",
    smtp_password="your-app-password",
    use_tls=True,
    from_email="your-email@gmail.com",
    from_name="Your Company",
    is_default=True
)

service = CommunicationService(db)
config = service.create_email_configuration(user_id=1, config=email_config)
```

### 2. Create Template
```python
from backend.models.communication_schemas import TemplateCreate, TemplateType

template = TemplateCreate(
    name="Welcome Email",
    type=TemplateType.EMAIL,
    subject="Welcome to {{company_name}}!",
    body="<h1>Hello {{customer_name}}</h1><p>Welcome to our service!</p>",
    variables=["company_name", "customer_name"],
    category="onboarding"
)

template_obj = service.create_template(user_id=1, template=template)
```

### 3. Send Email
```python
from backend.models.communication_schemas import CommunicationCreate, CommunicationType

communication = CommunicationCreate(
    customer_id=123,
    type=CommunicationType.EMAIL,
    subject="Welcome!",
    body="<h1>Hello John</h1><p>Welcome to our service!</p>",
    to_addresses=["customer@example.com"],
    template_id=template_obj.id
)

comm_obj = service.create_communication(user_id=1, communication=communication)
service.send_email(comm_obj.id)
```

### 4. Schedule Recurring Communication
```python
from backend.models.communication_schemas import ScheduleCreate
from datetime import datetime

schedule = ScheduleCreate(
    name="Weekly Newsletter",
    type=CommunicationType.EMAIL,
    is_recurring=True,
    recurrence_pattern="weekly",
    recurrence_days=[1],  # Monday
    start_date=datetime.now(),
    time_of_day="09:00",
    template_id=template_obj.id,
    recipient_criteria={"status": "active"}
)

schedule_obj = service.create_schedule(user_id=1, schedule=schedule)
```

### 5. Create Campaign
```python
from backend.models.communication_schemas import CampaignCreate

campaign = CampaignCreate(
    name="Summer Promotion",
    type=CommunicationType.EMAIL,
    description="Summer 2024 promotional campaign",
    start_date=datetime.now(),
    target_criteria={"segment": "premium"},
    template_id=template_obj.id
)

campaign_obj = service.create_campaign(user_id=1, campaign=campaign)
```

### 6. Get Analytics
```python
# Get communication analytics
analytics = service.get_communication_analytics(communication_id=comm_obj.id)

# Get campaign statistics
stats = service.get_campaign_statistics(campaign_id=campaign_obj.id)

# Get analytics summary
summary = service.get_analytics_summary(
    user_id=1,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31)
)
```

## Communication Status Flow

```
DRAFT → SCHEDULED → SENT → DELIVERED → OPENED → CLICKED → REPLIED
                      ↓
                   FAILED
                      ↓
                   BOUNCED
```

## Template Variables

Use `{{variable_name}}` syntax in templates:

```html
<h1>Hello {{customer_name}}</h1>
<p>Your order #{{order_number}} has been shipped!</p>
<p>Tracking: {{tracking_number}}</p>
```

## Recurrence Patterns

- **daily**: Every day
- **weekly**: Every week on specified days
- **monthly**: Every month on specified days
- **yearly**: Every year on specified date

## Rate Limiting

Configure limits per email/SMS configuration:
- `daily_limit`: Maximum sends per day
- `hourly_limit`: Maximum sends per hour

## Error Handling

Communications automatically retry on failure:
- `retry_count`: Number of retry attempts
- `error_message`: Last error message
- Maximum 3 retries before marking as FAILED

## Best Practices

1. **Use Templates**: Create reusable templates for common communications
2. **Test First**: Send test emails before bulk campaigns
3. **Monitor Analytics**: Track open and click rates
4. **Segment Recipients**: Use criteria to target specific customer groups
5. **Schedule Wisely**: Send at optimal times for your audience
6. **Handle Bounces**: Monitor bounce rates and clean lists
7. **Respect Limits**: Configure appropriate rate limits
8. **Track Engagement**: Use analytics to improve future communications

## Database Tables

- `communications`: Communication records
- `communication_templates`: Reusable templates
- `communication_campaigns`: Campaign management
- `communication_schedules`: Recurring schedules
- `communication_analytics`: Engagement tracking
- `email_configurations`: SMTP settings
- `sms_configurations`: SMS provider settings

## API Endpoints (To Be Implemented)

- `POST /api/v1/communications` - Create communication
- `GET /api/v1/communications` - List communications
- `GET /api/v1/communications/{id}` - Get communication
- `PUT /api/v1/communications/{id}` - Update communication
- `DELETE /api/v1/communications/{id}` - Delete communication
- `POST /api/v1/communications/{id}/send` - Send communication
- `POST /api/v1/communications/bulk` - Bulk create
- `GET /api/v1/communications/{id}/analytics` - Get analytics
- `POST /api/v1/templates` - Create template
- `GET /api/v1/templates` - List templates
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/campaigns` - List campaigns
- `GET /api/v1/campaigns/{id}/stats` - Campaign statistics
- `POST /api/v1/schedules` - Create schedule
- `GET /api/v1/schedules` - List schedules
- `POST /api/v1/email-configs` - Create email config
- `POST /api/v1/sms-configs` - Create SMS config

## Support

For issues or questions:
- Check error logs in `communication.error_message`
- Review analytics for delivery issues
- Verify configuration settings
- Test with single recipient first

## Next Steps

1. Run database migration
2. Configure email/SMS providers
3. Create templates
4. Test with sample communications
5. Set up campaigns and schedules
6. Monitor analytics and optimize
