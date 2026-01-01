# TAMA 38 Enhanced Database Description
## Commercial-Grade CRM & Project Management System

---

**Version:** 2.0 Enhanced  
**Date:** December 25, 2025  
**Target:** Production SaaS with Enterprise CRM, Project Management, and Analytics Capabilities  
**Database:** PostgreSQL on AWS RDS  

---

## Table of Contents

1. Core Entity Tables
2. CRM & Communication Tables
3. Project Management Tables
4. Financial & Incentive Tables
5. Stakeholder Management Tables
6. Knowledge Management Tables
7. Reporting & Analytics Tables
8. Enhanced Audit & Compliance Tables
9. Sample Queries & Reports

---

## CORE ENTITY TABLES

---

### 1. PROJECTS Table

**Purpose:** Top-level container for TAMA 38 urban renewal initiatives with configuration and legal requirements.

**Use Case:** Managing multiple concurrent urban renewal projects with different legal thresholds, timelines, and stakeholders.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| project_id | UUID | Primary key, unique identifier |
| project_name | VARCHAR(255) | Display name, must be unique |
| project_code | VARCHAR(50) | Short code for reports (e.g., "TAMA38_JLM_001") |
| project_type | ENUM | Type: TAMA38_1, TAMA38_2, PINUI_BINUI |
| location_city | VARCHAR(100) | Municipal location |
| location_address | TEXT | Full street address with postal code |
| location_coordinates | POINT | POSTGIS geometry for mapping |
| description | TEXT | Project background and goals |
| project_stage | ENUM | Current phase: PLANNING, ACTIVE, APPROVAL, COMPLETED, ARCHIVED |
| budget_total_ils | DECIMAL(15,2) | Total project budget in ILS |
| budget_consumed_ils | DECIMAL(15,2) | Amount spent to date |
| required_majority_percent | DECIMAL(5,2) | Legal threshold (typically 66.67 or 75%) |
| majority_calc_type | ENUM | Calculation: HEADCOUNT, AREA, WEIGHTED, CUSTOM |
| critical_threshold_percent | DECIMAL(5,2) | Red alert threshold (typically 50%) |
| launch_date | DATE | Project start date |
| estimated_completion_date | DATE | Expected project completion |
| actual_completion_date | DATE | Actual completion date (if completed) |
| business_sponsor | VARCHAR(255) | Main stakeholder/authority responsible |
| project_manager_id | UUID | FK to users (primary contact) |
| is_template | BOOLEAN | TRUE if template for future projects |
| custom_config | JSONB | Store custom settings per project (thresholds, workflows) |
| created_by | UUID | FK to users |
| created_at | TIMESTAMP | Creation timestamp |
| updated_by | UUID | FK to users |
| updated_at | TIMESTAMP | Last update timestamp |
| is_deleted | BOOLEAN | Soft delete flag |

**Key Indexes:**
- idx_projects_city ON location_city
- idx_projects_status ON project_stage
- idx_projects_created_by ON created_by

---

### 2. BUILDINGS Table

**Purpose:** Physical buildings within a project with structural info, progress metrics, and unit aggregates.

**Use Case:** Dashboard monitoring, multi-building comparison, progress tracking across renovation projects.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| building_id | UUID | Primary key |
| project_id | UUID | FK to projects |
| building_name | VARCHAR(255) | Display name (e.g., "Bldg A, 23 Herzl St") |
| building_code | VARCHAR(50) | Municipal cadastral reference |
| address | TEXT | Full building address |
| coordinates | POINT | POSTGIS point for mapping |
| floor_count | INTEGER | Total number of floors |
| total_units | INTEGER | Total units in building |
| total_area_sqm | DECIMAL(10,2) | Total built-up area |
| construction_year | SMALLINT | Year built (for age assessment) |
| structure_type | ENUM | CONCRETE, MASONRY, MIXED, OTHER |
| seismic_rating | ENUM | UNSAFE, REQUIRES_REINFORCEMENT, REINFORCED, MODERN |
| current_status | ENUM | INITIAL, NEGOTIATING, APPROVED, RENOVATION_PLANNING, RENOVATION_ONGOING, COMPLETED |
| signature_percentage | DECIMAL(5,2) | % of owners who signed (headcount) |
| signature_percentage_by_area | DECIMAL(5,2) | % by area (weighted by unit size) |
| signature_percentage_by_cost | DECIMAL(5,2) | % by estimated cost share (for incentive models) |
| traffic_light_status | ENUM | GREEN (≥majority), YELLOW (≥critical), RED (<critical), GRAY (no data) |
| units_signed | INTEGER | Count of units with ≥1 owner signature |
| units_partially_signed | INTEGER | Count of units with some (but not all) owners signed |
| units_not_signed | INTEGER | Count of units with zero signatures |
| units_refused | INTEGER | Count of units where owners refused |
| estimated_bonus_ils | DECIMAL(15,2) | Estimated government incentive if approved |
| actual_bonus_ils | DECIMAL(15,2) | Actual bonus received |
| assigned_agent_id | UUID | FK to users (primary agent) |
| secondary_agent_ids | UUID[] | Additional agents assigned |
| inspector_id | UUID | FK to users (building inspector/supervisor) |
| difficulty_score | INTEGER | 1-10 scale, updated by agents (1=easy, 10=very difficult) |
| notes | TEXT | General notes about the building |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| is_deleted | BOOLEAN | Soft delete flag |

