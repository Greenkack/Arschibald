# Communication History - Quick Reference

## Overview

The Communication History feature provides a comprehensive system for managing all customer communications including emails, calls, meetings, notes, and document attachments.

## Components

### 1. CommunicationLog
**Purpose:** Display all communications with a customer in a unified view

**Features:**
- View all communication types in one table
- Filter by communication type (email, call, meeting, note, etc.)
- Search communications by content
- Toggle archived communications
- View detailed communication information
- Sort by date, type, or creator

**Usage:**
```tsx
import { CommunicationLog } from '../components/crm';

<CommunicationLog customerId={123} />
```

### 2. EmailIntegration
**Purpose:** Manage email communications with customers

**Features:**
- View all email communications
- Compose new emails
- Reply to existing emails
- Attach files to emails
- View email details and attachments
- Track email history

**Usage:**
```tsx
import { EmailIntegration } from '../components/crm';

<EmailIntegration 
  customerId={123}
  customerEmail="customer@example.com"
/>
```

### 3. CallLogging
**Purpose:** Log and track phone call communications

**Features:**
- Log new calls (inbound, outbound, missed)
- Record call duration and outcome
- Add detailed call notes
- Mark calls requiring follow-up
- View call history
- Track call statistics

**Usage:**
```tsx
import { CallLogging } from '../components/crm';

<CallLogging 
  customerId={123}
  customerPhone="+49 123 456789"
/>
```

### 4. DocumentAttachments
**Purpose:** Manage document attachments for customers

**Features:**
- Upload multiple documents
- View document list with metadata
- Download attachments
- Delete documents with confirmation
- Add descriptions to documents
- Track upload history

**Usage:**
```tsx
import { DocumentAttachments } from '../components/crm';

<DocumentAttachments customerId={123} />
```

### 5. CommunicationSearch
**Purpose:** Advanced search across all communications

**Features:**
- Full-text search in subject and content
- Filter by communication type
- Date range filtering
- Search across all customers or specific customer
- View search results in table format
- Sort and paginate results

**Usage:**
```tsx
import { CommunicationSearch } from '../components/crm';

<CommunicationSearch customerId={123} />
```

## API Endpoints

### Activities (Communications)

**Create Activity:**
```
POST /api/v1/crm/activities
Body: {
  customer_id: number,
  activity_type: string,
  title: string,
  content: string,
  created_by?: string,
  is_important?: boolean,
  attachments?: string[]
}
```

**Get Customer Activities:**
```
GET /api/v1/crm/activities/customer/{customer_id}
Query params:
  - activity_type?: string
  - include_archived?: boolean
  - limit?: number
```

**Search Activities:**
```
GET /api/v1/crm/activities/search
Query params:
  - search_term: string (required)
  - customer_id?: number
  - activity_type?: string
  - limit?: number
```

**Get Activity:**
```
GET /api/v1/crm/activities/{activity_id}
```

**Update Activity:**
```
PUT /api/v1/crm/activities/{activity_id}
Body: Partial activity data
```

**Delete Activity:**
```
DELETE /api/v1/crm/activities/{activity_id}
```

## Activity Types

- `email` - Email communications
- `call` - Phone calls
- `meeting` - Meetings
- `note` - General notes
- `appointment` - Scheduled appointments
- `task` - Tasks
- `other` - Other communications

## Data Model

```typescript
interface Activity {
  id: number;
  customer_id: number;
  activity_type: string;
  title: string;
  content: string;
  created_at: string;
  created_by?: string;
  is_important: boolean;
  is_archived: boolean;
  attachments?: string[];
}
```

## Best Practices

1. **Always log communications** - Keep a complete record of all customer interactions
2. **Use descriptive titles** - Make it easy to identify communications at a glance
3. **Add detailed notes** - Include all relevant information in the content field
4. **Mark important items** - Use the is_important flag for follow-ups
5. **Attach relevant documents** - Keep all related files with the communication
6. **Use appropriate types** - Select the correct activity_type for better organization
7. **Search effectively** - Use filters and date ranges to find specific communications

## Common Workflows

### Logging a Phone Call
1. Navigate to Call History tab
2. Click "Log Call"
3. Select call type (inbound/outbound/missed)
4. Enter phone number, subject, and notes
5. Record duration and outcome
6. Save the call log

### Sending an Email
1. Navigate to Emails tab
2. Click "Compose Email"
3. Enter recipient, subject, and message
4. Attach files if needed
5. Click "Send"
6. Email is logged automatically

### Uploading Documents
1. Navigate to Documents tab
2. Click "Upload Document"
3. Enter title and description
4. Select files to upload
5. Click "Upload"
6. Documents are attached to customer record

### Searching Communications
1. Navigate to Search tab
2. Enter search term
3. Select filters (type, date range)
4. Click "Search"
5. View and sort results

## Troubleshooting

**Problem:** Communications not loading
- Check customer ID is valid
- Verify API connection
- Check browser console for errors

**Problem:** Search returns no results
- Verify search term is correct
- Check date range filters
- Try removing filters one by one

**Problem:** Cannot upload documents
- Check file size (max 50MB)
- Verify file format is supported
- Check network connection

## Integration with Other Features

- **Customer Management:** Communications are linked to customer records
- **Task Management:** Tasks can be created from communications
- **Offer Tracking:** Communications can reference offers
- **PDF Generation:** Communication history can be included in reports

## Future Enhancements

- Email template system
- Automated email campaigns
- SMS integration
- Video call logging
- AI-powered communication insights
- Automated follow-up reminders
- Communication analytics dashboard
