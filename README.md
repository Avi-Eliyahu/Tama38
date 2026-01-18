# TAMA38 Urban Renewal Management Platform

## Phase 1 Development

This is the Phase 1 implementation of the TAMA38 Urban Renewal Management Platform - a comprehensive SaaS solution for managing Israeli Urban Renewal projects (TAMA 38 / Pinui Binui).

## Quick Start

### Prerequisites

- Docker Desktop for Windows
- Git
- Node.js 18+ (for local frontend development, optional)
- Python 3.11+ (for local backend development, optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tama38
   ```

2. **Copy environment file (optional)**
   ```bash
   cp .env.example .env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Create initial admin user**
   ```bash
   docker-compose exec backend python scripts/create_admin.py
   ```

6. **Access the applications**
   - Frontend: http://localhost:3000
   - Backend API Docs: http://localhost:8000/docs
   - Backend Health: http://localhost:8000/health
   - Database: localhost:5432 (user: postgres, password: postgres)

## Development

### Backend Development

The backend is built with:
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- Alembic (Database migrations)
- PostgreSQL (Database)

**Running backend locally:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

The frontend is built with:
- React 18 + TypeScript
- Vite (Build tool)
- Tailwind CSS (Styling)
- Redux Toolkit (State management)

**Running frontend locally:**
```bash
cd frontend
npm install
npm run dev
```

## Testing

### Run all tests
```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test

# E2E tests
./scripts/e2e_test.sh
```

### Infrastructure tests
```bash
./scripts/test_infrastructure.sh
```

## Project Structure

```
tama38/
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── api/         # API route handlers
│   │   ├── core/        # Core configuration
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic services
│   │   └── utils/       # Utility functions
│   ├── tests/           # Test files
│   └── alembic/         # Database migrations
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── store/       # Redux store
│   │   └── utils/      # Utility functions
│   └── public/         # Static assets
├── scripts/             # Utility scripts
├── docs/               # Documentation
└── docker-compose.yml  # Docker Compose configuration
```

## Phase 1 Features

- ✅ Local development environment (Docker Compose)
- ✅ Mock services for WhatsApp and SMS
- ✅ Local file storage
- ✅ Local JWT authentication
- ✅ Project management (CRUD)
- ✅ Wizard-like project creation UI
- ✅ Multi-unit ownership support
- ✅ CRM & Interaction logging
- ✅ Document management
- ✅ Approval workflow
- ✅ Majority calculation engine
- ✅ Dashboard & Analytics
- ✅ Mobile Agent Application
- ✅ Task Management

## Phase 2 (Future)

- AWS cloud deployment (ECS/EKS, RDS, S3)
- Twilio integration for WhatsApp and SMS
- AWS Cognito authentication
- Production-grade infrastructure and monitoring

## Documentation

- [Design Document](TAMA38_Design_document.md)
- [Development Plan](docs/development_plan.md)
- [API Documentation](http://localhost:8000/docs) (when backend is running)

## License

[To be determined]

