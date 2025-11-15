# Design Document

## Overview

Diese Design-Spezifikation beschreibt die Architektur für die Migration der bestehenden Streamlit-Anwendung zu einer modernen Desktop-Anwendung mit React-Frontend, FastAPI-Backend und Electron-Wrapper. Das Design folgt dem Prinzip der minimalen Änderungen am bestehenden Python-Code und maximaler Wiederverwendbarkeit.

### Architektur-Prinzipien

1. **Separation of Concerns**: Klare Trennung zwischen UI (React), Business Logic (Python/FastAPI) und Desktop-Integration (Electron)
2. **Code Preservation**: Bestehender Python-Code wird nicht modifiziert, sondern gekapselt
3. **API-First**: Alle Funktionen werden über REST/WebSocket APIs exponiert
4. **Progressive Migration**: Schrittweise Migration einzelner Module möglich
5. **Platform Native**: Native Desktop-Features nutzen (Menüs, Dialoge, Notifications)

## Architecture

### High-Level Architecture

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

### Technology Stack

**Frontend:**
- React 18+ with TypeScript
- PrimeReact (empfohlen) oder Material-UI
- React Router v6 (Routing)
- Zustand oder Redux Toolkit (State Management)
- Axios (HTTP Client)
- Socket.IO Client (WebSocket)
- Recharts oder Chart.js (Visualisierung)
- React Hook Form (Formulare)

**Backend:**
- Python 3.10+
- FastAPI 0.100+
- Uvicorn (ASGI Server)
- Pydantic (Validation)
- SQLAlchemy (ORM)
- python-socketio (WebSocket)
- python-jose (JWT)
- bcrypt (Password Hashing)

**Desktop:**
- Electron 27+
- electron-builder (Packaging)
- electron-updater (Auto-Update)
- electron-store (Settings)


## Components and Interfaces

### 1. Backend Service Layer

#### API Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── config.py              # Configuration management
├── dependencies.py        # Dependency injection
├── middleware/
│   ├── auth.py           # JWT authentication
│   ├── cors.py           # CORS configuration
│   └── error_handler.py  # Global error handling
├── api/
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── auth.py       # Login, logout, user management
│   │   ├── solar.py      # Solar calculator endpoints
│   │   ├── heatpump.py   # Heat pump endpoints
│   │   ├── pricing.py    # Price matrix endpoints
│   │   ├── pdf.py        # PDF generation endpoints
│   │   ├── crm.py        # CRM endpoints
│   │   ├── products.py   # Product database endpoints
│   │   └── admin.py      # Admin panel endpoints
├── services/
│   ├── solar_service.py
│   ├── heatpump_service.py
│   ├── pricing_service.py
│   ├── pdf_service.py
│   ├── crm_service.py
│   └── product_service.py
├── models/
│   ├── schemas.py        # Pydantic models
│   └── database.py       # SQLAlchemy models
├── core/
│   ├── security.py       # Password hashing, JWT
│   └── database.py       # Database connection
└── legacy/               # Wrapper für bestehenden Code
    ├── calculations_wrapper.py
    ├── database_wrapper.py
    ├── pdf_wrapper.py
    └── utils_wrapper.py
```

#### Key API Endpoints

**Authentication:**
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
POST   /api/v1/auth/refresh
```

**Solar Calculator:**
```
POST   /api/v1/solar/calculate
GET    /api/v1/solar/projects
GET    /api/v1/solar/projects/{id}
POST   /api/v1/solar/projects
PUT    /api/v1/solar/projects/{id}
DELETE /api/v1/solar/projects/{id}
POST   /api/v1/solar/3d-visualization
```

**Price Matrix:**
```
GET    /api/v1/pricing/matrix
POST   /api/v1/pricing/matrix/upload
GET    /api/v1/pricing/calculate
POST   /api/v1/pricing/validate
```

**PDF Generation:**
```
POST   /api/v1/pdf/generate
GET    /api/v1/pdf/templates
POST   /api/v1/pdf/preview
```

**Products:**
```
GET    /api/v1/products
GET    /api/v1/products/{id}
POST   /api/v1/products
PUT    /api/v1/products/{id}
DELETE /api/v1/products/{id}
GET    /api/v1/products/search
```


### 2. Frontend Application Structure