**Key Indexes:**
- idx_buildings_project_id
- idx_buildings_status
- idx_buildings_signature_pct (for sorting by progress)
- idx_buildings_traffic_light

---

### 3. UNITS Table

**Purpose:** Individual apartments/properties with status, owner aggregates, and contract references.

**Use Case:** Unit-level progress tracking, owner management, signature workflow completion.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| unit_id | UUID | Primary key |
| building_id | UUID | FK to buildings |
| floor_number | SMALLINT | Floor number (0 for ground floor) |
| unit_number | VARCHAR(10) | Unit number on floor (e.g., "1", "1A", "101") |
| unit_code | VARCHAR(50) | Cadastral/municipal identifier |
| unit_full_identifier | VARCHAR(50) | Computed field: "Floor-Unit" for UI display |
| area_sqm | DECIMAL(8,2) | Unit area in square meters |
| room_count | SMALLINT | Number of rooms/bedrooms |
| estimated_value_ils | DECIMAL(12,2) | Estimated property value (for negotiations) |
| estimated_renovation_cost_ils | DECIMAL(12,2) | Estimated renovation cost |
| unit_status | ENUM | NOT_CONTACTED, NEGOTIATING, AGREED_TO_SIGN, SIGNED, FINALIZED, REFUSED, INACTIVE |
| total_owners | INTEGER | Count of current owners |
| owners_signed | INTEGER | Count of owners who signed (current_owner=TRUE and status=SIGNED) |
| signature_percentage | DECIMAL(5,2) | (owners_signed / total_owners) * 100 |
| is_co_owned | BOOLEAN | TRUE if multiple owners |
| is_rented | BOOLEAN | TRUE if unit is rented (impacts outreach strategy) |
| tenant_name | VARCHAR(255) | Name of tenant if rented (for contact attempt) |
| first_contact_date | DATE | Date of first agent contact |
| last_contact_date | DATE | Most recent contact date |
| last_activity_timestamp | TIMESTAMP | Last interaction (call, meeting, signature) |
| days_since_contact | INTEGER | Computed: CURRENT_DATE - last_contact_date (for aging reports) |
| primary_contract_id | UUID | FK to documents (main contract) |
| renovation_plan_document_id | UUID | FK to documents (if available) |
| complexity_notes | TEXT | Special circumstances (elderly, language barrier, disputes) |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| is_deleted | BOOLEAN | Soft delete flag |

---

### 4. OWNERS Table

**Purpose:** Legal entities with ownership stakes in units, contact info, and signature status.

**Use Case:** Owner management, outreach campaigns, signature workflows, elderly/vulnerable person support.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| owner_id | UUID | Primary key |
| unit_id | UUID | FK to units |
| full_name | VARCHAR(255) | Full name (encrypted PII) |
| id_number_encrypted | BYTEA | ID encrypted with AWS KMS |
| id_number_hash | BYTEA | Hash for lookups without decryption |
| id_type | ENUM | ISRAELI_ID, PASSPORT, BUSINESS_ID, OTHER |
| date_of_birth | DATE | Encrypted (for age-sensitive workflows) |
| phone_encrypted | BYTEA | Primary phone (encrypted) |
| phone_hash | BYTEA | Phone hash for lookups |
| phone_for_contact | VARCHAR(20) | Masked phone for display (e.g., "050-XXX-5678") |
| email | VARCHAR(255) | Email address |
| preferred_contact_method | ENUM | PHONE, WHATSAPP, EMAIL, IN_PERSON, NONE |
| preferred_language | ENUM | HEBREW, ARABIC, RUSSIAN, ENGLISH, OTHER |
| accessibility_needs | TEXT | Wheelchair, hearing aid, vision impaired, cognitive support, etc. |
| is_elderly | BOOLEAN | Age > 65 (for special handling) |
| is_vulnerable | BOOLEAN | Flagged by agent as needing extra support |
| ownership_share_percent | DECIMAL(5,2) | % ownership of unit |
| ownership_type | ENUM | SOLE_OWNER, CO_OWNER_JOINT, CO_OWNER_SEPARATE, TENANT_REPRESENTATIVE |
| is_primary_contact | BOOLEAN | TRUE if main contact for the unit |
| owner_status | ENUM | NOT_CONTACTED, PENDING_SIGNATURE, NEGOTIATING, AGREED_TO_SIGN, SIGNED, REFUSED, DECEASED, INCAPACITATED |
| refusal_reason | ENUM | NOT_INTERESTED, PRICE_OBJECTION, LEGAL_DISPUTE, NO_CONSENSUS_WITH_CO_OWNER, OTHER |
| refusal_reason_detail | TEXT | Additional explanation |
| signature_date | DATE | Date owner signed (if status=SIGNED) |
| signature_session_id | UUID | FK to document_signatures for tracking |
| assigned_agent_id | UUID | FK to users (primary agent for this owner) |
| is_current_owner | BOOLEAN | FALSE if ownership changed during project |
| ownership_start_date | DATE | When ownership began |
| ownership_end_date | DATE | When ownership ended (if transferred) |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| is_deleted | BOOLEAN | Soft delete flag |

---

### 5. INTERACTIONS_LOG Table

**Purpose:** Immutable audit trail of all agent-owner touches for workflow and performance tracking.

