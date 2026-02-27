# Lumber HRIS — Master Development Plan

## Document Info
- **Created**: 2026-02-27T04:00Z
- **Author**: Opus (AI) — supervised by Franco Schiavone
- **Status**: ACTIVE
- **Version**: 1.0

---

## 1. Executive Summary

Build a fully working, dockerized HRIS (Human Resource Information System) for Lumber, a construction workforce management platform. The application will cover 6 core modules: Dashboard, Employee Management, Org Chart, Performance Management, LMS, and Analytics. It will be a production-ready demo application with real authentication, role-based access, realistic seed data (300+ employees of a construction company), and Lumber branding throughout.

The deliverable is:
1. A fully functional web application (frontend + backend)
2. Docker deployment configuration
3. Pre-loaded demo users for testing
4. A video demo in English showcasing all features

---

## 2. Environment Constraints & Architecture Decisions

### 2.1 Constraints Discovered During Permissions Audit

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| Root filesystem is READ-ONLY | Cannot pip install to system | Use Node.js full-stack (npm installs to project dir) |
| /tmp is noexec | Cannot run compiled Python extensions from /tmp | SQLite DB stored in workspace, not /tmp |
| docker-compose not available | Cannot orchestrate multi-container deploys locally | Provide docker-compose.yml for host deployment; use shell script + single containers for dev |
| DinD networking: sibling containers can't reach each other | Cannot connect app → PostgreSQL in Docker | Use SQLite for development; PostgreSQL in Docker config for production |
| Sub-agents have NO exec access | Cannot delegate coding/build tasks to GLM-5 | All development done by Opus directly; sub-agents used for code generation/planning only |
| 258GB disk, 7.8GB RAM, 10 CPUs | Sufficient resources | No constraints |
| Node.js 22, npm 10.9.4 | Modern runtime | Full Next.js 14 support |
| Docker 20.10 available | Can build and run images | Dockerfiles + compose provided |

### 2.2 Architecture Decision: Full-Stack Next.js

Given the constraints above, the optimal architecture is:

```
┌─────────────────────────────────────────────┐
│              Next.js 14 (App Router)         │
│                                              │
│  ┌──────────────┐  ┌─────────────────────┐  │
│  │   Frontend    │  │   API Routes        │  │
│  │   React/TSX   │  │   /api/*            │  │
│  │   Tailwind    │  │   CRUD, Auth,       │  │
│  │   shadcn/ui   │  │   Business Logic    │  │
│  │   D3.js       │  │                     │  │
│  │   Chart.js    │  │                     │  │
│  └──────────────┘  └─────────┬───────────┘  │
│                              │               │
│                    ┌─────────▼───────────┐   │
│                    │    Prisma ORM       │   │
│                    │    (Type-safe)      │   │
│                    └─────────┬───────────┘   │
│                              │               │
└──────────────────────────────┼───────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   SQLite (dev)      │
                    │   PostgreSQL (prod) │
                    └─────────────────────┘
```

**Why this architecture:**
- **Single codebase**: Simpler to develop, test, and deploy
- **No networking issues**: Frontend and API are the same process
- **Prisma**: Supports both SQLite (dev) and PostgreSQL (prod) with zero code changes
- **Type-safe end-to-end**: TypeScript from UI to database
- **Battle-tested**: This is what Vercel, Linear, Cal.com, and most modern SaaS use
- **Easy Docker**: Single Dockerfile, one image to deploy
- **Matches Lumber's likely stack**: Construction SaaS companies use modern JS frameworks

### 2.3 Technology Stack (Final)

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Framework | Next.js | 14.x | Full-stack React framework |
| Language | TypeScript | 5.x | Type safety |
| UI Library | shadcn/ui | latest | Pre-built accessible components |
| CSS | Tailwind CSS | 3.x | Utility-first styling |
| ORM | Prisma | 5.x | Type-safe database access |
| Database (dev) | SQLite | 3.x | Zero-config development |
| Database (prod) | PostgreSQL | 16 | Production deployment |
| Authentication | NextAuth.js | 4.x | JWT-based auth with roles |
| Org Chart | D3.js | 7.x | Interactive org visualization |
| Charts | Chart.js + react-chartjs-2 | 4.x | Analytics dashboards |
| Icons | Lucide React | latest | Consistent icon set |
| Date Utils | date-fns | 3.x | Date formatting |
| Containerization | Docker + Docker Compose | - | Deployment |

---

## 3. Module Specifications

Each module below maps directly to the Lumber HRIS PRD requirements. References to specific requirement IDs from the TSG HRIS Requirements spreadsheet are included.

### 3.1 Module: Authentication & Authorization

**Source**: PRD Section 8.1 (Field Worker UX Constraint), Org Chart PRD (RBAC)

#### 3.1.1 Demo Users (Pre-loaded)

| Username | Password | Role | Persona | What they can see |
|----------|----------|------|---------|-------------------|
| `admin@lumber.com` | `LumberAdmin2026!` | Admin | IT Ian | Everything, all modules |
| `hr@lumber.com` | `LumberHR2026!` | HR Manager | HR Helen | Full HR access, all employees |
| `pm@lumber.com` | `LumberPM2026!` | Project Manager | Project Paula | Org chart, performance (own projects), analytics |
| `foreman@lumber.com` | `LumberForeman2026!` | Manager/Foreman | Foreman Francisco | Crew management, performance (own crew) |
| `worker@lumber.com` | `LumberWorker2026!` | Employee | Tradesman Tony | Own profile, own reviews, own training |

#### 3.1.2 Features

- Login page with Lumber branding
- JWT-based session management
- Role-based route protection (middleware)
- Role-based UI element visibility (buttons, menus, actions)
- Session persistence (30-day tokens)
- Logout with redirect
- "Access Denied" page for unauthorized routes

#### 3.1.3 Role Permission Matrix

