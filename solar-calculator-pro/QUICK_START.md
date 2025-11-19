# Quick Start Guide

Get up and running with Solar Calculator Pro in minutes.

## Prerequisites Check

Before starting, ensure you have:

```bash
# Check Node.js (should be 18+)
node --version

# Check npm (should be 9+)
npm --version

# Check Python (should be 3.10+)
python --version
# or
python3 --version

# Check Git
git --version
```

## Installation (5 minutes)

### 1. Install Root Dependencies

```bash
cd solar-calculator-pro
npm install
```

This installs Electron, build tools, and development utilities.

### 2. Setup Frontend

```bash
cd frontend
npm install
cp .env.example .env
```

Edit `.env` if needed (defaults work for local development).

### 3. Setup Backend

```bash
cd ../backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

Edit `.env` and change `SECRET_KEY` to a random string for security.

### 4. Initialize Git Hooks

```bash
cd ..
npm run prepare
```

## Running the Application

### Option 1: All-in-One (Recommended)

From the root directory:

```bash
npm run electron:dev
```

This starts everything:
- Backend API (http://localhost:8000)
- Frontend dev server (http://localhost:3000)
- Electron desktop window

### Option 2: Separate Terminals

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
electron .
```

## Verify Installation

### 1. Check Backend

Open http://localhost:8000/docs in your browser. You should see the API documentation.

### 2. Check Frontend

Open http://localhost:3000 in your browser. You should see "Solar Calculator Pro" with a message.

### 3. Check Electron

The Electron window should open automatically showing the frontend.

## Running Tests

```bash
# All tests
npm test

# Frontend only
cd frontend && npm test

# Backend only
cd backend && pytest
```

## Code Quality Checks

```bash
# Lint all code
npm run lint

# Format all code
npm run format

# Type check frontend
cd frontend && npm run type-check
```

## Common Issues

### Port Already in Use

If port 8000 or 3000 is in use:

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

### Backend Won't Start

1. Ensure Python 3.10+ is installed
2. Verify virtual environment is activated (you should see `(venv)` in terminal)
3. Try reinstalling: `pip install -r requirements.txt --force-reinstall`

### Frontend Won't Start

1. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
2. Clear Vite cache: `rm -rf node_modules/.vite`
3. Check Node version is 18+

### Electron Won't Launch

1. Ensure backend is running: `curl http://localhost:8000/health`
2. Ensure frontend is running: Open http://localhost:3000 in browser
3. Check terminal for error messages

## Next Steps

1. ✅ Installation complete
2. 📖 Read the [README.md](README.md) for detailed information
3. 🏗️ Review [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for development workflow
4. 📋 Check the [task list](.kiro/specs/streamlit-to-electron-migration/tasks.md)
5. 🎨 Start building features!

## Development Workflow

1. **Make changes** to frontend or backend code
2. **See changes instantly** with hot reload
3. **Run tests** before committing: `npm test`
4. **Commit** - Git hooks will automatically lint and format
5. **Push** your changes

## Building for Production

```bash
# Build for current platform
npm run electron:build

# Build for specific platform
npm run electron:build:win   # Windows
npm run electron:build:mac   # macOS
npm run electron:build:linux # Linux
```

Builds will be in the `release/` directory.

## Getting Help

- 📖 [Full Documentation](docs/)
- 🐛 [Report Issues](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)

## Success! 🎉

You're now ready to develop Solar Calculator Pro. Happy coding!