**Use Case:** Activity history, agent performance metrics, follow-up management, call logging compliance.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| log_id | UUID | Primary key |
| owner_id | UUID | FK to owners (who was contacted) |
| agent_id | UUID | FK to users (agent making contact) |
| interaction_type | ENUM | PHONE_CALL, IN_PERSON_MEETING, WHATSAPP, EMAIL, SMS, VIDEO_CALL, SCHEDULED_MEETING |
| interaction_date | DATE | Date of interaction |
| interaction_timestamp | TIMESTAMP | Exact time of interaction |
| duration_minutes | INTEGER | Call/meeting duration |
| outcome | ENUM | POSITIVE, NEUTRAL, NEGATIVE, NOT_AVAILABLE, DECLINED, AGREED_TO_MEET, AGREED_TO_SIGN |
| call_summary | TEXT | Agent notes/summary (mandatory) |
| key_objection | VARCHAR(255) | Main concern raised by owner (if negative) |
| next_action | VARCHAR(500) | Planned follow-up action |
| next_follow_up_date | DATE | Scheduled follow-up date |
| follow_up_type | ENUM | REMINDER_CALL, MEETING, SEND_DOCUMENT, FOLLOW_WITH_MANAGER |
| sentiment | ENUM | VERY_POSITIVE, POSITIVE, NEUTRAL, NEGATIVE, VERY_NEGATIVE |
| is_escalated | BOOLEAN | TRUE if escalated to manager |
| escalation_reason | TEXT | Why escalated |
| attempted | BOOLEAN | TRUE if owner was reached, FALSE if no answer |
| contact_method_used | ENUM | PHONE, WHATSAPP, EMAIL, IN_PERSON |
| source | ENUM | MOBILE_APP, WEB_APP, MANUAL_ENTRY, CRM_INTEGRATION |
| created_at | TIMESTAMP | Immutable creation time |

**Key Indexes:**
- idx_interactions_owner_id
- idx_interactions_agent_id
- idx_interactions_date (for aging reports)
- idx_interactions_outcome

---

## CRM & COMMUNICATION TABLES

---

### 6. COMMUNICATION_TEMPLATES Table

**Purpose:** Reusable email, SMS, WhatsApp templates for consistent messaging.

**Use Case:** Standardized outreach, localization, A/B testing messaging effectiveness.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| template_id | UUID | Primary key |
| project_id | UUID | FK to projects (if project-specific) |
| template_name | VARCHAR(255) | Display name (e.g., "Initial Contact - Hebrew") |
| template_type | ENUM | EMAIL, SMS, WHATSAPP, IN_APP_NOTIFICATION |
| language | ENUM | HEBREW, ARABIC, RUSSIAN, ENGLISH |
| subject_line | VARCHAR(255) | Email subject (if applicable) |
| body_text | TEXT | Template body with {{variables}} |
| variables_required | JSONB | List of required variables: {name, phone, building, unit, etc.} |
| sender_name | VARCHAR(100) | Display name (e.g., "Agent Roni") |
| sender_email | VARCHAR(255) | From address |
| tone | ENUM | FORMAL, FRIENDLY, URGENT, INFORMATIVE |
| priority_level | ENUM | LOW, MEDIUM, HIGH |
| is_active | BOOLEAN | TRUE if currently in use |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| version | INTEGER | Version number for tracking changes |

---

### 7. COMMUNICATION_LOG Table

**Purpose:** Complete audit of all sent communications (emails, SMS, WhatsApp, in-app).

**Use Case:** Compliance tracking, delivery verification, audit trail, customer communication history.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| comm_log_id | UUID | Primary key |
| owner_id | UUID | FK to owners (recipient) |
| agent_id | UUID | FK to users (sender) |
| template_id | UUID | FK to communication_templates (if from template) |
| comm_type | ENUM | EMAIL, SMS, WHATSAPP, PUSH_NOTIFICATION, IN_APP_MESSAGE |
| recipient_address | VARCHAR(255) | Email, phone, or app ID |
| subject | VARCHAR(255) | Message subject |
| message_body | TEXT | Actual message sent (rendered template) |
| sent_at | TIMESTAMP | When sent |
| delivery_status | ENUM | PENDING, SENT, DELIVERED, FAILED, BOUNCED, UNSUBSCRIBED |
| delivery_error_message | TEXT | If failed, why |
| read_status | ENUM | NOT_SENT, SENT, DELIVERED, READ, CLICKED (for email) |
| read_at | TIMESTAMP | When opened/clicked |
| open_count | INTEGER | How many times opened |
| click_count | INTEGER | How many links clicked |
| response_status | ENUM | AWAITING_RESPONSE, RESPONDED, NO_RESPONSE |
| response_received_at | TIMESTAMP | If owner replied |
| external_message_id | VARCHAR(255) | ID from email provider (for tracking) |
| provider | ENUM | AWS_SES, TWILIO, WHATSAPP_API, INTERNAL |
| is_automated | BOOLEAN | TRUE if system-triggered (alert, reminder) |
| created_at | TIMESTAMP | Creation timestamp |

---

### 8. OWNER_CONTACT_PREFERENCES Table

**Purpose:** Manage owner communication opt-ins, preferences, and do-not-contact requests.

