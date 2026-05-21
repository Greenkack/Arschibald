# CRM Service Guide

## Overview

The CRM Service provides a comprehensive API for managing customer relationships, including:
- Customer management (CRUD operations)
- Offer tracking and follow-ups
- Task management with priorities and due dates
- Communication history and notes

## Architecture

The CRM Service wraps the existing CRM modules from the legacy Streamlit application:
- `crm/features/offer_tracker.py` - Offer tracking functionality
- `crm/features/task_manager.py` - Task management functionality
- `crm/features/note_manager.py` - Communication history and notes

## Service Initialization

```python
from backend.services.crm_service import get_crm_service

# Get the singleton service instance
crm_service = get_crm_service()

# Check service health
health = crm_service.health_check()
print(f"Service status: {health.status}")
```

## Customer Management

### Create a Customer

```python
customer_data = {
    "first_name": "Max",
    "last_name": "Mustermann",
    "company_name": "Mustermann GmbH",
    "email": "max@mustermann.de",
    "phone_mobile": "+49 170 1234567",
    "street": "Musterstraße 123",
    "city": "Berlin",
    "postal_code": "10115",
    "country": "Deutschland"
}

customer = crm_service.create_customer(customer_data)
print(f"Created customer ID: {customer['id']}")
```

### Get a Customer

```python
customer = crm_service.get_customer(customer_id=1)
print(f"Customer: {customer['first_name']} {customer['last_name']}")
```

### List Customers

```python
# List all customers
customers = crm_service.list_customers(limit=100, offset=0)

# Search customers
customers = crm_service.list_customers(search="Mustermann")
```

### Update a Customer

```python
update_data = {
    "email": "new.email@mustermann.de",
    "phone_mobile": "+49 170 9876543"
}

updated_customer = crm_service.update_customer(customer_id=1, customer_data=update_data)
```

### Delete a Customer

```python
success = crm_service.delete_customer(customer_id=1)
```

## Offer Tracking

### Get Offer Status

```python
offer = crm_service.get_offer_status(project_id=1)
print(f"Offer status: {offer['offer_status']}")
print(f"Offer value: {offer['offer_value']} EUR")
```

### Update Offer Status

```python
# Mark offer as sent
success = crm_service.update_offer_status(
    project_id=1,
    new_status="sent",
    offer_value=25000.00,
    offer_version=1
)

# Mark offer as accepted
success = crm_service.update_offer_status(
    project_id=1,
    new_status="accepted"
)

# Mark offer as rejected
success = crm_service.update_offer_status(
    project_id=1,
    new_status="rejected",
    rejection_reason="Preis zu hoch",
    rejection_notes="Kunde möchte günstigeres Angebot"
)
```

### List Offers

```python
# List all offers
offers = crm_service.list_offers()

# Filter by status
sent_offers = crm_service.list_offers(status_filter="sent")
accepted_offers = crm_service.list_offers(status_filter="accepted")
```

### Get Pending Follow-ups

```python
follow_ups = crm_service.get_pending_follow_ups()
for follow_up in follow_ups:
    print(f"Project: {follow_up['project_name']}")
    print(f"Follow-up date: {follow_up['follow_up_date']}")
```

### Mark Follow-up as Completed

```python
success = crm_service.mark_follow_up_completed(project_id=1)
```

### Get Offer Statistics

```python
stats = crm_service.get_offer_statistics()
print(f"Total offers: {stats['total_offers']}")
print(f"Conversion rate: {stats['conversion_rate']}%")
print(f"Average offer value: {stats['avg_offer_value']} EUR")
```

## Task Management

### Create a Task

```python
from datetime import date, timedelta

task_data = {
    "title": "Angebot nachfassen",
    "description": "Kunde anrufen und nach Entscheidung fragen",
    "status": "open",
    "priority": "high",
    "due_date": date.today() + timedelta(days=7),
    "customer_id": 1,
    "project_id": 1,
    "assigned_to": "Max Mustermann"
}

task_id = crm_service.create_task(task_data)
print(f"Created task ID: {task_id}")
```

### Get a Task

```python
task = crm_service.get_task(task_id=1)
print(f"Task: {task['title']}")
print(f"Status: {task['status']}")
print(f"Priority: {task['priority']}")
```

### List Tasks

```python
# List all tasks
tasks = crm_service.list_tasks()

# Filter by status
open_tasks = crm_service.list_tasks(filters={"status": "open"})

# Filter by priority
high_priority_tasks = crm_service.list_tasks(filters={"priority": "high"})

# Filter by customer
customer_tasks = crm_service.list_tasks(filters={"customer_id": 1})

# Get overdue tasks
overdue_tasks = crm_service.list_tasks(filters={"overdue_only": True})

# Get tasks due soon
due_soon = crm_service.list_tasks(filters={"due_soon_days": 7})
```

### Update a Task

```python
update_data = {
    "status": "in_progress",
    "priority": "medium"
}

success = crm_service.update_task(task_id=1, task_data=update_data)
```

### Mark Task as Completed

```python
success = crm_service.mark_task_completed(task_id=1)
```

