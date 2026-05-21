# Coding Standards

## Overview

This document defines the coding standards for the Solar Calculator Pro project. Following these standards ensures code consistency, maintainability, and quality across the codebase.

## General Principles

1. **Readability First** - Code is read more often than written
2. **Consistency** - Follow existing patterns in the codebase
3. **Simplicity** - Prefer simple solutions over clever ones
4. **Documentation** - Document complex logic and public APIs
5. **Testing** - Write tests for new functionality
6. **Performance** - Consider performance, but don't optimize prematurely
7. **Security** - Always validate inputs and handle errors

---

## Python (Backend)

### Style Guide

Follow **PEP 8** with these project-specific rules:

- **Line Length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Imports**: Organized in three groups (standard, third-party, local)

### Naming Conventions

```python
# Modules and packages
my_module.py
my_package/

# Classes
class SolarCalculator:
    pass

class HTTPException:
    pass

# Functions and variables
def calculate_production():
    pass

module_count = 30
annual_production = 12000.0

# Constants
MAX_MODULE_COUNT = 200
DEFAULT_EFFICIENCY = 0.85
API_VERSION = "v1"

# Private (internal use)
def _internal_helper():
    pass

_private_variable = "internal"
```

### Type Hints

Always use type hints for function signatures:

```python
from typing import List, Dict, Optional, Union, Any

# Function with type hints
def calculate_system_size(
    roof_area: float,
    module_power: float,
    efficiency: float = 0.85
) -> float:
    """Calculate system size in kWp."""
    return roof_area * module_power * efficiency

# Complex types
def process_data(
    items: List[Dict[str, Any]],
    filter_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Process list of dictionaries."""
    pass

# Union types
def get_value(key: str) -> Union[int, str, None]:
    """Get value that could be int, str, or None."""
    pass
```

### Docstrings

Use **Google-style** docstrings:

```python
def calculate_solar_production(
    module_count: int,
    module_power: float,
    location: str,
    orientation: str = "south"
) -> Dict[str, float]:
    """
    Calculate annual solar production.
    
    This function calculates the expected annual energy production
    based on module specifications and location data.
    
    Args:
        module_count: Number of PV modules to install
        module_power: Power rating per module in Wp
        location: Installation location (city name)
        orientation: Module orientation (default: "south")
        
    Returns:
        Dictionary containing:
        - 'annual_production': Annual production in kWh
        - 'daily_average': Average daily production in kWh
        - 'peak_power': Peak system power in kWp
        
    Raises:
        ValueError: If module_count is negative or zero
        ValueError: If module_power is negative or zero
        LocationError: If location is not found in database
        
    Example:
        >>> result = calculate_solar_production(30, 400, "Berlin")
        >>> print(result['annual_production'])
        12000.0
        
    Note:
        Production values are estimates based on historical data
        and may vary based on actual weather conditions.
    """
    if module_count <= 0:
        raise ValueError("Module count must be positive")
    
    if module_power <= 0:
        raise ValueError("Module power must be positive")
    
    # Implementation
    peak_power = (module_count * module_power) / 1000
    annual_production = peak_power * 1000  # Simplified
    daily_average = annual_production / 365
    
    return {
        'annual_production': annual_production,
        'daily_average': daily_average,
        'peak_power': peak_power
    }
```

### Error Handling

```python
from core.exceptions import APIError, ValidationError, NotFoundError

# Raise specific exceptions
def get_project(project_id: int) -> Project:
    """Get project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise NotFoundError(
            message=f"Project {project_id} not found",
            details={"project_id": project_id}
        )
    
    return project

# Validate inputs
def create_project(data: ProjectCreate) -> Project:
    """Create new project."""
    if data.module_count < 0:
        raise ValidationError(
            message="Module count must be non-negative",
            details={"field": "module_count", "value": data.module_count}
        )
    
    try:
        project = Project(**data.dict())
        db.add(project)
        db.commit()
        return project
    except IntegrityError as e:
        db.rollback()
        raise APIError(
            message="Failed to create project",
            details={"error": str(e)}
        )

# Handle exceptions in endpoints
@router.post("/projects")
async def create_project_endpoint(
    data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create project endpoint."""
    try:
        project = create_project(data)
        return project
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except APIError as e:
        logger.exception("Failed to create project")
        raise HTTPException(status_code=500, detail=e.message)
```