**Use Case:** GDPR compliance, respecting owner wishes, contact preference management.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| preference_id | UUID | Primary key |
| owner_id | UUID | FK to owners |
| email_opt_in | BOOLEAN | Willing to receive emails |
| sms_opt_in | BOOLEAN | Willing to receive SMS |
| whatsapp_opt_in | BOOLEAN | Willing to receive WhatsApp |
| phone_call_opt_in | BOOLEAN | Willing to receive calls |
| marketing_opt_in | BOOLEAN | Willing to receive promotional messages |
| do_not_contact_until | DATE | Temporary DNC until this date |
| do_not_contact_reason | TEXT | Why DNC (e.g., "Already decided", "Will call later") |
| communication_frequency | ENUM | DAILY, WEEKLY, BI_WEEKLY, MONTHLY, AS_NEEDED |
| preferred_contact_time | VARCHAR(50) | Time range (e.g., "9:00-17:00") |
| timezone | VARCHAR(50) | Timezone for scheduling |
| last_preference_update | TIMESTAMP | When owner last updated preferences |
| updated_by_user_id | UUID | User who made the update |

---

### 9. CUSTOMER_SENTIMENT_TRACKING Table

**Purpose:** Track owner sentiment progression over project lifecycle for engagement strategy.

**Use Case:** Identify at-risk owners, detect opinion shifts, tailor messaging based on sentiment.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| sentiment_id | UUID | Primary key |
| owner_id | UUID | FK to owners |
| recorded_date | DATE | Date of sentiment assessment |
| recorded_by_agent_id | UUID | FK to users (agent assessing) |
| sentiment_score | INTEGER | 1-10 scale (1=very negative, 10=very positive) |
| sentiment_category | ENUM | VERY_POSITIVE, POSITIVE, NEUTRAL, NEGATIVE, VERY_NEGATIVE |
| key_drivers | JSONB | {"price": 7, "renovation_scope": 5, "neighbor_support": 8} |
| concerns | TEXT | Owner's main concerns or questions |
| previous_sentiment_score | INTEGER | Score from last assessment (for trending) |
| trending | ENUM | IMPROVING, STABLE, DECLINING |
| action_items | TEXT | What team should do next to improve sentiment |
| created_at | TIMESTAMP | Creation timestamp |

---

## PROJECT MANAGEMENT TABLES

---

### 10. PROJECT_MILESTONES Table

**Purpose:** Key project milestones and deadlines for overall project management.

**Use Case:** Project timeline tracking, governance reporting, deadline alerts.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| milestone_id | UUID | Primary key |
| project_id | UUID | FK to projects |
| milestone_name | VARCHAR(255) | Display name (e.g., "Reach 60% Signatures") |
| milestone_type | ENUM | SIGNATURE_THRESHOLD, GOVERNMENT_APPROVAL, BUILDING_APPROVAL, RENOVATION_START, RENOVATION_COMPLETE |
| target_date | DATE | Expected completion date |
| actual_date | DATE | Actual completion date (if completed) |
| status | ENUM | NOT_STARTED, IN_PROGRESS, AT_RISK, COMPLETED, FAILED, SKIPPED |
| target_value | DECIMAL(10,2) | Target metric value (e.g., 60.00 for 60% signatures) |
| actual_value | DECIMAL(10,2) | Actual value achieved |
| description | TEXT | Details about what success looks like |
| responsible_party | VARCHAR(255) | Who owns this milestone |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

---

### 11. TASKS Table

**Purpose:** Agent action items, follow-ups, and to-do management integrated with project workflow.

**Use Case:** Task assignment, reminder management, workload distribution, bottleneck identification.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| task_id | UUID | Primary key |
| building_id | UUID | FK to buildings (context) |
| owner_id | UUID | FK to owners (if owner-specific task) |
| task_type | ENUM | FOLLOW_UP_CALL, SCHEDULE_MEETING, SEND_DOCUMENT, MANAGER_REVIEW, SITE_VISIT, HANDLE_OBJECTION |
| title | VARCHAR(255) | Task title |
| description | TEXT | Detailed task description |
| assigned_to_agent_id | UUID | FK to users (assigned agent) |
| assigned_by_user_id | UUID | FK to users (who created the task) |
| due_date | DATE | When task is due |
| due_time | TIME | Specific time if applicable |
| status | ENUM | NOT_STARTED, IN_PROGRESS, BLOCKED, COMPLETED, OVERDUE, CANCELLED |
| priority | ENUM | LOW, MEDIUM, HIGH, CRITICAL |
| estimated_hours | DECIMAL(4,2) | Time estimate |
| actual_hours | DECIMAL(4,2) | Time spent |
| dependencies | UUID[] | IDs of tasks that must be completed first |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| completed_at | TIMESTAMP | When marked complete |
| notes | TEXT | Agent notes during execution |

---

### 12. PROJECT_EVENTS Table

**Purpose:** Timeline events for project audit trail and status changes.

**Use Case:** Project history, governance audit, key decision tracking.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| event_id | UUID | Primary key |
| project_id | UUID | FK to projects |
| event_type | ENUM | STATUS_CHANGE, MILESTONE_REACHED, ALERT_TRIGGERED, MANAGER_APPROVAL, OWNER_REFUSED, MEETING_HELD, DOCUMENT_RECEIVED |
| event_date | DATE | When event occurred |
| event_timestamp | TIMESTAMP | Exact timestamp |
| title | VARCHAR(255) | Event description |
| description | TEXT | Detailed description |
| related_building_id | UUID | FK to buildings (if applicable) |
| related_owner_id | UUID | FK to owners (if applicable) |
| triggered_by_user_id | UUID | FK to users (who caused the event) |
| event_data | JSONB | Additional context (e.g., {"old_status": "PLANNING", "new_status": "ACTIVE"}) |
| is_public | BOOLEAN | TRUE if visible to all stakeholders |
| created_at | TIMESTAMP | Creation timestamp |

