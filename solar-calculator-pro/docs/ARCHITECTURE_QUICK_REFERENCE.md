# Architecture Documentation - Quick Reference

## 📚 Documentation Index

| Document | Purpose | Audience |
|----------|---------|----------|
| [Architecture Overview](./ARCHITECTURE_OVERVIEW.md) | System overview and entry point | All |
| [Data Flow Architecture](./DATA_FLOW_ARCHITECTURE.md) | How data moves through the system | Developers |
| [Deployment Architecture](./DEPLOYMENT_ARCHITECTURE.md) | Build and deployment guide | DevOps |
| [Security Architecture](./SECURITY_ARCHITECTURE.md) | Security implementation details | Security, Developers |
| [Integration Points](./INTEGRATION_POINTS.md) | Internal and external integrations | Developers |
| [System Diagrams](./SYSTEM_DIAGRAMS.md) | Visual architecture diagrams | All |

## 🏗️ System Architecture at a Glance

```
┌─────────────────────────────────────┐
│     Electron Desktop Application     │
│  ┌─────────────┐  ┌──────────────┐ │
│  │   React     │  │   FastAPI    │ │
│  │  Frontend   │◄─┤   Backend    │ │
│  │ (Port 3000) │  │  (Port 8000) │ │
│  └─────────────┘  └──────────────┘ │
│                          │           │
│                          ▼           │
│                    ┌──────────┐     │
│                    │  SQLite  │     │
│                    │ Database │     │
│                    └──────────┘     │
└─────────────────────────────────────┘
```

## 🔑 Key Technologies

### Frontend
- React 18+ with TypeScript
- PrimeReact UI components
- Zustand state management
- Axios for HTTP
- Socket.IO for WebSocket

### Backend
- Python 3.10+
- FastAPI REST framework
- SQLAlchemy ORM
- Pydantic validation
- JWT authentication

### Desktop
- Electron 27+
- electron-builder
- electron-updater
- electron-store

## 📊 Data Flow Patterns

### 1. Standard API Request
```
User → React → Axios → FastAPI → Service → Database → Response
```

### 2. Real-Time Updates
```
User → React → Socket.IO → FastAPI → Service → Progress Events
```

### 3. File Operations
```
User → React → Electron IPC → Native Dialog → File System
```

## 🔒 Security Layers

1. **Authentication**: JWT tokens with bcrypt password hashing
2. **Authorization**: Role-based access control (RBAC)
3. **Network**: HTTPS/TLS for all communication
4. **Data**: AES-256 encryption at rest
5. **Input**: Validation and sanitization
6. **Electron**: Context isolation and secure IPC

## 🚀 Deployment Targets

| Platform | Installer | Format |
|----------|-----------|--------|
| Windows | NSIS | .exe |
| macOS | DMG | .dmg |
| Linux | AppImage/DEB | .AppImage, .deb |

## 🔌 Integration Points

### Internal
- Frontend ↔ Backend: REST API + WebSocket
- Electron ↔ Frontend: IPC bridge
- Electron ↔ Backend: Process management
- Backend ↔ Database: SQLAlchemy ORM

### External
- Weather API: Solar radiation data
- Maps API: Geocoding and location
- Email Service: PDF delivery
- Payment Gateway: Stripe integration
- Cloud Storage: Google Cloud Storage

## 📁 Project Structure

```
solar-calculator-pro/
├── electron/          # Electron main process
├── frontend/          # React application
├── backend/           # FastAPI backend
├── docs/              # Documentation
└── release/           # Built applications
```

## 🛠️ Development Commands

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev

# Electron
npm run electron:dev

# Build All
npm run build
```

## 📖 Common Use Cases

### Adding a New API Endpoint
1. Define Pydantic schema in `backend/models/schemas.py`
2. Create service method in `backend/services/`
3. Add endpoint in `backend/api/v1/`
4. Create frontend service call in `frontend/src/services/`
5. Use in React component

### Adding a New Page
1. Create page component in `frontend/src/pages/`
2. Add route in `frontend/src/routes/index.tsx`
3. Add navigation link in sidebar
4. Create necessary API calls

### Implementing Security
1. Add authentication check: `Depends(get_current_user)`
2. Add permission check: `@require_permission("resource:action")`
3. Validate input with Pydantic models
4. Sanitize output data

## 🔍 Troubleshooting

### Backend Not Starting
- Check Python version (3.10+)
- Verify dependencies: `pip install -r requirements.txt`
- Check port 8000 availability

### Frontend Build Errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version (18+)
- Verify TypeScript compilation

### Electron Issues
- Check backend process is running
- Verify IPC channels are registered
- Check console for errors

## 📞 Support Resources

- **Architecture Questions**: See detailed docs in `/docs`
- **API Reference**: `backend/docs/API_DOCUMENTATION.md`
- **Component Docs**: `frontend/COMPONENT_DOCUMENTATION.md`
- **Security**: `docs/SECURITY_ARCHITECTURE.md`

## 🎯 Quick Links

- [Full Architecture Overview](./ARCHITECTURE_OVERVIEW.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Developer Guide](./DEVELOPER_GUIDE.md)
- [Deployment Guide](./DEPLOYMENT_ARCHITECTURE.md)
- [Security Guide](./SECURITY_ARCHITECTURE.md)

---

**Last Updated**: 2025-01-20
**Version**: 1.0.0