### Logging

```python
import logging

# Get logger for module
logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.exception("Error with full traceback")

# Include context
logger.info(
    "Solar calculation completed",
    extra={
        "user_id": user.id,
        "project_id": project.id,
        "module_count": 30,
        "production": 12000
    }
)

# Log exceptions properly
try:
    result = risky_operation()
except Exception as e:
    logger.exception("Operation failed")  # Includes traceback
    raise
```

### Code Organization

```python
"""
Module docstring describing the module purpose.

This module contains solar calculation logic including
system sizing, production estimation, and financial analysis.
"""

# 1. Standard library imports
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# 3. Local application imports
from core.database import get_db
from core.exceptions import ValidationError
from models.schemas import SolarRequest, SolarResponse
from services.solar_service import SolarService

# 4. Constants
MAX_MODULE_COUNT = 200
MIN_MODULE_COUNT = 1
DEFAULT_EFFICIENCY = 0.85
HOURS_PER_YEAR = 8760

# 5. Module-level variables (if needed)
_cache = {}

# 6. Functions and classes
def helper_function():
    """Helper function."""
    pass

class SolarCalculator:
    """Main solar calculator class."""
    
    def __init__(self):
        """Initialize calculator."""
        pass
    
    def calculate(self, data: SolarRequest) -> SolarResponse:
        """Perform calculation."""
        pass
```

### Best Practices

```python
# Use list comprehensions
# Good
squares = [x**2 for x in range(10)]

# Avoid
squares = []
for x in range(10):
    squares.append(x**2)

# Use context managers
# Good
with open('file.txt', 'r') as f:
    content = f.read()

# Avoid
f = open('file.txt', 'r')
content = f.read()
f.close()

# Use f-strings
# Good
message = f"User {user.name} has {user.points} points"

# Avoid
message = "User {} has {} points".format(user.name, user.points)

# Use enumerate
# Good
for i, item in enumerate(items):
    print(f"{i}: {item}")

# Avoid
for i in range(len(items)):
    print(f"{i}: {items[i]}")

# Use dict.get() with default
# Good
value = config.get('key', default_value)

# Avoid
value = config['key'] if 'key' in config else default_value

# Use pathlib for file paths
# Good
from pathlib import Path
file_path = Path('data') / 'file.txt'

# Avoid
import os
file_path = os.path.join('data', 'file.txt')
```

---

## TypeScript/React (Frontend)

### Style Guide

Follow **Airbnb JavaScript Style Guide** with TypeScript extensions:

- **Line Length**: 100 characters
- **Indentation**: 2 spaces
- **Quotes**: Single quotes for strings
- **Semicolons**: Always use semicolons

### Naming Conventions

```typescript
// Files
ComponentName.tsx
useCamelCase.ts
camelCase.ts
ComponentName.css

// Components
export const SolarCalculator: React.FC<Props> = () => {};

// Interfaces and Types
interface User {
  id: number;
  name: string;
}

type Status = 'idle' | 'loading' | 'success' | 'error';

// Functions and variables
const calculateTotal = () => {};
const userName = 'John';
let counter = 0;

// Constants
const MAX_RETRIES = 3;
const API_URL = 'http://localhost:8000';

// Enums
enum UserRole {
  Admin = 'admin',
  User = 'user',
  Guest = 'guest'
}

// Private (prefix with underscore)
const _internalHelper = () => {};
```

### Component Structure

