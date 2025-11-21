# System Architecture Overview

## Table of Contents

1. [Introduction](#introduction)
2. [High-Level Architecture](#high-level-architecture)
3. [Technology Stack](#technology-stack)
4. [Component Architecture](#component-architecture)
5. [Related Documentation](#related-documentation)

## Introduction

Solar Calculator Pro is a modern desktop application built with Electron, React, and FastAPI. The application migrates from a Streamlit-based Python application to a professional desktop solution while preserving all existing business logic.

### Architecture Principles

- **Separation of Concerns**: Clear boundaries between UI, business logic, and data layers
- **Code Preservation**: Existing Python code wrapped, not rewritten
- **API-First Design**: All functionality exposed through REST/WebSocket APIs
- **Progressive Enhancement**: Features can be added incrementally
- **Platform Native**: Leverages native desktop capabilities

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Desktop App                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              React Frontend (Port 3000)                 │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │  Pages   │  │Components│  │  State   │            │ │
│  │  │ (Routes) │  │(PrimeReact│  │Management│            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           │ HTTP/WebSocket                   │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         FastAPI Backend (Port 8000)                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │   API    │  │ Services │  │ Database │            │ │
│  │  │ Endpoints│  │  Layer   │  │  Layer   │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  │         │                                               │ │
│  │         ▼                                               │ │
│  │  ┌────────────────────────────────────────────┐       │ │
│  │  │     Existing Python Modules (Wrapped)      │       │ │
│  │  │  • calculations.py                         │       │ │
│  │  │  • database.py                             │       │ │
│  │  │  • pdf_generator.py                        │       │ │
│  │  │  • price_matrix_*.py                       │       │ │
│  │  │  • pv3d.py, solar_calculator.py            │       │ │
│  │  └────────────────────────────────────────────┘       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **React 18+** with TypeScript
- **PrimeReact** for UI components
- **React Router v6** for routing
- **Zustand** for state management
- **Axios** for HTTP communication
- **Socket.IO Client** for WebSocket
- **Recharts** for data visualization
- **React Hook Form** for forms

### Backend
- **Python 3.10+**
- **FastAPI 0.100+** for REST API
- **Uvicorn** as ASGI server
- **Pydantic** for validation
- **SQLAlchemy** for ORM
- **python-socketio** for WebSocket
- **python-jose** for JWT
- **bcrypt** for password hashing

### Desktop
- **Electron 27+**
- **electron-builder** for packaging
- **electron-updater** for auto-updates
- **electron-store** for settings

## Component Architecture

See detailed documentation:
- [Data Flow Architecture](./DATA_FLOW_ARCHITECTURE.md)
- [Deployment Architecture](./DEPLOYMENT_ARCHITECTURE.md)
- [Security Architecture](./SECURITY_ARCHITECTURE.md)
- [Integration Points](./INTEGRATION_POINTS.md)

## Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Component Documentation](../frontend/COMPONENT_DOCUMENTATION.md)
- [Developer Guide](./DEVELOPER_GUIDE.md)
- [User Manual](./USER_MANUAL.md)
