# Solar Calculator Pro

Professional Solar Calculator Desktop Application built with React, FastAPI, and Electron.

## Project Structure

```
solar-calculator-pro/
├── frontend/           # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   ├── utils/
│   │   └── styles/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/            # FastAPI Python backend
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── core/
│   ├── legacy/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── electron/           # Electron main process
│   ├── main.js
│   ├── preload.js
│   └── backend-manager.js
└── package.json        # Root package.json
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Git

## Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd solar-calculator-pro

# Install root dependencies
npm install

# This will automatically install frontend and backend dependencies
```

### 2. Environment Configuration

**Frontend:**
```bash
cd frontend
cp .env.example .env
# Edit .env with your configuration
```

**Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env with your configuration

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Development

### Run All Services

From the root directory:

```bash
npm run electron:dev
```

This will:
1. Start the Python backend (port 8000)
2. Start the React frontend dev server (port 3000)
3. Launch Electron window

### Run Services Individually

**Backend only:**
```bash
npm run backend:dev
# or
cd backend && python -m uvicorn main:app --reload --port 8000
```

**Frontend only:**
```bash
npm run frontend:dev
# or
cd frontend && npm run dev
```

**Electron only (requires backend and frontend running):**
```bash
electron .
```

## Testing

### Run All Tests

```bash
npm test
```

### Frontend Tests

```bash
npm run frontend:test
# or
cd frontend && npm test
```

### Backend Tests

```bash
npm run backend:test
# or
cd backend && pytest tests/ -v --cov=backend
```

## Code Quality

### Linting

```bash
# All
npm run lint

# Frontend only
npm run frontend:lint

# Backend only
npm run backend:lint
```

### Formatting

```bash
# All
npm run format

# Frontend only
npm run frontend:format

# Backend only
npm run backend:format
```

## Building

### Development Build

```bash
npm run electron:build
```

### Platform-Specific Builds

```bash
# Windows
npm run electron:build:win

# macOS
npm run electron:build:mac

# Linux
npm run electron:build:linux
```

Build outputs will be in the `release/` directory.

## Technology Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **PrimeReact** - UI component library
- **Zustand** - State management
- **React Router** - Routing
- **Axios** - HTTP client
- **Recharts** - Data visualization

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **pytest** - Testing framework

### Desktop
- **Electron** - Desktop wrapper
- **electron-builder** - Packaging
- **electron-updater** - Auto-updates

## API Documentation

When the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Status

This project is currently in active development. See the implementation plan in `.kiro/specs/streamlit-to-electron-migration/` for details.

## License

MIT