| Feature | Admin | HR Manager | Project Manager | Foreman | Employee |
|---------|-------|------------|-----------------|---------|----------|
| View Dashboard | ✅ Full | ✅ Full | ✅ Limited | ✅ Limited | ✅ Own |
| Manage Employees | ✅ CRUD | ✅ CRUD | ❌ View only | ❌ View crew | ❌ Own profile |
| Org Chart | ✅ Full | ✅ Full | ✅ Project view | ✅ Crew view | ✅ Read-only |
| Performance Reviews | ✅ All | ✅ All | ✅ Own team | ✅ Own crew | ✅ Own |
| Create Reviews | ✅ | ✅ | ✅ | ✅ | ❌ Self-review only |
| LMS Admin | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Training | ✅ All | ✅ All | ✅ Team | ✅ Crew | ✅ Own |
| Analytics | ✅ Full | ✅ Full | ✅ Limited | ❌ | ❌ |
| System Settings | ✅ | ❌ | ❌ | ❌ | ❌ |

---

### 3.2 Module: Dashboard

**Source**: PRD Section 4.5 (Analytics), Capabilities Analysis

#### 3.2.1 Layout

Top-level overview with KPI cards, charts, and action items. Personalized by role.

#### 3.2.2 KPI Cards (Admin/HR View)

| KPI | Source Data | Visual |
|-----|-----------|--------|
| Total Headcount | Employee count (active) | Number + trend arrow |
| Open Positions | Unfilled positions | Number + warning if > threshold |
| Pending Reviews | Reviews awaiting completion | Number + due date |
| Expiring Certifications | Certs expiring in 30 days | Number + urgency color |
| Employee Turnover (YTD) | Terminations / avg headcount | Percentage |
| Average Tenure | Mean employee tenure in years | Number |
| Training Compliance Rate | Valid certs / required certs | Percentage + progress bar |
| Active Projects | Projects with assigned crews | Number |

#### 3.2.3 Charts

1. **Headcount by Department** — Horizontal bar chart
2. **Headcount Trend (12-month)** — Line chart
3. **Employee Distribution by Type** — Donut chart (Full-time, Part-time, Contractor)
4. **Upcoming Reviews Timeline** — Calendar/timeline view
5. **Certification Compliance by Department** — Stacked bar (valid/expiring/expired)
6. **Recent Activity Feed** — Scrollable list of recent events (new hires, reviews completed, certs earned)

#### 3.2.4 Role-Specific Views

- **Foreman**: Crew headcount, crew certifications, pending crew reviews, recent incidents
- **Project Manager**: Project staffing, project performance summary, crew compliance
- **Employee**: Own training status, upcoming reviews, personal alerts

---

### 3.3 Module: Employee Management

**Source**: TSG Requirements Sheet "Core HR Records" (25 requirements), PRD Section 2

#### 3.3.1 Employee List View

- Paginated table with search and filters
- Filters: Department, Job Type (Full-time/Part-time/Contractor), Status (Active/Leave/Terminated), Location, Trade, Union Status
- Columns: Photo/Avatar, Name, Employee ID, Department, Job Title, Trade, Location, Status, Hire Date
- Sort by any column
- Bulk actions: Export CSV, Export PDF
- Quick actions: View Profile, Edit, Create Review

#### 3.3.2 Employee Profile Page

