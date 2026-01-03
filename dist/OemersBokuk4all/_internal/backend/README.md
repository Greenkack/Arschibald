# Solar Calculator Pro - Backend API

FastAPI backend for the Solar Calculator Pro desktop application.

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── core/                  # Core functionality
│   ├── config.py         # Configuration management
│   └── database.py       # Database connection
├── api/                   # API endpoints
│   └── v1/               # API version 1
│       ├── auth.py       # Authentication endpoints
│       ├── solar.py      # Solar calculator endpoints
│       ├── heatpump.py   # Heat pump endpoints
│       ├── pricing.py    # Price matrix endpoints
│       ├── pdf.py        # PDF generation endpoints
│       ├── crm.py        # CRM endpoints
│       ├── products.py   # Product database endpoints
│       └── admin.py      # Admin panel endpoints
├── services/              # Business logic services
│   ├── solar_service.py
│   ├── heatpump_service.py
│   ├── pricing_service.py
│   ├── pdf_service.py
│   ├── crm_service.py
│   └── product_service.py
├── models/                # Data models
│   ├── schemas.py        # Pydantic models
│   └── database.py       # SQLAlchemy models
└── middleware/            # Middleware
    └── error_handler.py  # Global error handling
```

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
```

### 4. Run Development Server

```bash
# From backend directory
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Health Check: http://localhost:8000/health

## Development

### Running with Auto-Reload

```bash
uvicorn main:app --reload --port 8000
```

### Running Tests

```bash
pytest
```

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DEBUG`: Enable debug mode (True/False)
- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 8000)
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

## Health Check

The backend provides a health check endpoint:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Solar Calculator Pro Backend",
  "version": "1.0.0"
}
```

## Next Steps

This is the foundation setup. Subsequent tasks will add:
1. Authentication system (Task 4)
2. Database models and migrations (Task 3)
3. Service layer for business logic (Phase 2)
4. API endpoints for all features (Phase 2)
5. WebSocket support (Task 18)
6. Testing infrastructure (Phase 15)