```typescript
import React, { useState, useEffect, useCallback } from 'react';
import { Button } from 'primereact/button';
import { useAuth } from '@/hooks/useAuth';
import { SolarService } from '@/services/solarService';
import './SolarCalculator.css';

// 1. Types and Interfaces
interface SolarCalculatorProps {
  projectId?: number;
  initialData?: SolarData;
  onComplete?: (result: SolarResult) => void;
  onError?: (error: Error) => void;
}

interface SolarData {
  roofArea: number;
  moduleType: string;
}

interface SolarResult {
  systemSize: number;
  production: number;
  cost: number;
}

// 2. Component
export const SolarCalculator: React.FC<SolarCalculatorProps> = ({
  projectId,
  initialData,
  onComplete,
  onError
}) => {
  // 3. Hooks (in order: context, state, refs, custom hooks)
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SolarData | null>(initialData || null);
  const [result, setResult] = useState<SolarResult | null>(null);
  const [error, setError] = useState<Error | null>(null);

  // 4. Effects
  useEffect(() => {
    if (projectId) {
      loadProject(projectId);
    }
  }, [projectId]);

  useEffect(() => {
    if (error && onError) {
      onError(error);
    }
  }, [error, onError]);

  // 5. Callbacks and handlers
  const loadProject = useCallback(async (id: number) => {
    try {
      const project = await SolarService.getProject(id);
      setData(project.data);
    } catch (err) {
      setError(err as Error);
    }
  }, []);

  const handleCalculate = async () => {
    if (!data) return;

    setLoading(true);
    setError(null);

    try {
      const calculationResult = await SolarService.calculate(data);
      setResult(calculationResult);
      onComplete?.(calculationResult);
    } catch (err) {
      const error = err as Error;
      setError(error);
      console.error('Calculation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof SolarData, value: any) => {
    setData(prev => prev ? { ...prev, [field]: value } : null);
  };

  // 6. Render helpers (if needed)
  const renderResults = () => {
    if (!result) return null;

    return (
      <div className="results">
        <h3>Results</h3>
        <p>System Size: {result.systemSize} kWp</p>
        <p>Production: {result.production} kWh/year</p>
        <p>Cost: {result.cost} EUR</p>
      </div>
    );
  };

  // 7. Main render
  return (
    <div className="solar-calculator">
      <h2>Solar Calculator</h2>
      
      {error && (
        <div className="error-message">
          {error.message}
        </div>
      )}

      <div className="form">
        {/* Form fields */}
      </div>

      <Button
        label="Calculate"
        onClick={handleCalculate}
        loading={loading}
        disabled={!data}
      />

      {renderResults()}
    </div>
  );
};

// 8. Default props (if using class components)
SolarCalculator.defaultProps = {
  projectId: undefined,
  initialData: undefined,
};
```

### Type Definitions

```typescript
// Use interfaces for objects
interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}

// Use types for unions, intersections, and primitives
type Status = 'idle' | 'loading' | 'success' | 'error';
type ID = string | number;
type UserWithTimestamps = User & {
  createdAt: Date;
  updatedAt: Date;
};

// Use generics
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

// Utility types
type Partial<T> = { [P in keyof T]?: T[P] };
type Required<T> = { [P in keyof T]-?: T[P] };
type Pick<T, K extends keyof T> = { [P in K]: T[P] };
type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;

// Export types
export type { User, Status, ApiResponse, PaginatedResponse };
```

### Hooks

```typescript
// Custom hook structure
export const useSolarCalculation = (projectId?: number) => {
  const [data, setData] = useState<SolarResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const calculate = useCallback(async (input: SolarInput) => {
    setLoading(true);
    setError(null);

    try {
      const result = await SolarService.calculate(input);
      setData(result);
      return result;
    } catch (err) {
      const error = err as Error;
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
  }, []);

  useEffect(() => {
    if (projectId) {
      // Load project data
    }
  }, [projectId]);

  return {
    data,
    loading,
    error,
    calculate,
    reset
  };
};
```

### Best Practices

```typescript
// Use optional chaining
const userName = user?.profile?.name ?? 'Guest';

// Use nullish coalescing
const port = config.port ?? 3000;

// Use destructuring
const { name, email } = user;
const [first, ...rest] = items;

// Use spread operator
const newUser = { ...user, name: 'New Name' };
const newItems = [...items, newItem];

// Use template literals
const message = `Hello, ${user.name}!`;

// Use arrow functions
const double = (x: number) => x * 2;

// Use async/await
const fetchData = async () => {
  try {
    const response = await api.get('/data');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch:', error);
    throw error;
  }
};

// Use early returns
const processUser = (user: User | null) => {
  if (!user) return null;
  if (!user.isActive) return null;
  
  // Process active user
  return user.name;
};

// Use const for immutable values
const MAX_RETRIES = 3;
const API_URL = 'http://localhost:8000';

// Use meaningful variable names
// Good
const userCount = users.length;
const isAuthenticated = !!token;

// Avoid
const n = users.length;
const flag = !!token;
```

