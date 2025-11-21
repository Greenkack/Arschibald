# System Architecture Diagrams

## Table of Contents

1. [High-Level System Architecture](#high-level-system-architecture)
2. [Component Interaction Diagram](#component-interaction-diagram)
3. [Data Flow Diagram](#data-flow-diagram)
4. [Deployment Diagram](#deployment-diagram)
5. [Security Architecture Diagram](#security-architecture-diagram)
6. [Integration Architecture](#integration-architecture)

## High-Level System Architecture

```mermaid
graph TB
    subgraph "Electron Desktop Application"
        subgraph "Renderer Process"
            UI[React Frontend<br/>Port 3000]
            Router[React Router]
            State[Zustand Store]
            Components[PrimeReact Components]
        end
        
        subgraph "Main Process"
            Main[Electron Main]
            Preload[Preload Script]
            BackendMgr[Backend Manager]
            Menu[Application Menu]
            Tray[System Tray]
            Updater[Auto Updater]
        end
        
        subgraph "Backend Process"
            FastAPI[FastAPI Server<br/>Port 8000]
            Services[Service Layer]
            Database[(SQLite Database)]
            Legacy[Legacy Python Modules]
        end
    end
    
    UI -->|IPC| Preload
    Preload -->|IPC| Main
    Main -->|Manages| BackendMgr
    BackendMgr -->|Spawns| FastAPI
    UI -->|HTTP/WebSocket| FastAPI
    FastAPI --> Services
    Services --> Database
    Services --> Legacy
    
    style UI fill:#61dafb
    style FastAPI fill:#009688
    style Database fill:#ffa726
    style Legacy fill:#ff6b6b
```

## Component Interaction Diagram

```mermaid
sequenceDiagram
    participant User
    participant React as React Component
    participant Zustand as Zustand Store
    participant Axios as Axios Client
    participant FastAPI as FastAPI Endpoint
    participant Service as Service Layer
    participant DB as Database
    participant Legacy as Legacy Code
    
    User->>React: Interact (e.g., Calculate)
    React->>Zustand: Dispatch Action
    Zustand->>Axios: API Call
    Axios->>FastAPI: HTTP Request
    FastAPI->>FastAPI: Validate Request
    FastAPI->>Service: Call Service Method
    Service->>Legacy: Execute Legacy Logic
    Legacy-->>Service: Return Result
    Service->>DB: Save to Database
    DB-->>Service: Confirm Save
    Service-->>FastAPI: Return Response
    FastAPI-->>Axios: HTTP Response
    Axios-->>Zustand: Update State
    Zustand-->>React: Trigger Re-render
    React-->>User: Display Result
```

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph "Frontend"
        A[User Input] --> B[Form Validation]
        B --> C[API Request]
    end
    
    subgraph "Backend"
        C --> D[Request Validation]
        D --> E[Service Layer]
        E --> F{Operation Type}
        F -->|Read| G[Database Query]
        F -->|Write| H[Database Insert/Update]
        F -->|Calculate| I[Legacy Calculation]
        F -->|Generate| J[PDF Generation]
        
        G --> K[Format Response]
        H --> K
        I --> K
        J --> K
    end
    
    subgraph "Data Storage"
        G -.-> L[(Database)]
        H -.-> L
        L -.-> M[Backup]
    end
    
    K --> N[API Response]
    N --> O[Frontend Update]
    O --> P[UI Render]
    
    style A fill:#e3f2fd
    style L fill:#fff3e0
    style P fill:#e8f5e9
```

## Deployment Diagram

```mermaid
graph TB
    subgraph "User's Computer"
        subgraph "Windows/macOS/Linux"
            App[Solar Calculator Pro<br/>Electron Application]
            
            subgraph "Application Bundle"
                Frontend[Frontend Assets<br/>HTML/CSS/JS]
                Backend[Backend Executable<br/>Python + FastAPI]
                DB[(Local Database<br/>SQLite)]
            end
        end
    end
    
    subgraph "External Services"
        Weather[Weather API]
        Maps[Maps API]
        Email[Email Service]
        Updates[Update Server<br/>GitHub Releases]
    end
    
    App --> Frontend
    App --> Backend
    Backend --> DB
    Backend -.->|HTTPS| Weather
    Backend -.->|HTTPS| Maps
    Backend -.->|SMTP| Email
    App -.->|HTTPS| Updates
    
    style App fill:#4caf50
    style Frontend fill:#2196f3
    style Backend fill:#ff9800
    style DB fill:#9c27b0
```

## Security Architecture Diagram

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Application Layer"
            A1[Input Validation]
            A2[XSS Prevention]
            A3[CSRF Protection]
        end
        
        subgraph "Authentication Layer"
            B1[JWT Tokens]
            B2[Password Hashing]
            B3[Session Management]
        end
        
        subgraph "Network Layer"
            C1[HTTPS/TLS]
            C2[Rate Limiting]
            C3[Security Headers]
        end
        
        subgraph "Data Layer"
            D1[Database Encryption]
            D2[Field Encryption]
            D3[Backup Encryption]
        end
        
        subgraph "Electron Layer"
            E1[Context Isolation]
            E2[Secure IPC]
            E3[CSP]
        end
    end
    
    User[User] --> A1
    A1 --> B1
    B1 --> C1
    C1 --> D1
    E1 --> A1
    
    style A1 fill:#f44336
    style B1 fill:#ff9800
    style C1 fill:#ffc107
    style D1 fill:#4caf50
    style E1 fill:#2196f3
```

## Integration Architecture

```mermaid
graph LR
    subgraph "Solar Calculator Pro"
        Core[Core Application]
    end
    
    subgraph "Internal Integrations"
        Frontend[React Frontend]
        Backend[FastAPI Backend]
        DB[(Database)]
        Legacy[Legacy Modules]
    end
    
    subgraph "External Integrations"
        Weather[Weather API]
        Maps[Maps API]
        Email[Email Service]
        Payment[Payment Gateway]
        Storage[Cloud Storage]
    end
    
    Core --> Frontend
    Core --> Backend
    Backend --> DB
    Backend --> Legacy
    
    Backend -.->|REST API| Weather
    Backend -.->|REST API| Maps
    Backend -.->|SMTP| Email
    Backend -.->|REST API| Payment
    Backend -.->|REST API| Storage
    
    style Core fill:#4caf50
    style Frontend fill:#2196f3
    style Backend fill:#ff9800
    style DB fill:#9c27b0
```

## Authentication Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant DB
    
    User->>Frontend: Enter Credentials
    Frontend->>Backend: POST /api/v1/auth/login
    Backend->>DB: Query User
    DB-->>Backend: User Data
    Backend->>Backend: Verify Password (bcrypt)
    Backend->>Backend: Generate JWT Tokens
    Backend-->>Frontend: Access Token + Refresh Token
    Frontend->>Frontend: Store Tokens
    Frontend-->>User: Login Success
    
    Note over Frontend,Backend: Subsequent Requests
    
    Frontend->>Backend: API Request + Access Token
    Backend->>Backend: Validate JWT
    Backend-->>Frontend: Protected Resource
    
    Note over Frontend,Backend: Token Refresh
    
    Frontend->>Backend: POST /api/v1/auth/refresh
    Backend->>Backend: Validate Refresh Token
    Backend->>Backend: Generate New Access Token
    Backend-->>Frontend: New Access Token
```

## Calculation Flow Diagram

```mermaid
flowchart TD
    Start[User Starts Calculation] --> Input[Enter Parameters]
    Input --> Validate{Valid Input?}
    Validate -->|No| Error[Show Error]
    Error --> Input
    Validate -->|Yes| API[Send to Backend]
    
    API --> Auth{Authenticated?}
    Auth -->|No| Login[Redirect to Login]
    Auth -->|Yes| Service[Solar Service]
    
    Service --> Legacy[Legacy Calculator]
    Legacy --> Pricing[Price Matrix Lookup]
    Pricing --> Save[Save to Database]
    Save --> Response[Format Response]
    
    Response --> Frontend[Update Frontend]
    Frontend --> Display[Display Results]
    Display --> Actions{User Action}
    
    Actions -->|Generate PDF| PDF[PDF Service]
    Actions -->|Save Project| SaveProj[Save Project]
    Actions -->|New Calculation| Input
    Actions -->|Exit| End[End]
    
    PDF --> Download[Download PDF]
    SaveProj --> Confirm[Show Confirmation]
    
    style Start fill:#4caf50
    style Display fill:#2196f3
    style Error fill:#f44336
    style End fill:#9e9e9e
```

## WebSocket Real-Time Communication

```mermaid
sequenceDiagram
    participant Frontend
    participant SocketIO as Socket.IO Client
    participant Server as Socket.IO Server
    participant Service as Calculation Service
    
    Frontend->>SocketIO: Connect
    SocketIO->>Server: Establish Connection
    Server-->>SocketIO: Connection Confirmed
    
    Frontend->>SocketIO: Start Calculation
    SocketIO->>Server: calculation:start
    Server->>Service: Begin Calculation
    
    loop Progress Updates
        Service->>Server: Progress Event (0-100%)
        Server->>SocketIO: calculation:progress
        SocketIO->>Frontend: Update Progress Bar
    end
    
    Service->>Server: Calculation Complete
    Server->>SocketIO: calculation:complete
    SocketIO->>Frontend: Display Results
    
    Frontend->>SocketIO: Disconnect
    SocketIO->>Server: Close Connection
```

## Database Schema Diagram

```mermaid
erDiagram
    USERS ||--o{ PROJECTS : creates
    USERS ||--o{ SESSIONS : has
    PROJECTS ||--o{ CALCULATIONS : contains
    PROJECTS ||--o{ DOCUMENTS : has
    CALCULATIONS ||--o{ RESULTS : produces
    
    USERS {
        int id PK
        string username
        string email
        string password_hash
        string role
        datetime created_at
    }
    
    PROJECTS {
        int id PK
        int user_id FK
        string name
        string type
        json data
        datetime created_at
        datetime updated_at
    }
    
    CALCULATIONS {
        int id PK
        int project_id FK
        string type
        json input_data
        json result_data
        string dynamic_key
        datetime created_at
    }
    
    DOCUMENTS {
        int id PK
        int project_id FK
        string filename
        string type
        blob pdf_bytes
        datetime created_at
    }
    
    RESULTS {
        int id PK
        int calculation_id FK
        string metric_name
        float value
        string unit
    }
    
    SESSIONS {
        int id PK
        int user_id FK
        string token
        datetime expires_at
    }
```

## Electron Process Architecture

```mermaid
graph TB
    subgraph "Main Process"
        Main[main.js]
        Backend[backend-manager.js]
        Menu[menu.js]
        Tray[tray.js]
        Updater[updater.js]
        
        Main --> Backend
        Main --> Menu
        Main --> Tray
        Main --> Updater
    end
    
    subgraph "Renderer Process"
        Window[BrowserWindow]
        Preload[preload.js]
        React[React App]
        
        Window --> Preload
        Preload --> React
    end
    
    subgraph "Backend Process"
        Python[Python Backend]
        FastAPI[FastAPI Server]
        
        Python --> FastAPI
    end
    
    Main -->|Creates| Window
    Main -->|IPC| Preload
    Backend -->|Spawns| Python
    React -->|HTTP| FastAPI
    
    style Main fill:#4caf50
    style Window fill:#2196f3
    style Python fill:#ff9800
```

## Summary

These diagrams provide visual representations of:

- **System Architecture**: Overall structure and components
- **Component Interactions**: How components communicate
- **Data Flow**: How data moves through the system
- **Deployment**: How the application is deployed
- **Security**: Security layers and mechanisms
- **Integration**: Internal and external integrations
- **Authentication**: User authentication flow
- **Calculations**: Calculation process flow
- **Real-Time**: WebSocket communication
- **Database**: Data model relationships
- **Electron**: Process architecture

All diagrams use Mermaid syntax and can be rendered in any Markdown viewer that supports Mermaid.
