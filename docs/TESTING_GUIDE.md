# TAMA38 Phase 1 Testing Guide

## Overview

This guide provides instructions for testing all components of the TAMA38 Phase 1 system.

## Prerequisites

1. **Start the system:**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

3. **Create admin user:**
   ```bash
   docker-compose exec backend python scripts/create_admin.py
   ```

4. **Create test users (optional):**
   ```bash
   docker-compose exec backend python scripts/create_test_users.py
   ```

## Test Scripts

### 1. Signing Workflow E2E Test

Tests the complete signing workflow from initiation to approval.

**Run:**
```bash
python scripts/test_signing_workflow.py
```

**What it tests:**
- Login and authentication
- Project/Building/Unit/Owner creation
- Document upload
- Signature initiation
- Token validation (public endpoint)
- Document signing (public endpoint)
- Approval queue retrieval
- Signature approval
- Error handling (invalid tokens, already signed documents)

**Expected output:**
- All 14 steps should pass
- Summary with IDs and signing token
- Signing URL for UI testing

### 2. Create Test Signing Link

Creates a fresh signing link for UI testing.

**Run:**
```bash
python scripts/create_test_signing_link.py
```

**What it does:**
- Logs in as admin
- Finds first available owner and document
- Creates a new signature with WAIT_FOR_SIGN status
- Outputs signing URL

**Use case:**
- Quick way to get a signing link for frontend testing
- Use the URL in browser to test the signing interface

## Manual Testing

### Frontend Testing

#### 1. Login
- URL: `http://localhost:3000/login`
- Credentials: `admin@tama38.local` / `Admin123!@#`
- Expected: Redirect to dashboard

#### 2. Dashboard
- URL: `http://localhost:3000/dashboard`
- Expected: KPIs displayed, statistics charts visible

#### 3. Projects
- URL: `http://localhost:3000/projects`
- Expected: List of projects, ability to create new project

#### 4. Project Wizard
- URL: `http://localhost:3000/projects/new`
- Expected: 5-step wizard (Project Info → Buildings → Units → Owners → Review)

#### 5. Buildings
- URL: `http://localhost:3000/buildings`
- Expected: List of buildings, filter by project, view details

#### 6. Owners
- URL: `http://localhost:3000/owners`
- Expected: List of owners, search functionality, multi-unit support

#### 7. Interactions
- URL: `http://localhost:3000/interactions`
- Expected: Log interactions, view history, filter by owner/agent

#### 8. Tasks
- URL: `http://localhost:3000/tasks`
- Expected: View tasks, mark complete, filter (my tasks, overdue, all)

#### 9. Approvals
- URL: `http://localhost:3000/approvals`
- Expected: View pending approvals, approve/reject signatures

#### 10. Signing Interface (Public)
- URL: `http://localhost:3000/sign/{token}`
- Expected: 
  - Token validation
  - Document review
  - Signature canvas
  - Success page

**To get a signing token:**
```bash
python scripts/create_test_signing_link.py
```

### Backend API Testing

#### Interactive API Documentation
- URL: `http://localhost:8000/docs`
- Features:
  - Browse all endpoints
  - Test endpoints interactively
  - View request/response schemas
  - Authenticate with Bearer token

#### Health Check
```bash
curl http://localhost:8000/health
```

Expected: `{"status": "healthy"}`

## Test Scenarios

### Scenario 1: Complete Project Creation Workflow

1. Login as admin
2. Navigate to Projects → New Project
3. Complete wizard:
   - Step 1: Project Info
   - Step 2: Add Buildings
   - Step 3: Add Units to Buildings
   - Step 4: Add Owners to Units
   - Step 5: Review and Complete
4. Verify project appears in projects list
5. Click project to view details

### Scenario 2: Signing Workflow

1. Create a project with building, unit, and owner (via wizard or API)
2. Upload a document for the owner
3. Initiate signature (via Approvals page or API)
4. Copy signing token
5. Open signing URL in browser: `http://localhost:3000/sign/{token}`
6. Review document
7. Sign on canvas
8. Submit signature
9. Verify signature appears in approval queue
10. Approve signature as manager
11. Verify signature status changes to FINALIZED

### Scenario 3: Interaction Logging

1. Navigate to Interactions page
2. Click "Log Interaction"
3. Select owner
4. Fill in interaction details:
   - Type: Phone Call
   - Date: Today
   - Call Summary: (mandatory)
   - Sentiment: Positive
5. Submit
6. Verify interaction appears in history

### Scenario 4: Task Management

1. Navigate to Tasks page
2. View "My Tasks" filter
3. Create a new task (if API available)
4. Mark task as complete
5. Verify task status updates

## Automated Testing

### Running All Tests

```bash
# Signing workflow test
python scripts/test_signing_workflow.py

# Infrastructure test (if available)
bash scripts/test_infrastructure.sh
```

## Known Issues & Limitations

1. **Document Upload UI**: Backend API ready, frontend UI pending
2. **Unit Detail Page**: Units can be viewed through buildings
3. **Mobile Responsiveness**: Some pages may need mobile optimization
4. **ID Upload**: Simplified in Phase 1 (not implemented in signing interface)

## Performance Testing

### Load Testing (Future)

```bash
# Example with Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health
```

### Database Query Performance

Check logs for query performance warnings:
- Majority calculation should complete in <3 seconds
- Dashboard queries should be optimized

## Debugging

### Backend Logs
```bash
docker-compose logs backend --tail 100
```

### Frontend Console
- Open browser DevTools (F12)
- Check Console for errors
- Check Network tab for API calls

### Database Access
```bash
docker-compose exec database psql -U postgres -d tama38_dev
```

## Test Data

### Default Users

- **Super Admin**: `admin@tama38.local` / `Admin123!@#`
- **Project Manager**: `pm@tama38.local` / `Pm123!@#` (if created)
- **Agent**: `agent@tama38.local` / `Agent123!@#` (if created)

### Sample Data

Use the test scripts to create sample data:
- Projects, Buildings, Units, Owners
- Documents
- Signatures

## Reporting Issues

When reporting issues, include:
1. Test scenario that failed
2. Expected vs actual behavior
3. Backend logs (if applicable)
4. Frontend console errors (if applicable)
5. Steps to reproduce