---

## FINANCIAL & INCENTIVE TABLES

---

### 13. INCENTIVE_PROGRAMS Table

**Purpose:** Government incentives, rebates, and financial programs associated with projects.

**Use Case:** Budget planning, owner motivation, financial modeling.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| program_id | UUID | Primary key |
| project_id | UUID | FK to projects |
| program_name | VARCHAR(255) | Name of incentive (e.g., "Tax Exemption - 5 Years") |
| program_type | ENUM | TAX_EXEMPTION, CASH_INCENTIVE, SUBSIDY, LOAN_GUARANTEE, BUILDING_INSURANCE |
| incentive_amount_ils | DECIMAL(15,2) | Maximum incentive per unit (or total) |
| eligibility_criteria | JSONB | Who qualifies: {"age": "65+", "income": "<X"} |
| application_deadline | DATE | When application closes |
| is_active | BOOLEAN | TRUE if currently available |
| description | TEXT | Program details |
| created_at | TIMESTAMP | Creation timestamp |

---

### 14. OWNER_INCENTIVE_CLAIMS Table

**Purpose:** Track owner incentive applications and claims.

**Use Case:** Incentive distribution, owner benefit tracking, financial settlement.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| claim_id | UUID | Primary key |
| owner_id | UUID | FK to owners |
| program_id | UUID | FK to incentive_programs |
| claim_date | DATE | When claim filed |
| claimed_amount_ils | DECIMAL(12,2) | Amount claimed |
| approved_amount_ils | DECIMAL(12,2) | Amount approved |
| claim_status | ENUM | SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, PAID, APPEALED |
| eligibility_verified | BOOLEAN | Verified against program criteria |
| approval_date | DATE | Date approved |
| payment_date | DATE | Date payment made |
| payment_method | ENUM | BANK_TRANSFER, CHECK, CASH |
| notes | TEXT | Additional notes |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

---

### 15. BUILDING_BUDGET Table

**Purpose:** Financial tracking for building renovation budgets.

**Use Case:** Cost control, budget forecasting, financial reporting.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| budget_id | UUID | Primary key |
| building_id | UUID | FK to buildings |
| estimated_renovation_cost_ils | DECIMAL(15,2) | Total estimated cost |
| contingency_percent | DECIMAL(5,2) | Contingency buffer (typically 10-15%) |
| contingency_amount_ils | DECIMAL(15,2) | Calculated contingency |
| government_subsidy_ils | DECIMAL(15,2) | Expected government contribution |
| owner_contribution_ils | DECIMAL(15,2) | Expected from owners |
| contractor_cost_ils | DECIMAL(15,2) | Contractor bid/estimate |
| actual_spent_ils | DECIMAL(15,2) | Actual amount spent to date |
| encumbered_ils | DECIMAL(15,2) | Committed but not yet paid |
| status | ENUM | PLANNING, APPROVED, IN_PROGRESS, COMPLETE, OVER_BUDGET, UNDER_BUDGET |
| last_updated_by_user_id | UUID | FK to users |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

---

## STAKEHOLDER MANAGEMENT TABLES

---

### 16. STAKEHOLDERS Table

**Purpose:** Non-owner stakeholders involved in project (contractors, inspectors, authorities, service providers).

**Use Case:** Multi-party coordination, accountability tracking, contact management.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| stakeholder_id | UUID | Primary key |
| project_id | UUID | FK to projects |
| stakeholder_type | ENUM | CONTRACTOR, ARCHITECT, ENGINEER, GOVERNMENT_INSPECTOR, MUNICIPALITY, SERVICE_PROVIDER, LEGAL_ADVISOR, REAL_ESTATE_APPRAISER |
| organization_name | VARCHAR(255) | Company/entity name |
| contact_person_name | VARCHAR(255) | Primary contact person |
| email | VARCHAR(255) | Contact email |
| phone | VARCHAR(20) | Contact phone |
| role_description | TEXT | What they do for the project |
| assigned_buildings | UUID[] | Which buildings they work with |
| is_active | BOOLEAN | TRUE if currently involved |
| contract_start_date | DATE | When engagement started |
| contract_end_date | DATE | When engagement ends |
| contract_value_ils | DECIMAL(12,2) | Contract amount |
| performance_rating | INTEGER | 1-5 stars (after engagement complete) |
| feedback_notes | TEXT | Performance feedback |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

---

### 17. STAKEHOLDER_COMMUNICATIONS Table

**Purpose:** Separate channel for non-owner stakeholder communications.

**Use Case:** Contractor coordination, authority follow-ups, service provider management.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| comm_id | UUID | Primary key |
| stakeholder_id | UUID | FK to stakeholders |
| building_id | UUID | FK to buildings |
| comm_date | DATE | Communication date |
| comm_type | ENUM | EMAIL, PHONE, MEETING, SITE_INSPECTION, DOCUMENT_SUBMISSION |
| title | VARCHAR(255) | Subject |
| details | TEXT | What was communicated |
| outcome | ENUM | ACTION_REQUIRED, NOTED, APPROVED, REJECTED, PENDING_RESPONSE |
| next_action | VARCHAR(500) | Follow-up required |
| next_action_date | DATE | When to follow up |
| communication_by_user_id | UUID | FK to users |
| created_at | TIMESTAMP | Creation timestamp |

