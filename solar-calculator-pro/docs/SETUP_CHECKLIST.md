# Development Setup Checklist

Use this checklist to ensure your development environment is properly configured.

## Prerequisites

### Required Software

- [ ] **Node.js 18.x or higher** installed
  ```bash
  node --version  # Should be v18.x.x or higher
  ```

- [ ] **Python 3.10 or higher** installed
  ```bash
  python --version  # Should be 3.10.x or higher
  ```

- [ ] **Git 2.30 or higher** installed
  ```bash
  git --version  # Should be 2.30.x or higher
  ```

- [ ] **npm 9.x or higher** installed
  ```bash
  npm --version  # Should be 9.x.x or higher
  ```

### Recommended Software

- [ ] **VS Code** or preferred IDE installed
- [ ] **Postman** or **Insomnia** for API testing
- [ ] **Docker** (optional, for database testing)

## Repository Setup

- [ ] Repository cloned
  ```bash
  git clone <repository-url>
  cd solar-calculator-pro
  ```

- [ ] Git configured
  ```bash
  git config user.name "Your Name"
  git config user.email "your.email@example.com"
  ```

- [ ] Upstream remote added (if forked)
  ```bash
  git remote add upstream <original-repo-url>
  ```

## Backend Setup

- [ ] Navigate to backend directory
  ```bash
  cd backend
  ```

- [ ] Virtual environment created
  ```bash
  python -m venv venv
  ```

- [ ] Virtual environment activated
  ```bash
  # Linux/Mac:
  source venv/bin/activate
  # Windows:
  venv\Scripts\activate
  ```

- [ ] Dependencies installed
  ```bash
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  ```

- [ ] `.env` file created
  ```bash
  cp .env.example .env
  # Edit .env with your settings
  ```

- [ ] Environment variables configured
  - [ ] `DATABASE_URL` set
  - [ ] `SECRET_KEY` set (generate new for production)
  - [ ] `CORS_ORIGINS` includes frontend URL
  - [ ] `PORT` set (default: 8000)

- [ ] Database initialized
  ```bash
  alembic upgrade head
  ```

- [ ] Database seeded (optional)
  ```bash
  python scripts/seed_database.py
  ```

- [ ] Backend server starts successfully
  ```bash
  uvicorn main:app --reload
  # Should start on http://localhost:8000
  ```

- [ ] API documentation accessible
  - [ ] Swagger UI: http://localhost:8000/docs
  - [ ] ReDoc: http://localhost:8000/redoc

- [ ] Backend tests pass
  ```bash
  pytest
  ```

## Frontend Setup

- [ ] Navigate to frontend directory
  ```bash
  cd frontend
  ```

- [ ] Dependencies installed
  ```bash
  npm install
  ```

- [ ] `.env` file created
  ```bash
  cp .env.example .env
  # Edit .env with your settings
  ```

- [ ] Environment variables configured
  - [ ] `VITE_API_URL` points to backend
  - [ ] `VITE_WS_URL` points to WebSocket
  - [ ] `VITE_APP_NAME` set
  - [ ] `VITE_APP_VERSION` set

- [ ] Frontend dev server starts successfully
  ```bash
  npm run dev
  # Should start on http://localhost:3000 or http://localhost:5173
  ```

- [ ] Frontend tests pass
  ```bash
  npm test
  ```

- [ ] TypeScript compiles without errors
  ```bash
  npm run type-check
  ```

- [ ] Linting passes
  ```bash
  npm run lint
  ```

## Electron Setup

- [ ] Navigate to project root
  ```bash
  cd ..  # From frontend or backend
  ```

- [ ] Root dependencies installed
  ```bash
  npm install
  ```

- [ ] Electron starts successfully
  ```bash
  npm run electron:dev
  ```

- [ ] Backend starts automatically with Electron
  - [ ] Check terminal for backend startup logs
  - [ ] Backend accessible at http://localhost:8000

- [ ] Frontend loads in Electron window
  - [ ] Window opens
  - [ ] No blank screen
  - [ ] No console errors (check DevTools: Ctrl+Shift+I)

## IDE Configuration

### VS Code

- [ ] Workspace opened
  ```bash
  code .
  ```

- [ ] Recommended extensions installed
  - [ ] ESLint
  - [ ] Prettier
  - [ ] Python
  - [ ] Pylance
  - [ ] TypeScript Vue Plugin (Volar)
  - [ ] GitLens

- [ ] Settings synced
  - [ ] `.vscode/settings.json` applied
  - [ ] Formatting on save enabled
  - [ ] Linting enabled