```
frontend/
├── public/
│   ├── index.html
│   └── assets/
├── src/
│   ├── main.tsx          # Entry point
│   ├── App.tsx           # Root component
│   ├── routes/
│   │   └── index.tsx     # Route configuration
│   ├── pages/
│   │   ├── Dashboard/
│   │   ├── SolarCalculator/
│   │   ├── HeatPump/
│   │   ├── PriceMatrix/
│   │   ├── CRM/
│   │   ├── Products/
│   │   ├── Admin/
│   │   └── Settings/
│   ├── components/
│   │   ├── common/       # Reusable components
│   │   ├── forms/        # Form components
│   │   ├── charts/       # Chart components
│   │   ├── layout/       # Layout components
│   │   └── 3d/           # 3D visualization
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── useWebSocket.ts
│   ├── services/
│   │   ├── api.ts        # Axios instance
│   │   ├── auth.ts       # Auth service
│   │   └── websocket.ts  # WebSocket service
│   ├── store/
│   │   ├── index.ts      # Store configuration
│   │   ├── slices/       # Redux slices or Zustand stores
│   │   │   ├── authSlice.ts
│   │   │   ├── projectSlice.ts
│   │   │   └── uiSlice.ts
│   ├── types/
│   │   ├── api.ts        # API types
│   │   └── models.ts     # Data models
│   ├── utils/
│   │   ├── formatters.ts
│   │   └── validators.ts
│   └── styles/
│       ├── theme.ts      # PrimeReact theme
│       └── global.css
```

#### Component Mapping (Streamlit → React)

| Streamlit Component | React Equivalent |
|---------------------|------------------|
| `st.title()` | `<h1>` with PrimeReact styling |
| `st.text_input()` | `<InputText>` from PrimeReact |
| `st.number_input()` | `<InputNumber>` from PrimeReact |
| `st.selectbox()` | `<Dropdown>` from PrimeReact |
| `st.multiselect()` | `<MultiSelect>` from PrimeReact |
| `st.slider()` | `<Slider>` from PrimeReact |
| `st.button()` | `<Button>` from PrimeReact |
| `st.checkbox()` | `<Checkbox>` from PrimeReact |
| `st.radio()` | `<RadioButton>` from PrimeReact |
| `st.dataframe()` | `<DataTable>` from PrimeReact |
| `st.plotly_chart()` | Recharts or Chart.js |
| `st.file_uploader()` | `<FileUpload>` + Electron dialog |
| `st.tabs()` | `<TabView>` from PrimeReact |
| `st.expander()` | `<Accordion>` from PrimeReact |
| `st.sidebar` | `<Sidebar>` from PrimeReact |
| `st.columns()` | CSS Grid or Flexbox |
| `st.form()` | React Hook Form |
| `st.session_state` | Zustand/Redux store |


### 3. Electron Main Process

```
electron/
├── main.js               # Main process entry
├── preload.js           # Preload script (IPC bridge)
├── menu.js              # Application menu
├── tray.js              # System tray
├── updater.js           # Auto-update logic
└── backend-manager.js   # Python backend process manager
```

#### Backend Process Management

```javascript
// backend-manager.js
class BackendManager {
  constructor() {
    this.process = null;
    this.port = 8000;
  }

  async start() {
    // Start Python backend as child process
    const pythonPath = this.getPythonPath();
    const backendPath = path.join(__dirname, '../backend/main.py');
    
    this.process = spawn(pythonPath, ['-m', 'uvicorn', 'main:app', 
                                      '--port', this.port]);
    
    // Wait for backend to be ready
    await this.waitForBackend();
  }

  async stop() {
    if (this.process) {
      this.process.kill();
    }
  }

  async waitForBackend() {
    // Poll backend health endpoint
    const maxRetries = 30;
    for (let i = 0; i < maxRetries; i++) {
      try {
        await axios.get(`http://localhost:${this.port}/health`);
        return;
      } catch (e) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    throw new Error('Backend failed to start');
  }
}
```

#### IPC Communication

```javascript
// preload.js - Expose safe APIs to renderer
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  selectFile: () => ipcRenderer.invoke('dialog:openFile'),
  saveFile: (data) => ipcRenderer.invoke('dialog:saveFile', data),
  
  // Backend communication
  getBackendUrl: () => ipcRenderer.invoke('backend:getUrl'),
  
  // App operations
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),
  
  // Updates
  checkForUpdates: () => ipcRenderer.invoke('updater:check'),
  onUpdateAvailable: (callback) => 
    ipcRenderer.on('updater:available', callback),
});
```


## Data Models

### API Request/Response Models

```python
# backend/models/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Authentication
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime

