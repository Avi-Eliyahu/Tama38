# TAMA38 Urban Renewal Management Platform
## System Design Document

**Version:** 1.1  
**Date:** December 2025  
**Status:** Draft for Implementation  
**Target Environment:** Phase 1 - Local Development, Phase 2 - Amazon AWS (ECS/EKS)  
**Development Environment:** Local Windows with Docker

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2025 | System Architect | Initial design document |
| 1.1 | Dec 2025 | System Architect | Phase 1 updates: Added wizard UI for project creation, clarified multi-unit ownership, added WAIT_FOR_SIGN state, Phase 1 local development without AWS/Twilio, added mock services for WhatsApp/SMS simulation, updated migration path |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Requirements Summary](#2-system-requirements-summary)
3. [System Architecture](#3-system-architecture)
4. [Module Design](#4-module-design)
5. [Database Design](#5-database-design)
6. [API Design](#6-api-design)
7. [UI/UX Design](#7-uiux-design)
8. [Integration Design](#8-integration-design)
9. [Security Design](#9-security-design)
10. [Performance & Scalability](#10-performance--scalability)
11. [Deployment & DevOps](#11-deployment--devops)
12. [Testing Strategy](#12-testing-strategy)
13. [Monitoring & Maintenance](#13-monitoring--maintenance)
14. [Future Enhancements](#14-future-enhancements)
15. [Appendices](#15-appendices)

---

## 1. Executive Summary

### 1.1 System Overview

The TAMA38 Urban Renewal Management Platform is a comprehensive SaaS solution designed to manage the end-to-end lifecycle of tenants (property owners) in Israeli Urban Renewal projects (TAMA 38 / Pinui Binui). The system replaces traditional manual processes with a digital platform that streamlines signature collection, document management, and project tracking.

**Key Value Propositions:**
- Centralized management of Project → Building → Unit → Owner hierarchy
- Real-time signature percentage calculation with traffic light status indicators
- WhatsApp-based tenant communication reducing friction for elderly users (Phase 2)
- Mobile-optimized agent application for field work
- Manager approval workflow ensuring legal compliance
- Comprehensive audit trail for regulatory compliance

**Development Phases:**

**Phase 1 (Initial Development):**
- Local development environment (Docker Compose)
- Mock services for WhatsApp and SMS (no external dependencies)
- Local file storage (no AWS S3)
- Local JWT authentication (no AWS Cognito)
- Full core functionality: Project management, CRM, approvals, reporting
- Wizard-like project creation UI
- Support for owners owning multiple units across buildings

**Phase 2 (Production Deployment):**
- AWS cloud deployment (ECS/EKS, RDS, S3)
- Twilio integration for WhatsApp and SMS
- AWS Cognito authentication
- Production-grade infrastructure and monitoring

### 1.2 Key Stakeholders

| Stakeholder | Role | Primary Goals |
|-------------|------|---------------|
| **Property Developers** | System sponsors | Track project progress, ensure legal thresholds are met |
| **Project Managers** | Operations & approval | Monitor building status, approve signatures, manage agents |
| **Field Agents** | Direct tenant interaction | Collect signatures, log interactions, manage leads |
| **Property Owners (Tenants)** | End users | Receive updates, sign documents, access information |
| **Government Authorities** | Regulatory oversight | Ensure compliance with TAMA 38 regulations |

### 1.3 Use Cases

**Primary Use Cases:**
1. **Signature Collection Workflow** - Agent initiates, tenant signs via WhatsApp, manager approves
2. **Real-time Progress Monitoring** - Dashboard shows building-level signature percentages with traffic lights
3. **Document Management** - Store, version, and retrieve contracts and supporting documents
4. **Interaction Logging** - Track all agent-tenant communications for compliance
5. **Manual Override Processing** - Handle paper documents for non-digital users
6. **Ownership Transfer Management** - Update ownership records and recalculate percentages
7. **Multi-channel Communication** - Email, SMS, WhatsApp messaging with templates
8. **Performance Analytics** - Track agent performance and building progress

### 1.4 High-Level Architecture Diagram

```mermaid
graph TB
    subgraph Users
        PM[Project Manager<br/>Desktop Web]
        Agent[Field Agent<br/>Mobile Web]
        Owner[Property Owner<br/>WhatsApp]
    end
    
    subgraph AWS_Cloud[AWS Cloud Infrastructure]
        subgraph ECS_Cluster[ECS/EKS Cluster]
            Frontend[React Frontend<br/>Nginx Container]
            Backend[FastAPI Backend<br/>Python Container]
            Worker[Background Worker<br/>Celery Optional]
        end
        
        subgraph Data_Layer[Data Layer]
            RDS[(PostgreSQL<br/>RDS)]
            S3[S3 Bucket<br/>Documents]
        end
        
        subgraph Auth_Services[Authentication]
            Cognito[AWS Cognito<br/>User Pool]
        end
        
        subgraph Communication[Communication Services]
            SES[AWS SES<br/>Email]
            Twilio[Twilio API<br/>SMS + WhatsApp]
        end
    end
    
    PM -->|HTTPS| Frontend
    Agent -->|HTTPS| Frontend
    Owner -->|WhatsApp| Twilio
    
    Frontend -->|API Calls| Backend
    Backend -->|Auth| Cognito
    Backend -->|Query/Update| RDS
    Backend -->|Upload/Download| S3
    Backend -->|Send Email| SES
    Backend -->|Send SMS/WhatsApp| Twilio
    
    Twilio -->|Webhooks| Backend
```

---

## 2. System Requirements Summary

### 2.1 Consolidated Functional Requirements

#### 2.1.1 Core Objectives (from SRD)

1. **Single Source of Truth**
   - Centralized database managing Project → Building → Unit → Owner hierarchy
   - Historical tracking of ownership changes
   - Comprehensive audit trail

2. **Weighted Majority Engine**
   - Real-time calculation of "Required Majority" (Rov Nidrash)
   - Configurable thresholds per project (typically 66.67% or 75%)
   - Multiple calculation methods: Headcount, Area, Weighted, Custom
   - Performance requirement: <3 seconds propagation

3. **Hybrid Workflow**
   - Digital signatures via WhatsApp
   - Manual override capability for paper documents
   - Camera integration for document scanning

4. **Manager Approval Gate**
   - No signature is final without manager validation
   - Document verification workflow
   - Manual override audit requirements

#### 2.1.2 Functional Requirements by Module

**A. Authentication & Authorization**
- FR-AUTH-001: System shall support AWS Cognito authentication (Phase 2) or local JWT-based authentication (Phase 1)
- FR-AUTH-002: System shall enforce role-based access control (RBAC)
- FR-AUTH-003: System shall support four user roles: Super Admin, Project Manager, Agent, Tenant
- FR-AUTH-004: System shall enforce data isolation per project for agents
- FR-AUTH-005: System shall support session management with configurable timeout
- FR-AUTH-006: Phase 1 authentication must be easily migratable to Cognito in Phase 2

**B. Project Management**
- FR-PROJ-001: System shall support multiple concurrent projects
- FR-PROJ-002: System shall maintain Project → Building → Unit → Owner hierarchy with wizard-like step-by-step creation flow
- FR-PROJ-003: System shall configure legal thresholds per project
- FR-PROJ-004: System shall track project milestones and deadlines
- FR-PROJ-005: System shall support building-level agent assignment
- FR-PROJ-006: System shall provide wizard UI for creating new projects, buildings, and units with owners in a guided step-by-step process

**C. Majority Engine**
- FR-MAJ-001: System shall calculate signature percentages in real-time
- FR-MAJ-002: System shall support multiple calculation types (Headcount, Area, Weighted)
- FR-MAJ-003: System shall display traffic light status (Green ≥75%, Yellow 50-75%, Red <50%)
- FR-MAJ-004: System shall recalculate percentages on signature approval
- FR-MAJ-005: System shall generate alerts when thresholds are crossed

**D. Owner Management**
- FR-OWN-001: System shall store owner personal information (encrypted)
- FR-OWN-002: System shall support multiple owners per unit AND allow owners to own multiple units (potentially across multiple buildings within the same project)
- FR-OWN-003: System shall track ownership share percentages per unit
- FR-OWN-004: System shall maintain historical owner records
- FR-OWN-005: System shall support ownership transfer workflow
- FR-OWN-006: System shall display all units owned by a single owner across buildings in owner detail view

**E. Interaction Management**
- FR-INT-001: System shall log all agent-owner interactions
- FR-INT-002: System shall require call summary after phone interactions
- FR-INT-003: System shall track interaction outcome and sentiment
- FR-INT-004: System shall support follow-up task creation
- FR-INT-005: System shall track days since last contact

**F. Document Management**
- FR-DOC-001: System shall store documents in AWS S3 (Phase 2) or local file system (Phase 1)
- FR-DOC-002: System shall generate presigned URLs for secure document access (Phase 2) or local file URLs (Phase 1)
- FR-DOC-003: System shall support document versioning
- FR-DOC-004: System shall enforce 7-year retention policy
- FR-DOC-005: System shall support PDF generation and digital signing
- FR-DOC-006: Phase 1 local storage must be easily migratable to S3 in Phase 2

**G. Approval Workflow**
- FR-APP-001: System shall require manager approval for all signatures
- FR-APP-002: System shall maintain approval queue for managers
- FR-APP-003: System shall support status transitions: WAIT_FOR_SIGN → SIGNED_PENDING_APPROVAL → FINALIZED (or REJECTED)
- FR-APP-004: System shall support manual override with mandatory explanation
- FR-APP-005: System shall log all approval actions for audit
- FR-APP-006: When owner agrees to sign, system shall generate signing link/document and set status to WAIT_FOR_SIGN

**H. Communication**
- FR-COM-001: System shall support email via AWS SES (Phase 2) or local SMTP server (Phase 1)
- FR-COM-002: System shall support SMS via Twilio (Phase 2) or mock SMS service (Phase 1)
- FR-COM-003: System shall support WhatsApp via Twilio WhatsApp API (Phase 2) or mock WhatsApp service (Phase 1)
- FR-COM-004: System shall support communication templates
- FR-COM-005: System shall track delivery and read status
- FR-COM-006: System shall support multi-language (Hebrew, Arabic, Russian, English)
- FR-COM-007: Phase 1 shall include mock services that simulate WhatsApp and SMS without external dependencies

**I. WhatsApp Chatbot (Phase 2)**
- FR-BOT-001: System shall provide status updates via WhatsApp (push/pull) - Phase 2 only
- FR-BOT-002: System shall deliver document links via WhatsApp - Phase 2 only
- FR-BOT-003: System shall initiate digital signing via WhatsApp link - Phase 2 only
- FR-BOT-004: System shall provide Q&A support via WhatsApp - Phase 2 only
- FR-BOT-005: System shall escalate complex queries to human agents - Phase 2 only
- FR-BOT-006: Phase 1 shall include UI simulation of WhatsApp chat interface for testing and demonstration

**J. Mobile Agent Application**
- FR-MOB-001: System shall provide mobile-responsive agent interface
- FR-MOB-002: System shall support lead management and prioritization
- FR-MOB-003: System shall provide click-to-call functionality
- FR-MOB-004: System shall support camera integration for document scanning
- FR-MOB-005: System shall optimize UI for thumb-friendly field work

**K. Task Management**
- FR-TSK-001: System shall support task creation and assignment
- FR-TSK-002: System shall track task priority and due dates
- FR-TSK-003: System shall support task dependencies
- FR-TSK-004: System shall provide task list views for agents
- FR-TSK-005: System shall generate automatic follow-up tasks

**L. Reporting & Analytics**
- FR-REP-001: System shall provide dashboard with KPI cards
- FR-REP-002: System shall display building progress with traffic lights
- FR-REP-003: System shall track agent performance metrics
- FR-REP-004: System shall support custom report generation
- FR-REP-005: System shall support data export (PDF, Excel)

**M. Alerts & Notifications**
- FR-ALT-001: System shall generate alerts for threshold violations
- FR-ALT-002: System shall alert on agent inactivity (3+ days)
- FR-ALT-003: System shall support multi-channel alert delivery
- FR-ALT-004: System shall provide alert configuration interface
- FR-ALT-005: System shall track alert resolution

### 2.2 Non-Functional Requirements

#### 2.2.1 Performance Requirements

| Requirement | Target | Critical Path |
|-------------|--------|---------------|
| Dashboard Load Time | <3 seconds | Initial page load |
| Majority Calculation Propagation | <3 seconds | After signature approval |
| API Response Time (95th percentile) | <500ms | All API calls |
| Database Query Performance | <200ms | Complex queries |
| Document Upload | <5 seconds | Up to 10MB files |
| Page Refresh Rate | 30 seconds | Dashboard polling |

#### 2.2.2 Security Requirements

- **NFR-SEC-001**: All PII must be encrypted at rest using AWS KMS
- **NFR-SEC-002**: All data in transit must use TLS 1.2+
- **NFR-SEC-003**: Role-based access control must be enforced at API level
- **NFR-SEC-004**: Data isolation must prevent cross-project access
- **NFR-SEC-005**: Audit trail must be immutable and comprehensive
- **NFR-SEC-006**: Password policy must enforce strong passwords (8+ chars, mixed case, numbers, symbols)
- **NFR-SEC-007**: Sessions must expire after 8 hours of inactivity
- **NFR-SEC-008**: Failed login attempts must be rate-limited (5 attempts per 15 minutes)

#### 2.2.3 Availability & Reliability

- **NFR-AVL-001**: System uptime SLA: 99.5% (excluding planned maintenance)
- **NFR-AVL-002**: Planned maintenance window: Sundays 2:00-6:00 AM local time
- **NFR-AVL-003**: Database backup: Daily automated backups with 7-year retention
- **NFR-AVL-004**: RTO (Recovery Time Objective): 4 hours
- **NFR-AVL-005**: RPO (Recovery Point Objective): 24 hours

#### 2.2.4 Scalability Requirements

- **NFR-SCA-001**: Support up to 100 concurrent projects
- **NFR-SCA-002**: Support up to 10,000 buildings across all projects
- **NFR-SCA-003**: Support up to 100,000 property owners
- **NFR-SCA-004**: Support up to 50 concurrent agent users
- **NFR-SCA-005**: Support up to 10 concurrent project managers
- **NFR-SCA-006**: Horizontal scaling capability for backend services

#### 2.2.5 Usability Requirements

- **NFR-USA-001**: Desktop interface must support Chrome, Firefox, Safari, Edge (latest 2 versions)
- **NFR-USA-002**: Mobile interface must support iOS 14+ and Android 10+
- **NFR-USA-003**: Mobile buttons must be minimum 44x44 pixels (thumb-friendly)
- **NFR-USA-004**: Support RTL (right-to-left) for Hebrew and Arabic
- **NFR-USA-005**: Accessibility: WCAG 2.1 Level AA compliance for elderly users
- **NFR-USA-006**: Font sizes must be configurable (default minimum 14px)

#### 2.2.6 Compliance & Audit

- **NFR-COM-001**: Document retention: 7 years minimum (legal requirement)
- **NFR-COM-002**: Audit trail: Log all data modifications with user, timestamp, reason
- **NFR-COM-003**: Manual overrides: Require mandatory text explanation
- **NFR-COM-004**: GDPR compliance: Support data export and deletion requests
- **NFR-COM-005**: Data residency: Store data in EU/Israel AWS regions

### 2.3 Resolved Contradictions & Architectural Decisions

| Issue | SRD Specification | Resolution | Rationale |
|-------|-------------------|------------|-----------|
| **Compute Architecture** | AWS Lambda (serverless) | Containers (ECS/EKS) | Better for local development, easier migration path, consistent with user requirements |
| **Frontend Technology** | Not specified | React with TypeScript | Modern component-based framework, strong typing, large ecosystem |
| **Backend Framework** | Not specified | FastAPI (Python 3.11+) | Modern async framework, auto-documentation, high performance |
| **Real-time Updates** | Not specified | Polling (30-second intervals) | Simpler implementation, adequate for dashboard requirements |
| **WhatsApp Integration** | WhatsApp Business API | Twilio WhatsApp API | Easier setup, no Meta approval delays, includes SMS capability |
| **Document Delivery** | Presigned URLs | S3 Presigned URLs | Secure, time-limited access, simple implementation |
| **Building Matrix View** | Required in SRD | Phase 2 (Future) | Complex UI, not in mockups, defer to focus on core functionality |
| **Biometric Verification** | AWS Rekognition | Phase 2 (Future) | Complex integration, defer to focus on core signing workflow |
| **AWS Deployment** | AWS required | Phase 1: Local, Phase 2: AWS | Phase 1 focuses on core functionality, Phase 2 adds cloud deployment |
| **WhatsApp Integration** | Twilio WhatsApp API | Phase 1: Mock service, Phase 2: Twilio | Phase 1 uses mock service for development/testing, Phase 2 integrates real Twilio |
| **SMS Integration** | Twilio SMS | Phase 1: Mock service, Phase 2: Twilio | Phase 1 uses mock service, Phase 2 integrates real Twilio |
| **Document Storage** | AWS S3 | Phase 1: Local filesystem, Phase 2: S3 | Phase 1 uses local storage, Phase 2 migrates to S3 with clear migration path |
| **Authentication** | AWS Cognito | Phase 1: Local JWT, Phase 2: Cognito | Phase 1 uses local auth, Phase 2 migrates to Cognito |
| **Project Creation** | Not specified | Wizard-like step-by-step UI | Guided multi-step form for creating projects, buildings, units with owners |
| **Approval Workflow** | Signed → Pending → Finalized | WAIT_FOR_SIGN → SIGNED_PENDING_APPROVAL → FINALIZED | Added initial WAIT_FOR_SIGN state when signing link is sent |

---


## 3. System Architecture

### 3.1 High-Level Architecture

The TAMA38 platform follows a modern microservices-inspired architecture with clear separation between frontend, backend API, and data layers. All components are containerized for consistency across local development and AWS production environments.

**Architecture Principles:**
1. Separation of Concerns - Frontend/Backend/Data layers
2. Scalability - Horizontal scaling via containers  
3. Security by Design - Encryption, RBAC, comprehensive audit
4. API-First - All functionality exposed via REST APIs
5. Cloud-Native - Leverage AWS managed services
6. Local Development Parity - Docker-based local environment

### 3.2 Technology Stack Summary

**Frontend:** React 18 + TypeScript, Tailwind CSS, Redux Toolkit, React Router, Vite

**Backend:** FastAPI (Python 3.11+), SQLAlchemy, Alembic, Pydantic, Uvicorn

**Database:**
- **Phase 1:** PostgreSQL 15+ (local Docker container)
- **Phase 2:** PostgreSQL 15+ on AWS RDS

**Storage:**
- **Phase 1:** Local filesystem (mounted volume in Docker)
- **Phase 2:** AWS S3 for documents

**Authentication:**
- **Phase 1:** Local JWT-based authentication (Python-JOSE)
- **Phase 2:** AWS Cognito

**Communication:**
- **Phase 1:** Mock services (simulated WhatsApp/SMS), Local SMTP server
- **Phase 2:** Twilio (WhatsApp + SMS), AWS SES (Email)

**Deployment:**
- **Phase 1:** Docker Compose (local development)
- **Phase 2:** Docker, AWS ECS/EKS, Application Load Balancer

**Monitoring:**
- **Phase 1:** Local logging (stdout/stderr)
- **Phase 2:** AWS CloudWatch

### 3.3 Deployment Strategy

**Phase 1: Local Development (No AWS/Twilio)**
- Docker Compose with services: frontend, backend, PostgreSQL, Mock Communication Service, Local File Storage
- Hot reload for both frontend and backend
- Access: Frontend (localhost:3000), Backend API (localhost:8000), Database (localhost:5432)
- **Mock Services:**
  - Mock WhatsApp Service: Simulates WhatsApp API, stores messages in database, provides UI for viewing simulated conversations
  - Mock SMS Service: Simulates SMS API, stores messages in database
  - Local File Storage: Documents stored in `./storage/documents` directory
  - Local Authentication: JWT-based auth with users stored in database
- **No External Dependencies:** All services run locally without AWS or Twilio

**Phase 2: AWS Production Deployment**
- Multi-AZ VPC with public/private subnets
- ECS Fargate for container orchestration
- Multi-AZ RDS PostgreSQL with automated backups
- S3 with versioning and lifecycle policies
- Application Load Balancer with HTTPS termination
- Cognito User Pool for authentication
- Twilio integration for WhatsApp and SMS

**Migration Path (Phase 1 → Phase 2):**
1. **Phase 1 Development:** Develop and test fully on local Docker environment with mock services
2. **Prepare for Migration:**
   - Ensure all environment variables are externalized
   - Abstract communication service interface (mock vs real)
   - Abstract storage service interface (local filesystem vs S3)
   - Abstract authentication service interface (local JWT vs Cognito)
3. **Provision AWS Infrastructure:** Terraform/CloudFormation for VPC, RDS, S3, Cognito, ECS
4. **Build and Push Images:** Push Docker images to ECR
5. **Deploy to ECS:** Deploy services with auto-scaling
6. **Migrate Data:**
   - Database: pg_dump from local PostgreSQL, restore to RDS
   - Documents: Upload local filesystem documents to S3
   - Users: Migrate user accounts to Cognito (or keep in database with Cognito integration)
7. **Switch Services:**
   - Replace mock communication service with Twilio integration
   - Replace local file storage with S3
   - Replace local auth with Cognito (or integrate Cognito with existing users)
8. **DNS Switchover:** Update DNS to point to ALB
9. **Testing & Monitoring:** Verify all functionality, configure CloudWatch monitoring

---

## 4. Module Design

This section describes the 13 core modules of the TAMA38 system, their responsibilities, key components, and inter-dependencies.

### 4.1 Authentication & Authorization Module

**Purpose:** Manage user authentication, authorization, and session management using AWS Cognito.

**Key Components:**
- AWS Cognito User Pool integration
- JWT token generation and validation
- Role-based access control (RBAC) enforcement
- Session management middleware
- Password reset and MFA workflows

**User Roles & Permissions:**

| Role | Permissions |
|------|-------------|
| **Super Admin** | Full system access, configure thresholds, manage users, view all projects |
| **Project Manager** | Approve signatures, manage agents, view assigned projects, generate reports |
| **Agent** | Log interactions, initiate signatures, manage assigned owners, view assigned buildings |
| **Tenant (Owner)** | View own status, sign documents, request information via WhatsApp |

**API Endpoints:**
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Invalidate session
- `POST /api/auth/forgot-password` - Initiate password reset
- `GET /api/auth/me` - Get current user profile

### 4.2 Project Management Module

**Purpose:** Manage the Project → Building → Unit → Owner hierarchy with guided wizard-like creation flow.

**Key Features:**
- **Wizard-like Project Creation:** Step-by-step guided flow for creating new projects, buildings, and units with owners
- Project CRUD operations with threshold configuration
- Building management with agent assignment
- Unit management with ownership tracking
- Owner management with historical records
- Ownership transfer workflow
- Support for owners owning multiple units across multiple buildings

**Project Creation Wizard Flow:**

The wizard guides Project Managers through creating a complete project setup in sequential steps:

**Step 1: Project Information**
- Project name and code
- Project type (TAMA38_1, TAMA38_2, PINUI_BINUI)
- Location (city, address, coordinates)
- Description
- Legal thresholds (Required Majority %, Critical Threshold %)
- Calculation type (Headcount, Area, Weighted, Custom)
- Project manager assignment
- Launch date and estimated completion date

**Step 2: Buildings Setup**
- Add buildings one by one or bulk import
- For each building:
  - Building name and code
  - Address and coordinates
  - Floor count
  - Structure type
  - Seismic rating
  - Assigned agent(s)
  - Estimated bonus amount

**Step 3: Units Setup**
- For each building, add units:
  - Unit number (e.g., "101", "1A", "304")
  - Floor number
  - Area (m²)
  - Room count
  - Estimated value
  - Unit status (initial: NOT_CONTACTED)

**Step 4: Owners Setup**
- For each unit, add owners:
  - Owner full name
  - ID number (encrypted)
  - Phone number (encrypted)
  - Email
  - Ownership share percentage (must total 100% per unit)
  - Preferred contact method
  - Preferred language
  - Notes (elderly, accessibility needs, etc.)
- **Multi-unit ownership:** System allows adding same owner to multiple units (within same building or across buildings)
- **Owner lookup:** When entering owner details, system checks if owner already exists and offers to link to existing owner record

**Step 5: Review & Confirm**
- Summary view showing:
  - Project details
  - Number of buildings
  - Number of units
  - Number of unique owners
  - Total estimated value
- Option to go back and edit any step
- Final confirmation creates all entities in database

**Wizard UI Features:**
- Progress indicator showing current step (e.g., "Step 2 of 5")
- "Previous" and "Next" buttons for navigation
- "Save Draft" functionality to save incomplete wizard state
- Validation at each step before allowing progression
- Bulk import option for buildings/units/owners (CSV upload)
- Template selection for common project types

**Database Tables:**
- projects, buildings, units, owners
- project_milestones, project_events
- wizard_drafts (temporary storage for incomplete wizard sessions)

**API Endpoints:**
- `GET/POST /api/projects` - List/create projects
- `GET/PUT/DELETE /api/projects/{id}` - Get/update/delete project
- `POST /api/projects/wizard/start` - Initialize wizard session
- `POST /api/projects/wizard/step/{step_number}` - Save wizard step data
- `GET /api/projects/wizard/draft/{draft_id}` - Retrieve saved draft
- `POST /api/projects/wizard/complete` - Finalize wizard and create project
- `GET/POST /api/buildings` - List/create buildings
- `GET/PUT/DELETE /api/buildings/{id}` - Get/update/delete building
- `GET/POST /api/units` - List/create units
- `GET/PUT/DELETE /api/units/{id}` - Get/update/delete unit
- `GET/POST /api/owners` - List/create owners
- `GET /api/owners/search?query={name_or_id}` - Search for existing owners
- `GET/PUT/DELETE /api/owners/{id}` - Get/update/delete owner
- `GET /api/owners/{id}/units` - Get all units owned by this owner
- `POST /api/owners/{id}/transfer` - Transfer ownership

### 4.3 Majority Engine Module

**Purpose:** Calculate signature percentages and traffic light status in real-time.

**Calculation Types:**
1. **Headcount:** (Signed Owners / Total Owners) × 100
2. **Area:** (Signed Area / Total Area) × 100
3. **Weighted:** Configurable formula combining headcount and area
4. **Custom:** Project-specific calculation logic

**Traffic Light Logic:**
- 🟢 GREEN: Signature % ≥ Required Majority (typically 75%)
- 🟡 YELLOW: Critical Threshold ≤ Signature % < Required Majority (50-75%)
- 🔴 RED: Signature % < Critical Threshold (<50%)

**Trigger Events:**
- Signature approval/rejection
- Ownership transfer
- Owner addition/removal
- Manual status override

**Performance Requirement:** Recalculation must complete in <3 seconds

**API Endpoints:**
- `GET /api/buildings/{id}/majority` - Get current majority calculation
- `POST /api/buildings/{id}/recalculate` - Force recalculation

### 4.4 CRM & Interaction Module

**Purpose:** Track all agent-owner communications for compliance and performance analysis.

**Interaction Types:**
- Phone Call (with mandatory summary)
- In-Person Meeting
- WhatsApp Message
- Email
- SMS

**Key Features:**
- Mandatory call summary after phone interactions
- Sentiment tracking (Very Positive, Positive, Neutral, Negative, Very Negative)
- Follow-up task auto-generation
- Days-since-contact tracking
- Agent activity monitoring

**Database Tables:**
- interactions_log, customer_sentiment_tracking

**API Endpoints:**
- `POST /api/interactions` - Log interaction
- `GET /api/interactions?owner_id={id}` - Get owner interaction history
- `GET /api/interactions?agent_id={id}` - Get agent interaction history
- `GET /api/interactions/recent` - Get recent interactions (last 24 hours)

### 4.5 Communication Module

**Purpose:** Multi-channel communication with owners using templates and delivery tracking.

**Supported Channels:**

**Phase 1 (Local Development):**
- Email (Local SMTP server or mock email service)
- SMS (Mock SMS service - simulates Twilio API)
- WhatsApp (Mock WhatsApp service - simulates Twilio WhatsApp API)
- In-App Notifications (future)

**Phase 2 (Production):**
- Email (AWS SES)
- SMS (Twilio)
- WhatsApp (Twilio WhatsApp API)
- In-App Notifications (future)

**Mock Services (Phase 1):**

**Mock WhatsApp Service:**
- Simulates Twilio WhatsApp API interface
- Stores messages in `whatsapp_messages` table
- Provides UI interface for viewing simulated conversations
- Supports template messages
- Tracks delivery and read status (simulated)
- Webhook simulation for incoming messages

**Mock SMS Service:**
- Simulates Twilio SMS API interface
- Stores messages in `communication_log` table with type=SMS
- Provides UI interface for viewing SMS history
- Tracks delivery status (simulated)

**Key Features:**
- Communication templates with variable substitution
- Multi-language support (Hebrew, Arabic, Russian, English)
- Delivery status tracking
- Read receipt tracking (email, WhatsApp)
- Contact preference management
- Do-not-contact compliance
- **Service Abstraction:** Communication service interface allows switching between mock (Phase 1) and real (Phase 2) services without code changes

**Database Tables:**
- communication_templates, communication_log, owner_contact_preferences
- whatsapp_messages (Phase 1 mock + Phase 2 real)

**API Endpoints:**
- `GET /api/templates` - List templates
- `POST /api/communications/send` - Send message (works with mock or real service)
- `GET /api/communications/{id}/status` - Get delivery status
- `GET /api/communications/log?owner_id={id}` - Get communication history
- `GET /api/communications/mock/whatsapp/conversations` - View simulated WhatsApp conversations (Phase 1 only)
- `GET /api/communications/mock/sms/history` - View simulated SMS history (Phase 1 only)

### 4.6 Document Management Module

**Purpose:** Store, version, and deliver documents securely.

**Storage:**
- **Phase 1:** Local filesystem storage (`./storage/documents/`)
- **Phase 2:** AWS S3 storage with versioning

**Document Types:**
- Contracts (signed/unsigned)
- ID Cards (scanned)
- Property Documents (Taba)
- Building Plans
- Photos
- Supporting Documents

**Key Features:**
- **Phase 1:** Local filesystem storage with directory structure
- **Phase 2:** S3 storage with versioning
- **Phase 1:** Local file URLs (time-limited via token)
- **Phase 2:** Presigned URL generation (time-limited, 15-minute expiry)
- Document approval workflow
- PDF generation for contracts
- Document viewer integration
- 7-year retention policy
- **Storage Abstraction:** Service interface allows switching between local (Phase 1) and S3 (Phase 2) without code changes

**Database Tables:**
- documents, document_versions, document_signatures

**API Endpoints:**
- `POST /api/documents/upload` - Upload document (works with local or S3 storage)
- `GET /api/documents/{id}` - Get document metadata
- `GET /api/documents/{id}/download` - Get presigned URL (Phase 2) or local file URL (Phase 1)
- `POST /api/documents/{id}/version` - Create new version
- `GET /api/documents?owner_id={id}` - List owner documents

### 4.7 Manager Approval Module

**Purpose:** Enforce manager approval gate for all signatures before finalization.

**Approval Workflow States:**
1. **WAIT_FOR_SIGN:** Agent initiated signing process, owner has been sent signing link/document, awaiting owner signature
2. **SIGNED_PENDING_APPROVAL:** Owner signed, awaiting manager review
3. **APPROVED (FINALIZED):** Manager approved, signature is final
4. **REJECTED:** Manager rejected, requires re-signature (returns to WAIT_FOR_SIGN)
5. **MANUAL_OVERRIDE:** Manager manually approved paper document

**Workflow State Transitions:**
```
Agent initiates → WAIT_FOR_SIGN
Owner signs → SIGNED_PENDING_APPROVAL
Manager approves → FINALIZED
Manager rejects → WAIT_FOR_SIGN (with rejection reason)
Manager manual override → FINALIZED (with override reason)
```

**Key Features:**
- **Signing Initiation:** When agent initiates signing or owner agrees to sign, system generates signing link/document and sets status to WAIT_FOR_SIGN
- Approval queue for managers (shows SIGNED_PENDING_APPROVAL items)
- Document verification interface
- Side-by-side comparison (ID vs contract details)
- Mandatory approval/rejection reason
- Manual override with explanation requirement
- Comprehensive audit trail
- Status tracking: System tracks time spent in each state for analytics

**Database Tables:**
- document_signatures (with approval_status field: WAIT_FOR_SIGN, SIGNED_PENDING_APPROVAL, FINALIZED, REJECTED, MANUAL_OVERRIDE)
- audit_log_extended

**API Endpoints:**
- `POST /api/signatures/initiate` - Initiate signing process (creates signature record with WAIT_FOR_SIGN status)
- `GET /api/signatures/waiting` - Get signatures waiting for owner to sign (WAIT_FOR_SIGN status)
- `GET /api/approvals/queue` - Get pending approvals (SIGNED_PENDING_APPROVAL status)
- `GET /api/approvals/{signature_id}` - Get approval details
- `POST /api/approvals/{signature_id}/approve` - Approve signature
- `POST /api/approvals/{signature_id}/reject` - Reject signature (returns to WAIT_FOR_SIGN)
- `POST /api/approvals/{signature_id}/manual-override` - Manual approval

### 4.8 Mobile Agent Application Module

**Purpose:** Mobile-optimized interface for field agents to manage leads and log interactions.

**Key Features:**
- Mobile-responsive design (thumb-friendly UI, buttons ≥44px)
- Lead list with priority sorting
- Click-to-call integration (tel: links)
- Camera integration for document scanning
- Quick interaction logging with dropdown/selectors
- GPS location tracking (optional, for field visit verification)
- Offline capability (future enhancement)

**Screens:**
- Lead List (assigned owners/units)
- Owner Detail View
- Quick Interaction Log Form
- Document Scanner
- Task List

**Technology:**
- React responsive design
- Progressive Web App (PWA) capabilities
- Camera API integration
- Service Worker for offline (future)

### 4.9 WhatsApp Chatbot Module

**Purpose:** Provide WhatsApp-based interface for owner self-service and digital signing.

**Phase 1: UI Simulation Only**
- WhatsApp chat interface UI for testing and demonstration
- Simulated conversation flows (no actual WhatsApp integration)
- Mock message sending/receiving for development
- UI allows agents/managers to simulate owner WhatsApp interactions
- Messages stored in database for testing purposes

**Phase 2: Full Integration (Twilio WhatsApp API)**

**Services:**

**A. Status Updates (Push/Pull)**
- Owner sends "Status" → Bot replies with building progress
- Automated push messages on milestones (e.g., "Permit Received")

**B. Document Retrieval**
- Owner requests "My Contract" → Bot sends presigned S3 link (Phase 2) or local file URL (Phase 1)
- Time-limited URLs (15 minutes)

**C. Digital Signing**
- Agent initiates signing → Owner receives WhatsApp link (Phase 2) or email/SMS link (Phase 1)
- Mobile web interface for ID verification and signing
- Flow: Upload ID → Liveness Check (future) → Review → Sign

**D. Q&A Support**
- Menu-driven support (1. Legal, 2. Technical, 3. Status)
- Escalation to human agent (creates task)

**Implementation:**

**Phase 1:**
- Mock WhatsApp service (simulates Twilio API)
- UI chat interface for testing
- Messages stored in database
- No actual WhatsApp delivery

**Phase 2:**
- Twilio WhatsApp API
- Webhook handler for incoming messages
- Message queue for outgoing messages
- State machine for conversation flows
- Template messages for compliance

**Database Tables:**
- whatsapp_messages, whatsapp_conversation_state

**API Endpoints:**
- `POST /api/whatsapp/webhook` - Handle incoming messages (Phase 2) or simulate incoming (Phase 1)
- `POST /api/whatsapp/send` - Send outgoing message (works with mock or real service)
- `GET /api/whatsapp/conversations?owner_id={id}` - Get conversation history
- `GET /api/whatsapp/simulate` - Simulate WhatsApp conversation (Phase 1 only)

### 4.10 Task Management Module

**Purpose:** Manage follow-ups, assignments, and agent workload.

**Task Types:**
- Follow-up Call
- Schedule Meeting
- Send Document
- Manager Review
- Site Visit
- Handle Objection

**Key Features:**
- Task creation (manual and automatic)
- Priority levels (Low, Medium, High, Critical)
- Due date tracking with overdue alerts
- Task dependencies
- Agent assignment and workload balancing
- Completion tracking

**Database Tables:**
- tasks

**API Endpoints:**
- `GET/POST /api/tasks` - List/create tasks
- `GET/PUT /api/tasks/{id}` - Get/update task
- `POST /api/tasks/{id}/complete` - Mark task complete
- `GET /api/tasks/my-tasks` - Get current user's tasks
- `GET /api/tasks/overdue` - Get overdue tasks

### 4.11 Financial & Incentive Module

**Purpose:** Manage incentive programs and owner claims.

**Incentive Types:**
- Tax Exemption
- Cash Incentive
- Subsidy
- Loan Guarantee
- Building Insurance

**Key Features:**
- Program configuration per project
- Eligibility criteria management
- Claim submission and tracking
- Approval workflow
- Payment tracking
- Budget management

**Database Tables:**
- incentive_programs, owner_incentive_claims, building_budget

**API Endpoints:**
- `GET/POST /api/incentives` - List/create programs
- `POST /api/incentives/{id}/claim` - Submit claim
- `GET /api/incentives/claims?owner_id={id}` - Get owner claims
- `PUT /api/incentives/claims/{id}/approve` - Approve claim

### 4.12 Reporting & Analytics Module

**Purpose:** Provide dashboards, KPIs, and custom reports for decision-making.

**Dashboard Components:**
- KPI Cards (Active Projects, Total Buildings, Signature %, Total Owners)
- Traffic Light Status Overview (Green/Yellow/Red counts)
- Building Progress Table
- Recent Interactions Timeline
- Agent Performance Metrics
- Signature Rate Trends

**Reports:**
- Building Progress Report
- Agent Performance Report
- Interaction History Report
- Financial Summary Report
- Compliance Audit Report

**Key Features:**
- Real-time dashboard updates (30-second polling)
- Pre-computed analytics snapshots (daily ETL)
- Custom report builder
- Export to PDF/Excel
- Scheduled report delivery

**Database Tables:**
- analytics_snapshot, agent_performance_metrics, building_performance_dashboard

**API Endpoints:**
- `GET /api/dashboard/data` - Get dashboard data
- `GET /api/reports/generate?type={type}` - Generate report
- `GET /api/analytics/agent-performance?period={month}` - Get agent metrics

### 4.13 Alert & Notification Module

**Purpose:** Generate and deliver alerts for critical events.

**Alert Types:**
- Threshold Violation (building drops below critical %)
- Agent Inactivity (no activity for 3+ days)
- Overdue Task
- Pending Approval
- Ownership Transfer
- System Error

**Delivery Channels:**
- In-App Notification
- Email
- SMS
- WhatsApp (for critical alerts)

**Key Features:**
- Configurable alert rules
- Alert escalation logic
- Multi-channel delivery
- Alert history and resolution tracking
- Alert snooze/dismiss

**Database Tables:**
- alert_rules, alerts, alert_history

**API Endpoints:**
- `GET /api/alerts` - Get active alerts
- `GET /api/alerts/history` - Get alert history
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert
- `POST /api/alerts/{id}/resolve` - Resolve alert

---

## 5. Database Design

### 5.1 Schema Overview

The database schema is comprehensively documented in [enhanced_db_docx_ready.md](enhanced_db_docx_ready.md). This section provides a summary and additional tables required for the complete system.

**Core Entity Tables (25+):**
1. projects, buildings, units, owners
2. interactions_log, communication_templates, communication_log
3. tasks, project_milestones, project_events
4. documents, document_signatures
5. incentive_programs, owner_incentive_claims, building_budget
6. stakeholders, stakeholder_communications
7. agent_knowledge_base, objection_handling_guide
8. analytics_snapshot, agent_performance_metrics, building_performance_dashboard
9. audit_log_extended, compliance_checklist
10. users, user_roles, role_permissions

**Additional Tables for Complete System:**

**26. whatsapp_messages**
```sql
CREATE TABLE whatsapp_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES owners(owner_id),
    direction ENUM('INBOUND', 'OUTBOUND'),
    message_type ENUM('TEXT', 'TEMPLATE', 'MEDIA', 'INTERACTIVE'),
    message_body TEXT,
    template_id UUID REFERENCES communication_templates(template_id),
    twilio_message_sid VARCHAR(100),
    status ENUM('QUEUED', 'SENT', 'DELIVERED', 'READ', 'FAILED'),
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**27. whatsapp_conversation_state**
```sql
CREATE TABLE whatsapp_conversation_state (
    state_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES owners(owner_id) UNIQUE,
    current_flow ENUM('IDLE', 'STATUS_QUERY', 'DOCUMENT_REQUEST', 'SIGNING', 'QA_SUPPORT'),
    current_step VARCHAR(100),
    context_data JSONB,
    last_message_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**28. alert_rules**
```sql
CREATE TABLE alert_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(255),
    rule_type ENUM('THRESHOLD_VIOLATION', 'AGENT_INACTIVITY', 'OVERDUE_TASK', 'PENDING_APPROVAL', 'OWNERSHIP_TRANSFER'),
    condition_logic JSONB,
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
    delivery_channels TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**29. alerts**
```sql
CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID REFERENCES alert_rules(rule_id),
    alert_type ENUM('THRESHOLD_VIOLATION', 'AGENT_INACTIVITY', 'OVERDUE_TASK', 'PENDING_APPROVAL', 'OWNERSHIP_TRANSFER', 'SYSTEM_ERROR'),
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
    title VARCHAR(255),
    message TEXT,
    related_entity_type ENUM('PROJECT', 'BUILDING', 'UNIT', 'OWNER', 'AGENT'),
    related_entity_id UUID,
    status ENUM('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'DISMISSED'),
    assigned_to UUID REFERENCES users(user_id),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**30. document_versions**
```sql
CREATE TABLE document_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(document_id),
    version_number INTEGER,
    s3_key VARCHAR(500),
    file_size_bytes BIGINT,
    uploaded_by UUID REFERENCES users(user_id),
    change_description TEXT,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**31. wizard_drafts**
```sql
CREATE TABLE wizard_drafts (
    draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by UUID REFERENCES users(user_id),
    current_step INTEGER DEFAULT 1,
    wizard_data JSONB,  -- Stores all wizard step data
    expires_at TIMESTAMP,  -- Auto-delete after 7 days
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 Key Relationships

```
Project (1) ──< (N) Buildings
Building (1) ──< (N) Units
Unit (1) ──< (N) Owners (M:N relationship)
Owner (1) ──< (N) Units (M:N relationship - owners can own multiple units)
Owner (1) ──< (N) Interactions
Owner (1) ──< (N) Documents
Owner (1) ──< (N) Signatures
Owner (1) ──< (N) WhatsApp Messages
Agent (1) ──< (N) Interactions
Agent (1) ──< (N) Tasks
Manager (1) ──< (N) Approvals
```

**Multi-Unit Ownership:**
- An owner can own multiple units within the same building
- An owner can own units across multiple buildings within the same project
- Each owner-unit relationship has its own ownership share percentage
- The `owners` table links to `units` via `unit_id` foreign key, allowing multiple records per owner
- To find all units owned by an owner: `SELECT * FROM owners WHERE owner_id = ? AND is_current_owner = TRUE`
- To find all owners of a unit: `SELECT * FROM owners WHERE unit_id = ? AND is_current_owner = TRUE`

### 5.3 Indexing Strategy

**Performance-Critical Indexes:**
```sql
-- Projects
CREATE INDEX idx_projects_status ON projects(project_stage) WHERE is_deleted = FALSE;

-- Buildings
CREATE INDEX idx_buildings_project ON buildings(project_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_buildings_status ON buildings(current_status);
CREATE INDEX idx_buildings_signature_pct ON buildings(signature_percentage DESC);
CREATE INDEX idx_buildings_traffic_light ON buildings(traffic_light_status);

-- Units
CREATE INDEX idx_units_building ON units(building_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_units_status ON units(unit_status);

-- Owners
CREATE INDEX idx_owners_unit ON owners(unit_id) WHERE is_deleted = FALSE AND is_current_owner = TRUE;
CREATE INDEX idx_owners_owner_id ON owners(owner_id) WHERE is_deleted = FALSE AND is_current_owner = TRUE; -- For finding all units owned by an owner
CREATE INDEX idx_owners_status ON owners(owner_status);
CREATE INDEX idx_owners_id_hash ON owners(id_number_hash);
CREATE INDEX idx_owners_phone_hash ON owners(phone_hash);

-- Interactions
CREATE INDEX idx_interactions_owner ON interactions_log(owner_id);
CREATE INDEX idx_interactions_agent ON interactions_log(agent_id);
CREATE INDEX idx_interactions_date ON interactions_log(interaction_date DESC);

-- Documents
CREATE INDEX idx_documents_owner ON documents(owner_id);
CREATE INDEX idx_documents_type ON documents(document_type);

-- Tasks
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to_agent_id) WHERE status IN ('NOT_STARTED', 'IN_PROGRESS');
CREATE INDEX idx_tasks_due ON tasks(due_date) WHERE status != 'COMPLETED';

-- WhatsApp Messages
CREATE INDEX idx_whatsapp_owner ON whatsapp_messages(owner_id);
CREATE INDEX idx_whatsapp_created ON whatsapp_messages(created_at DESC);

-- Alerts
CREATE INDEX idx_alerts_active ON alerts(created_at DESC) WHERE status = 'ACTIVE';
```

---

## 6. API Design

### 6.1 API Principles

- **RESTful Design**: Resources mapped to HTTP verbs (GET, POST, PUT, DELETE)
- **JSON Format**: All requests and responses use JSON
- **Versioning**: API versioned via URL path (`/api/v1/...`)
- **Authentication**: JWT Bearer token in Authorization header
- **Error Handling**: Consistent error response format with HTTP status codes
- **Pagination**: Cursor-based pagination for list endpoints
- **Rate Limiting**: 1000 requests per hour per user

### 6.2 API Structure

**Base URL:** `https://api.tama38.example.com/api/v1`

**Authentication Header:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Standard Response Format:**
```json
{
  "success": true,
  "data": { },
  "meta": {
    "timestamp": "2025-12-30T10:00:00Z",
    "request_id": "uuid"
  }
}
```

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-12-30T10:00:00Z",
    "request_id": "uuid"
  }
}
```

### 6.3 Key API Endpoints Summary

**Authentication:**
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - Logout
- `GET /auth/me` - Get current user

**Projects:**
- `GET /projects` - List projects (paginated)
- `POST /projects` - Create project (direct creation, bypass wizard)
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Soft delete project
- `POST /projects/wizard/start` - Initialize wizard session (returns draft_id)
- `POST /projects/wizard/step/{step_number}` - Save wizard step data
- `GET /projects/wizard/draft/{draft_id}` - Retrieve saved draft
- `POST /projects/wizard/complete` - Finalize wizard and create project

**Buildings:**
- `GET /buildings?project_id={id}` - List buildings
- `POST /buildings` - Create building
- `GET /buildings/{id}` - Get building details
- `PUT /buildings/{id}` - Update building
- `GET /buildings/{id}/majority` - Get majority calculation

**Units:**
- `GET /units?building_id={id}` - List units
- `POST /units` - Create unit
- `GET /units/{id}` - Get unit details
- `PUT /units/{id}` - Update unit

**Owners:**
- `GET /owners?unit_id={id}` - List owners for a unit
- `GET /owners?project_id={id}` - List all owners in a project
- `POST /owners` - Create owner
- `GET /owners/{id}` - Get owner details
- `GET /owners/{id}/units` - Get all units owned by this owner (across buildings)
- `GET /owners/search?query={name_or_id}` - Search for existing owners (for wizard owner lookup)
- `PUT /owners/{id}` - Update owner
- `POST /owners/{id}/transfer` - Transfer ownership

**Interactions:**
- `POST /interactions` - Log interaction
- `GET /interactions?owner_id={id}` - Get interactions
- `GET /interactions/recent` - Recent interactions

**Documents:**
- `POST /documents/upload` - Upload document
- `GET /documents/{id}/download` - Get presigned URL
- `GET /documents?owner_id={id}` - List documents

**Signatures:**
- `POST /signatures/initiate` - Initiate signing (creates signature with WAIT_FOR_SIGN status, generates signing link)
- `GET /signatures/waiting` - Get signatures waiting for owner to sign (WAIT_FOR_SIGN status)
- `GET /signatures/{id}` - Get signature details
- `POST /signatures/{id}/sign` - Submit signature (changes status from WAIT_FOR_SIGN to SIGNED_PENDING_APPROVAL)

**Approvals:**
- `GET /approvals/queue` - Get approval queue
- `POST /approvals/{id}/approve` - Approve signature
- `POST /approvals/{id}/reject` - Reject signature

**Tasks:**
- `GET /tasks/my-tasks` - Get user's tasks
- `POST /tasks` - Create task
- `PUT /tasks/{id}/complete` - Complete task

**Dashboard:**
- `GET /dashboard/data` - Get dashboard metrics
- `GET /dashboard/kpis` - Get KPI summary

**WhatsApp:**
- `POST /whatsapp/webhook` - Twilio webhook handler
- `POST /whatsapp/send` - Send WhatsApp message

**Reports:**
- `GET /reports/generate?type={type}` - Generate report
- `GET /reports/export?format={format}` - Export data

---

## 7. UI/UX Design

### 7.1 Desktop Web Application

**Based on:** [TAMA38_UI_Mockup.html](TAMA38_UI_Mockup.html) and [Tama38_UI_Mockup_heb.html](Tama38_UI_Mockup_heb.html)

**Layout Structure:**
- **Sidebar Navigation** (260px width)
  - Logo and branding
  - Sectioned menu: Main, Projects, CRM, Operations, Financial, Reports
  - Active state indication
  
- **Top Navigation Bar** (64px height)
  - Breadcrumb trail
  - Global search
  - User menu with avatar
  - Notifications (future)

- **Main Content Area**
  - Page header with title and subtitle
  - Content sections (KPI cards, tables, forms)
  - Responsive grid layout

**Key Screens:**

1. **Dashboard**
   - 4 KPI cards (Active Projects, Total Buildings, Signature %, Total Owners)
   - Traffic light status visualization (3 circles: Green, Yellow, Red)
   - Top buildings table sorted by priority
   - Recent interactions timeline

2. **Projects List**
   - Searchable/filterable table
   - Columns: Name, Buildings, Signature %, Status, Manager
   - + New Project button (opens wizard)

3. **Project Creation Wizard** (NEW)
   - **Multi-step form** with progress indicator at top
   - **Step 1: Project Information**
     - Form fields: Name, Code, Type, Location, Description, Thresholds, Manager, Dates
     - Validation before allowing "Next"
   - **Step 2: Buildings Setup**
     - "Add Building" button opens building form modal
     - List of added buildings with edit/delete
     - Bulk import option (CSV upload)
     - "Previous" and "Next" buttons
   - **Step 3: Units Setup**
     - Select building from dropdown
     - "Add Unit" button opens unit form
     - Unit form: Unit number, Floor, Area, Rooms, Value
     - List of units per building (grouped by building)
     - "Previous" and "Next" buttons
   - **Step 4: Owners Setup**
     - Select unit from dropdown
     - "Add Owner" button opens owner form
     - Owner form: Name, ID, Phone, Email, Ownership %, Contact preferences
     - **Owner Lookup:** Search field to find existing owners (by name or ID)
     - If owner exists, option to "Link to Existing Owner" or "Create New"
     - List of owners per unit (showing ownership %)
     - Validation: Ownership % must total 100% per unit
     - "Previous" and "Next" buttons
   - **Step 5: Review & Confirm**
     - Summary cards showing: Project details, Building count, Unit count, Owner count
     - Expandable sections to review each step's data
     - "Edit" links to go back to specific steps
     - "Save Draft" button (saves incomplete wizard state)
     - "Create Project" button (final confirmation)
   - **Wizard Features:**
     - Progress bar: "Step 2 of 5"
     - Auto-save draft every 30 seconds
     - Browser back/forward navigation support
     - Responsive design (works on tablet)

4. **Building Detail**
   - KPI cards (Signature Rate, Total Units, Traffic Light, Last Activity)
   - Tabbed interface: Units, Owners, Interactions, Tasks, Communications
   - Building-specific data tables

4. **Owner Detail**
   - Contact information card
   - TAMA38 status card
   - **Units Owned Section** (NEW - shows all units owned by this owner)
     - Table/list showing: Building, Unit Number, Ownership %, Signature Status
     - Units can be in different buildings within the same project
     - Click unit to navigate to unit detail
   - Interaction history timeline

5. **Approval Queue** (NEW - not in mockup)
   - List of pending signature approvals
   - Side-by-side view: Document + ID verification
   - Approve/Reject/Manual Override buttons

6. **Task Management**
   - Kanban-style board (future) or list view
   - Filter by: Assigned to me, Due today, Overdue, All
   - Quick task creation

7. **Reports & Analytics**
   - Agent performance table
   - Chart placeholders (will use Recharts)
   - Export functionality

**Color Scheme:**
- Primary: `#218090` (Teal)
- Success/Green: `#10B981`
- Warning/Yellow: `#F59E0B`
- Danger/Red: `#EF4444`
- Neutral Gray: `#6B7280`
- Background: `#F9FAFB`

### 7.2 Mobile Agent Application

**Design Principles:**
- Thumb-friendly: All interactive elements ≥44x44px
- Minimal typing: Use dropdowns, radio buttons, checkboxes
- Quick actions: One-tap call, one-tap WhatsApp
- Large fonts: Minimum 14px, scalable to 18px
- High contrast: For outdoor visibility

**Key Screens:**

1. **Lead List**
   - Sorted by: Priority, Last Contact, Signature Status
   - Card layout with: Owner name, Unit, Status badge, Days since contact
   - Quick actions: Call, WhatsApp, Log Interaction

2. **Quick Interaction Log**
   - Pre-filled owner/unit info
   - Dropdown: Interaction type
   - Dropdown: Outcome
   - Text area: Summary (voice-to-text enabled)
   - Dropdown: Next action
   - Date picker: Follow-up date
   - Submit button

3. **Document Scanner**
   - Camera interface
   - Real-time edge detection (future)
   - Multiple page capture
   - Tag document type (ID, Contract, Other)
   - Upload to pending approval queue

4. **Task List**
   - Today's tasks
   - Overdue tasks (highlighted)
   - Complete task with one tap

### 7.3 Mobile Web Signing Interface

**Triggered from:**
- **Phase 1:** Email or SMS link with unique token (simulated WhatsApp)
- **Phase 2:** WhatsApp link with unique token

**Flow:**
1. **Landing Page**
   - Welcome message
   - Security information
   - "Start Signing Process" button

2. **ID Verification**
   - Upload ID photo (front and back)
   - OCR extraction and validation
   - Match against database record

3. **Liveness Check** (Phase 2/Future)
   - Take selfie
   - AWS Rekognition comparison

4. **Document Review**
   - PDF viewer (responsive)
   - Scroll to read entire contract
   - Checkbox: "I have read and understood"

5. **Digital Signature**
   - Canvas for signature drawing
   - Clear and redo options
   - Confirm signature button

6. **Completion**
   - Success message
   - "Your signature is pending manager approval"
   - **Phase 1:** "You will receive confirmation via email/SMS"
   - **Phase 2:** "You will receive confirmation via WhatsApp"

### 7.4 Multi-language Support

**Supported Languages:**
- Hebrew (עברית) - RTL
- Arabic (العربية) - RTL
- Russian (Русский) - LTR
- English - LTR

**Implementation:**
- `react-i18next` for React components
- JSON translation files: `en.json`, `he.json`, `ar.json`, `ru.json`
- Language switcher in user menu
- RTL support: Mirror layout for Hebrew/Arabic
- Date/number formatting per locale

**RTL Considerations:**
- Flexbox `flex-direction: row-reverse`
- Text alignment: `text-align: right`
- Padding/margin reversal
- Icon positioning adjustments

---

## 8. Integration Design

### 8.1 Phase 1 Mock Services (Local Development)

**Purpose:** Provide simulated communication services for Phase 1 development without external dependencies.

#### 8.1.1 Mock WhatsApp Service

**Implementation:**
- Simulates Twilio WhatsApp API interface
- Stores messages in `whatsapp_messages` database table
- Provides UI interface for viewing/managing simulated conversations
- No actual WhatsApp delivery

**Service Interface:**
```python
class MockWhatsAppService:
    async def send_message(self, to: str, body: str, template_id: Optional[str] = None):
        """Simulate sending WhatsApp message"""
        # Store message in database with status=QUEUED
        # Simulate delivery delay (1-2 seconds)
        # Update status to SENT, then DELIVERED
        # Return mock message SID
    
    async def send_template(self, to: str, template_name: str, parameters: dict):
        """Simulate sending template message"""
        # Render template with parameters
        # Store in database
        # Return mock message SID
    
    async def handle_webhook(self, message_data: dict):
        """Simulate incoming webhook"""
        # Store incoming message in database
        # Process message and generate response
        # Return response message
```

**UI Interface:**
- Admin/Manager screen: "Simulated WhatsApp Conversations"
- View all simulated conversations
- Manually trigger incoming messages (for testing)
- View message delivery status
- Simulate read receipts

**API Endpoints:**
- `POST /api/whatsapp/mock/send` - Send simulated WhatsApp message
- `POST /api/whatsapp/mock/webhook` - Simulate incoming webhook
- `GET /api/whatsapp/mock/conversations` - Get all simulated conversations
- `GET /api/whatsapp/mock/conversations/{owner_id}` - Get conversation for owner

#### 8.1.2 Mock SMS Service

**Implementation:**
- Simulates Twilio SMS API interface
- Stores messages in `communication_log` table with type=SMS
- Provides UI interface for viewing SMS history
- No actual SMS delivery

**Service Interface:**
```python
class MockSMSService:
    async def send_sms(self, to: str, body: str):
        """Simulate sending SMS"""
        # Store message in database with status=QUEUED
        # Simulate delivery delay
        # Update status to SENT, then DELIVERED
        # Return mock message SID
```

**UI Interface:**
- Admin/Manager screen: "Simulated SMS History"
- View all simulated SMS messages
- Filter by recipient, date, status

**API Endpoints:**
- `POST /api/sms/mock/send` - Send simulated SMS
- `GET /api/sms/mock/history` - Get SMS history

#### 8.1.3 Service Abstraction Layer

**Purpose:** Allow switching between mock (Phase 1) and real (Phase 2) services without code changes.

**Implementation:**
```python
# Abstract base class
class CommunicationService(ABC):
    @abstractmethod
    async def send_whatsapp(self, to: str, body: str):
        pass
    
    @abstractmethod
    async def send_sms(self, to: str, body: str):
        pass

# Phase 1 implementation
class MockCommunicationService(CommunicationService):
    # Uses mock services

# Phase 2 implementation
class TwilioCommunicationService(CommunicationService):
    # Uses real Twilio API

# Factory pattern
def get_communication_service() -> CommunicationService:
    if settings.ENVIRONMENT == "local" or settings.USE_MOCK_SERVICES:
        return MockCommunicationService()
    else:
        return TwilioCommunicationService()
```

**Configuration:**
```python
# .env.local (Phase 1)
USE_MOCK_SERVICES=true
COMMUNICATION_SERVICE=mock

# .env.production (Phase 2)
USE_MOCK_SERVICES=false
COMMUNICATION_SERVICE=twilio
TWILIO_ACCOUNT_SID=<sid>
TWILIO_AUTH_TOKEN=<token>
```

#### 8.1.4 Local File Storage Service

**Purpose:** Store documents locally in Phase 1, migrate to S3 in Phase 2.

**Implementation:**
```python
class LocalStorageService:
    def __init__(self, base_path: str = "./storage/documents"):
        self.base_path = base_path
    
    async def upload_file(self, file: bytes, key: str) -> str:
        """Save file to local filesystem"""
        file_path = os.path.join(self.base_path, key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file)
        return f"/api/files/{key}"  # Local URL
    
    async def get_file_url(self, key: str, expiration: int = 900) -> str:
        """Generate local file URL"""
        return f"/api/files/{key}?expires={expiration}"

class S3StorageService:
    # Phase 2 implementation using boto3
    pass

# Factory pattern
def get_storage_service() -> StorageService:
    if settings.ENVIRONMENT == "local":
        return LocalStorageService()
    else:
        return S3StorageService()
```

**Migration Path:**
- Phase 1: Files stored in `./storage/documents/` directory
- Phase 2: Upload all files to S3 using migration script
- Script preserves directory structure as S3 keys

### 8.2 Twilio WhatsApp Integration (Phase 2)

**Setup:**
1. Create Twilio account
2. Request WhatsApp Business API access
3. Configure WhatsApp Business Profile
4. Set up Twilio Phone Number for WhatsApp
5. Configure webhook URL: `https://api.tama38.example.com/api/v1/whatsapp/webhook`

**Webhook Handler:**
```python
@app.post("/api/v1/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    # Verify Twilio signature
    # Parse incoming message
    # Determine conversation state
    # Route to appropriate handler (status, document, signing, qa)
    # Update conversation state
    # Send response via Twilio API
```

**Message Flow:**
1. Owner sends message → Twilio webhook → Backend handler
2. Backend processes message → Determines response
3. Backend calls Twilio API → Twilio delivers to owner

**Template Messages:**
```json
{
  "name": "signature_request",
  "language": "he",
  "components": [
    {
      "type": "body",
      "parameters": [
        {"type": "text", "text": "{{owner_name}}"},
        {"type": "text", "text": "{{building_address}}"}
      ]
    },
    {
      "type": "button",
      "sub_type": "url",
      "parameters": [
        {"type": "text", "text": "{{signing_token}}"}
      ]
    }
  ]
}
```

### 8.2 AWS Services Integration

**S3 Configuration:**
```python
import boto3
from botocore.config import Config

s3_client = boto3.client(
    's3',
    region_name='eu-central-1',
    config=Config(signature_version='s3v4')
)

def generate_presigned_url(bucket, key, expiration=900):
    """Generate presigned URL valid for 15 minutes"""
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiration
    )
```

**Cognito Integration:**
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jose.jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jose.jwt.decode(
            token,
            cognito_public_key,
            algorithms=["RS256"],
            audience=cognito_client_id
        )
        return User.from_cognito_payload(payload)
    except jose.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**SES for Email:**
```python
import boto3

ses_client = boto3.client('ses', region_name='eu-central-1')

def send_email(to_address, subject, body_html, body_text):
    response = ses_client.send_email(
        Source='noreply@tama38.example.com',
        Destination={'ToAddresses': [to_address]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Html': {'Data': body_html},
                'Text': {'Data': body_text}
            }
        }
    )
    return response['MessageId']
```

### 8.3 External Service Configuration

**Environment Variables:**
```bash
# AWS
AWS_REGION=eu-central-1
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
S3_BUCKET_NAME=tama38-documents-prod

# Cognito
COGNITO_USER_POOL_ID=<pool-id>
COGNITO_CLIENT_ID=<client-id>
COGNITO_REGION=eu-central-1

# Twilio
TWILIO_ACCOUNT_SID=<sid>
TWILIO_AUTH_TOKEN=<token>
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Database
DATABASE_URL=postgresql://user:pass@host:5432/tama38_prod

# Application
SECRET_KEY=<secret>
ENVIRONMENT=production
DEBUG=false
```

**Secrets Management:**
- Use AWS Secrets Manager for production
- Rotate secrets every 90 days
- Never commit secrets to version control
- Use IAM roles for AWS service access (no hardcoded keys in production)

---

## 9. Security Design

### 9.1 Data Encryption

**Encryption at Rest:**
- **Database**: AWS RDS encryption with AWS KMS
- **S3**: Server-side encryption (SSE-S3) enabled by default
- **PII Fields**: Additional application-level encryption for sensitive fields
  - ID numbers: AES-256 encryption
  - Phone numbers: AES-256 encryption
  - Hash fields for lookups without decryption

**Encryption in Transit:**
- **HTTPS Only**: TLS 1.2+ for all API communication
- **Certificate Management**: AWS Certificate Manager (ACM)
- **HSTS Headers**: Enforce HTTPS in browsers

**PII Encryption Example:**
```python
from cryptography.fernet import Fernet
import hashlib

class PIIEncryption:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, data: bytes) -> str:
        return self.cipher.decrypt(data).decode()
    
    @staticmethod
    def hash(data: str) -> bytes:
        return hashlib.sha256(data.encode()).digest()
```

### 9.2 Access Control

**Role-Based Permissions Matrix:**

| Resource | Super Admin | Project Manager | Agent | Tenant |
|----------|-------------|-----------------|-------|--------|
| View All Projects | ✓ | ✗ (assigned only) | ✗ (assigned only) | ✗ |
| Create Project | ✓ | ✗ | ✗ | ✗ |
| View Buildings | ✓ | ✓ (assigned projects) | ✓ (assigned buildings) | ✗ |
| Approve Signatures | ✓ | ✓ | ✗ | ✗ |
| Log Interactions | ✓ | ✓ | ✓ | ✗ |
| View Own Data | ✓ | ✓ | ✓ | ✓ |
| Sign Documents | ✗ | ✗ | ✗ | ✓ |

**API Authorization:**
```python
from functools import wraps

def require_role(*allowed_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Forbidden")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

@app.post("/api/v1/approvals/{id}/approve")
@require_role("SUPER_ADMIN", "PROJECT_MANAGER")
async def approve_signature(id: str, current_user: User):
    # Approve signature logic
    pass
```

**Data Isolation:**
- Agents can only view buildings/owners assigned to them
- Project Managers can only view projects assigned to them
- Enforce in database queries with WHERE clauses

### 9.3 Audit Trail

**Comprehensive Logging:**
- All data modifications logged in `audit_log_extended` table
- Include: user_id, timestamp, table_name, record_id, old_values, new_values, reason
- Immutable logs (INSERT only, no UPDATE/DELETE)

**Manual Override Audit:**
- Mandatory reason field (minimum 20 characters)
- Additional approval workflow for manual overrides
- Email notification to Super Admin

**Example Audit Log Entry:**
```json
{
  "audit_id": "uuid",
  "table_name": "owners",
  "record_id": "owner-uuid",
  "action": "MANUAL_OVERRIDE",
  "old_values": {"owner_status": "NEGOTIATING"},
  "new_values": {"owner_status": "SIGNED"},
  "changed_by_user_id": "manager-uuid",
  "changed_at": "2025-12-30T10:00:00Z",
  "reason_text": "Paper contract signed offline, scanned and verified",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

---

## 10. Performance & Scalability

### 10.1 Performance Requirements

| Metric | Target | Critical Path |
|--------|--------|---------------|
| Dashboard Load Time | <3 seconds | Initial page load |
| Majority Calculation | <3 seconds | After signature approval |
| API Response (p95) | <500ms | All endpoints |
| Database Query | <200ms | Complex queries |
| Document Upload | <5 seconds | Up to 10MB |

### 10.2 Optimization Strategies

**Database Optimization:**
- Strategic indexes on frequently queried fields
- Connection pooling (min 10, max 50 connections)
- Query optimization with EXPLAIN ANALYZE
- Materialized views for dashboard data (refresh every 5 minutes)

**API Optimization:**
- Response caching with ETags
- Pagination for list endpoints (limit 50 items per page)
- Field filtering (`?fields=id,name,status`)
- Gzip compression for responses

**Frontend Optimization:**
- Code splitting by route
- Lazy loading for images and components
- Memoization for expensive calculations
- Virtual scrolling for large tables

**Caching Strategy (Optional):**
- Redis for session storage
- Cache dashboard metrics (TTL 30 seconds)
- Cache user permissions (TTL 5 minutes)

### 10.3 Scalability Strategy

**Horizontal Scaling:**
- ECS auto-scaling based on CPU/Memory (target: 70% utilization)
- Minimum 2 tasks, maximum 10 tasks per service
- Load balancer distributes traffic across tasks

**Database Scaling:**
- Vertical scaling: Upgrade RDS instance type as needed
- Read replicas: Add for read-heavy workloads (future)
- Connection pooling: Prevent connection exhaustion

**S3 Scaling:**
- Automatic, managed by AWS
- CloudFront CDN for frequently accessed documents (future)

---

## 11. Deployment & DevOps

### 11.1 Local Development Setup

**Prerequisites:**
- Docker Desktop for Windows
- Git
- Node.js 18+ (for frontend development outside Docker)
- Python 3.11+ (for backend development outside Docker)

**Phase 1 Setup Steps (No AWS/Twilio):**
```bash
# Clone repository
git clone https://github.com/example/tama38.git
cd tama38

# Copy environment file
cp .env.example .env.local

# Edit .env.local with Phase 1 configuration
# DATABASE_URL=postgresql://postgres:postgres@database:5432/tama38_dev
# USE_MOCK_SERVICES=true
# COMMUNICATION_SERVICE=mock
# STORAGE_SERVICE=local
# STORAGE_PATH=./storage/documents
# AUTH_SERVICE=local
# SECRET_KEY=<generate-random-key>
# ENVIRONMENT=local
# DEBUG=true

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create initial admin user
docker-compose exec backend python scripts/create_admin.py

# Access applications
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
# Database: localhost:5432 (user: postgres, password: postgres)
# Mock WhatsApp UI: http://localhost:3000/admin/mock-whatsapp
# Mock SMS UI: http://localhost:3000/admin/mock-sms
```

**Phase 1 Docker Compose File Structure:**
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    environment:
      - VITE_API_URL=http://localhost:8000
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./storage:/app/storage  # Local file storage
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@database:5432/tama38_dev
      - USE_MOCK_SERVICES=true
      - COMMUNICATION_SERVICE=mock
      - STORAGE_SERVICE=local
      - STORAGE_PATH=/app/storage/documents
      - AUTH_SERVICE=local
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=local
    depends_on:
      - database
  
  database:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=tama38_dev
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Phase 2 Docker Compose (for AWS deployment preparation):**
- Same structure but with AWS environment variables
- Remove mock service flags
- Add AWS credentials and endpoints

### 11.2 AWS Production Deployment

**Infrastructure Setup (Terraform Example):**
```hcl
# VPC and Networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name = "tama38-vpc"
  cidr = "10.0.0.0/16"
  azs = ["eu-central-1a", "eu-central-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets = ["10.0.101.0/24", "10.0.102.0/24"]
  enable_nat_gateway = true
}

# RDS PostgreSQL
resource "aws_db_instance" "tama38_db" {
  identifier = "tama38-prod"
  engine = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.medium"
  allocated_storage = 100
  storage_encrypted = true
  multi_az = true
  db_name = "tama38_prod"
  username = "tama38admin"
  password = var.db_password
  backup_retention_period = 30
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name = aws_db_subnet_group.tama38.name
}

# S3 Bucket
resource "aws_s3_bucket" "documents" {
  bucket = "tama38-documents-prod"
  versioning {
    enabled = true
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  lifecycle_rule {
    enabled = true
    transition {
      days = 365
      storage_class = "GLACIER"
    }
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "tama38" {
  name = "tama38-prod"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family = "tama38-app"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = "1024"
  memory = "2048"
  container_definitions = jsonencode([
    {
      name = "frontend"
      image = "${aws_ecr_repository.frontend.repository_url}:latest"
      portMappings = [{
        containerPort = 80
      }]
    },
    {
      name = "backend"
      image = "${aws_ecr_repository.backend.repository_url}:latest"
      portMappings = [{
        containerPort = 8000
      }]
      environment = [
        {name = "DATABASE_URL", value = "postgresql://..."},
        {name = "S3_BUCKET_NAME", value = aws_s3_bucket.documents.id}
      ]
    }
  ])
}

# Application Load Balancer
resource "aws_lb" "tama38" {
  name = "tama38-alb"
  internal = false
  load_balancer_type = "application"
  security_groups = [aws_security_group.alb.id]
  subnets = module.vpc.public_subnets
}
```

**CI/CD Pipeline (GitHub Actions Example):**
```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-central-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push frontend image
        run: |
          cd frontend
          docker build -t $ECR_REGISTRY/tama38-frontend:$IMAGE_TAG .
          docker push $ECR_REGISTRY/tama38-frontend:$IMAGE_TAG
      
      - name: Build and push backend image
        run: |
          cd backend
          docker build -t $ECR_REGISTRY/tama38-backend:$IMAGE_TAG .
          docker push $ECR_REGISTRY/tama38-backend:$IMAGE_TAG
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster tama38-prod \
            --service tama38-app --force-new-deployment
```

### 11.3 Migration Checklist: Phase 1 → Phase 2

**Phase 1 Development (Complete First):**
- [ ] Develop and test all features locally with mock services
- [ ] Ensure all environment variables are externalized
- [ ] Verify service abstraction layer works (mock ↔ real)
- [ ] Test wizard UI for project creation
- [ ] Test multi-unit ownership functionality
- [ ] Test WAIT_FOR_SIGN workflow
- [ ] Document all Phase 1 features

**Phase 2 AWS Infrastructure Setup:**
- [ ] Provision AWS infrastructure (VPC, RDS, S3, Cognito, ECS)
- [ ] Configure security groups and IAM roles
- [ ] Set up Secrets Manager with API keys (Twilio, AWS credentials)
- [ ] Create S3 bucket with versioning and lifecycle policies
- [ ] Set up Cognito User Pool
- [ ] Configure RDS PostgreSQL (Multi-AZ, encrypted, backups)

**Phase 2 Service Migration:**
- [ ] **Twilio Setup:**
  - [ ] Create Twilio account
  - [ ] Request WhatsApp Business API access
  - [ ] Configure WhatsApp Business Profile
  - [ ] Set up Twilio Phone Number
  - [ ] Test Twilio API connectivity
- [ ] **Storage Migration:**
  - [ ] Upload all local filesystem documents to S3
  - [ ] Preserve directory structure as S3 keys
  - [ ] Verify file integrity after upload
  - [ ] Update environment variables to use S3
- [ ] **Authentication Migration:**
  - [ ] Migrate user accounts to Cognito (or integrate Cognito with existing users)
  - [ ] Test authentication flow with Cognito
  - [ ] Update environment variables to use Cognito

**Phase 2 Deployment:**
- [ ] Build and push Docker images to ECR
- [ ] Update environment variables in ECS task definitions
- [ ] Switch service flags: `USE_MOCK_SERVICES=false`, `COMMUNICATION_SERVICE=twilio`, `STORAGE_SERVICE=s3`, `AUTH_SERVICE=cognito`
- [ ] Deploy to ECS with auto-scaling
- [ ] Configure ALB with SSL certificate
- [ ] Run database migrations on RDS (if schema changes)
- [ ] Migrate database data (pg_dump from local, restore to RDS)

**Phase 2 Testing & Go-Live:**
- [ ] Test all critical workflows with real services
- [ ] Verify WhatsApp integration works end-to-end
- [ ] Verify SMS integration works
- [ ] Verify S3 document storage and retrieval
- [ ] Verify Cognito authentication
- [ ] Configure CloudWatch alarms and monitoring
- [ ] Update DNS records to point to ALB
- [ ] Monitor for 24 hours
- [ ] Document runbooks for common operations
- [ ] Remove mock service UI (or keep for admin testing)

**Rollback Plan:**
- Keep Phase 1 environment running during migration
- Can switch back to mock services via environment variables if issues occur
- Database can be restored from backup if needed

---

## 12. Testing Strategy

### 12.1 Testing Approach

**Unit Testing:**
- Backend: Pytest with 80%+ code coverage
- Frontend: Jest + React Testing Library
- Test individual functions and components in isolation

**Integration Testing:**
- Test API endpoints with test database
- Test external service integrations (Twilio, AWS) with mocks
- Test database transactions and constraints

**End-to-End Testing:**
- Playwright or Cypress for browser automation
- Test complete user workflows (login → signature → approval)
- Run against staging environment

**Performance Testing:**
- Apache JMeter or k6 for load testing
- Test with 100 concurrent users
- Verify <3 second response times

### 12.2 Test Data Management

**Test Database:**
- Separate test database with sample data
- Reset before each test run
- Fixtures for common test scenarios

**Sample Data:**
- 3 projects
- 10 buildings per project
- 20 units per building
- 1-3 owners per unit
- 100+ interactions
- 50+ documents

---

## 13. Monitoring & Maintenance

### 13.1 Monitoring Strategy

**AWS CloudWatch:**
- Application logs (DEBUG, INFO, WARNING, ERROR levels)
- Container metrics (CPU, Memory, Network)
- RDS metrics (Connections, Query performance)
- Custom metrics (Signature rate, API latency)

**Alerts:**
- ECS task failures
- RDS high CPU (>80%)
- API error rate >1%
- Majority calculation >5 seconds
- Disk space <20%

**Dashboard:**
- Real-time service health
- Request rate and latency
- Error rate trends
- Database performance

### 13.2 Backup & Recovery

**Database Backup:**
- Automated daily snapshots (retained 30 days)
- Point-in-time recovery enabled (7 days)
- Monthly backups archived for 7 years (compliance)

**S3 Backup:**
- Versioning enabled
- Cross-region replication (optional, for DR)
- Lifecycle policy: Standard → Glacier after 1 year

**Disaster Recovery Plan:**
1. Detect outage (automated monitoring)
2. Assess impact and root cause
3. Restore from latest backup
4. Verify data integrity
5. Communicate with users
6. Conduct post-mortem

**RTO: 4 hours | RPO: 24 hours**

---

## 14. Future Enhancements

### Phase 2 Features

1. **Building Matrix View**
   - Grid visualization (Rows = Floors, Cells = Apartments)
   - Color-coded status
   - Interactive drill-down
   - Estimated effort: 2 weeks

2. **Biometric Verification**
   - AWS Rekognition integration
   - Selfie vs ID photo comparison
   - Liveness detection
   - Estimated effort: 3 weeks

3. **WebSocket Real-time Updates**
   - Replace polling with WebSocket connections
   - Instant dashboard updates
   - Push notifications
   - Estimated effort: 2 weeks

4. **Offline Capability for Mobile App**
   - Service Worker implementation
   - Local storage for interactions
   - Sync when online
   - Estimated effort: 3 weeks

5. **Advanced Analytics & ML**
   - Predictive signature success rate
   - Sentiment analysis from interaction notes
   - Agent performance recommendations
   - Estimated effort: 4 weeks

6. **Mobile Native Apps**
   - React Native for iOS and Android
   - Enhanced camera and offline features
   - Estimated effort: 8 weeks

---

## 15. Appendices

### Appendix A: Glossary

- **TAMA 38**: Israeli urban renewal program for strengthening buildings
- **Pinui Binui**: Evacuation and reconstruction program
- **Required Majority (Rov Nidrash)**: Legal threshold of owner signatures (typically 67% or 75%)
- **Traffic Light**: Status visualization (Green, Yellow, Red)
- **Presigned URL**: Time-limited secure link to S3 object
- **ECS**: Amazon Elastic Container Service
- **Fargate**: Serverless container compute engine
- **RDS**: Amazon Relational Database Service

### Appendix B: Acronyms

- **API**: Application Programming Interface
- **AWS**: Amazon Web Services
- **CDN**: Content Delivery Network
- **CRM**: Customer Relationship Management
- **ECS**: Elastic Container Service
- **ERD**: Entity Relationship Diagram
- **JWT**: JSON Web Token
- **KPI**: Key Performance Indicator
- **MFA**: Multi-Factor Authentication
- **NFR**: Non-Functional Requirement
- **OCR**: Optical Character Recognition
- **PII**: Personally Identifiable Information
- **RBAC**: Role-Based Access Control
- **REST**: Representational State Transfer
- **RTL**: Right-to-Left (language direction)
- **SaaS**: Software as a Service
- **SES**: Simple Email Service
- **S3**: Simple Storage Service
- **SRD**: System Requirements Document
- **SSL/TLS**: Secure Sockets Layer / Transport Layer Security
- **UI/UX**: User Interface / User Experience
- **VPC**: Virtual Private Cloud

### Appendix C: References

- [Tama38_SRD.md](Tama38_SRD.md) - System Requirements Document
- [TAMA38_UI_Mockup.html](TAMA38_UI_Mockup.html) - English UI Mockup
- [Tama38_UI_Mockup_heb.html](Tama38_UI_Mockup_heb.html) - Hebrew UI Mockup
- [enhanced_db_docx_ready.md](enhanced_db_docx_ready.md) - Database Schema
- [TAMA38_Analysis_Issues.md](TAMA38_Analysis_Issues.md) - Issues and Contradictions Analysis

### Appendix D: Contact Information

For questions regarding this design document, contact:
- System Architect: [To be assigned]
- Project Manager: [To be assigned]
- Technical Lead: [To be assigned]

---

**END OF DESIGN DOCUMENT**

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Status:** Ready for Implementation

---