---

## KNOWLEDGE MANAGEMENT TABLES

---

### 18. AGENT_KNOWLEDGE_BASE Table

**Purpose:** Centralized library of best practices, objection handling, FAQs for agents.

**Use Case:** Agent training, objection response consistency, knowledge sharing, onboarding.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| kb_id | UUID | Primary key |
| category | ENUM | OBJECTION_HANDLING, FAQ, BEST_PRACTICE, LEGAL_INFO, TECHNICAL_ISSUE, ELDERLY_CARE |
| title | VARCHAR(255) | Article title |
| content | TEXT | Article body (markdown) |
| tags | TEXT[] | Searchable tags |
| effectiveness_score | INTEGER | 1-5: How effective is this article (rated by agents) |
| updated_date | DATE | Last update |
| created_by_user_id | UUID | FK to users (author/expert) |
| is_published | BOOLEAN | TRUE if available to agents |
| created_at | TIMESTAMP | Creation timestamp |

---

### 19. OBJECTION_HANDLING_GUIDE Table

**Purpose:** Specific handling instructions for common owner objections.

**Use Case:** Agent training on objection handling, scripting, success rate improvement.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| guide_id | UUID | Primary key |
| objection_type | ENUM | PRICE_TOO_HIGH, DISAGREE_WITH_SCOPE, LEGAL_DISPUTE, NO_CONSENSUS_WITH_FAMILY, ELDERLY_HESITANT, LANGUAGE_BARRIER, OTHER |
| objection_phrase | VARCHAR(500) | Example owner quote |
| recommended_response | TEXT | What agent should say/do |
| do_dont_notes | JSONB | {"do": ["Listen fully", "Validate concern"], "dont": ["Be defensive"]} |
| escalation_criteria | TEXT | When to escalate to manager |
| success_rate | DECIMAL(3,2) | % of times this approach succeeds (0-1) |
| language | ENUM | HEBREW, ARABIC, RUSSIAN, ENGLISH |
| created_by_user_id | UUID | FK to users (expert) |
| created_at | TIMESTAMP | Creation timestamp |

---

### 20. BUILDING_TEMPLATES Table

**Purpose:** Reusable building configuration templates for new projects.

**Use Case:** Faster project setup, consistency across similar projects.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| template_id | UUID | Primary key |
| template_name | VARCHAR(255) | Name (e.g., "Standard Urban 6-Floor Building") |
| structure_type | ENUM | CONCRETE, MASONRY, MIXED |
| seismic_rating | ENUM | UNSAFE, REQUIRES_REINFORCEMENT, REINFORCED, MODERN |
| typical_unit_count | INTEGER | Expected units |
| typical_floor_count | INTEGER | Expected floors |
| typical_renovation_scope | TEXT | Standard renovation package |
| typical_timeline_months | INTEGER | Expected duration |
| created_by_user_id | UUID | FK to users |
| created_at | TIMESTAMP | Creation timestamp |

---

## REPORTING & ANALYTICS TABLES

---

### 21. ANALYTICS_SNAPSHOT Table

**Purpose:** Pre-computed analytics snapshots for fast report generation.

**Use Case:** Dashboard caching, trend analysis, historical comparison.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| snapshot_id | UUID | Primary key |
| snapshot_date | DATE | Date of snapshot |
| project_id | UUID | FK to projects |
| building_id | UUID | FK to buildings (if building-level) |
| metric_name | VARCHAR(255) | Name (e.g., "signature_percentage", "daily_interaction_count") |
| metric_value | DECIMAL(15,4) | Value |
| previous_value | DECIMAL(15,4) | Value from previous snapshot (for trend) |
| trend | ENUM | UP, DOWN, STABLE |
| dimension_1 | VARCHAR(100) | Extra grouping (e.g., "AGENT_ID", "OWNER_STATUS") |
| dimension_1_value | VARCHAR(255) | Value of dimension |
| created_at | TIMESTAMP | Creation timestamp |

Note: Populated daily via scheduled ETL job.

---

### 22. AGENT_PERFORMANCE_METRICS Table

**Purpose:** KPI tracking for agent performance management.

**Use Case:** Performance evaluation, incentive calculation, training identification.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| metric_id | UUID | Primary key |
| agent_id | UUID | FK to users |
| period_start_date | DATE | Start of period (usually month) |
| period_end_date | DATE | End of period |
| units_assigned | INTEGER | Units assigned to this agent |
| units_signed | INTEGER | Units with ≥1 owner signature |
| signatures_count | INTEGER | Total signatures obtained |
| interactions_count | INTEGER | Total interactions logged |
| avg_interaction_duration_minutes | DECIMAL(6,2) | Average call/meeting length |
| avg_sentiment_score | DECIMAL(3,2) | Average sentiment from interactions |
| follow_up_compliance_percent | DECIMAL(5,2) | % of interactions with scheduled follow-ups |
| signature_rate_percent | DECIMAL(5,2) | (signatures_count / interactions_count) * 100 |
| refusal_count | INTEGER | How many owners refused |
| escalation_count | INTEGER | How many cases escalated |
| created_at | TIMESTAMP | Creation timestamp |

---

