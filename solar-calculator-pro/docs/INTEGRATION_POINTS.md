# Integration Points

## Table of Contents

1. [Overview](#overview)
2. [Internal Integrations](#internal-integrations)
3. [External Integrations](#external-integrations)
4. [Data Exchange Formats](#data-exchange-formats)
5. [Integration Patterns](#integration-patterns)
6. [Error Handling](#error-handling)

## Overview

This document describes all integration points in Solar Calculator Pro, including internal component integrations and external system integrations.

## Internal Integrations

### Frontend-Backend Integration

```
┌─────────────────────────────────────────────────────────┐
│          Frontend-Backend Communication                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  HTTP REST API                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  React Components ◄──────► FastAPI Endpoints     │  │
│  │                                                   │  │
│  │  • GET /api/v1/projects                          │  │
│  │  • POST /api/v1/solar/calculate                  │  │
│  │  • PUT /api/v1/projects/{id}                     │  │
│  │  • DELETE /api/v1/projects/{id}                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  WebSocket                                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  React Components ◄──────► Socket.IO Server      │  │
│  │                                                   │  │
│  │  • Real-time calculation progress                │  │
│  │  • Live notifications                            │  │
│  │  • Collaborative editing                         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Electron-Frontend Integration

```javascript
// electron/preload.js - IPC Bridge

contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  selectFile: () => ipcRenderer.invoke('dialog:openFile'),
  saveFile: (data) => ipcRenderer.invoke('dialog:saveFile', data),
  
  // Backend communication
  getBackendUrl: () => ipcRenderer.invoke('backend:getUrl'),
  checkBackendHealth: () => ipcRenderer.invoke('backend:health'),
  
  // Window operations
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),
  
  // System operations
  openExternal: (url) => ipcRenderer.invoke('shell:openExternal', url),
  showItemInFolder: (path) => ipcRenderer.invoke('shell:showItemInFolder', path),
  
  // Updates
  checkForUpdates: () => ipcRenderer.invoke('updater:check'),
  onUpdateAvailable: (callback) => ipcRenderer.on('updater:available', callback),
  onUpdateDownloaded: (callback) => ipcRenderer.on('updater:downloaded', callback)
});
```

### Electron-Backend Integration

```javascript
// electron/backend-manager.js

class BackendManager {
  constructor() {
    this.process = null;
    this.port = 8000;
    this.maxRetries = 3;
  }

  async start() {
    const backendPath = this.getBackendPath();
    
    this.process = spawn(backendPath, ['--port', this.port], {
      cwd: path.dirname(backendPath),
      env: {
        ...process.env,
        PYTHONUNBUFFERED: '1'
      }
    });
    
    this.process.stdout.on('data', (data) => {
      console.log(`Backend: ${data}`);
    });
    
    this.process.stderr.on('data', (data) => {
      console.error(`Backend Error: ${data}`);
    });
    
    await this.waitForBackend();
  }

  async waitForBackend() {
    for (let i = 0; i < this.maxRetries; i++) {
      try {
        const response = await axios.get(`http://localhost:${this.port}/health`);
        if (response.status === 200) {
          console.log('Backend is ready');
          return;
        }
      } catch (error) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    throw new Error('Backend failed to start');
  }

  async stop() {
    if (this.process) {
      this.process.kill('SIGTERM');
      await new Promise(resolve => setTimeout(resolve, 1000));
      if (!this.process.killed) {
        this.process.kill('SIGKILL');
      }
    }
  }
}
```

### Backend Service Layer Integration

```python
# backend/services/solar_service.py

class SolarService:
    def __init__(self, db: Session):
        self.db = db
        self.calculator = LegacyCalculatorWrapper()
        self.pricing = PricingService(db)
        self.pdf = PDFService(db)
    
    async def calculate_and_save(
        self,
        request: SolarCalculationRequest,
        user_id: int
    ) -> SolarCalculationResponse:
        # Calculate using legacy code
        result = self.calculator.calculate(request)
        
        # Get pricing
        pricing = await self.pricing.calculate_price(
            module_count=result.module_count,
            battery_model=request.battery_model
        )
        result.total_cost = pricing.total_price
        
        # Save to database
        project = Project(
            user_id=user_id,
            name=request.project_name,
            data=result.dict()
        )
        self.db.add(project)
        self.db.commit()
        
        return result
```

### Database Integration

```python
# backend/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./solar_calculator.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoints
@app.get("/api/v1/projects")
async def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    return projects
```

## External Integrations

### Weather API Integration

```python
# backend/services/weather_service.py

import httpx
from typing import Dict, Any

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = 'https://api.openweathermap.org/data/2.5'
    
    async def get_solar_radiation(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/solar_radiation',
                params={
                    'lat': latitude,
                    'lon': longitude,
                    'appid': self.api_key
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_historical_data(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/history',
                params={
                    'lat': latitude,
                    'lon': longitude,
                    'start': start_date,
                    'end': end_date,
                    'appid': self.api_key
                }
            )
            response.raise_for_status()
            return response.json()
```

### Mapping API Integration

```typescript
// frontend/src/services/mapService.ts

import axios from 'axios';

class MapService {
  private apiKey: string;
  private baseUrl = 'https://maps.googleapis.com/maps/api';

  async geocode(address: string): Promise<GeocodeResult> {
    const response = await axios.get(`${this.baseUrl}/geocode/json`, {
      params: {
        address,
        key: this.apiKey
      }
    });
    
    if (response.data.status !== 'OK') {
      throw new Error(`Geocoding failed: ${response.data.status}`);
    }
    
    return response.data.results[0];
  }

  async reverseGeocode(lat: number, lng: number): Promise<string> {
    const response = await axios.get(`${this.baseUrl}/geocode/json`, {
      params: {
        latlng: `${lat},${lng}`,
        key: this.apiKey
      }
    });
    
    if (response.data.status !== 'OK') {
      throw new Error(`Reverse geocoding failed: ${response.data.status}`);
    }
    
    return response.data.results[0].formatted_address;
  }
}

export const mapService = new MapService();
```

### Email Service Integration

```python
# backend/services/email_service.py

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
            MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
            MAIL_FROM=os.getenv('MAIL_FROM'),
            MAIL_PORT=587,
            MAIL_SERVER='smtp.gmail.com',
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False
        )
        self.mail = FastMail(self.conf)
    
    async def send_pdf(
        self,
        recipient: str,
        subject: str,
        body: str,
        pdf_bytes: bytes,
        pdf_filename: str
    ):
        message = MessageSchema(
            subject=subject,
            recipients=[recipient],
            body=body,
            subtype='html',
            attachments=[{
                'file': pdf_bytes,
                'filename': pdf_filename,
                'mimetype': 'application/pdf'
            }]
        )
        
        await self.mail.send_message(message)
    
    async def send_notification(
        self,
        recipients: List[str],
        subject: str,
        template: str,
        context: dict
    ):
        # Render template with context
        body = self.render_template(template, context)
        
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype='html'
        )
        
        await self.mail.send_message(message)
```

### Payment Gateway Integration

```python
# backend/services/payment_service.py

import stripe
from typing import Dict, Any

class PaymentService:
    def __init__(self):
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = 'eur',
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata=metadata or {}
        )
        return {
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        }
    
    async def confirm_payment(
        self,
        payment_intent_id: str
    ) -> bool:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return intent.status == 'succeeded'
    
    async def create_customer(
        self,
        email: str,
        name: str
    ) -> str:
        customer = stripe.Customer.create(
            email=email,
            name=name
        )
        return customer.id
```

### Cloud Storage Integration

```python
# backend/services/storage_service.py

from google.cloud import storage
from typing import BinaryIO

class StorageService:
    def __init__(self):
        self.client = storage.Client()
        self.bucket_name = os.getenv('GCS_BUCKET_NAME')
        self.bucket = self.client.bucket(self.bucket_name)
    
    async def upload_file(
        self,
        file: BinaryIO,
        destination_path: str,
        content_type: str = 'application/octet-stream'
    ) -> str:
        blob = self.bucket.blob(destination_path)
        blob.upload_from_file(file, content_type=content_type)
        return blob.public_url
    
    async def download_file(
        self,
        source_path: str
    ) -> bytes:
        blob = self.bucket.blob(source_path)
        return blob.download_as_bytes()
    
    async def delete_file(
        self,
        file_path: str
    ):
        blob = self.bucket.blob(file_path)
        blob.delete()
```

## Data Exchange Formats

### API Request/Response Format

```json
// POST /api/v1/solar/calculate
{
  "roof_area": 50.0,
  "roof_type": "flat",
  "roof_angle": 30.0,
  "orientation": "south",
  "module_type": "standard",
  "annual_consumption": 4000.0,
  "location": "Berlin",
  "battery_model": "Tesla Powerwall 2"
}

// Response
{
  "system_size": 10.5,
  "module_count": 30,
  "annual_production": 12000.0,
  "self_consumption_rate": 0.65,
  "payback_period": 8.5,
  "total_cost": 18500.00,
  "savings_25_years": 45000.00,
  "co2_savings": 150.0,
  "dynamic_key": "solar_calc_123_20250120143022",
  "pdf_bytes": "base64_encoded_pdf_data..."
}
```

### WebSocket Message Format

```json
// Progress update
{
  "type": "progress",
  "calculation_id": "calc_123",
  "progress": 45,
  "message": "Calculating module placement...",
  "timestamp": "2025-01-20T14:30:22Z"
}

// Completion
{
  "type": "complete",
  "calculation_id": "calc_123",
  "result": {
    "system_size": 10.5,
    "module_count": 30,
    ...
  },
  "timestamp": "2025-01-20T14:30:45Z"
}

// Error
{
  "type": "error",
  "calculation_id": "calc_123",
  "error": {
    "code": "CALCULATION_FAILED",
    "message": "Invalid roof dimensions",
    "details": {}
  },
  "timestamp": "2025-01-20T14:30:30Z"
}
```

### Database Export Format

```json
// Project export
{
  "version": "1.0",
  "export_date": "2025-01-20T14:30:00Z",
  "projects": [
    {
      "id": 1,
      "name": "Customer A Solar System",
      "created_at": "2025-01-15T10:00:00Z",
      "data": {
        "calculation": {...},
        "pricing": {...},
        "documents": [...]
      }
    }
  ]
}
```

## Integration Patterns

### Retry Pattern

```python
# backend/utils/retry.py

from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_external_api(url: str, params: dict):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
```

### Circuit Breaker Pattern

```python
# backend/utils/circuit_breaker.py

from pybreaker import CircuitBreaker

weather_breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=60
)

@weather_breaker
async def get_weather_data(location: str):
    return await weather_service.get_data(location)
```

### Adapter Pattern

```python
# backend/adapters/legacy_adapter.py

class LegacyCalculatorAdapter:
    """Adapter for legacy calculation code"""
    
    def __init__(self):
        # Import legacy module
        from legacy import calculations
        self.legacy_calc = calculations
    
    def calculate(self, request: SolarCalculationRequest) -> dict:
        # Convert modern request to legacy format
        legacy_input = self._convert_to_legacy(request)
        
        # Call legacy function
        legacy_result = self.legacy_calc.calculate_solar_system(legacy_input)
        
        # Convert legacy result to modern format
        return self._convert_from_legacy(legacy_result)
    
    def _convert_to_legacy(self, request: SolarCalculationRequest) -> dict:
        return {
            'dachflaeche': request.roof_area,
            'dachtyp': request.roof_type,
            'neigung': request.roof_angle,
            'ausrichtung': request.orientation,
            'modultyp': request.module_type,
            'jahresverbrauch': request.annual_consumption,
            'standort': request.location
        }
    
    def _convert_from_legacy(self, result: dict) -> dict:
        return {
            'system_size': result['systemgroesse'],
            'module_count': result['modulanzahl'],
            'annual_production': result['jahresertrag'],
            ...
        }
```

## Error Handling

### Integration Error Handling

```python
# backend/core/integration_errors.py

class IntegrationError(Exception):
    """Base class for integration errors"""
    pass

class ExternalAPIError(IntegrationError):
    """External API call failed"""
    def __init__(self, service: str, status_code: int, message: str):
        self.service = service
        self.status_code = status_code
        self.message = message
        super().__init__(f"{service} API error ({status_code}): {message}")

class DatabaseConnectionError(IntegrationError):
    """Database connection failed"""
    pass

class LegacyCodeError(IntegrationError):
    """Legacy code execution failed"""
    pass

# Usage
try:
    result = await weather_service.get_data(location)
except httpx.HTTPStatusError as e:
    raise ExternalAPIError(
        service='Weather API',
        status_code=e.response.status_code,
        message=str(e)
    )
```

### Graceful Degradation

```python
# backend/services/solar_service.py

async def calculate_with_weather(
    self,
    request: SolarCalculationRequest
) -> SolarCalculationResponse:
    try:
        # Try to get real weather data
        weather_data = await self.weather_service.get_data(request.location)
    except ExternalAPIError:
        # Fall back to historical averages
        logger.warning(f"Weather API unavailable, using historical data")
        weather_data = self.get_historical_average(request.location)
    
    # Continue with calculation
    return self.calculate(request, weather_data)
```

## Summary

The integration architecture provides:

- **Internal Integration**: Seamless communication between components
- **External Integration**: Robust connections to external services
- **Data Exchange**: Standardized formats for all integrations
- **Error Handling**: Comprehensive error handling and recovery
- **Patterns**: Proven integration patterns (retry, circuit breaker, adapter)
- **Graceful Degradation**: Fallback mechanisms for external failures
- **Monitoring**: Integration health monitoring and logging