---

## CSS/Styling

### BEM Naming Convention

```css
/* Block */
.solar-calculator {
  padding: 20px;
}

/* Element */
.solar-calculator__header {
  font-size: 24px;
  margin-bottom: 16px;
}

.solar-calculator__form {
  display: flex;
  flex-direction: column;
}

.solar-calculator__button {
  margin-top: 16px;
}

/* Modifier */
.solar-calculator__button--primary {
  background-color: blue;
}

.solar-calculator__button--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* State */
.solar-calculator.is-loading {
  opacity: 0.7;
}

.solar-calculator__form.has-error {
  border-color: red;
}
```

### CSS Variables

```css
:root {
  /* Colors */
  --color-primary: #007bff;
  --color-secondary: #6c757d;
  --color-success: #28a745;
  --color-danger: #dc3545;
  --color-warning: #ffc107;
  --color-info: #17a2b8;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Typography */
  --font-family: 'Inter', sans-serif;
  --font-size-sm: 12px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 20px;
  
  /* Borders */
  --border-radius: 4px;
  --border-width: 1px;
  --border-color: #dee2e6;
}

/* Usage */
.button {
  background-color: var(--color-primary);
  padding: var(--spacing-md);
  border-radius: var(--border-radius);
  font-size: var(--font-size-md);
}
```

### Responsive Design

```css
/* Mobile-first approach */
.container {
  width: 100%;
  padding: var(--spacing-md);
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    width: 750px;
    margin: 0 auto;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    width: 960px;
  }
}

/* Large desktop */
@media (min-width: 1280px) {
  .container {
    width: 1200px;
  }
}
```

---

## Git Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `build`: Build system changes
- `revert`: Revert previous commit

### Examples

```bash
# Simple feature
feat(solar): add battery storage calculation

# Bug fix with details
fix(pricing): correct INDEX/MATCH formula logic

The formula was using incorrect column indices when looking up
prices in the matrix. This fix ensures the correct cell is
referenced based on module count and battery model.

Closes #123

# Documentation
docs(api): update authentication guide

# Multiple changes
feat(solar): add multiple features

- Add battery storage calculation
- Implement shading analysis
- Add weather data integration

# Breaking change
feat(api)!: change authentication flow

BREAKING CHANGE: The authentication endpoint now requires
a refresh token in addition to the access token.

Migration guide: Update your API calls to include the
refresh_token parameter.
```

---

## Code Review Checklist

### Functionality
- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No obvious bugs

### Code Quality
- [ ] Follows coding standards
- [ ] Is readable and maintainable
- [ ] No code smells
- [ ] Properly documented
- [ ] No commented-out code
- [ ] No console.log/print statements

### Tests
- [ ] Tests are included
- [ ] Tests cover the changes
- [ ] Tests are meaningful
- [ ] Tests pass

### Performance
- [ ] No performance concerns
- [ ] Caching used appropriately
- [ ] Queries optimized
- [ ] No unnecessary re-renders (React)

### Security
- [ ] Inputs are validated
- [ ] Authentication/authorization correct
- [ ] No security vulnerabilities
- [ ] Sensitive data protected

### Documentation
- [ ] Code is documented
- [ ] API documentation updated
- [ ] README updated if needed
- [ ] Migration guide if breaking change

---

## Tools and Automation

### Linting

**Backend (Python):**
```bash
# Flake8
flake8 .

# Black (formatter)
black .

# isort (import sorting)
isort .

# mypy (type checking)
mypy .
```

**Frontend (TypeScript):**
```bash
# ESLint
npm run lint

# Prettier (formatter)
npm run format

# TypeScript compiler
npm run type-check
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### CI/CD

All checks run automatically on:
- Pull requests
- Commits to main/develop
- Release tags

---

## Resources

- [PEP 8](https://pep8.org/)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [React Best Practices](https://react.dev/learn)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## Questions?

If you have questions about coding standards:
1. Check this document
2. Look at existing code for examples
3. Ask in team chat
4. Create a GitHub Discussion

---

**Remember: Consistency is key. When in doubt, follow existing patterns in the codebase.**
