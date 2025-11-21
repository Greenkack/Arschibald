# Developer Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Procedures](#testing-procedures)
7. [Contribution Guidelines](#contribution-guidelines)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

Before you begin development, ensure you have the following installed:

**Required:**
- **Node.js** 18.x or higher
- **Python** 3.10 or higher
- **Git** 2.30 or higher
- **npm** 9.x or higher (comes with Node.js)

**Recommended:**
- **VS Code** with recommended extensions (see `.vscode/extensions.json`)
- **Docker** (for database testing)
- **Postman** or **Insomnia** (for API testing)

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd solar-calculator-pro

# Install dependencies
npm install

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install

# Run development environment
cd ..
npm run dev
```

This will start:
- Backend API server on `http://localhost:8000`
- Frontend dev server on `http://localhost:3000`
- Electron app with hot reload

---

## Development Environment Setup

### Backend Setup


#### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

#### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=sqlite:///./solar_calculator.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

#### 4. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Seed database (optional)
python scripts/seed_database.py
```

#### 5. Run Backend Server

```bash
# Development mode with hot reload
uvicorn main:app --reload --port 8000

# Or use the npm script from root
npm run backend:dev
```

### Frontend Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

#### 2. Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=Solar Calculator Pro
VITE_APP_VERSION=1.0.0
```

#### 3. Run Frontend Dev Server

```bash
# Development mode with hot reload
npm run dev

# Or use the npm script from root
npm run frontend:dev
```

### Electron Setup

#### 1. Install Dependencies

```bash
# From project root
npm install
```

#### 2. Run Electron in Development Mode

```bash
# This starts backend, frontend, and Electron
npm run electron:dev
```

### IDE Configuration

#### VS Code (Recommended)

Install recommended extensions:
- ESLint
- Prettier
- Python
- Pylance
- TypeScript Vue Plugin (Volar)
- GitLens
- Thunder Client (API testing)

**Settings:**
The project includes `.vscode/settings.json` with recommended configurations.

#### PyCharm/IntelliJ

1. Mark `backend` as Sources Root
2. Set Python interpreter to the virtual environment
3. Enable ESLint and Prettier for frontend code
4. Configure run configurations for backend and frontend

---

## Project Structure

```
solar-calculator-pro/
├── backend/                    # Python FastAPI backend
│   ├── alembic/               # Database migrations
│   ├── api/                   # API endpoints
│   │   └── v1/               # API version 1
│   ├── core/                  # Core functionality
│   ├── models/                # Data models
│   ├── services/              # Business logic
│   ├── middleware/            # Middleware
│   ├── tests/                 # Backend tests
│   ├── docs/                  # Backend documentation
│   ├── main.py               # Application entry point
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React TypeScript frontend
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom hooks
│   │   ├── services/         # API services
│   │   ├── store/            # State management
│   │   ├── types/            # TypeScript types
│   │   ├── utils/            # Utility functions
│   │   ├── styles/           # Global styles
│   │   └── App.tsx           # Root component
│   ├── tests/                # Frontend tests
│   └── package.json          # Node dependencies
├── electron/                   # Electron main process
│   ├── main.js               # Main process entry
│   ├── preload.js            # Preload script
│   ├── menu.js               # Application menu
│   ├── tray.js               # System tray
│   ├── backend-manager.js    # Backend process manager
│   └── updater.js            # Auto-update logic
├── docs/                       # Project documentation
├── build/                      # Build scripts
├── tests/                      # E2E tests
├── .github/                    # GitHub workflows
└── package.json               # Root package.json
```

### Key Directories

**Backend:**
- `api/v1/`: REST API endpoints organized by feature
- `services/`: Business logic layer (wraps legacy code)
- `models/`: Pydantic schemas and SQLAlchemy models
- `core/`: Core utilities (auth, database, errors)
- `middleware/`: Request/response middleware
- `legacy/`: Wrappers for existing Streamlit code

**Frontend:**
- `components/`: Reusable UI components
- `pages/`: Top-level page components
- `hooks/`: Custom React hooks
- `services/`: API client and service layer
- `store/`: Zustand state management
- `types/`: TypeScript type definitions

**Electron:**
- `main.js`: Main process (window management, IPC)
- `preload.js`: Secure IPC bridge
- `backend-manager.js`: Python backend lifecycle

---

## Development Workflow

### Branch Strategy

We follow **Git Flow** branching model:

```
main (production)
  └── develop (integration)
       ├── feature/feature-name
       ├── bugfix/bug-description
       ├── hotfix/critical-fix
       └── release/version-number
```

### Creating a Feature


1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Develop Feature**
   - Write code following coding standards
   - Write tests for new functionality
   - Update documentation as needed

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add feature description"
   ```

4. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Create PR on GitHub/GitLab
   - Request code review
   - Address review comments

5. **Merge to Develop**
   - After approval, merge to `develop`
   - Delete feature branch

### Commit Message Convention

We follow **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

**Examples:**
```bash
feat(solar): add battery storage calculation
fix(pricing): correct INDEX/MATCH formula logic
docs(api): update authentication guide
test(backend): add unit tests for solar service
refactor(frontend): extract common form components
```

### Code Review Process

1. **Self-Review**
   - Review your own code before requesting review
   - Run all tests locally
   - Check for console errors/warnings
   - Verify code follows standards

2. **Peer Review**
   - At least one approval required
   - Address all comments
   - Re-request review after changes

3. **Review Checklist**
   - [ ] Code follows project standards
   - [ ] Tests are included and passing
   - [ ] Documentation is updated
   - [ ] No console errors/warnings
   - [ ] Performance is acceptable
   - [ ] Security considerations addressed
   - [ ] Accessibility requirements met

### Daily Development Workflow

```bash
# 1. Start your day
git checkout develop
git pull origin develop

# 2. Start development servers
npm run dev  # Starts backend, frontend, and Electron

# 3. Make changes
# - Edit code
# - Save (hot reload will update)
# - Test in running app

# 4. Run tests frequently
npm run test:backend
npm run test:frontend

# 5. Commit regularly
git add .
git commit -m "feat: description"

# 6. Push at end of day
git push origin feature/your-branch
```

### Hot Reload

**Backend:**
- Uvicorn watches for file changes
- Automatically reloads on save
- Check terminal for reload confirmation

**Frontend:**
- Vite HMR (Hot Module Replacement)
- Instant updates in browser
- Preserves component state when possible

**Electron:**
- Electron-reload watches main process
- Automatically restarts on changes
- Frontend changes don't require restart

---

## Coding Standards

### Python (Backend)

#### Style Guide

Follow **PEP 8** with these specifics:

```python
# Line length: 100 characters (not 79)
# Indentation: 4 spaces
# Quotes: Double quotes for strings

# Good
def calculate_solar_production(
    module_count: int,
    module_power: float,
    location: str
) -> float:
    """
    Calculate annual solar production.
    
    Args:
        module_count: Number of PV modules
        module_power: Power per module in Wp
        location: Installation location
        
    Returns:
        Annual production in kWh
        
    Raises:
        ValueError: If module_count is negative
    """
    if module_count < 0:
        raise ValueError("Module count must be non-negative")
    
    # Implementation
    return module_count * module_power * 1000
```

#### Type Hints

Always use type hints:

```python
from typing import List, Dict, Optional, Union

def process_data(
    items: List[Dict[str, Any]],
    filter_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Process data with optional filtering."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    One-line summary.
    
    Longer description if needed. Can span multiple lines
    and include examples.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Dictionary containing results with keys:
        - 'status': Operation status
        - 'data': Result data
        
    Raises:
        ValueError: If param2 is negative
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result['status'])
        'success'
    """
    pass
```

#### Error Handling

```python
# Use custom exceptions
from core.exceptions import APIError, ValidationError

# Raise with context
if not valid:
    raise ValidationError(
        message="Invalid input",
        details={"field": "module_count", "value": -1}
    )

# Handle specific exceptions
try:
    result = risky_operation()
except ValidationError as e:
    logger.error(f"Validation failed: {e.message}")
    raise
except Exception as e:
    logger.exception("Unexpected error")
    raise APIError("Internal server error")
```

#### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Detailed information for debugging")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Error with traceback")

# Include context
logger.info(
    "Solar calculation completed",
    extra={
        "module_count": 30,
        "production": 12000,
        "user_id": user.id
    }
)
```

#### Code Organization

```python
# 1. Standard library imports
import os
import sys
from datetime import datetime

# 2. Third-party imports
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. Local imports
from core.database import get_db
from models.schemas import SolarRequest
from services.solar_service import SolarService

# 4. Constants
MAX_MODULE_COUNT = 200
DEFAULT_EFFICIENCY = 0.85

# 5. Functions/Classes
class SolarCalculator:
    """Solar calculation logic."""
    pass
```

### TypeScript/React (Frontend)

#### Style Guide

Follow **Airbnb JavaScript Style Guide** with TypeScript:

```typescript
// Use const/let, never var
const API_URL = 'http://localhost:8000';
let counter = 0;

// Use arrow functions
const calculateTotal = (items: Item[]): number => {
  return items.reduce((sum, item) => sum + item.price, 0);
};

// Use template literals
const message = `Total: ${total} EUR`;

// Use destructuring
const { name, email } = user;
const [first, ...rest] = items;

// Use optional chaining
const userName = user?.profile?.name ?? 'Guest';
```

#### Component Structure

```typescript
import React, { useState, useEffect } from 'react';
import { Button } from 'primereact/button';
import { useAuth } from '@/hooks/useAuth';
import { SolarService } from '@/services/solarService';
import './SolarCalculator.css';

// 1. Types/Interfaces
interface SolarCalculatorProps {
  projectId?: number;
  onComplete?: (result: SolarResult) => void;
}

interface SolarResult {
  systemSize: number;
  production: number;
}

// 2. Component
export const SolarCalculator: React.FC<SolarCalculatorProps> = ({
  projectId,
  onComplete
}) => {
  // 3. Hooks
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SolarResult | null>(null);

  // 4. Effects
  useEffect(() => {
    if (projectId) {
      loadProject(projectId);
    }
  }, [projectId]);

  // 5. Handlers
  const handleCalculate = async () => {
    setLoading(true);
    try {
      const data = await SolarService.calculate(formData);
      setResult(data);
      onComplete?.(data);
    } catch (error) {
      console.error('Calculation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // 6. Render
  return (
    <div className="solar-calculator">
      {/* Component JSX */}
    </div>
  );
};
```

#### Type Definitions

```typescript
// Use interfaces for objects
interface User {
  id: number;
  name: string;
  email: string;
}

// Use types for unions/intersections
type Status = 'idle' | 'loading' | 'success' | 'error';
type UserWithRole = User & { role: string };

// Use generics
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

// Export types
export type { User, Status, ApiResponse };
```

#### Hooks

```typescript
// Custom hook example
export const useSolarCalculation = (projectId?: number) => {
  const [data, setData] = useState<SolarResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const calculate = async (input: SolarInput) => {
    setLoading(true);
    setError(null);
    try {
      const result = await SolarService.calculate(input);
      setData(result);
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, calculate };
};
```

### CSS/Styling

```css
/* Use BEM naming convention */
.solar-calculator {
  /* Block */
}

.solar-calculator__header {
  /* Element */
}

.solar-calculator__header--highlighted {
  /* Modifier */
}

/* Use CSS variables for theming */
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --spacing-unit: 8px;
}

.button {
  background-color: var(--primary-color);
  padding: calc(var(--spacing-unit) * 2);
}

/* Mobile-first responsive design */
.container {
  width: 100%;
}

@media (min-width: 768px) {
  .container {
    width: 750px;
  }
}
```

### File Naming

**Backend:**
- Python files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`

**Frontend:**
- Components: `PascalCase.tsx`
- Hooks: `useCamelCase.ts`
- Utils: `camelCase.ts`
- Types: `camelCase.ts` or `types.ts`
- Styles: `ComponentName.css`

---

## Testing Procedures

### Backend Testing

#### Unit Tests

```python
# tests/test_solar_service.py
import pytest
from services.solar_service import SolarService
from models.schemas import SolarCalculationRequest

@pytest.fixture
def solar_service():
    return SolarService()

@pytest.fixture
def valid_request():
    return SolarCalculationRequest(
        roof_area=50.0,
        roof_type="flat",
        roof_angle=30.0,
        orientation="south",
        module_type="standard",
        annual_consumption=4000.0,
        location="Berlin"
    )

def test_calculate_system_size(solar_service, valid_request):
    """Test system size calculation."""
    result = solar_service.calculate(valid_request)
    
    assert result.system_size > 0
    assert result.module_count > 0
    assert result.annual_production > 0

def test_invalid_roof_area(solar_service):
    """Test validation of negative roof area."""
    with pytest.raises(ValueError, match="Roof area must be positive"):
        request = SolarCalculationRequest(
            roof_area=-10.0,
            # ... other fields
        )
        solar_service.calculate(request)

@pytest.mark.parametrize("roof_area,expected_min_size", [
    (30.0, 5.0),
    (50.0, 8.0),
    (100.0, 15.0),
])
def test_system_size_scaling(solar_service, roof_area, expected_min_size):
    """Test that system size scales with roof area."""
    request = SolarCalculationRequest(roof_area=roof_area, ...)
    result = solar_service.calculate(request)
    assert result.system_size >= expected_min_size
```

#### Running Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_solar_service.py

# Run specific test
pytest tests/test_solar_service.py::test_calculate_system_size

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Frontend Testing

#### Component Tests

```typescript
// src/components/SolarCalculator.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SolarCalculator } from './SolarCalculator';
import { SolarService } from '@/services/solarService';

// Mock service
jest.mock('@/services/solarService');

describe('SolarCalculator', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

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
    
    (SolarService.calculate as jest.Mock).mockResolvedValue(mockResult);
    
    render(<SolarCalculator />);
    
    // Fill form
    fireEvent.change(screen.getByLabelText('Roof Area'), {
      target: { value: '50' }
    });
    
    // Submit
    fireEvent.click(screen.getByRole('button', { name: 'Calculate' }));
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText(/System Size: 10.5 kWp/)).toBeInTheDocument();
    });
  });

  it('displays error on calculation failure', async () => {
    (SolarService.calculate as jest.Mock).mockRejectedValue(
      new Error('Calculation failed')
    );
    
    render(<SolarCalculator />);
    
    fireEvent.click(screen.getByRole('button', { name: 'Calculate' }));
    
    await waitFor(() => {
      expect(screen.getByText(/Calculation failed/)).toBeInTheDocument();
    });
  });
});
```

#### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm test -- SolarCalculator.test.tsx

# Update snapshots
npm test -- -u
```

### E2E Testing

```typescript
// tests/e2e/solar-calculator.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Solar Calculator Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Login
    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/dashboard');
  });

  test('complete solar calculation', async ({ page }) => {
    // Navigate to calculator
    await page.click('text=Solar Calculator');
    await expect(page).toHaveURL('/solar-calculator');
    
    // Fill form
    await page.fill('[name="roofArea"]', '50');
    await page.selectOption('[name="roofType"]', 'flat');
    await page.fill('[name="roofAngle"]', '30');
    await page.selectOption('[name="orientation"]', 'south');
    
    // Submit
    await page.click('button:has-text("Calculate")');
    
    // Verify results
    await expect(page.locator('.results')).toBeVisible();
    await expect(page.locator('.system-size')).toContainText('kWp');
    await expect(page.locator('.module-count')).toContainText('modules');
  });

  test('save project', async ({ page }) => {
    // ... perform calculation
    
    // Save project
    await page.click('button:has-text("Save Project")');
    await page.fill('[name="projectName"]', 'Test Project');
    await page.click('button:has-text("Save")');
    
    // Verify saved
    await expect(page.locator('.toast-success')).toContainText('Project saved');
  });
});
```

#### Running E2E Tests

```bash
# Install Playwright
npx playwright install

# Run E2E tests
npm run test:e2e

# Run in headed mode (see browser)
npm run test:e2e -- --headed

# Run specific test
npm run test:e2e -- solar-calculator.spec.ts

# Debug mode
npm run test:e2e -- --debug
```

### Test Coverage Goals

- **Backend:** Minimum 80% coverage
- **Frontend:** Minimum 70% coverage
- **Critical paths:** 100% coverage

### Testing Best Practices

1. **Write tests first (TDD)** when possible
2. **Test behavior, not implementation**
3. **Use descriptive test names**
4. **Keep tests independent**
5. **Mock external dependencies**
6. **Test edge cases and error conditions**
7. **Keep tests fast**
8. **Review test coverage regularly**

---

## Contribution Guidelines

### Before Contributing

1. **Check existing issues** - Avoid duplicate work
2. **Discuss major changes** - Open an issue first
3. **Read the code** - Understand the codebase
4. **Follow standards** - Adhere to coding standards

### Contribution Process


1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/solar-calculator-pro.git
   cd solar-calculator-pro
   
   # Add upstream remote
   git remote add upstream https://github.com/ORIGINAL_OWNER/solar-calculator-pro.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Write code
   - Add tests
   - Update documentation
   - Follow coding standards

4. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   
   # E2E tests
   npm run test:e2e
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add feature description"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill in PR template
   - Request review

### Pull Request Guidelines

**PR Title:**
Follow conventional commits format:
```
feat(solar): add battery storage calculation
fix(pricing): correct INDEX/MATCH formula
docs(api): update authentication guide
```

**PR Description Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots]

## Checklist
- [ ] Code follows project standards
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No console errors/warnings
- [ ] Reviewed own code
```

### Code Review Expectations

**As Author:**
- Respond to comments promptly
- Be open to feedback
- Explain your decisions
- Make requested changes
- Re-request review after changes

**As Reviewer:**
- Be constructive and respectful
- Explain reasoning for suggestions
- Approve when satisfied
- Test the changes if possible

### What to Review

1. **Functionality**
   - Does it work as intended?
   - Are edge cases handled?
   - Is error handling appropriate?

2. **Code Quality**
   - Follows coding standards?
   - Is it readable and maintainable?
   - Are there code smells?
   - Is it properly documented?

3. **Tests**
   - Are tests included?
   - Do tests cover the changes?
   - Are tests meaningful?

4. **Performance**
   - Are there performance concerns?
   - Is caching used appropriately?
   - Are queries optimized?

5. **Security**
   - Are inputs validated?
   - Is authentication/authorization correct?
   - Are there security vulnerabilities?

### Reporting Bugs

Use the bug report template:

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Screenshots
[Add screenshots]

## Environment
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

## Additional Context
Any other relevant information
```

### Suggesting Features

Use the feature request template:

```markdown
## Feature Description
Clear description of the feature

## Problem it Solves
What problem does this solve?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Mockups, examples, etc.
```

---

## Troubleshooting

### Common Issues

#### Backend Won't Start

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
```

---

**Problem:** `Database connection error`

**Solution:**
```bash
# Check if database file exists
ls solar_calculator.db

# If not, run migrations
alembic upgrade head

# Check .env file has correct DATABASE_URL
cat .env | grep DATABASE_URL
```

---

**Problem:** `Port 8000 already in use`

**Solution:**
```bash
# Find process using port 8000
# Linux/Mac:
lsof -i :8000
# Windows:
netstat -ano | findstr :8000

# Kill the process
# Linux/Mac:
kill -9 <PID>
# Windows:
taskkill /PID <PID> /F

# Or use a different port
uvicorn main:app --port 8001
```

#### Frontend Won't Start

**Problem:** `Cannot find module 'react'`

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

**Problem:** `CORS error when calling API`

**Solution:**
Check backend `.env` file:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Restart backend after changing.

---

**Problem:** `Vite build fails`

**Solution:**
```bash
# Clear cache
rm -rf node_modules/.vite

# Rebuild
npm run build
```

#### Electron Issues

**Problem:** `Electron window is blank`

**Solution:**
1. Check if backend is running (port 8000)
2. Check if frontend is built
3. Open DevTools (Ctrl+Shift+I) and check console
4. Check electron logs in terminal

---

**Problem:** `Backend doesn't start with Electron`

**Solution:**
```bash
# Check backend-manager.js configuration
# Verify Python path is correct
# Check if backend/main.py exists

# Test backend manually
cd backend
python -m uvicorn main:app --port 8000
```

#### Database Issues

**Problem:** `Alembic migration fails`

**Solution:**
```bash
# Check current version
alembic current

# Check migration history
alembic history

# Downgrade one version
alembic downgrade -1

# Upgrade again
alembic upgrade head

# If stuck, reset database (CAUTION: loses data)
rm solar_calculator.db
alembic upgrade head
```

---

**Problem:** `Database locked error`

**Solution:**
```bash
# SQLite database is locked by another process
# Close all connections to database
# Restart backend

# If persists, check for zombie processes
ps aux | grep python
kill -9 <PID>
```

#### Testing Issues

**Problem:** `Tests fail with import errors`

**Solution:**
```bash
# Backend
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest

# Or install package in editable mode
pip install -e .
```

---

**Problem:** `Frontend tests timeout`

**Solution:**
```javascript
// Increase timeout in test
test('slow test', async () => {
  // ...
}, 10000); // 10 seconds

// Or in jest.config.js
module.exports = {
  testTimeout: 10000
};
```

#### Build Issues

**Problem:** `Electron build fails`

**Solution:**
```bash
# Clear build cache
rm -rf dist release

# Rebuild
npm run electron:build

# Check electron-builder logs
# Usually in ~/.electron-builder/
```

---

**Problem:** `Python backend packaging fails`

**Solution:**
```bash
cd backend

# Test PyInstaller manually
pyinstaller --onefile main.py

# Check for missing imports
python -c "import main"

# Add hidden imports to spec file
# backend.spec:
# hiddenimports=['uvicorn', 'sqlalchemy', ...]
```

### Getting Help

1. **Check Documentation**
   - README.md
   - API Documentation
   - Architecture Documentation

2. **Search Issues**
   - GitHub Issues
   - Stack Overflow

3. **Ask the Team**
   - Create GitHub Discussion
   - Ask in team chat
   - Email maintainers

4. **Debug Yourself**
   - Use debugger (pdb, VS Code debugger)
   - Add logging
   - Check browser DevTools
   - Read error messages carefully

### Debugging Tips

**Backend Debugging:**
```python
# Use pdb
import pdb; pdb.set_trace()

# Or use VS Code debugger
# Add breakpoint in editor
# Run "Python: Debug Current File"

# Add detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Variable value: {variable}")
```

**Frontend Debugging:**
```typescript
// Use browser DevTools
console.log('Debug:', variable);
console.table(arrayData);
console.trace(); // Show call stack

// Use VS Code debugger
// Add breakpoint in editor
// Run "Debug: Start Debugging"

// React DevTools
// Install React DevTools extension
// Inspect component props and state
```

**Network Debugging:**
```bash
# Check API calls in browser DevTools Network tab
# Look for:
# - Request URL
# - Request method
# - Request headers
# - Request payload
# - Response status
# - Response data

# Use curl to test API
curl -X POST http://localhost:8000/api/v1/solar/calculate \
  -H "Content-Type: application/json" \
  -d '{"roof_area": 50, ...}'

# Use Postman/Insomnia for complex requests
```

---

## Additional Resources

### Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Architecture Overview](./ARCHITECTURE_OVERVIEW.md)
- [Deployment Guide](./DEPLOYMENT_ARCHITECTURE.md)
- [Security Guide](./SECURITY_ARCHITECTURE.md)

### External Resources

**Backend:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)

**Frontend:**
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [PrimeReact Documentation](https://primereact.org/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [React Testing Library](https://testing-library.com/react)

**Electron:**
- [Electron Documentation](https://www.electronjs.org/docs)
- [Electron Builder](https://www.electron.build/)
- [Electron Updater](https://www.electron.build/auto-update)

**Tools:**
- [Git Documentation](https://git-scm.com/doc)
- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Playwright Documentation](https://playwright.dev/)

### Community

- GitHub Discussions
- Stack Overflow (tag: solar-calculator-pro)
- Discord Server (if available)

---

## Appendix

### Environment Variables Reference

**Backend (.env):**
```env
# Database
DATABASE_URL=sqlite:///./solar_calculator.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# External APIs (optional)
WEATHER_API_KEY=your-key
MAPS_API_KEY=your-key
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=Solar Calculator Pro
VITE_APP_VERSION=1.0.0
VITE_ENABLE_ANALYTICS=false
```

### Useful Commands

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload
pytest
pytest --cov
alembic upgrade head
alembic revision --autogenerate -m "message"

# Frontend
cd frontend
npm run dev
npm run build
npm test
npm run lint
npm run type-check

# Electron
npm run electron:dev
npm run electron:build
npm run electron:build:win
npm run electron:build:mac
npm run electron:build:linux

# Root
npm run dev  # Start all
npm run test  # Run all tests
npm run lint  # Lint all
npm run format  # Format all
```

### Keyboard Shortcuts

**VS Code:**
- `Ctrl+P` - Quick file open
- `Ctrl+Shift+P` - Command palette
- `F5` - Start debugging
- `Ctrl+` - Toggle terminal
- `Ctrl+B` - Toggle sidebar
- `Ctrl+/` - Toggle comment
- `Alt+Up/Down` - Move line
- `Ctrl+D` - Select next occurrence

**Browser DevTools:**
- `F12` - Open DevTools
- `Ctrl+Shift+C` - Inspect element
- `Ctrl+Shift+M` - Toggle device toolbar
- `Ctrl+Shift+I` - Open DevTools
- `Ctrl+R` - Reload page
- `Ctrl+Shift+R` - Hard reload

---

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial developer guide
- Setup instructions
- Coding standards
- Testing procedures
- Contribution guidelines

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Contact

For questions or support:
- GitHub Issues: [Project Issues](https://github.com/your-org/solar-calculator-pro/issues)
- Email: dev@solarcalculator.com
- Documentation: [Full Documentation](./README.md)

---

**Happy Coding! 🚀**