### 23. BUILDING_PERFORMANCE_DASHBOARD Table

**Purpose:** Pre-aggregated view of building metrics for dashboard fast rendering.

**Use Case:** Real-time dashboard, manager oversight, trend analysis.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| dashboard_id | UUID | Primary key |
| building_id | UUID | FK to buildings |
| last_updated_at | TIMESTAMP | When metrics were calculated |
| total_units | INTEGER | Total units |
| total_owners | INTEGER | Total owners |
| units_signed_count | INTEGER | Units with ≥1 owner signature |
| units_signed_percent | DECIMAL(5,2) | % of units |
| signature_percentage_overall | DECIMAL(5,2) | Owner count basis |
| signature_percentage_by_area | DECIMAL(5,2) | Area-weighted basis |
| traffic_light | ENUM | GREEN, YELLOW, RED |
| days_elapsed | INTEGER | Days since first contact |
| estimated_days_to_completion | INTEGER | Forecast |
| active_agents_count | INTEGER | Agents actively working this building |
| interactions_last_7_days | INTEGER | Recent activity |
| pending_approvals_count | INTEGER | Signatures awaiting manager review |
| refusals_count | INTEGER | Owners who refused |
| created_at | TIMESTAMP | Creation timestamp |

---

## ENHANCED AUDIT & COMPLIANCE TABLES

---

### 24. AUDIT_LOG_EXTENDED Table

**Purpose:** Comprehensive audit trail for compliance, including data changes and user actions.

**Use Case:** Regulatory compliance, forensics, change history.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| audit_id | UUID | Primary key |
| table_name | VARCHAR(100) | Which table was modified |
| record_id | UUID | Which record |
| action | ENUM | INSERT, UPDATE, DELETE, MANUAL_OVERRIDE |
| old_values | JSONB | Before state |
| new_values | JSONB | After state |
| changed_by_user_id | UUID | FK to users (who made change) |
| changed_at | TIMESTAMP | When |
| reason_text | TEXT | Why (mandatory for MANUAL_OVERRIDE) |
| ip_address | INET | Source IP |
| user_agent | VARCHAR(500) | Browser/app info |
| change_impact | TEXT | Business impact of change |
| created_at | TIMESTAMP | Creation timestamp |

---

### 25. COMPLIANCE_CHECKLIST Table

**Purpose:** Track regulatory and operational compliance tasks per building/project.

**Use Case:** Governance, audit readiness, requirement management.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| checklist_id | UUID | Primary key |
| project_id | UUID | FK to projects |
| building_id | UUID | FK to buildings (optional) |
| checklist_type | ENUM | GDPR, DATA_RETENTION, SIGNATURE_VERIFICATION, MANAGER_APPROVAL, DOCUMENT_ARCHIVE |
| requirement_name | VARCHAR(255) | Description |
| is_required | BOOLEAN | TRUE if mandatory |
| status | ENUM | NOT_STARTED, IN_PROGRESS, COMPLETED, NOT_APPLICABLE |
| completion_date | DATE | When completed |
| completed_by_user_id | UUID | FK to users |
| evidence_document_ids | UUID[] | References to documents proving completion |
| notes | TEXT | Additional notes |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

---

## SAMPLE QUERIES & REPORTS

---

### Report 1: Building Progress Dashboard

**Purpose:** High-level view of all buildings in a project with key metrics.

**Query Type:** Used for primary dashboard, updates every 5 minutes.

**Sample SQL Query:**

```
SELECT 
    b.building_id,
    b.building_name,
    b.address,
    b.total_units,
    b.total_owners,
    COUNT(DISTINCT CASE WHEN o.owner_status IN ('SIGNED') 
          THEN o.owner_id END) AS owners_signed,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.owner_status = 'SIGNED' 
          THEN o.owner_id END) / NULLIF(COUNT(DISTINCT o.owner_id), 0), 2) 
          AS signature_percentage,
    ROUND(b.signature_percentage_by_area, 2) AS signature_by_area_percent,
    p.required_majority_percent,
    CASE 
        WHEN b.signature_percentage >= p.required_majority_percent THEN 'GREEN'
        WHEN b.signature_percentage >= p.critical_threshold_percent THEN 'YELLOW'
        ELSE 'RED'
    END AS traffic_light,
    COUNT(DISTINCT u.unit_id) AS total_units_count,
    COUNT(DISTINCT CASE WHEN u.unit_status = 'FINALIZED' 
          THEN u.unit_id END) AS units_signed,
    MAX(il.interaction_date) AS last_activity_date,
    u_a.full_name AS assigned_agent,
    COUNT(DISTINCT t.task_id) AS pending_tasks
FROM buildings b
JOIN projects p ON b.project_id = p.project_id
JOIN units u ON b.building_id = u.building_id
LEFT JOIN owners o ON u.unit_id = o.unit_id 
    AND o.is_current_owner = TRUE
LEFT JOIN interaction_logs il ON o.owner_id = il.owner_id
LEFT JOIN users u_a ON b.assigned_agent_id = u_a.user_id
LEFT JOIN tasks t ON (t.building_id = b.building_id 
    AND t.status IN ('NOT_STARTED', 'IN_PROGRESS'))
WHERE b.project_id = $1 AND b.is_deleted = FALSE
GROUP BY b.building_id, b.building_name, b.address, b.total_units, 
         b.total_owners, b.signature_percentage, 
         b.signature_percentage_by_area, p.required_majority_percent,
         p.critical_threshold_percent, u_a.full_name
ORDER BY b.signature_percentage ASC;
```

