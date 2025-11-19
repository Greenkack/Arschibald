# CRM Service Quick Reference

## Service Initialization

```python
from backend.services.crm_service import get_crm_service
crm_service = get_crm_service()
```

## Customer Management

```python
# Create
customer = crm_service.create_customer({
    "first_name": "Max", "last_name": "Mustermann",
    "email": "max@example.com"
})

# Get
customer = crm_service.get_customer(customer_id=1)

# List
customers = crm_service.list_customers(limit=100, search="Mustermann")

# Update
customer = crm_service.update_customer(1, {"email": "new@example.com"})

# Delete
success = crm_service.delete_customer(customer_id=1)
```

## Offer Tracking

```python
# Get status
offer = crm_service.get_offer_status(project_id=1)

# Update status
crm_service.update_offer_status(1, "sent", offer_value=25000.00)
crm_service.update_offer_status(1, "accepted")
crm_service.update_offer_status(1, "rejected", rejection_reason="Preis zu hoch")

# List offers
offers = crm_service.list_offers(status_filter="sent")

# Follow-ups
follow_ups = crm_service.get_pending_follow_ups()
crm_service.mark_follow_up_completed(project_id=1)

# Statistics
stats = crm_service.get_offer_statistics()
```

## Task Management

```python
from datetime import date, timedelta

# Create
task_id = crm_service.create_task({
    "title": "Follow up with customer",
    "status": "open",
    "priority": "high",
    "due_date": date.today() + timedelta(days=7),
    "customer_id": 1
})

# Get
task = crm_service.get_task(task_id=1)

# List
tasks = crm_service.list_tasks(filters={"status": "open"})
overdue = crm_service.list_tasks(filters={"overdue_only": True})

# Update
crm_service.update_task(1, {"status": "in_progress"})

# Complete
crm_service.mark_task_completed(task_id=1)

# Delete
crm_service.delete_task(task_id=1)

# Statistics
stats = crm_service.get_task_statistics()
```

## Communication History

```python
# Create activity
activity_id = crm_service.create_activity({
    "customer_id": 1,
    "activity_type": "note",
    "title": "Phone call",
    "content": "Customer is interested",
    "is_important": True
})

# Get
activity = crm_service.get_activity(activity_id=1)

# List customer activities
activities = crm_service.get_customer_activities(
    customer_id=1,
    activity_type="call"
)

# Update
crm_service.update_activity(1, {"is_important": False})

# Delete
crm_service.delete_activity(activity_id=1)

# Search
results = crm_service.search_activities("Angebot", customer_id=1)

# Statistics
stats = crm_service.get_activity_statistics(customer_id=1)
```

## Activity Types

- `note` - General note
- `email` - Email communication
- `call` - Phone call
- `appointment` - Appointment
- `meeting` - Meeting
- `task` - Task-related
- `other` - Other

## Task Status Values

- `open` - Open/pending
- `in_progress` - In progress
- `completed` - Completed

## Task Priority Values

- `low` - Low priority
- `medium` - Medium priority
- `high` - High priority

## Offer Status Values

- `draft` - Draft offer
- `sent` - Sent to customer
- `accepted` - Accepted by customer
- `rejected` - Rejected by customer

## API Endpoints

### Customers
- `POST /api/v1/crm/customers`
- `GET /api/v1/crm/customers/{id}`
- `GET /api/v1/crm/customers?search=term`
- `PUT /api/v1/crm/customers/{id}`
- `DELETE /api/v1/crm/customers/{id}`

### Offers
- `GET /api/v1/crm/offers/{project_id}`
- `PUT /api/v1/crm/offers/{project_id}/status`
- `GET /api/v1/crm/offers?status_filter=sent`
- `GET /api/v1/crm/offers/follow-ups/pending`
- `POST /api/v1/crm/offers/{project_id}/follow-up/complete`
- `GET /api/v1/crm/offers/statistics`

### Tasks
- `POST /api/v1/crm/tasks`
- `GET /api/v1/crm/tasks/{id}`
- `GET /api/v1/crm/tasks?status=open&priority=high`
- `PUT /api/v1/crm/tasks/{id}`
- `DELETE /api/v1/crm/tasks/{id}`
- `POST /api/v1/crm/tasks/{id}/complete`
- `GET /api/v1/crm/tasks/overdue`
- `GET /api/v1/crm/tasks/statistics`

### Activities
- `POST /api/v1/crm/activities`
- `GET /api/v1/crm/activities/{id}`
- `GET /api/v1/crm/activities/customer/{customer_id}`
- `PUT /api/v1/crm/activities/{id}`
- `DELETE /api/v1/crm/activities/{id}`
- `GET /api/v1/crm/activities/search?search_term=text`
- `GET /api/v1/crm/activities/statistics/customer/{customer_id}`

## Error Handling

```python
try:
    customer = crm_service.get_customer(999)
except ValueError as e:
    # Validation error
    pass
except RuntimeError as e:
    # Database/runtime error
    pass
```

## Health Check

```python
health = crm_service.health_check()
print(health.status)  # HEALTHY, DEGRADED, or UNHEALTHY
```
