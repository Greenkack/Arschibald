# Setup Guide

## Initial Setup

### 1. System Requirements

- **Node.js**: 18.x or higher
- **Python**: 3.10 or higher
- **npm**: 9.x or higher
- **Git**: Latest version

### 2. Install Dependencies

#### Root Dependencies
```bash
cd solar-calculator-pro
npm install
```

This will install:
- Electron
- electron-builder
- Concurrently (for running multiple processes)
- Husky (for Git hooks)
- wait-on (for waiting on services)

#### Frontend Dependencies
```bash
cd frontend
npm install
```

This installs React, TypeScript, Vite, PrimeReact, and all frontend dependencies.

#### Backend Dependencies
```bash
cd backend

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

### 3. Environment Configuration

#### Frontend Environment
```bash
cd frontend
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=Solar Calculator Pro
VITE_APP_VERSION=1.0.0
```

#### Backend Environment
```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```env
APP_NAME=Solar Calculator Pro
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite+aiosqlite:///./solar_calculator.db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
LOG_LEVEL=INFO
```

### 4. Initialize Git Hooks

```bash
cd solar-calculator-pro
npm run prepare
```

This sets up Husky for pre-commit hooks that will:
- Run ESLint on frontend code
- Run Black and Flake8 on backend code
- Format code with Prettier

## Development Workflow

### Starting Development Environment

From the root directory:
```bash
npm run electron:dev
```

This single command will:
1. Start the FastAPI backend on port 8000
2. Start the Vite dev server on port 3000
3. Wait for both services to be ready
4. Launch the Electron window

### Running Services Separately

If you prefer to run services in separate terminals:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Electron:**
```bash
# Wait for backend and frontend to be ready, then:
electron .
```

### Hot Reload

- **Frontend**: Vite provides instant hot module replacement (HMR)
- **Backend**: Uvicorn auto-reloads on file changes
- **Electron**: Restart manually or use electron-reload (optional)

## Testing

### Running Tests

**All tests:**
```bash
npm test
```

**Frontend tests only:**
```bash
cd frontend
npm test
```

**Backend tests only:**
```bash
cd backend
pytest tests/ -v --cov=backend
```

**With coverage:**
```bash
# Frontend
cd frontend
npm run test:coverage

# Backend
cd backend
pytest tests/ -v --cov=backend --cov-report=html
```

### Writing Tests

**Frontend (Vitest + React Testing Library):**
```typescript
// src/components/MyComponent.test.tsx
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

**Backend (pytest):**
```python
# tests/test_my_endpoint.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_my_endpoint():
    response = client.get("/api/v1/my-endpoint")
    assert response.status_code == 200
```

## Code Quality

### Linting

**Check all code:**
```bash
npm run lint
```

**Auto-fix issues:**
```bash
# Frontend
cd frontend
npm run lint -- --fix

# Backend
cd backend
black .
```

### Formatting

**Format all code:**
```bash
npm run format
```

### Type Checking

**Frontend TypeScript:**
```bash
cd frontend
npm run type-check
```

**Backend (optional with mypy):**
```bash
cd backend
mypy .
```

## Building for Production

### Create Production Build

**All platforms:**
```bash
npm run electron:build
```

**Specific platform:**
```bash
npm run electron:build:win   # Windows
npm run electron:build:mac   # macOS
npm run electron:build:linux # Linux
```

### Build Output

Builds are created in the `release/` directory:
- Windows: `.exe` installer
- macOS: `.dmg` installer
- Linux: `.AppImage` and `.deb` packages

## Troubleshooting

### Backend Won't Start

1. Check Python version: `python --version` (should be 3.10+)
2. Verify virtual environment is activated
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Check port 8000 is not in use

### Frontend Won't Start

1. Check Node version: `node --version` (should be 18+)
2. Clear node_modules: `rm -rf node_modules && npm install`
3. Check port 3000 is not in use
4. Clear Vite cache: `rm -rf node_modules/.vite`

### Electron Won't Launch

1. Ensure backend and frontend are running
2. Check backend health: `curl http://localhost:8000/health`
3. Check frontend: Open `http://localhost:3000` in browser
4. Check Electron logs in terminal

### Tests Failing

1. Ensure all dependencies are installed
2. Check test database is clean
3. Run tests in isolation: `npm test -- --no-coverage`
4. Check for port conflicts

## Next Steps

After setup is complete:

1. Review the architecture documentation in `docs/ARCHITECTURE.md`
2. Check the API documentation at `http://localhost:8000/docs`
3. Explore the component library in `frontend/src/components/`
4. Start implementing features from the task list

## Getting Help

- Check the main README.md
- Review the design document in `.kiro/specs/streamlit-to-electron-migration/design.md`
- Check the requirements in `.kiro/specs/streamlit-to-electron-migration/requirements.md`
