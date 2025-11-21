# Developer Quick Reference

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd solar-calculator-pro
npm install

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head

# Frontend setup
cd ../frontend
npm install

# Run development
cd ..
npm run dev
```

## Common Commands

### Backend
```bash
cd backend
source venv/bin/activate

# Run server
uvicorn main:app --reload

# Tests
pytest
pytest --cov

# Database
alembic upgrade head
alembic revision --autogenerate -m "message"
```

### Frontend
```bash
cd frontend

# Development
npm run dev

# Tests
npm test
npm run test:coverage

# Build
npm run build

# Lint
npm run lint
npm run type-check
```

### Electron
```bash
# Development
npm run electron:dev

# Build
npm run electron:build
npm run electron:build:win
npm run electron:build:mac
npm run electron:build:linux
```

## Git Workflow

```bash
# Start feature
git checkout develop
git pull origin develop
git checkout -b feature/feature-name

# Commit
git add .
git commit -m "feat: description"

# Push
git push origin feature/feature-name

# Create PR on GitHub
```

## Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance
- `perf`: Performance
- `ci`: CI/CD

## Code Standards

### Python
```python
# Type hints
def calculate(value: float) -> float:
    """Calculate result."""
    return value * 2

# Docstrings (Google style)
def function(param: str) -> int:
    """
    One-line summary.
    
    Args:
        param: Description
        
    Returns:
        Result description
    """
    pass

# Error handling
from core.exceptions import ValidationError

if not valid:
    raise ValidationError("Message", details={})
```

### TypeScript
```typescript
// Component
export const Component: React.FC<Props> = ({ prop }) => {
  const [state, setState] = useState<Type>(initial);
  
  useEffect(() => {
    // Effect
  }, [dependencies]);
  
  const handler = async () => {
    // Handler
  };
  
  return <div>{/* JSX */}</div>;
};

// Types
interface User {
  id: number;
  name: string;
}

type Status = 'idle' | 'loading' | 'success' | 'error';
```

## Testing

### Backend
```python
# tests/test_service.py
import pytest

@pytest.fixture
def service():
    return Service()

def test_function(service):
    result = service.function()
    assert result == expected

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
])
def test_multiple(service, input, expected):
    assert service.function(input) == expected
```

### Frontend
```typescript
// Component.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';

describe('Component', () => {
  it('renders', () => {
    render(<Component />);
    expect(screen.getByText('Text')).toBeInTheDocument();
  });

  it('handles click', async () => {
    render(<Component />);
    fireEvent.click(screen.getByRole('button'));
    await waitFor(() => {
      expect(screen.getByText('Result')).toBeInTheDocument();
    });
  });
});
```

## Debugging

### Backend
```python
# Add breakpoint
import pdb; pdb.set_trace()

# Logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Value: {value}")
```

### Frontend
```typescript
// Console
console.log('Debug:', value);
console.table(array);
console.trace();

// Debugger
debugger;
```

## Troubleshooting

### Port in use
```bash
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Module not found
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database issues
```bash
cd backend
alembic current
alembic upgrade head

# Reset (CAUTION: loses data)
rm solar_calculator.db
alembic upgrade head
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./solar_calculator.db
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000
PORT=8000
DEBUG=True
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

## File Structure

```
solar-calculator-pro/
├── backend/           # Python FastAPI
│   ├── api/v1/       # Endpoints
│   ├── services/     # Business logic
│   ├── models/       # Data models
│   └── tests/        # Tests
├── frontend/          # React TypeScript
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── services/
│   └── tests/
├── electron/          # Electron main
└── docs/             # Documentation
```

## Resources

- [Full Developer Guide](./DEVELOPER_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Architecture](./ARCHITECTURE_OVERVIEW.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Electron Docs](https://www.electronjs.org/docs)

## Keyboard Shortcuts

### VS Code
- `Ctrl+P` - Quick open
- `Ctrl+Shift+P` - Command palette
- `F5` - Debug
- `Ctrl+`` - Terminal
- `Ctrl+/` - Comment

### DevTools
- `F12` - Open DevTools
- `Ctrl+Shift+C` - Inspect
- `Ctrl+Shift+M` - Device toolbar

## Contact

- Issues: [GitHub Issues](https://github.com/your-org/solar-calculator-pro/issues)
- Docs: [Documentation](./README.md)