# Solar Calculator
class SolarCalculationRequest(BaseModel):
    roof_area: float = Field(..., gt=0)
    roof_type: str
    roof_angle: float = Field(..., ge=0, le=90)
    orientation: str
    module_type: str
    annual_consumption: float = Field(..., gt=0)
    location: str
    
class SolarCalculationResponse(BaseModel):
    system_size: float
    module_count: int
    annual_production: float
    self_consumption_rate: float
    payback_period: float
    total_cost: float
    savings_25_years: float
    co2_savings: float

# Project Management
class ProjectCreate(BaseModel):
    name: str
    customer_name: str
    customer_email: Optional[str]
    project_type: str
    data: Dict[str, Any]

class ProjectResponse(BaseModel):
    id: int
    name: str
    customer_name: str
    project_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    data: Dict[str, Any]

# Price Matrix
class PriceMatrixUpload(BaseModel):
    file_name: str
    file_content: str  # Base64 encoded
    matrix_type: str

class PriceCalculationRequest(BaseModel):
    product_id: int
    quantity: int
    options: Dict[str, Any]

class PriceCalculationResponse(BaseModel):
    base_price: float
    total_price: float
    discount: float
    breakdown: Dict[str, float]

# PDF Generation
class PDFGenerationRequest(BaseModel):
    project_id: int
    template: str
    options: Dict[str, Any]

class PDFGenerationResponse(BaseModel):
    pdf_url: str
    file_name: str
    size_bytes: int
```


### Frontend TypeScript Types

```typescript
// frontend/src/types/models.ts

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  createdAt: string;
}

export interface Project {
  id: number;
  name: string;
  customerName: string;
  projectType: 'solar' | 'heatpump' | 'combined';
  status: 'draft' | 'active' | 'completed' | 'archived';
  createdAt: string;
  updatedAt: string;
  data: Record<string, any>;
}

export interface SolarCalculation {
  roofArea: number;
  roofType: string;
  roofAngle: number;
  orientation: string;
  moduleType: string;
  annualConsumption: number;
  location: string;
}

export interface SolarResult {
  systemSize: number;
  moduleCount: number;
  annualProduction: number;
  selfConsumptionRate: number;
  paybackPeriod: number;
  totalCost: number;
  savings25Years: number;
  co2Savings: number;
}

export interface Product {
  id: number;
  name: string;
  category: string;
  manufacturer: string;
  price: number;
  specifications: Record<string, any>;
  imageUrl?: string;
}
```


## Error Handling

### Backend Error Handling

```python
# backend/middleware/error_handler.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

class APIError(Exception):
    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}

async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details,
                "path": str(request.url)
            }
        }
    )

async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation error",
                "details": exc.errors(),
                "path": str(request.url)
            }
        }
    )

async def database_error_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Database error",
                "details": {"type": type(exc).__name__},
                "path": str(request.url)
            }
        }
    )
```

### Frontend Error Handling

```typescript
// frontend/src/services/api.ts

import axios, { AxiosError } from 'axios';
import { toast } from 'react-toastify';

export interface APIError {
  message: string;
  details?: Record<string, any>;
  path?: string;
}

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error: APIError }>) => {
    const apiError = error.response?.data?.error;
    
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    } else if (apiError) {
      // Show error toast
      toast.error(apiError.message);
    } else {
      // Network error
      toast.error('Network error. Please check your connection.');
    }
    
    return Promise.reject(error);
  }
);

export default api;
```


## Testing Strategy

### Backend Testing

**Unit Tests (pytest):**
```python
# tests/test_solar_service.py

import pytest
from backend.services.solar_service import SolarService
from backend.models.schemas import SolarCalculationRequest

@pytest.fixture
def solar_service():
    return SolarService()

def test_calculate_system_size(solar_service):
    request = SolarCalculationRequest(
        roof_area=50.0,
        roof_type="flat",
        roof_angle=30.0,
        orientation="south",
        module_type="standard",
        annual_consumption=4000.0,
        location="Berlin"
    )
    
    result = solar_service.calculate(request)
    
    assert result.system_size > 0
    assert result.module_count > 0
    assert result.annual_production > 0

