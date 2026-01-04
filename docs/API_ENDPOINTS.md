# TAMA38 API Endpoints Reference

## Base URL
`http://localhost:8000/api/v1`

## Authentication

### POST /auth/login
Login and get access token.

**Request:**
```json
{
  "email": "admin@tama38.local",
  "password": "Admin123!@#"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "user_id": "uuid",
    "email": "admin@tama38.local",
    "full_name": "System Administrator",
    "role": "SUPER_ADMIN"
  }
}
```

### POST /auth/refresh
Refresh access token using refresh token.

### GET /auth/me
Get current user information.

### POST /auth/logout
Logout (token invalidation handled client-side in Phase 1).

## Projects

### GET /projects
List all projects (with pagination and role-based filtering).

**Query Parameters:**
- `skip` (int): Pagination offset
- `limit` (int): Items per page (max 100)

### POST /projects
Create a new project (requires PROJECT_MANAGER or SUPER_ADMIN role).

### GET /projects/{project_id}
Get project details.

### PUT /projects/{project_id}
Update project (requires PROJECT_MANAGER or SUPER_ADMIN role).

### DELETE /projects/{project_id}
Soft delete project (requires SUPER_ADMIN role).

## Buildings

### GET /buildings
List buildings (optionally filtered by project_id).

**Query Parameters:**
- `project_id` (UUID): Filter by project
- `skip`, `limit`: Pagination

### POST /buildings
Create a new building.

### GET /buildings/{building_id}
Get building details.

## Units

### GET /units
List units (optionally filtered by building_id).

**Query Parameters:**
- `building_id` (UUID): Filter by building
- `skip`, `limit`: Pagination

### POST /units
Create a new unit.

### GET /units/{unit_id}
Get unit details.

## Owners

### GET /owners
List owners (optionally filtered by unit_id).

**Query Parameters:**
- `unit_id` (UUID): Filter by unit
- `skip`, `limit`: Pagination

### POST /owners
Create a new owner (supports multi-unit ownership via `link_to_existing`).

**Request:**
```json
{
  "unit_id": "uuid",
  "full_name": "Yael Kohen",
  "phone": "+972-50-123-4567",
  "email": "yael@example.com",
  "ownership_share_percent": 100.0,
  "link_to_existing": false,
  "existing_owner_id": "uuid"  // If linking to existing owner
}
```

### GET /owners/{owner_id}
Get owner details.

### GET /owners/{owner_id}/units
Get all units owned by this owner (multi-unit ownership support).

### GET /owners/search?query={name_or_id}
Search for existing owners by name, phone, or email.

## Wizard

### POST /projects/wizard/start
Initialize wizard session. Returns `draft_id`.

### POST /projects/wizard/step/1
Save Step 1: Project Information.

**Request:**
```json
{
  "draft_id": "uuid",
  "data": {
    "project_name": "Test Project",
    "project_code": "TEST001",
    "project_type": "TAMA38_1",
    "required_majority_percent": 75.0,
    ...
  }
}
```

### POST /projects/wizard/step/2
Save Step 2: Buildings Setup.

### POST /projects/wizard/step/3
Save Step 3: Units Setup.

### POST /projects/wizard/step/4
Save Step 4: Owners Setup.

### GET /projects/wizard/draft/{draft_id}
Retrieve saved draft.

### POST /projects/wizard/complete
Finalize wizard and create project with all entities.

## Interactions

### POST /interactions
Log an interaction (mandatory call summary).

**Request:**
```json
{
  "owner_id": "uuid",
  "interaction_type": "PHONE_CALL",
  "interaction_date": "2025-12-30",
  "duration_minutes": 15,
  "outcome": "POSITIVE",
  "call_summary": "Owner agreed to meet next week",  // MANDATORY
  "sentiment": "POSITIVE"
}
```

### GET /interactions
List interactions (filtered by owner_id or agent_id).

### GET /interactions/recent?hours=24
Get recent interactions (last N hours).

## Documents

### POST /documents/upload
Upload a document (multipart/form-data).

**Form Data:**
- `file`: File to upload
- `owner_id`: (optional) Owner ID
- `building_id`: (optional) Building ID
- `project_id`: (optional) Project ID
- `document_type`: CONTRACT, ID_CARD, SIGNATURE, etc.
- `description`: (optional) Description

### GET /documents/{document_id}/download
Get document download URL.

### GET /documents
List documents (filtered by owner_id, building_id, or project_id).

## Approval Workflow

### POST /approvals/signatures/initiate
Initiate signing process (creates signature with WAIT_FOR_SIGN status).

**Request:**
```json
{
  "owner_id": "uuid",
  "document_id": "uuid"
}
```

**Response includes `signing_token` for signing.**

### GET /approvals/signatures/waiting
Get signatures waiting for owner to sign.

### POST /approvals/signatures/{signature_id}/sign
Owner signs document (changes status to SIGNED_PENDING_APPROVAL).

**Request:**
```json
{
  "signing_token": "uuid",
  "signature_data": "base64_encoded_signature"
}
```

### GET /approvals/queue
Get approval queue (requires PROJECT_MANAGER or SUPER_ADMIN role).

### POST /approvals/{signature_id}/approve
Manager approves signature (changes status to FINALIZED).

**Request:**
```json
{
  "reason": "Document verified, ID matches, signature valid"  // Minimum 20 characters
}
```

### POST /approvals/{signature_id}/reject
Manager rejects signature (returns to WAIT_FOR_SIGN).

## Majority Engine

### GET /buildings/{building_id}/majority
Get current majority calculation for a building.

**Response:**
```json
{
  "signature_percentage": 75.0,
  "signature_percentage_by_area": 72.5,
  "traffic_light_status": "GREEN",
  "total_owners": 20,
  "owners_signed": 15,
  "calculation_time_ms": 250
}
```

### POST /buildings/{building_id}/recalculate
Force recalculation of majority for a building.

## Tasks

### GET /tasks
List tasks (filtered by assigned_to, status).

### GET /tasks/my-tasks
Get current user's tasks.

### GET /tasks/overdue
Get overdue tasks.

### POST /tasks
Create a new task.

### PUT /tasks/{task_id}/complete
Mark task as completed.

## Dashboard

### GET /dashboard/data
Get dashboard data (KPIs, traffic lights, recent interactions, top buildings).

**Response:**
```json
{
  "kpis": {
    "active_projects": 12,
    "total_buildings": 248,
    "overall_signature_percent": 67.0,
    "total_owners": 1842
  },
  "traffic_lights": {
    "green": 82,
    "yellow": 104,
    "red": 62
  },
  "recent_interactions": [...],
  "top_buildings": [...]
}
```

## Mock WhatsApp (Phase 1)

### POST /whatsapp/mock/send
Send a mock WhatsApp message.

**Request:**
```json
{
  "owner_id": "uuid",
  "message_body": "Hello, this is a test message",
  "message_type": "TEXT"
}
```

### POST /whatsapp/mock/webhook
Simulate incoming WhatsApp webhook (for testing).

### GET /whatsapp/conversations?owner_id={id}
Get WhatsApp conversation history (mock data in Phase 1).

## Files

### GET /files/{document_id}
Serve document file (local file serving in Phase 1).

## Error Responses

All endpoints return standard HTTP status codes:
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message"
}
```

## Request Headers

All authenticated requests require:
```
Authorization: Bearer {access_token}
```

Request ID is automatically added by middleware and returned in response headers:
```
X-Request-ID: {uuid}
```