**Personal Information** (TSG #1, #17, #18)
- Full name, Employee ID (auto-generated, TSG #7)
- Email, Phone, Address
- Date of Birth, SSN (masked, visible only to HR/Admin — TSG #1 note)
- Emergency contacts
- Photo/Avatar

**Employment Information** (TSG #5, #6, #8, #10, #14)
- Job Title, Department, Division, Location
- Employee Type (Full-time, Part-time, Contractor, Casual — TSG #6)
- Employment Status (Active, On Leave, Suspended, Terminated — TSG #14)
- Hire Date, Original Hire Date, Tenure (calculated — TSG #10)
- Reports To (with link to supervisor profile — TSG #5)
- Direct Reports list
- Cost Center (TSG #3)
- Pay Rate, Pay Type (Hourly/Salary)

**Job History** (TSG #8, #12)
- Timeline view of all position changes
- Each entry: Job Title, Department, Start Date, End Date, Reason for Change, Salary
- Visual timeline with date markers

**Union Information** (TSG #9, #11)
- Union Name, Local Number
- Union Seniority Date
- Classification/Trade
- CBA Reference

**Compliance** (TSG #24)
- I-9 Status, Veterans Status
- Work Authorization/Visa details
- EEO Category

**Custom Fields** (TSG #23)
- Bonus Eligible (checkbox)
- Per Diem Eligible
- Travel Authorization Level
- Vehicle Allowance

**Audit Trail** (TSG #21)
- Log of all changes to employee record
- Who changed, what changed, old value, new value, timestamp
- Filterable and exportable

#### 3.3.3 Employee CRUD Operations

- **Create**: New employee form with validation, auto-generate Employee ID
- **Edit**: Inline editing with confirmation and audit trail
- **Status Change**: Modal for changing status (Active → Leave, Active → Terminated, etc.) with effective date and reason
- **Self-Service** (TSG #19, #20): Employees can update own contact info, view pay info

#### 3.3.4 Data Requirements (from TSG)

All 25 Core HR Records requirements addressed:
- ✅ #1: PII storage with masking
- ✅ #2: Multiple geographies/locations/divisions  
- ✅ #3: Department cost centers
- ✅ #5: Employee hierarchy (reporting structure)
- ✅ #6: Multiple employee types
- ✅ #7: Auto-generated unique identifiers
- ✅ #8: Job/salary/status history
- ✅ #9, #11: Union tracking
- ✅ #10: Tenure details
- ✅ #12: Historic job details
- ✅ #14: Configurable status codes
- ✅ #15: Open text fields for notes
- ✅ #17: Demographic information
- ✅ #18: Life change support
- ✅ #19, #20: Employee self-service
- ✅ #21: Audit trail
- ✅ #22: Mass updates (via bulk actions)
- ✅ #23: Custom fields
- ✅ #24: Compliance records

---

### 3.4 Module: Org Chart

**Source**: Lumber Org Chart PRD (comprehensive), TSG Requirements Sheet "Organizational Structure" (9 requirements)

#### 3.4.1 Interactive Org Chart Canvas

**Technology**: D3.js with custom tree layout

**Core Features**:
- Interactive pan and zoom (mouse drag + scroll wheel)
- Click-to-expand/collapse branches
- Breadcrumb navigation (click to navigate back up the tree)
- Search: find any employee/position and zoom to their location
- Full-screen mode

**Node Cards** (per Org Chart PRD):
- Employee photo/avatar
- Name, Job Title
- Department/Division badge
- Trade/classification
- Direct reports count
- Certification status indicator (green/yellow/red)
- Click to open employee profile

**Views** (TSG #1, #2, Org Chart PRD):
1. **Corporate Hierarchy**: Company → Division → Department → Team → Employee
2. **Project/Crew View**: Project → Site → Crew → Workers (derived from project assignments)
3. Toggle between views with animated transition

#### 3.4.2 Drill-Down & Navigation (TSG #3)

- Click any node to expand its subtree
- Click manager to see all their reports
- "Focus on this node" — centers and zooms to a subtree
- Breadcrumbs show current path in hierarchy
- Back button restores previous view

#### 3.4.3 Supervisor & Hierarchy Features (TSG #5)

- Current supervisor shown on each node
- Click "History" to see supervisor history (effective dates, past supervisors)
- Dotted-line relationships shown with dashed connectors
- Matrix reporting overlay toggle

#### 3.4.4 Span of Control (Org Chart PRD)

- Each manager node shows span count
- Color-coded: Green (≤8), Yellow (9-12), Red (>12)
- Span analytics sidebar panel

#### 3.4.5 Delegates & Contingency (TSG #6, Org Chart PRD)

- Delegate badge shown on nodes with active delegates
- Hover to see delegate name and scope/dates

#### 3.4.6 Snapshots (TSG #4)

- "As of" date picker to view historical org structure
- Compare snapshots side-by-side (added/removed/moved)

#### 3.4.7 Export (TSG #9)

- Export as PNG image (with legend and watermark)
- Export as PDF (with page breaks and table of contents)
- Export as CSV/Excel (tabular: Name, Title, Department, Reports To, etc.)

#### 3.4.8 Bilingual Support (Org Chart PRD)

- EN/ES toggle for all labels and navigation
- Node cards respect language setting

---

### 3.5 Module: Performance Management

**Source**: Lumber Performance Management PRD (comprehensive), TSG Requirements Sheet "Performance Management" (15 requirements)

#### 3.5.1 Goals & Objectives (TSG #1, #2, #3)

**Features**:
- Create goals with: Title, Description, Category (Safety/Quality/Productivity/Leadership), Target Date, Weight
- Date-effective goals with version history (TSG #1)
- Cascade goals from company → department → individual (TSG #2)
- Track % completion with progress bar (TSG #3)
- Evidence/attachment support
- Status: Not Started, In Progress, At Risk, Completed, Deferred

**Goal Categories (Construction-specific)**:
- Safety Goals (zero incidents, safety training completion)
- Quality Goals (rework rate, inspection pass rate)
- Productivity Goals (hours vs estimate, output metrics)
- Professional Development Goals (certifications, skills)
- Leadership Goals (crew retention, mentoring)

#### 3.5.2 Review Cycles (TSG #4, #5, #6, #8, #9)

**Review Types** (TSG #4):
1. **Annual Review**: Full comprehensive review
2. **Mid-Year Check-in**: Progress update
3. **30/60/90 Day Review**: New hire probationary
4. **Project Closeout Review**: End of project evaluation
5. **Performance Improvement Plan (PIP)**: Remediation

**Configuration** (TSG #5, #8):
- Configurable intervals (quarterly, annually, ad hoc)
- Customizable criteria with weights and scoring scales
- Rating scales: 1-5 (Unsatisfactory → Exceptional)
- Competency areas with behavioral anchors

**Workflow** (TSG #6):
- Self-review step (employee fills their portion)
- Manager review step (manager provides ratings + feedback)
- Sign-off/acknowledgment (both parties e-sign)
- HR approval step (for PIPs or disputed reviews)
- Reviewer can attach evidence (TSG #7)

#### 3.5.3 Review Form

**Sections**:
1. **Core Competencies** (configurable, weighted — TSG #8, #9)
   - Safety Compliance (weight: 25%)
   - Quality of Work (weight: 25%)
   - Productivity & Efficiency (weight: 20%)
   - Teamwork & Communication (weight: 15%)
   - Reliability & Attendance (weight: 15%)

2. **Goal Achievement** — auto-populated from active goals with completion %

3. **Overall Rating** — calculated from weighted scores (TSG #9)

4. **Manager Comments** — rich text with attachment support (TSG #7)

5. **Employee Comments** — response section

6. **Development Plan** — recommended training, career path notes (TSG #12)

7. **Signatures** — electronic sign-off with timestamp (TSG #6)

#### 3.5.4 Performance History (TSG #10, #11)

- Timeline view of all reviews for an employee
- Trend chart showing rating progression over time
- Summary and detailed reporting (TSG #11)
- Historical data by supervisor, department, or project

#### 3.5.5 Incidents & Commendations (Performance PRD)

**Incident Logging**:
- Quick-add incident form (mobile-friendly)
- Type: Safety Violation, Attendance Issue, Quality Issue, Conduct Issue
- Severity: Minor, Moderate, Major, Critical
- Description, date, location, witnesses
- Attachment support (photos)
- Linked to employee record

**Commendations**:
- Quick "shout-out" form
- Categories: Safety, Quality, Teamwork, Above & Beyond
- Public/Private toggle
- Badge/recognition system

#### 3.5.6 Performance Improvement Plans (TSG #14)

- PIP creation wizard
- Required fields: Issue description, improvement targets, timeline, check-in dates
- Milestone tracking with due dates
- Document storage for related communications
- Auto-alerts for approaching deadlines
- Outcome: Completed, Extended, Terminated

#### 3.5.7 Calibration (Performance PRD)

- View all reviews in a 3x3 grid (Performance vs Potential)
- Drag-and-drop calibration
- Side-by-side comparison of similar roles
- Distribution analysis (forced normal curve view)

#### 3.5.8 Performance → Pay Link (TSG #15)

- Final ratings linked to merit increase matrix
- Bonus recommendation field
- Export to payroll format

---

### 3.6 Module: Learning Management System (LMS)

**Source**: PRD Section 4.3, TSG Requirements Sheet "Learning & Development" (25 requirements)

#### 3.6.1 Training Catalog (TSG #1, #4, #5)

**Course Management**:
- Course details: Title, Description, Category, Duration, Format (e-Learning/Instructor-Led/Toolbox Talk)
- Prerequisites (TSG #1)
- Required certifications upon completion
- Course catalog browsable by category (TSG #4)
- Catalog filtered by job class/trade (TSG #5)

**Course Categories**:
- OSHA Safety (OSHA 10, OSHA 30, confined spaces, fall protection, etc.)
- Trade-Specific (welding certs, crane operation, etc.)
- Equipment Operation
- Company Policies & Compliance
- Professional Development
- Union Apprenticeship Hours

#### 3.6.2 Certification Tracking (PRD Section 4.3, key feature)

**Dashboard** (Safety Sam's primary view):
- Certification compliance rate by department/project
- Expiring within 30/60/90 days
- Expired certifications (red alerts)
- Per-employee cert status grid

**Certification Records**:
- Certification name, issuing body, number
- Issue date, expiration date
- Status: Valid, Expiring Soon, Expired, Revoked
- Attachment: scanned cert document
- Auto-calculated renewal dates

**Alerts** (TSG #12):
- 90-day warning: Email/notification
- 30-day warning: Urgent notification
- Expired: Block from scheduling (integration point)
- Manager notification for team expiring certs

#### 3.6.3 Training Assignments (TSG #2, #3, #11)

- Assign training individually or in bulk (by department, trade, project) (TSG #22)
- Self-enrollment for elective courses (TSG #2)
- Manager enrollment capability (TSG #3)
- Track status: Assigned, In Progress, Completed, Overdue
- Completion tracking with dates and scores (TSG #11, #24)
- Due dates with reminder notifications

#### 3.6.4 Training History & Reporting (TSG #14, #17, #24)

- Per-employee training transcript
- Department-level completion reports
- Compliance gap analysis
- Training hours by employee (for union apprenticeship tracking)
- Export to CSV/PDF (TSG #17)

#### 3.6.5 Integration Points

- **Performance Management**: Low review scores trigger training recommendations (TSG #10)
- **Onboarding**: New hire triggers mandatory training assignment sequence
- **Org Chart**: Cert status indicators on org chart nodes
- **Scheduling**: Workers with expired certs flagged

---

### 3.7 Module: Analytics & Reporting

**Source**: PRD Section 4.5, Capabilities Analysis

#### 3.7.1 Pre-Built Dashboards

1. **Workforce Overview**
   - Headcount by department, location, trade, employee type
   - Headcount trends (hiring, terminations, net change over 12 months)
   - Average tenure by department
   - Turnover rate by department (voluntary/involuntary)

2. **Performance Analytics**
   - Rating distribution (histogram)
   - Performance trends by department
   - Goal completion rates
   - Review completion rates (on-time vs overdue)
   - Incident frequency by type, department, month

3. **Training & Compliance**
   - Certification compliance rate by department
   - Training hours per employee
   - Course completion rates
   - Expiring certifications forecast (30/60/90 day view)
   - Apprenticeship hour tracking

4. **Organizational Health**
   - Span of control distribution
   - Vacancy/fill rate by department
   - Employee distribution by level/grade
   - Cost center headcount analysis

#### 3.7.2 Chart Types

- Line charts (trends over time)
- Bar charts (comparisons by category)
- Donut/pie charts (distributions)
- Heatmaps (department × metric matrices)
- Data tables with sort, filter, and pagination

#### 3.7.3 Export & Sharing

- Export any chart as PNG
- Export underlying data as CSV or Excel
- Export full report as PDF
- Date range selectors on all dashboards
- Department/location filters

---

## 4. Database Schema

### 4.1 Entity Relationship Overview

```
User (auth) ─── Employee ─── Department
                    │              │
                    ├── JobHistory  │
                    │              │
                    ├── PerformanceReview ── ReviewCriteria
                    │       │
                    │       ├── Goal
                    │       └── Signature
                    │
                    ├── Incident
                    │
                    ├── Commendation
                    │
                    ├── TrainingAssignment ── Course
                    │
                    ├── Certification
                    │
                    ├── PIP ── PIPMilestone
                    │
                    └── AuditLog
                    
Division ─── Department
Company  ─── Division
Project  ─── ProjectAssignment ─── Employee
Site     ─── Project
```

### 4.2 Key Models

**User**: id, email, password (hashed), role (ADMIN/HR/MANAGER/EMPLOYEE), employeeId, createdAt, updatedAt

**Employee**: id, employeeNumber (auto-gen), firstName, lastName, email, phone, address, city, state, zip, dateOfBirth, ssn (encrypted), gender, ethnicity, veteranStatus, photo, employeeType (FULL_TIME/PART_TIME/CONTRACTOR/CASUAL), status (ACTIVE/ON_LEAVE/SUSPENDED/TERMINATED), hireDate, originalHireDate, terminationDate, terminationReason, departmentId, divisionId, locationId, jobTitle, trade, payRate, payType (HOURLY/SALARY), reportsToId, unionName, unionLocal, unionSeniorityDate, costCenter, bonusEligible, eeoCategory, i9Status, workAuthExpiry, createdAt, updatedAt

**Department**: id, name, code, divisionId, costCenter, managerId

**Division**: id, name, code, companyId

**Company**: id, name, code, address

**Location**: id, name, address, city, state, type (OFFICE/FIELD/WAREHOUSE)

**Project**: id, name, code, status (ACTIVE/COMPLETED/PLANNED), locationId, startDate, endDate, projectManagerId

**ProjectAssignment**: id, projectId, employeeId, role, crewName, startDate, endDate

**JobHistory**: id, employeeId, jobTitle, department, location, startDate, endDate, reason, salary, changedBy

**PerformanceReview**: id, employeeId, reviewerId, type (ANNUAL/MID_YEAR/30_60_90/PROJECT_CLOSEOUT/PIP), status (DRAFT/IN_PROGRESS/PENDING_SIGN_OFF/COMPLETED), period, dueDate, overallRating, managerComments, employeeComments, developmentPlan, completedAt, createdAt

**ReviewCriteria**: id, reviewId, name, category, weight, rating (1-5), comments

**Goal**: id, employeeId, title, description, category (SAFETY/QUALITY/PRODUCTIVITY/DEVELOPMENT/LEADERSHIP), targetDate, weight, percentComplete, status (NOT_STARTED/IN_PROGRESS/AT_RISK/COMPLETED/DEFERRED), createdAt, updatedAt

**Incident**: id, employeeId, reportedById, type (SAFETY/ATTENDANCE/QUALITY/CONDUCT), severity (MINOR/MODERATE/MAJOR/CRITICAL), description, date, location, witnesses, attachments, status (OPEN/INVESTIGATING/RESOLVED/CLOSED), resolution, createdAt

**Commendation**: id, employeeId, awardedById, category (SAFETY/QUALITY/TEAMWORK/ABOVE_AND_BEYOND), description, isPublic, createdAt

**Course**: id, title, description, category, format (E_LEARNING/INSTRUCTOR_LED/TOOLBOX_TALK), duration, prerequisiteIds, certificationGranted, provider, isRequired, tradeSpecific

**TrainingAssignment**: id, employeeId, courseId, assignedById, status (ASSIGNED/IN_PROGRESS/COMPLETED/OVERDUE), dueDate, completedDate, score, certificateUrl, createdAt

**Certification**: id, employeeId, name, issuingBody, certNumber, issueDate, expirationDate, status (VALID/EXPIRING_SOON/EXPIRED/REVOKED), attachmentUrl, courseId

**PIP**: id, employeeId, createdById, issueDescription, improvementTargets, startDate, endDate, status (ACTIVE/COMPLETED/EXTENDED/FAILED), outcome, createdAt

**PIPMilestone**: id, pipId, title, description, dueDate, completedDate, status (PENDING/COMPLETED/MISSED)

**AuditLog**: id, entityType, entityId, action (CREATE/UPDATE/DELETE), field, oldValue, newValue, userId, timestamp

---

## 5. Seed Data Specification

### 5.1 Company Structure

**Summit Construction Group** (fictional, realistic construction company)

```
Summit Construction Group
├── Heavy Civil Division
│   ├── Bridge & Structures Dept (45 employees)
│   ├── Highway & Roads Dept (52 employees)
│   └── Utilities Dept (38 employees)
├── Building Division  
│   ├── Commercial Construction Dept (48 employees)
│   ├── Industrial Construction Dept (35 employees)
│   └── Renovation & Retrofit Dept (28 employees)
├── Specialty Division
│   ├── Electrical Dept (32 employees)
│   ├── Mechanical/HVAC Dept (28 employees)
│   └── Plumbing & Fire Protection Dept (22 employees)
└── Corporate
    ├── Executive Office (8 employees)
    ├── Human Resources (12 employees)
    ├── Finance & Accounting (10 employees)
    ├── Safety & Compliance (8 employees)
    ├── Estimating (6 employees)
    └── IT & Technology (5 employees)
```

**Total: ~375 employees**

### 5.2 Project & Crew Data

8-10 active projects with crews assigned:
- Downtown Office Tower (Building/Commercial)
- I-95 Bridge Rehabilitation (Heavy Civil/Bridge)
- Municipal Water Treatment Upgrade (Heavy Civil/Utilities)
- Amazon Distribution Center (Building/Industrial)
- Hospital Wing Addition (Building/Commercial)
- Highway 301 Widening (Heavy Civil/Highway)
- Solar Farm Electrical (Specialty/Electrical)
- Residential Complex HVAC (Specialty/Mechanical)

### 5.3 Employee Demographics

Realistic distribution:
- 85% male, 15% female (construction industry)
- 60% journeyman, 20% apprentice, 10% foreman, 10% admin/management
- 40% union, 60% non-union
- 70% full-time, 15% part-time, 15% contractor
- Mix of tenures: 30% < 1 year, 30% 1-5 years, 25% 5-15 years, 15% > 15 years
- Trades: Carpentry, Electrical, Plumbing, Ironwork, Concrete, Welding, Heavy Equipment, HVAC, Pipe Fitting, Painting

### 5.4 Performance Data

- Recent annual review cycle with varied ratings (bell curve distribution)
- 15-20 active goals across employees
- 8-10 incidents (mix of types and severities)
- 15-20 commendations
- 3-4 active PIPs
- 30/60/90 day reviews for recent hires

### 5.5 Training Data

- 30+ courses in catalog
- 500+ training assignments (completed and in-progress)
- 200+ certifications (mix of valid, expiring, and expired)
- OSHA 10/30 for all field workers
- Trade-specific certs (welding, crane, confined space, etc.)

---

## 6. UI/UX Specifications

### 6.1 Branding (Lumber)

Based on the HTML prototypes in the Design Iterations folder:
- **Primary Color**: Deep blue (#1e40af / blue-800) — Lumber brand
- **Accent**: Amber/orange for alerts and CTAs
- **Background**: Light gray (#f8fafc)
- **Sidebar**: Dark blue with white text
- **Typography**: System font stack (Inter preferred)
- **Cards**: White with subtle shadow, rounded corners
- **Tables**: Alternating row colors, sticky headers

### 6.2 Layout

```
┌──────────────────────────────────────────────────┐
│  🪵 Lumber HRIS    [Search]     [🔔] [👤 User ▼] │
├────────┬─────────────────────────────────────────┤
│        │                                         │
│  🏠 Dash│        Main Content Area               │
│  👥 Empl│                                         │
│  🏢 Org │        (scrollable)                     │
│  📊 Perf│                                         │
│  📚 LMS │                                         │
│  📈 Anal│                                         │
│        │                                         │
│        │                                         │
│ ────── │                                         │
│  ⚙️ Set │                                         │
│        │                                         │
└────────┴─────────────────────────────────────────┘
```

- Collapsible sidebar (icon-only mode on mobile)
- Sticky header with global search
- Notification bell with badge count
- User menu with role indicator and logout

### 6.3 Responsive Design

- Desktop-first (primary use case for HR admin)
- Tablet-compatible (sidebar collapses)
- Mobile-accessible (stacked layouts, touch-friendly)

---

## 7. Development Phases & Checkpoints

### CRITICAL RULE: Opus Quality Gates

After each phase, Opus (me) will:
1. Read ALL generated code files
2. Run the application and verify functionality
3. Check against requirements from the PRDs
4. Verify UI matches Lumber branding and design iterations
5. Test edge cases and error handling
6. Log findings in a checkpoint report
7. ONLY proceed to next phase if checkpoint passes

If a checkpoint FAILS:
- Document specific issues
- Fix issues before proceeding
- Re-run checkpoint verification

---

### Phase 1: Project Setup & Database Schema
**Estimated Time**: 45 min
**Checkpoint**: SETUP_01

**Tasks**:
1.1. Initialize Next.js 14 project with TypeScript
1.2. Install all dependencies (shadcn/ui, Prisma, NextAuth, D3, Chart.js, etc.)
1.3. Configure Tailwind with Lumber brand colors
1.4. Define complete Prisma schema (all models from Section 4)
1.5. Generate Prisma client
1.6. Create database migrations
1.7. Build seed script with all demo data (Section 5)
1.8. Run seed and verify database

**Checkpoint SETUP_01 Criteria**:
- [ ] Project builds without errors
- [ ] All dependencies installed
- [ ] Prisma schema compiles
- [ ] Database seeded with 375+ employees
- [ ] Seed data covers all categories (departments, projects, reviews, certs)
- [ ] Demo users created with correct roles

---

### Phase 2: Authentication & App Shell
**Estimated Time**: 30 min
**Checkpoint**: AUTH_01

**Tasks**:
2.1. Configure NextAuth.js with Credentials provider
2.2. Create login page with Lumber branding
2.3. Implement JWT session with role payload
2.4. Create middleware for route protection
2.5. Build app layout (sidebar, header, navigation)
2.6. Implement role-based menu visibility
2.7. Create "Access Denied" page
2.8. Test all 5 demo user logins

**Checkpoint AUTH_01 Criteria**:
- [ ] All 5 demo users can log in
- [ ] Invalid credentials show error
- [ ] Role-based routing works (employee can't access admin pages)
- [ ] Sidebar navigation matches design
- [ ] Lumber branding applied (colors, logo area)
- [ ] Logout works correctly
- [ ] Session persists on refresh

---

### Phase 3: Employee Management
**Estimated Time**: 60 min
**Checkpoint**: EMP_01

**Tasks**:
3.1. Build Employee List page with search, filter, sort, pagination
3.2. Build Employee Profile page with all sections
3.3. Build Employee Create/Edit forms with validation
3.4. Implement Job History timeline
3.5. Implement Audit Trail logging
3.6. Add bulk export (CSV)
3.7. Add employee status management (active, leave, terminated)
3.8. Implement self-service view for Employee role

**Checkpoint EMP_01 Criteria**:
- [ ] Employee list loads with all 375+ employees
- [ ] Search works (by name, ID, department)
- [ ] Filters work (department, status, type, trade)
- [ ] Pagination works correctly
- [ ] Profile page shows all employee data
- [ ] Job history timeline renders correctly
- [ ] Create new employee works with validation
- [ ] Edit employee updates correctly with audit trail
- [ ] Status change records in history
- [ ] CSV export downloads correctly
- [ ] Employee role sees only own profile

---

### Phase 4: Org Chart
**Estimated Time**: 60 min
**Checkpoint**: ORG_01

**Tasks**:
4.1. Build D3.js tree layout with pan/zoom
4.2. Create node cards (photo, name, title, dept, reports count)
4.3. Implement Corporate Hierarchy view
4.4. Implement Project/Crew view
4.5. Add drill-down (click to expand/collapse)
4.6. Add breadcrumb navigation
4.7. Add search with zoom-to-employee
4.8. Add span-of-control indicators
4.9. Implement export (PNG/PDF)
4.10. Add view toggle (corporate ↔ project)

**Checkpoint ORG_01 Criteria**:
- [ ] Org chart renders full hierarchy without errors
- [ ] Pan and zoom work smoothly
- [ ] Click expand/collapse animates correctly
- [ ] Node cards display all required info
- [ ] Search finds employees and zooms to them
- [ ] Corporate view shows department hierarchy
- [ ] Project view shows project/crew structure
- [ ] Breadcrumbs update and navigate correctly
- [ ] Span-of-control colors are correct
- [ ] Export produces valid PNG/PDF
- [ ] Performance acceptable with 375+ nodes

---

### Phase 5: Performance Management
**Estimated Time**: 75 min
**Checkpoint**: PERF_01

**Tasks**:
5.1. Build Review Cycles list with status and filters
5.2. Build Review Form with all sections (competencies, goals, ratings, comments)
5.3. Implement weighted scoring calculation
5.4. Build Goals management (create, track progress, complete)
5.5. Build Incident logging with severity and type
5.6. Build Commendation system
5.7. Build PIP management (create, milestones, tracking)
5.8. Build Performance History timeline
5.9. Implement sign-off workflow (employee + manager)
5.10. Build Calibration grid view (9-box)
5.11. Add Performance → training recommendation link

**Checkpoint PERF_01 Criteria**:
- [ ] Review list shows all reviews with correct statuses
- [ ] Review form renders all sections correctly
- [ ] Weighted scoring calculates correctly
- [ ] Goals CRUD works (create, update progress, complete)
- [ ] Goal cascade displays correctly
- [ ] Incident form saves with all fields
- [ ] Commendation form works
- [ ] PIP creation wizard works end-to-end
- [ ] PIP milestones track correctly
- [ ] Performance history timeline renders
- [ ] Sign-off captures both signatures
- [ ] Calibration 9-box grid displays
- [ ] Foreman can only see own crew's reviews
- [ ] Employee can only see own reviews

---

### Phase 6: LMS (Learning Management)
**Estimated Time**: 45 min
**Checkpoint**: LMS_01

**Tasks**:
6.1. Build Training Catalog with categories and search
6.2. Build Course detail page
6.3. Build Certification Tracking dashboard
6.4. Build Training Assignment management
6.5. Build per-employee Training Transcript
6.6. Implement certification expiration alerts
6.7. Build compliance gap analysis view
6.8. Add cert status indicators (valid/expiring/expired)
6.9. Link training recommendations from performance reviews

**Checkpoint LMS_01 Criteria**:
- [ ] Course catalog displays all 30+ courses
- [ ] Courses filterable by category, trade, format
- [ ] Course detail page shows all info
- [ ] Cert dashboard shows compliance rates
- [ ] Expiring/expired certs highlighted correctly
- [ ] Training assignments can be created (individual and bulk)
- [ ] Assignment status tracking works
- [ ] Employee training transcript is complete
- [ ] Compliance gap analysis shows missing required certs
- [ ] Alerts show for expiring certifications
- [ ] Integration: low performance review triggers training suggestion

---

### Phase 7: Dashboard & Analytics
**Estimated Time**: 45 min
**Checkpoint**: ANALYTICS_01

**Tasks**:
7.1. Build main Dashboard with KPI cards
7.2. Implement headcount by department chart
7.3. Implement headcount trend line chart
7.4. Implement employee type distribution donut
7.5. Implement certification compliance chart
7.6. Build Analytics page with all 4 dashboards
7.7. Implement date range and department filters
7.8. Build performance distribution histogram
7.9. Build turnover analysis chart
7.10. Implement CSV/PDF export for all reports
7.11. Build role-specific dashboard views

**Checkpoint ANALYTICS_01 Criteria**:
- [ ] Dashboard loads with correct KPI numbers
- [ ] All charts render with correct data
- [ ] Charts are interactive (hover tooltips)
- [ ] Date range filter updates all charts
- [ ] Department filter works across analytics
- [ ] Export CSV produces valid data
- [ ] Export PDF produces formatted report
- [ ] Admin sees full dashboard
- [ ] Foreman sees crew-specific dashboard
- [ ] Employee sees personal dashboard
- [ ] Analytics page loads all 4 dashboards
- [ ] No performance issues with large dataset

---

### Phase 8: Docker & Polish
**Estimated Time**: 30 min
**Checkpoint**: DOCKER_01

**Tasks**:
8.1. Create production Dockerfile (multi-stage build)
8.2. Create docker-compose.yml (app + PostgreSQL)
8.3. Create .env.example with all required variables
8.4. Create start.sh script for easy local development
8.5. Final UI polish pass (alignment, spacing, responsive)
8.6. Error handling review (loading states, empty states, error pages)
8.7. Cross-module navigation testing
8.8. Performance optimization (lazy loading, pagination)
8.9. Create README.md with setup and usage instructions

**Checkpoint DOCKER_01 Criteria**:
- [ ] Dockerfile builds successfully
- [ ] docker-compose.yml is valid
- [ ] README documents all setup steps
- [ ] All loading states have spinners
- [ ] All empty states have helpful messages
- [ ] All error states show friendly messages
- [ ] Cross-module links work (employee → org chart, review → employee, etc.)
- [ ] Application is responsive on tablet/mobile
- [ ] No console errors in browser

---

### Phase 9: Video Demo
**Estimated Time**: 30 min
**Checkpoint**: FINAL

**Tasks**:
9.1. Plan demo script (ordered walkthrough of all features)
9.2. Record screen capture of full demo
9.3. Add background music (from TOOLS.md settings)
9.4. Export video
9.5. Send to Franco

**Demo Script Outline**:
1. Login as HR Helen
2. Dashboard overview (KPI cards, charts)
3. Employee Management (browse, search, create new employee, view profile)
4. Org Chart (corporate view, drill-down, search, project view, export)
5. Performance Management (review cycle, goals, incident, commendation, calibration)
6. LMS (course catalog, cert tracking, assign training, compliance)
7. Analytics (all 4 dashboards, export)
8. Login as Foreman Francisco (show role-based views)
9. Login as Employee (show self-service views)

---

## 8. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| npm install failures | Low | High | Pre-test all critical packages |
| D3.js performance with 375 nodes | Medium | Medium | Use collapsible tree, lazy loading |
| Prisma SQLite limitations | Low | Medium | Use PostgreSQL-compatible schema |
| Time overrun on Performance module (most complex) | Medium | High | Strict timeboxing; MVP features first, polish later |
| Video recording issues | Low | Medium | Use proven ffmpeg approach from SimulAI |

---

## 9. File Structure

```
lumber-hris/
├── PLAN.md                          # This document
├── README.md                        # Setup & usage instructions
├── Dockerfile                       # Production Docker build
├── docker-compose.yml               # Full stack deployment
├── .env.example                     # Environment variables
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
├── prisma/
│   ├── schema.prisma                # Database schema
│   ├── seed.ts                      # Seed data script
│   └── migrations/                  # Auto-generated migrations
├── src/
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Redirect to dashboard
│   │   ├── login/
│   │   │   └── page.tsx             # Login page
│   │   ├── dashboard/
│   │   │   └── page.tsx             # Dashboard
│   │   ├── employees/
│   │   │   ├── page.tsx             # Employee list
│   │   │   ├── new/page.tsx         # Create employee
│   │   │   └── [id]/
│   │   │       ├── page.tsx         # Employee profile
│   │   │       └── edit/page.tsx    # Edit employee
│   │   ├── org-chart/
│   │   │   └── page.tsx             # Org chart
│   │   ├── performance/
│   │   │   ├── page.tsx             # Reviews list
│   │   │   ├── goals/page.tsx       # Goals management
│   │   │   ├── incidents/page.tsx   # Incidents list
│   │   │   ├── calibration/page.tsx # 9-box grid
│   │   │   └── reviews/
│   │   │       ├── new/page.tsx     # Create review
│   │   │       └── [id]/page.tsx    # View/edit review
│   │   ├── lms/
│   │   │   ├── page.tsx             # LMS dashboard
│   │   │   ├── catalog/page.tsx     # Course catalog
│   │   │   ├── certs/page.tsx       # Certification tracking
│   │   │   └── assignments/page.tsx # Training assignments
│   │   ├── analytics/
│   │   │   └── page.tsx             # Analytics dashboards
│   │   └── api/
│   │       ├── auth/[...nextauth]/route.ts
│   │       ├── employees/route.ts
│   │       ├── employees/[id]/route.ts
│   │       ├── departments/route.ts
│   │       ├── org-chart/route.ts
│   │       ├── performance/
│   │       │   ├── reviews/route.ts
│   │       │   ├── goals/route.ts
│   │       │   ├── incidents/route.ts
│   │       │   └── calibration/route.ts
│   │       ├── lms/
│   │       │   ├── courses/route.ts
│   │       │   ├── certs/route.ts
│   │       │   └── assignments/route.ts
│   │       └── analytics/route.ts
│   ├── components/
│   │   ├── ui/                      # shadcn/ui components
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── AppShell.tsx
│   │   ├── employees/
│   │   │   ├── EmployeeTable.tsx
│   │   │   ├── EmployeeProfile.tsx
│   │   │   ├── EmployeeForm.tsx
│   │   │   └── JobHistoryTimeline.tsx
│   │   ├── org-chart/
│   │   │   ├── OrgChartCanvas.tsx
│   │   │   ├── OrgChartNode.tsx
│   │   │   └── OrgChartControls.tsx
│   │   ├── performance/
│   │   │   ├── ReviewForm.tsx
│   │   │   ├── GoalCard.tsx
│   │   │   ├── IncidentForm.tsx
│   │   │   ├── CalibrationGrid.tsx
│   │   │   └── PerformanceTimeline.tsx
│   │   ├── lms/
│   │   │   ├── CourseCatalog.tsx
│   │   │   ├── CertDashboard.tsx
│   │   │   └── TrainingTranscript.tsx
│   │   ├── analytics/
│   │   │   ├── KPICard.tsx
│   │   │   ├── HeadcountChart.tsx
│   │   │   ├── TurnoverChart.tsx
│   │   │   └── ComplianceChart.tsx
│   │   └── shared/
│   │       ├── DataTable.tsx
│   │       ├── SearchBar.tsx
│   │       ├── FilterPanel.tsx
│   │       ├── StatusBadge.tsx
│   │       └── ExportButton.tsx
│   ├── lib/
│   │   ├── prisma.ts                # Prisma client singleton
│   │   ├── auth.ts                  # Auth configuration
│   │   ├── utils.ts                 # Utility functions
│   │   └── constants.ts             # App constants
│   └── types/
│       └── index.ts                 # TypeScript type definitions
└── public/
    ├── lumber-logo.svg              # Lumber logo
    ├── favicon.ico
    └── avatars/                     # Employee avatar images
```

---

## 10. Execution Timeline

| Phase | Start | Duration | Checkpoint |
|-------|-------|----------|------------|
| 1. Setup & Schema | T+0 | 45 min | SETUP_01 |
| 2. Auth & Shell | T+45 | 30 min | AUTH_01 |
| 3. Employee Mgmt | T+75 | 60 min | EMP_01 |
| 4. Org Chart | T+135 | 60 min | ORG_01 |
| 5. Performance | T+195 | 75 min | PERF_01 |
| 6. LMS | T+270 | 45 min | LMS_01 |
| 7. Analytics | T+315 | 45 min | ANALYTICS_01 |
| 8. Docker & Polish | T+360 | 30 min | DOCKER_01 |
| 9. Video Demo | T+390 | 30 min | FINAL |
| **Total** | | **~7 hours** | |

---

## 11. Appendix: Requirements Traceability

### TSG HRIS Requirements Coverage

| Sheet | Requirements | Covered | Coverage |
|-------|-------------|---------|----------|
| Core HR Records | 25 | 23 | 92% |
| Organizational Structure | 9 | 9 | 100% |
| Performance Management | 15 | 15 | 100% |
| Learning & Development | 25 | 20 | 80% |
| Position Management | 12 | 10 | 83% |
| Payroll | 22 | N/A (out of scope — existing Lumber module) |
| Benefits | 25 | N/A (out of scope — Phase 4 per PRD) |
| Time & Attendance | 18 | N/A (out of scope — existing Lumber module) |
| Leave Management | 17 | N/A (out of scope — existing Lumber module) |
| Scheduling | 25 | N/A (out of scope — existing Lumber module) |
| Onboarding & Offboarding | 11 | 5 | 45% (basic) |
| Succession Planning | 14 | 4 | 29% (basic via calibration) |
| Compensation Management | 15 | 3 | 20% (basic via performance→pay) |
| Workforce Planning | 10 | N/A (Phase 3 per PRD) |

**Note**: Payroll, Benefits, Time & Attendance, Leave Management, and Scheduling are marked "Covered" or "Strong offering" in the Capabilities Analysis — they are existing Lumber modules and NOT in scope for this HRIS build per the PRD phasing strategy.