def test_invalid_roof_area(solar_service):
    with pytest.raises(ValueError):
        request = SolarCalculationRequest(
            roof_area=-10.0,  # Invalid
            # ... other fields
        )
```

**Integration Tests:**
```python
# tests/test_api_integration.py

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_solar_calculation_endpoint():
    response = client.post(
        "/api/v1/solar/calculate",
        json={
            "roof_area": 50.0,
            "roof_type": "flat",
            "roof_angle": 30.0,
            "orientation": "south",
            "module_type": "standard",
            "annual_consumption": 4000.0,
            "location": "Berlin"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "system_size" in data
    assert "module_count" in data

def test_authentication_required():
    response = client.get("/api/v1/projects")
    assert response.status_code == 401
```

### Frontend Testing

**Component Tests (Jest + React Testing Library):**
```typescript
// src/components/SolarCalculator.test.tsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SolarCalculator } from './SolarCalculator';
import * as api from '../services/api';

jest.mock('../services/api');

describe('SolarCalculator', () => {
  it('renders calculator form', () => {
    render(<SolarCalculator />);
    
    expect(screen.getByLabelText('Roof Area')).toBeInTheDocument();
    expect(screen.getByLabelText('Roof Type')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Calculate' })).toBeInTheDocument();
  });

  it('submits calculation and displays results', async () => {
    const mockResult = {
      systemSize: 10.5,
      moduleCount: 30,
      annualProduction: 12000,
    };
    
    (api.calculateSolar as jest.Mock).mockResolvedValue(mockResult);
    
    render(<SolarCalculator />);
    
    fireEvent.change(screen.getByLabelText('Roof Area'), {
      target: { value: '50' }
    });
    fireEvent.click(screen.getByRole('button', { name: 'Calculate' }));
    
    await waitFor(() => {
      expect(screen.getByText(/System Size: 10.5 kWp/)).toBeInTheDocument();
    });
  });
});
```

**E2E Tests (Playwright):**
```typescript
// e2e/solar-calculator.spec.ts

import { test, expect } from '@playwright/test';

test('complete solar calculation flow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Login
  await page.fill('[name="username"]', 'testuser');
  await page.fill('[name="password"]', 'password');
  await page.click('button[type="submit"]');
  
  // Navigate to solar calculator
  await page.click('text=Solar Calculator');
  
  // Fill form
  await page.fill('[name="roofArea"]', '50');
  await page.selectOption('[name="roofType"]', 'flat');
  await page.fill('[name="roofAngle"]', '30');
  
  // Submit
  await page.click('button:has-text("Calculate")');
  
  // Verify results
  await expect(page.locator('.results')).toBeVisible();
  await expect(page.locator('.system-size')).toContainText('kWp');
});
```


## Deployment and Build Process

### Development Environment

**Backend Development:**
```bash
# Install dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server with hot reload
uvicorn main:app --reload --port 8000

# Run tests
pytest tests/ -v --cov=backend
```

**Frontend Development:**
```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Run tests
npm test

# Type checking
npm run type-check
```

**Electron Development:**
```bash
# From project root
npm install

# Start Electron in development mode
npm run electron:dev

# This will:
# 1. Start backend (Python)
# 2. Start frontend dev server (React)
# 3. Launch Electron window
```

### Production Build

**Backend Packaging:**
```bash
# Create standalone Python executable with PyInstaller
cd backend
pyinstaller --onefile \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --hidden-import uvicorn \
  --hidden-import sqlalchemy \
  main.py

# Output: dist/main.exe (Windows) or dist/main (Linux/Mac)
```

**Frontend Build:**
```bash
cd frontend
npm run build

# Output: frontend/dist/
```

**Electron Packaging:**
```json
// package.json
{
  "name": "solar-calculator-pro",
  "version": "1.0.0",
  "main": "electron/main.js",
  "scripts": {
    "electron:dev": "concurrently \"npm run backend:dev\" \"npm run frontend:dev\" \"electron .\"",
    "electron:build": "npm run frontend:build && electron-builder",
    "electron:build:win": "electron-builder --win",
    "electron:build:mac": "electron-builder --mac",
    "electron:build:linux": "electron-builder --linux"
  },
  "build": {
    "appId": "com.yourcompany.solarcalculator",
    "productName": "Solar Calculator Pro",
    "directories": {
      "output": "release"
    },
    "files": [
      "electron/**/*",
      "frontend/dist/**/*",
      "backend/dist/**/*"
    ],
    "extraResources": [
      {
        "from": "backend/dist/main${os === 'win' ? '.exe' : ''}",
        "to": "backend/main${os === 'win' ? '.exe' : ''}"
      }
    ],
    "win": {
      "target": ["nsis"],
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": ["dmg"],
      "icon": "assets/icon.icns",
      "category": "public.app-category.business"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "assets/icon.png",
      "category": "Office"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

### Auto-Update Configuration

```javascript
// electron/updater.js
const { autoUpdater } = require('electron-updater');
const { dialog } = require('electron');

class UpdateManager {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.setupAutoUpdater();
  }

  setupAutoUpdater() {
    autoUpdater.autoDownload = false;
    autoUpdater.autoInstallOnAppQuit = true;

    autoUpdater.on('update-available', (info) => {
      dialog.showMessageBox(this.mainWindow, {
        type: 'info',
        title: 'Update Available',
        message: `Version ${info.version} is available. Do you want to download it now?`,
        buttons: ['Yes', 'No']
      }).then((result) => {
        if (result.response === 0) {
          autoUpdater.downloadUpdate();
        }
      });
    });

    autoUpdater.on('update-downloaded', () => {
      dialog.showMessageBox(this.mainWindow, {
        type: 'info',
        title: 'Update Ready',
        message: 'Update downloaded. The application will restart to install the update.',
        buttons: ['Restart Now', 'Later']
      }).then((result) => {
        if (result.response === 0) {
          autoUpdater.quitAndInstall();
        }
      });
    });
  }

  checkForUpdates() {
    autoUpdater.checkForUpdates();
  }
}

module.exports = UpdateManager;
```

### CI/CD Pipeline (GitHub Actions Example)

```yaml
# .github/workflows/build.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          npm install
          cd backend && pip install -r requirements.txt
      
      - name: Run tests
        run: |
          npm test
          cd backend && pytest
      
      - name: Build application
        run: npm run electron:build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-build
          path: release/*
      
      - name: Release
        uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: release/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```


## Migration Strategy

### Phase 1: Foundation Setup (Week 1-2)

1. **Project Structure Setup**
   - Initialize monorepo structure
   - Setup backend with FastAPI
   - Setup frontend with React + TypeScript + PrimeReact
   - Setup Electron wrapper
   - Configure build tools and CI/CD

2. **Core Infrastructure**
   - Implement authentication system
   - Setup database connections
   - Create API base structure
   - Implement error handling
   - Setup logging and monitoring

### Phase 2: Backend Service Layer (Week 3-4)

1. **Wrap Existing Python Modules**
   - Create service wrappers for:
     - `calculations.py` → `SolarService`
     - `database.py` → `DatabaseService`
     - `pdf_generator.py` → `PDFService`
     - `price_matrix_*.py` → `PricingService`
     - `pv3d.py` → `VisualizationService`
   
2. **Create API Endpoints**
   - Solar calculator endpoints
   - Price matrix endpoints
   - PDF generation endpoints
   - Product management endpoints
   - CRM endpoints

3. **Testing**
   - Unit tests for services
   - Integration tests for APIs
   - Load testing

### Phase 3: Frontend Core Components (Week 5-6)

1. **Layout and Navigation**
   - Main layout with sidebar
   - Navigation menu
   - Header with user menu
   - Dashboard page

2. **Common Components**
   - Form components
   - Data tables
   - Charts
   - Modals and dialogs
   - Loading states

3. **State Management**
   - Setup Zustand/Redux
   - Auth state
   - Project state
   - UI state

### Phase 4: Feature Migration (Week 7-10)

**Priority 1 - Core Features:**
1. Solar Calculator
   - Input forms
   - Calculation results
   - 3D visualization
   - Project management

2. Price Matrix
   - Matrix upload
   - Price calculation
   - Product selection

3. PDF Generation
   - Template selection
   - Preview
   - Generation and download

**Priority 2 - Extended Features:**
4. Heat Pump Calculator
5. CRM System
6. Product Database Management
7. Admin Panel

### Phase 5: Electron Integration (Week 11)

1. **Desktop Features**
   - Native menus
   - System tray
   - File dialogs
   - Notifications

2. **Backend Process Management**
   - Auto-start Python backend
   - Health monitoring
   - Graceful shutdown

3. **Packaging**
   - Windows installer
   - macOS DMG
   - Linux AppImage

### Phase 6: Testing and Optimization (Week 12)

1. **Testing**
   - E2E tests
   - Performance testing
   - User acceptance testing

2. **Optimization**
   - Bundle size optimization
   - API response time optimization
   - Memory usage optimization

3. **Documentation**
   - User manual
   - Developer documentation
   - API documentation

### Phase 7: Deployment and Rollout (Week 13-14)

1. **Beta Release**
   - Internal testing
   - Bug fixes
   - Performance tuning

2. **Production Release**
   - Final testing
   - Release notes
   - Distribution

### Parallel Operation Strategy

During migration, both systems can run in parallel:

1. **Data Sync**: Export/import functionality to move data between systems
2. **Feature Parity Check**: Ensure all Streamlit features are available in new app
3. **User Training**: Provide training materials and support
4. **Gradual Rollout**: Start with power users, then expand

### Rollback Plan

If issues arise:
1. Keep Streamlit version available
2. Maintain data compatibility
3. Document known issues
4. Provide clear communication to users


## Performance Considerations

### Backend Optimization

1. **Database Query Optimization**
   - Use SQLAlchemy query optimization
   - Implement connection pooling
   - Add database indexes for frequently queried fields
   - Use lazy loading for relationships

2. **Caching Strategy**
   ```python
   from functools import lru_cache
   from fastapi_cache import FastAPICache
   from fastapi_cache.backends.redis import RedisBackend
   
   # In-memory caching for expensive calculations
   @lru_cache(maxsize=128)
   def calculate_solar_production(params_hash: str):
       # Expensive calculation
       pass
   
   # Redis caching for API responses
   @router.get("/products")
   @cache(expire=3600)  # Cache for 1 hour
   async def get_products():
       pass
   ```

3. **Async Operations**
   - Use async/await for I/O operations
   - Background tasks for long-running operations
   - WebSocket for real-time updates

4. **API Response Optimization**
   - Pagination for large datasets
   - Field selection (sparse fieldsets)
   - Response compression (gzip)

### Frontend Optimization

1. **Code Splitting**
   ```typescript
   // Lazy load routes
   const SolarCalculator = lazy(() => import('./pages/SolarCalculator'));
   const HeatPump = lazy(() => import('./pages/HeatPump'));
   
   // Route configuration
   <Route path="/solar" element={
     <Suspense fallback={<Loading />}>
       <SolarCalculator />
     </Suspense>
   } />
   ```

2. **State Management Optimization**
   - Use selectors to prevent unnecessary re-renders
   - Memoize expensive computations
   - Implement virtual scrolling for large lists

3. **Asset Optimization**
   - Image lazy loading
   - WebP format for images
   - SVG for icons
   - Tree-shaking unused code

4. **Bundle Optimization**
   ```javascript
   // vite.config.ts
   export default {
     build: {
       rollupOptions: {
         output: {
           manualChunks: {
             'vendor': ['react', 'react-dom'],
             'ui': ['primereact'],
             'charts': ['recharts'],
           }
         }
       }
     }
   }
   ```

### Electron Optimization

1. **Memory Management**
   - Limit renderer process memory
   - Clean up unused resources
   - Monitor memory usage

2. **Startup Time**
   - Preload critical resources
   - Lazy load non-critical features
   - Optimize backend startup

3. **Update Strategy**
   - Delta updates (only changed files)
   - Background downloads
   - Smart update scheduling

## Security Considerations

### Backend Security

1. **Authentication & Authorization**
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import OAuth2PasswordBearer
   from jose import JWTError, jwt
   
   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
   
   async def get_current_user(token: str = Depends(oauth2_scheme)):
       try:
           payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
           username: str = payload.get("sub")
           if username is None:
               raise HTTPException(status_code=401)
           return username
       except JWTError:
           raise HTTPException(status_code=401)
   
   @router.get("/protected")
   async def protected_route(current_user: str = Depends(get_current_user)):
       return {"user": current_user}
   ```

2. **Input Validation**
   - Use Pydantic models for all inputs
   - Sanitize file uploads
   - Validate file types and sizes

3. **SQL Injection Prevention**
   - Use SQLAlchemy ORM (parameterized queries)
   - Never concatenate SQL strings

4. **Rate Limiting**
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.get("/api/v1/calculate")
   @limiter.limit("10/minute")
   async def calculate(request: Request):
       pass
   ```

### Frontend Security

1. **XSS Prevention**
   - React automatically escapes content
   - Sanitize HTML if using dangerouslySetInnerHTML
   - Use Content Security Policy

2. **CSRF Protection**
   - Use CSRF tokens for state-changing operations
   - Verify origin headers

3. **Secure Storage**
   ```typescript
   // Don't store sensitive data in localStorage
   // Use httpOnly cookies for tokens
   
   // For Electron, use electron-store with encryption
   import Store from 'electron-store';
   
   const store = new Store({
     encryptionKey: 'your-encryption-key'
   });
   ```

### Electron Security

1. **Context Isolation**
   ```javascript
   // Enable context isolation
   const mainWindow = new BrowserWindow({
     webPreferences: {
       contextIsolation: true,
       nodeIntegration: false,
       preload: path.join(__dirname, 'preload.js')
     }
   });
   ```

2. **Content Security Policy**
   ```javascript
   session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
     callback({
       responseHeaders: {
         ...details.responseHeaders,
         'Content-Security-Policy': ["default-src 'self'"]
       }
     });
   });
   ```

3. **Secure IPC**
   - Validate all IPC messages
   - Use whitelisted channels
   - Never expose Node.js APIs directly


## Monitoring and Logging

### Backend Logging

```python
# backend/core/logging_config.py

import logging
import sys
from pathlib import Path

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Separate error log
    error_handler = logging.FileHandler(log_dir / "error.log")
    error_handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(error_handler)

# Usage in services
import logging
logger = logging.getLogger(__name__)

class SolarService:
    def calculate(self, request):
        logger.info(f"Starting calculation for {request.location}")
        try:
            result = self._perform_calculation(request)
            logger.info(f"Calculation completed: {result.system_size} kWp")
            return result
        except Exception as e:
            logger.error(f"Calculation failed: {str(e)}", exc_info=True)
            raise
```

### Frontend Logging

```typescript
// frontend/src/utils/logger.ts

enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === 'development';

  private log(level: LogLevel, message: string, data?: any) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      data
    };

    // Console output in development
    if (this.isDevelopment) {
      console[level.toLowerCase()](message, data);
    }

    // Send to backend in production
    if (!this.isDevelopment && level === LogLevel.ERROR) {
      this.sendToBackend(logEntry);
    }
  }

  private async sendToBackend(logEntry: any) {
    try {
      await fetch('/api/v1/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logEntry)
      });
    } catch (e) {
      // Fail silently
    }
  }

  debug(message: string, data?: any) {
    this.log(LogLevel.DEBUG, message, data);
  }

  info(message: string, data?: any) {
    this.log(LogLevel.INFO, message, data);
  }

  warn(message: string, data?: any) {
    this.log(LogLevel.WARN, message, data);
  }

  error(message: string, error?: Error) {
    this.log(LogLevel.ERROR, message, {
      message: error?.message,
      stack: error?.stack
    });
  }
}

export const logger = new Logger();
```

### Application Monitoring

```python
# backend/middleware/monitoring.py

from fastapi import Request
import time
import psutil
from prometheus_client import Counter, Histogram

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

async def monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Record metrics
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    # Add timing header
    response.headers["X-Process-Time"] = str(duration)
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
```

## Conclusion

This design provides a comprehensive architecture for migrating from Streamlit to a modern Electron-based desktop application. The key benefits include:

1. **Preserved Business Logic**: All existing Python code remains intact and functional
2. **Modern UI**: Professional React-based interface with PrimeReact components
3. **Native Desktop Experience**: True desktop application with native features
4. **Scalable Architecture**: Clean separation of concerns allows for future growth
5. **Cross-Platform**: Single codebase for Windows, macOS, and Linux
6. **Maintainable**: Well-structured code with comprehensive testing
7. **Secure**: Industry-standard security practices throughout
8. **Performant**: Optimized for speed and efficiency

The migration can be done incrementally, allowing for parallel operation of both systems during the transition period.
