# Data Flow Architecture

## Table of Contents

1. [Overview](#overview)
2. [Request-Response Flow](#request-response-flow)
3. [WebSocket Real-Time Flow](#websocket-real-time-flow)
4. [State Management Flow](#state-management-flow)
5. [Data Persistence Flow](#data-persistence-flow)
6. [Calculation Flow](#calculation-flow)
7. [PDF Generation Flow](#pdf-generation-flow)

## Overview

This document describes how data flows through the Solar Calculator Pro application, from user interaction to data persistence and back.

## Request-Response Flow

### Standard API Request Flow

```
┌─────────┐      ┌──────────┐      ┌─────────┐      ┌──────────┐      ┌──────────┐
│  User   │─────▶│ React    │─────▶│  Axios  │─────▶│ FastAPI  │─────▶│ Service  │
│  Action │      │Component │      │ Request │      │ Endpoint │      │  Layer   │
└─────────┘      └──────────┘      └─────────┘      └──────────┘      └──────────┘
                                                                              │
                                                                              ▼
┌─────────┐      ┌──────────┐      ┌─────────┐      ┌──────────┐      ┌──────────┐
│  UI     │◀─────│ React    │◀─────│  Axios  │◀─────│ FastAPI  │◀─────│ Database │
│ Update  │      │Component │      │Response │      │ Response │      │  Query   │
└─────────┘      └──────────┘      └─────────┘      └──────────┘      └──────────┘
```

### Detailed Steps

1. **User Action**: User interacts with UI (button click, form submission)
2. **Component Handler**: React component captures event
3. **API Call**: Axios sends HTTP request to backend
4. **Authentication**: JWT token validated in middleware
5. **Endpoint Handler**: FastAPI route receives request
6. **Validation**: Pydantic validates request data
7. **Service Layer**: Business logic executed
8. **Database Query**: SQLAlchemy performs database operations
9. **Response Formation**: Data formatted as Pydantic model
10. **HTTP Response**: JSON response sent to frontend
11. **State Update**: Zustand store updated with new data
12. **UI Re-render**: React components re-render with new state

## WebSocket Real-Time Flow

### Long-Running Calculation Flow

```
┌─────────┐      ┌──────────┐      ┌─────────┐      ┌──────────┐
│  User   │─────▶│ React    │─────▶│Socket.IO│─────▶│ FastAPI  │
│ Starts  │      │Component │      │  Client │      │WebSocket │
│  Calc   │      │          │      │         │      │ Handler  │
└─────────┘      └──────────┘      └─────────┘      └──────────┘
                      │                  ▲                  │
                      │                  │                  ▼
                      │                  │            ┌──────────┐
                      │                  │            │ Service  │
                      │                  │            │  Layer   │
                      │                  │            └──────────┘
                      │                  │                  │
                      │                  │                  ▼
                      │            ┌─────────┐       ┌──────────┐
                      │            │Progress │◀──────│Calculation│
                      │            │ Updates │       │  Engine  │
                      │            └─────────┘       └──────────┘
                      │                  │
                      ▼                  ▼
                ┌──────────┐      ┌─────────┐
                │ Progress │◀─────│Socket.IO│
                │   Bar    │      │  Event  │
                └──────────┘      └─────────┘
```

### Progress Update Steps

1. User initiates long-running calculation
2. Frontend establishes WebSocket connection
3. Backend starts calculation in background task
4. Calculation engine emits progress events (0-100%)
5. WebSocket handler broadcasts progress to client
6. Frontend updates progress bar in real-time
7. On completion, final result sent via WebSocket
8. Frontend updates UI with final results

## State Management Flow

### Zustand Store Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Zustand Store                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │   Auth   │  │ Project  │  │    UI    │  │  User  │ │
│  │  Store   │  │  Store   │  │  Store   │  │ Store  │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────────────────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  Login   │  │ Project  │  │  Theme   │  │ Profile  │
│Component │  │   List   │  │ Selector │  │Component │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

### State Update Flow

1. **Action Dispatch**: Component calls store action
2. **State Mutation**: Store updates internal state
3. **Subscriber Notification**: All subscribed components notified
4. **Selective Re-render**: Only affected components re-render
5. **Persistence**: Critical state saved to localStorage
6. **Backend Sync**: State synchronized to backend (optional)

## Data Persistence Flow

### Database Write Flow

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│Frontend │─────▶│ FastAPI  │─────▶│ Service  │─────▶│SQLAlchemy│
│ Request │      │ Endpoint │      │  Layer   │      │   ORM    │
└─────────┘      └──────────┘      └──────────┘      └──────────┘
                                                             │
                                                             ▼
                                                       ┌──────────┐
                                                       │  SQLite  │
                                                       │ Database │
                                                       └──────────┘
```

### Database Read Flow

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│Frontend │─────▶│ FastAPI  │─────▶│ Service  │─────▶│SQLAlchemy│
│ Request │      │ Endpoint │      │  Layer   │      │  Query   │
└─────────┘      └──────────┘      └──────────┘      └──────────┘
                                                             │
                                                             ▼
                                                       ┌──────────┐
                                                       │  SQLite  │
                                                       │ Database │
                                                       └──────────┘
                                                             │
                                                             ▼
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│Frontend │◀─────│ FastAPI  │◀─────│ Service  │◀─────│ Pydantic │
│ Display │      │ Response │      │  Layer   │      │  Model   │
└─────────┘      └──────────┘      └──────────┘      └──────────┘
```

## Calculation Flow

### Solar Calculation Flow

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  User   │─────▶│  Solar   │─────▶│   API    │─────▶│  Solar   │
│  Input  │      │   Form   │      │  Request │      │ Service  │
└─────────┘      └──────────┘      └─────────┘      └──────────┘
                                                             │
                                                             ▼
                                                       ┌──────────┐
                                                       │Legacy    │
                                                       │Calc.py   │
                                                       │ Wrapper  │
                                                       └──────────┘
                                                             │
                                                             ▼
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│Results  │◀─────│  Solar   │◀─────│   API    │◀─────│Calculation│
│Display  │      │Component │      │ Response │      │  Results │
└─────────┘      └──────────┘      └─────────┘      └──────────┘
```

### Calculation Steps

1. User fills solar calculation form
2. Form validation on frontend
3. API request sent with calculation parameters
4. Backend validates request with Pydantic
5. SolarService wraps legacy calculations.py
6. Calculation performed using existing Python logic
7. Results formatted as Pydantic model
8. Response sent to frontend
9. Results displayed in UI with charts
10. Results saved to database for history

## PDF Generation Flow

### PDF Creation Flow

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  User   │─────▶│   PDF    │─────▶│   API    │─────▶│   PDF    │
│ Request │      │Component │      │  Request │      │ Service  │
└─────────┘      └──────────┘      └─────────┘      └──────────┘
                                                             │
                                                             ▼
                                                       ┌──────────┐
                                                       │ Template │
                                                       │  Engine  │
                                                       └──────────┘
                                                             │
                                                             ▼
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│Download │◀─────│   PDF    │◀─────│   API    │◀─────│   PDF    │
│  File   │      │Component │      │ Response │      │  Bytes   │
└─────────┘      └──────────┘      └─────────┘      └──────────┘
```

### PDF Generation Steps

1. User clicks "Generate PDF" button
2. Frontend sends project ID and options
3. Backend retrieves project data from database
4. PDFService wraps legacy pdf_generator.py
5. Template engine applies selected template
6. Charts rendered as images
7. Data formatted with German number formatting
8. PDF generated as bytes
9. PDF bytes sent to frontend
10. Browser triggers download

## Data Transformation Flow

### German Number Formatting Flow

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│Database │─────▶│ Backend  │─────▶│ Frontend │─────▶│  Display │
│ (Float) │      │(Standard)│      │(German)  │      │1.234,56  │
└─────────┘      └──────────┘      └──────────┘      └──────────┘
   1234.56          1234.56          "1.234,56"        1.234,56

┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  User   │─────▶│ Frontend │─────▶│ Backend  │─────▶│Database  │
│  Input  │      │(Parse)   │      │(Standard)│      │ (Float)  │
└─────────┘      └──────────┘      └──────────┘      └──────────┘
 "1.234,56"         1234.56          1234.56           1234.56
```

### Dynamic Keys Flow

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  Data   │─────▶│ Service  │─────▶│ Database │─────▶│  Stored  │
│ Created │      │  Layer   │      │  Insert  │      │with Key  │
└─────────┘      └──────────┘      └──────────┘      └──────────┘
                       │
                       ▼
                 ┌──────────┐
                 │ Generate │
                 │Dynamic   │
                 │   Key    │
                 └──────────┘
                       │
                       ▼
                 "solar_123_20250120..."
```

## Caching Flow

### Multi-Level Cache Architecture

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│Frontend │─────▶│ Browser  │─────▶│ Backend  │─────▶│ Database │
│ Request │      │  Cache   │      │  Cache   │      │  Query   │
└─────────┘      └──────────┘      └──────────┘      └──────────┘
     │                │                  │                  │
     │                │ Hit              │                  │
     │◀───────────────┘                  │                  │
     │                                   │ Hit              │
     │◀──────────────────────────────────┘                  │
     │                                                      │
     │◀─────────────────────────────────────────────────────┘
                                                        Miss
```

### Cache Invalidation Flow

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  Data   │─────▶│ Database │─────▶│ Backend  │─────▶│ Browser  │
│ Updated │      │  Update  │      │  Cache   │      │  Cache   │
└─────────┘      └──────────┘      │Invalidate│      │Invalidate│
                                    └──────────┘      └──────────┘
```

## Error Flow

### Error Handling Flow

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  Error  │─────▶│ Service  │─────▶│ FastAPI  │─────▶│ Frontend │
│ Occurs  │      │  Layer   │      │Middleware│      │  Handler │
└─────────┘      └──────────┘      └──────────┘      └──────────┘
                       │                  │                  │
                       ▼                  ▼                  ▼
                 ┌──────────┐      ┌──────────┐      ┌──────────┐
                 │  Log     │      │ Format   │      │  Toast   │
                 │  Error   │      │ Response │      │Notification│
                 └──────────┘      └──────────┘      └──────────┘
```

## Summary

The data flow architecture ensures:

- **Unidirectional Flow**: Data flows in predictable patterns
- **Separation of Concerns**: Each layer has specific responsibilities
- **Error Handling**: Errors caught and handled at appropriate levels
- **Performance**: Caching at multiple levels
- **Real-Time Updates**: WebSocket for long-running operations
- **Data Integrity**: Validation at multiple points
- **Persistence**: Reliable data storage and retrieval