**Key Metrics Returned:**
- Building identifier and address
- Total units and owners
- Owners signed count
- Signature percentage (headcount and area-weighted)
- Traffic light status (RED/YELLOW/GREEN)
- Total units and units signed count
- Last activity date
- Assigned agent name
- Pending tasks count

---

### Report 2: Agent Performance Summary

**Purpose:** Monthly KPI review for agents, used in performance evaluations.

**Query Type:** Generated monthly, sent to managers.

**Sample SQL Query:**

```
WITH agent_stats AS (
    SELECT 
        u.user_id,
        u.full_name,
        DATE_TRUNC('month', CURRENT_DATE)::DATE 
            AS period_month,
        COUNT(DISTINCT CASE WHEN il.interaction_type 
              IN ('PHONE_CALL', 'IN_PERSON_MEETING') 
              THEN il.log_id END) AS total_interactions,
        COUNT(DISTINCT CASE WHEN il.outcome 
              IN ('AGREED_TO_SIGN', 'AGREED_TO_MEET') 
              THEN il.log_id END) AS positive_outcomes,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN il.outcome 
              IN ('AGREED_TO_SIGN', 'AGREED_TO_MEET') 
              THEN il.log_id END) / NULLIF(COUNT(DISTINCT il.log_id), 0), 2) 
              AS success_rate_percent,
        COUNT(DISTINCT CASE WHEN il.outcome = 'NOT_INTERESTED' 
              THEN il.log_id END) AS refusals,
        AVG(CAST(il.duration_minutes AS DECIMAL)) 
            AS avg_call_duration_minutes,
        AVG(CAST(CASE WHEN il.sentiment = 'VERY_POSITIVE' THEN 5 
                       WHEN il.sentiment = 'POSITIVE' THEN 4
                       WHEN il.sentiment = 'NEUTRAL' THEN 3
                       WHEN il.sentiment = 'NEGATIVE' THEN 2
                       WHEN il.sentiment = 'VERY_NEGATIVE' THEN 1 
                       ELSE 3 END AS DECIMAL)) 
            AS avg_sentiment_score,
        COUNT(DISTINCT u_i.owner_id) AS unique_owners_contacted,
        COUNT(DISTINCT ds.signature_id) AS signatures_obtained
    FROM users u
    LEFT JOIN interaction_logs il ON u.user_id = il.agent_id 
        AND DATE_TRUNC('month', il.interaction_date) 
            = DATE_TRUNC('month', CURRENT_DATE)
    LEFT JOIN owners u_i ON il.owner_id = u_i.owner_id
    LEFT JOIN document_signatures ds ON u_i.owner_id = ds.owner_id 
        AND ds.signature_completed_at 
            >= DATE_TRUNC('month', CURRENT_DATE)
    WHERE u.role = 'AGENT' AND u.is_active = TRUE
    GROUP BY u.user_id, u.full_name
)
SELECT 
    user_id,
    full_name,
    period_month,
    total_interactions,
    positive_outcomes,
    success_rate_percent,
    refusals,
    ROUND(avg_call_duration_minutes, 1) 
        AS avg_call_duration_minutes,
    ROUND(avg_sentiment_score, 2) AS avg_sentiment_score,
    unique_owners_contacted,
    signatures_obtained
FROM agent_stats
ORDER BY success_rate_percent DESC;
```

**Key Metrics Returned:**
- Total interactions logged
- Positive outcomes count
- Success rate percentage
- Refusal count
- Average call/meeting duration
- Average sentiment score
- Unique owners contacted
- Total signatures obtained

---

## Summary

### New Capabilities Added

CRM Features
- Customer sentiment tracking with 1-10 scoring and trending
- Communication preferences management (GDPR compliant)
- Contact method preferences and languages
- Objection analysis and handling guides

Communication Management
- Multi-channel unified logging (Email, SMS, WhatsApp, Push)
- Communication templates for standardization
- Delivery and read status tracking
- Automated communication triggers

Project Management
- Task assignment and tracking with dependencies
- Project milestones with target dates and success metrics
- Project events audit trail
- Timeline tracking and forecasting

Financial Tracking
- Budget management with contingency calculation
- Government incentive programs and claims
- Cost control and variance analysis
- Owner contribution tracking

Stakeholder Management
- Contractor and service provider coordination
- Authority and inspector communication tracking
- Performance rating and feedback
- Contract term management

Knowledge Management
- Agent knowledge base and FAQs
- Objection handling guides with success rates
- Building templates for consistent setup
- Multi-language support

Analytics & Reporting
- Pre-computed analytics snapshots
- Agent performance KPI metrics
- Building performance dashboard
- Real-time trend analysis

Compliance & Audit
- Extended audit trail with impact analysis
- Compliance checklists per building/project
- GDPR and regulatory tracking
- 7-year document retention management

---

**Ready for Implementation**

This enhanced database specification provides production-grade functionality incorporating best practices from leading CRM, project management, and analytics platforms (Salesforce, HubSpot, Monday.com). All 25 tables are fully documented with field descriptions, purposes, and use cases.

Recommended next steps:
1. Generate DDL scripts from table specifications
2. Create appropriate indexes for performance
3. Set up row-level security policies
4. Implement triggers for audit logging
5. Create materialized views for reports