- [ ] Python interpreter selected
  - [ ] Select `backend/venv/bin/python`

- [ ] Debugger configured
  - [ ] Backend debug configuration works
  - [ ] Frontend debug configuration works

### PyCharm/IntelliJ (Optional)

- [ ] Project opened
- [ ] Python interpreter set to virtual environment
- [ ] `backend` marked as Sources Root
- [ ] ESLint and Prettier enabled for frontend
- [ ] Run configurations created

## Git Configuration

- [ ] Pre-commit hooks installed (if using)
  ```bash
  npm run prepare
  ```

- [ ] Git hooks working
  - [ ] Linting runs on commit
  - [ ] Tests run on push (if configured)

- [ ] `.gitignore` properly configured
  - [ ] `node_modules/` ignored
  - [ ] `venv/` ignored
  - [ ] `.env` ignored
  - [ ] Build artifacts ignored

## Testing Setup

- [ ] Backend tests run successfully
  ```bash
  cd backend
  pytest
  ```

- [ ] Backend test coverage generated
  ```bash
  pytest --cov --cov-report=html
  # Check htmlcov/index.html
  ```

- [ ] Frontend tests run successfully
  ```bash
  cd frontend
  npm test
  ```

- [ ] Frontend test coverage generated
  ```bash
  npm run test:coverage
  # Check coverage/index.html
  ```

- [ ] E2E tests setup (optional)
  ```bash
  npx playwright install
  npm run test:e2e
  ```

## Documentation Access

- [ ] README.md reviewed
- [ ] Developer Guide accessible
  - [ ] `docs/DEVELOPER_GUIDE.md`
- [ ] API Documentation accessible
  - [ ] `docs/API_DOCUMENTATION.md`
  - [ ] http://localhost:8000/docs (Swagger)
- [ ] Architecture Documentation accessible
  - [ ] `docs/ARCHITECTURE_OVERVIEW.md`

## Verification

### Backend Verification

- [ ] Health check endpoint works
  ```bash
  curl http://localhost:8000/health
  # Should return: {"status": "healthy"}
  ```

- [ ] Authentication endpoint works
  ```bash
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}'
  ```

- [ ] Database connection works
  - [ ] No connection errors in logs
  - [ ] Can query database

### Frontend Verification

- [ ] Application loads in browser
  - [ ] No blank screen
  - [ ] No console errors
  - [ ] Styles load correctly

- [ ] Can navigate between pages
  - [ ] Routing works
  - [ ] No 404 errors

- [ ] Can make API calls
  - [ ] Login works
  - [ ] Data fetches successfully
  - [ ] No CORS errors

### Electron Verification

- [ ] Application window opens
- [ ] Backend starts automatically
- [ ] Frontend loads in window
- [ ] Native menus work
- [ ] DevTools accessible (Ctrl+Shift+I)
- [ ] No errors in console

## Common Issues Checklist

If you encounter issues, check these:

### Backend Issues

- [ ] Virtual environment activated?
- [ ] All dependencies installed?
- [ ] `.env` file exists and configured?
- [ ] Database initialized?
- [ ] Port 8000 not in use?
- [ ] Python version correct?

### Frontend Issues

- [ ] Dependencies installed?
- [ ] `.env` file exists and configured?
- [ ] Backend running and accessible?
- [ ] No CORS errors?
- [ ] Node version correct?
- [ ] Port not in use?

### Electron Issues

- [ ] Backend and frontend dependencies installed?
- [ ] Backend starts with Electron?
- [ ] Frontend builds successfully?
- [ ] No errors in Electron console?

## Next Steps

Once all items are checked:

1. [ ] Read the [Developer Guide](./DEVELOPER_GUIDE.md)
2. [ ] Review [Coding Standards](./DEVELOPER_GUIDE.md#coding-standards)
3. [ ] Understand [Git Workflow](./DEVELOPER_GUIDE.md#development-workflow)
4. [ ] Check [Contribution Guidelines](./DEVELOPER_GUIDE.md#contribution-guidelines)
5. [ ] Start developing!

## Getting Help

If you're stuck:

1. Check [Troubleshooting](./DEVELOPER_GUIDE.md#troubleshooting)
2. Search [GitHub Issues](https://github.com/your-org/solar-calculator-pro/issues)
3. Ask in team chat
4. Create a new issue with details

## Checklist Complete! 🎉

If all items are checked, you're ready to start developing!

```bash
# Start development environment
npm run dev

# Or start components individually
npm run backend:dev   # Backend only
npm run frontend:dev  # Frontend only
npm run electron:dev  # Full Electron app
```

Happy coding! 🚀