### Delete a Task

```python
success = crm_service.delete_task(task_id=1)
```

### Get Task Statistics

```python
stats = crm_service.get_task_statistics()
print(f"Total tasks: {stats['total']}")
print(f"Overdue tasks: {stats['overdue']}")
print(f"Due today: {stats['due_today']}")
print(f"Due this week: {stats['due_this_week']}")
```

## Communication History and Notes

### Create an Activity

```python
activity_data = {
    "customer_id": 1,
    "activity_type": "note",
    "title": "Telefonat mit Kunde",
    "content": "Kunde ist sehr interessiert. Möchte Angebot bis Ende der Woche.",
    "created_by": "Max Mustermann",
    "is_important": True
}

activity_id = crm_service.create_activity(activity_data)
```

### Activity Types

- `note` - General note
- `email` - Email communication
- `call` - Phone call
- `appointment` - Appointment/meeting
- `meeting` - Meeting
- `task` - Task-related activity
- `other` - Other activity

### Get an Activity

```python
activity = crm_service.get_activity(activity_id=1)
print(f"Activity: {activity['title']}")
print(f"Type: {activity['activity_type_display']}")
```

### Get Customer Activities

```python
# Get all activities for a customer
activities = crm_service.get_customer_activities(customer_id=1)

# Filter by activity type
calls = crm_service.get_customer_activities(
    customer_id=1,
    activity_type="call"
)

# Include archived activities
all_activities = crm_service.get_customer_activities(
    customer_id=1,
    include_archived=True
)
```

### Update an Activity

```python
update_data = {
    "title": "Updated title",
    "content": "Updated content",
    "is_important": False
}

success = crm_service.update_activity(activity_id=1, activity_data=update_data)
```

### Delete an Activity

```python
success = crm_service.delete_activity(activity_id=1)
```

### Search Activities

```python
# Search in all activities
results = crm_service.search_activities(search_term="Angebot")

# Search for specific customer
results = crm_service.search_activities(
    search_term="Angebot",
    customer_id=1
)

# Search by activity type
results = crm_service.search_activities(
    search_term="Angebot",
    activity_type="note"
)
```

### Get Activity Statistics

```python
stats = crm_service.get_activity_statistics(customer_id=1)
print(f"Total activities: {stats['total']}")
print(f"Important activities: {stats['important']}")
print(f"Last activity: {stats['last_activity']}")
print(f"By type: {stats['by_type']}")
```

## Error Handling

The CRM Service uses the standard error handling framework:

```python
from backend.services.crm_service import get_crm_service

try:
    crm_service = get_crm_service()
    customer = crm_service.get_customer(customer_id=999)
except ValueError as e:
    print(f"Validation error: {e}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## API Endpoints

All CRM functionality is exposed via REST API endpoints:

### Customer Endpoints
- `POST /api/v1/crm/customers` - Create customer
- `GET /api/v1/crm/customers/{customer_id}` - Get customer
- `GET /api/v1/crm/customers` - List customers
- `PUT /api/v1/crm/customers/{customer_id}` - Update customer
- `DELETE /api/v1/crm/customers/{customer_id}` - Delete customer

### Offer Endpoints
- `GET /api/v1/crm/offers/{project_id}` - Get offer status
- `PUT /api/v1/crm/offers/{project_id}/status` - Update offer status
- `GET /api/v1/crm/offers` - List offers
- `GET /api/v1/crm/offers/follow-ups/pending` - Get pending follow-ups
- `POST /api/v1/crm/offers/{project_id}/follow-up/complete` - Mark follow-up completed
- `GET /api/v1/crm/offers/statistics` - Get offer statistics

### Task Endpoints
- `POST /api/v1/crm/tasks` - Create task
- `GET /api/v1/crm/tasks/{task_id}` - Get task
- `GET /api/v1/crm/tasks` - List tasks
- `PUT /api/v1/crm/tasks/{task_id}` - Update task
- `DELETE /api/v1/crm/tasks/{task_id}` - Delete task
- `POST /api/v1/crm/tasks/{task_id}/complete` - Mark task completed
- `GET /api/v1/crm/tasks/overdue` - Get overdue tasks
- `GET /api/v1/crm/tasks/statistics` - Get task statistics

### Activity Endpoints
- `POST /api/v1/crm/activities` - Create activity
- `GET /api/v1/crm/activities/{activity_id}` - Get activity
- `GET /api/v1/crm/activities/customer/{customer_id}` - Get customer activities
- `PUT /api/v1/crm/activities/{activity_id}` - Update activity
- `DELETE /api/v1/crm/activities/{activity_id}` - Delete activity
- `GET /api/v1/crm/activities/search` - Search activities
- `GET /api/v1/crm/activities/statistics/customer/{customer_id}` - Get activity statistics

## Testing

See the test file for comprehensive examples:
```bash
python backend/tests/test_crm_service.py
```

## See Also

- [CRM Service Quick Reference](CRM_SERVICE_QUICK_REFERENCE.md)
- [API Documentation](http://localhost:8000/api/docs)
