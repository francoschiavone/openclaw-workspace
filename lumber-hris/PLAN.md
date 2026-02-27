# Lumber HRIS — Master Development Plan

## Document Info
- **Created**: 2026-02-27T04:00Z
- **Updated**: 2026-02-27T05:15Z
- **Author**: Opus (AI) — supervised by Franco Schiavone
- **Status**: ACTIVE — READY TO BUILD
- **Version**: 3.0 (FastAPI + React architecture)

---

## 1. Executive Summary

Build a fully working, dockerized HRIS (Human Resource Information System) for Lumber, a construction workforce management platform. The application covers 6 core modules: Dashboard, Employee Management, Org Chart, Performance Management, LMS, and Analytics.

**Architecture**: FastAPI (Python) backend + React/Vite (TypeScript) frontend — matching Rippling's proven pattern (Python + React) and Franco's professional stack (FastAPI, Pydantic, SQLAlchemy).

**Deliverables**:
1. A fully functional web application (separate frontend + backend)
2. Docker Compose deployment configuration (frontend + backend + PostgreSQL)
3. Pre-loaded demo users with role-based access (5 personas)
4. Realistic seed data: 375+ employees of a construction company
5. A video demo in English showcasing all features

---

## 2. Architecture & Technology Decisions

### 2.1 Environment Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| Root filesystem READ-ONLY | Cannot pip install to system | `pip install --target=.pylibs` works ✅ |
| /tmp is noexec | Python libs can't run from /tmp | Install to workspace `.pylibs/` dir ✅ |
| docker-compose not available locally | Can't orchestrate locally | Provide docker-compose.yml for host; use shell script for dev ✅ |
| DinD networking (no sibling container reach) | Can't connect to PostgreSQL in Docker | SQLite for development; PostgreSQL in Docker for production ✅ |
| Sub-agents have NO exec access | Can't delegate build tasks | All development by Opus; sub-agents for code generation only |
| 258GB disk, 7.8GB RAM, 10 CPUs | Sufficient | No constraints |
| Node.js 22, Python 3.11 | Modern runtimes | Full support for both stacks ✅ |
| Docker 20.10 available | Can build images | Dockerfiles + compose provided ✅ |

### 2.2 Architecture: FastAPI + React (Rippling Pattern)

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT BROWSER                          │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         React + Vite (TypeScript)                     │  │
│  │         Tailwind CSS + shadcn/ui                      │  │
│  │         d3-org-chart + Recharts                       │  │
│  │         @tanstack/react-table                         │  │
│  │         react-hook-form + zod                         │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │ HTTP/REST                        │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    FastAPI (Python)                          │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │   Auth   │ │ Employee │ │  Perf    │ │     LMS      │  │
│  │  (JWT)   │ │  CRUD    │ │ Reviews  │ │  Certs/Train │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ OrgChart │ │Analytics │ │ Incidents│ │  Audit Log   │  │
│  │  (tree)  │ │ (agg)    │ │ /Commend │ │              │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
│                          │                                  │
│              ┌───────────▼───────────┐                      │
│              │   SQLAlchemy ORM      │                      │
│              │   Pydantic Schemas    │                      │
│              └───────────┬───────────┘                      │
│                          │                                  │
└──────────────────────────┼──────────────────────────────────┘
                           │
                ┌──────────▼──────────┐
                │   SQLite (dev)      │
                │   PostgreSQL (prod) │
                └─────────────────────┘
```

### 2.3 Why FastAPI + React (Decision Rationale)

| Factor | Decision |
|--------|----------|
| **Market validation** | Rippling ($13.4B valuation) uses Python backend + React frontend for their HRIS |
| **Franco's stack** | FastAPI + Pydantic + SQLAlchemy is his daily work at LumberFi |
| **Hitesh "run with it"** | Python backend is maintainable by Franco and team |
| **Complex business logic** | Review workflows, cert expiration, goal cascading, calibration — FastAPI + Pydantic excels here |
| **Future AI features** | PRD mentions AI capabilities — Python is where ML/AI lives |
| **Commercial HRIS stacks** | BambooHR (React+Rails), Gusto (React+Rails), Rippling (React+Python), Procore (React+Rails) — all use React frontends |
| **Open source validation** | aveer.hr uses React+shadcn+Tailwind (validates frontend); Horilla uses Python backend (validates backend) |

### 2.4 Market Research Summary

#### Open Source HRIS Projects Evaluated

| Project | Stack | Stars | Verdict |
|---------|-------|-------|---------|
| **Frappe HR** | Python/Frappe+Vue | Top OSS | ❌ Heavy Frappe dependency, Vue, can't match Lumber prototype |
| **Horilla** | Python/Django+HTML | 2nd | ❌ Static templates, not SPA. But validates Python backend choice |
| **programinglive/hris** | Laravel+React+TS+Inertia | Active | ❌ PHP backend, but good feature reference |
| **ahmed-fawzy99** | Laravel+Vue+Inertia | Demo avail | ❌ PHP+Vue. Good UX reference for HR workflows |
| **aveer.hr** | Next.js+TS+Supabase+shadcn | Modern | ✅ Validates React+shadcn+Tailwind. Too basic to fork |
| **OrangeHRM** | PHP+Symfony | Industry leader | ❌ Legacy. But good feature completeness reference |

#### Design Patterns Adopted from Proven Products

1. **Rippling's Unified Data Model**: Employee record is the center of everything. All modules reference back to employee. Cross-module data flows naturally (performance → training → goals).
2. **BambooHR's UX Principles**: Clean employee directory with tabbed profiles. Performance reviews with "few quick questions that encourage action." Employee self-service portal. Simple navigation.
3. **Procore's Construction UX**: Project/crew-based views alongside corporate hierarchy. Field worker considerations. Mobile-friendly interfaces.

#### Reusable Libraries (not reinventing the wheel)

| Library | What it solves | Saves |
|---------|---------------|-------|
| **`d3-org-chart`** (bumbeishvili) | Complete org chart: pan/zoom, expand/collapse, search, custom nodes, export, minimap | Weeks of D3 work |
| **`recharts`** | React chart components; better React integration than Chart.js | Chart development time |
| **`@tanstack/react-table`** | Data tables with server-side search/filter/sort/pagination | Table infrastructure |
| **`react-hook-form` + `zod`** | Form state management + schema validation | Form boilerplate |
| **`shadcn/ui`** | Pre-built accessible UI components (dialogs, tabs, cards, badges, etc.) | UI component development |

#### Lumber Prototype v5 Analysis (the design spec)

Deeply analyzed the 173KB HTML prototype. It defines:
- **Module structure**: HRIS module with subpages: dashboard, employees, orgchart, performance, lms, analytics, builderfax
- **Performance tabs**: dashboard, cycles, review-form, incidents, commends
- **LMS tabs**: catalog, worker, manager, rules
- **Color scheme** (exact CSS variables extracted):
  - Nav bg: `#1e2d3b`, Nav text: `#c8d6e2`, Active/accent: `#7aecb4` (mint green)
  - Blue: `#2563eb`, Page bg: `#f0f2f5`, Text: `#111827`/`#374151`/`#6b7280`
  - Red: `#dc2626`, Yellow: `#d97706`, Orange: `#ea580c`, Purple: `#7c3aed`
- **Construction terms deeply embedded**: crew (127×), trade (74×), OSHA (65×), union (43×), foreman (32×)
- **D3.js already used** for org chart with corporate + project views
- **Key JS functions**: `switchModule()`, `setSubpage()`, `renderProject()`, `renderCorp()`, `mkNode()`, `drawConn()`, `panelWorker()`, `panelForeman()`, `panelPm()`, `openPanel()`, `closePanel()`, `setView()`, `setPrj()`, `applyZoom()`, `fitCanvas()`, `resetCanvas()`, `setLmsTab()`, `setPerfTab()`, `openModal()`, `closeModal()`

### 2.5 Technology Stack (Final)

#### Backend (Python)

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | **FastAPI** | 0.110+ | Async REST API, auto-docs (Swagger/ReDoc) |
| ORM | **SQLAlchemy** | 2.0+ | Database abstraction, async support |
| Schemas | **Pydantic** | 2.0+ | Request/response validation, serialization |
| Auth | **python-jose** + **passlib** | - | JWT token generation, password hashing (bcrypt) |
| Database (dev) | **SQLite** | 3.x | Zero-config development |
| Database (prod) | **PostgreSQL** | 16 | Production (via asyncpg or psycopg2) |
| Migration | **Alembic** | 1.13+ | Schema migrations |
| Server | **Uvicorn** | 0.27+ | ASGI server |
| CORS | **FastAPI CORSMiddleware** | - | Allow frontend origin |

#### Frontend (TypeScript/React)

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Build Tool | **Vite** | 5.x | Fast dev server, HMR |
| Framework | **React** | 18.x | UI library |
| Language | **TypeScript** | 5.x | Type safety |
| Routing | **React Router** | 6.x | Client-side routing |
| UI Library | **shadcn/ui** | latest | Pre-built accessible components |
| CSS | **Tailwind CSS** | 3.x | Utility-first styling |
| Org Chart | **d3-org-chart** | 3.x | Interactive org visualization |
| Charts | **Recharts** | 2.x | Dashboard & analytics charts |
| Data Tables | **@tanstack/react-table** | 8.x | Employee list, review list, etc. |
| Forms | **react-hook-form** + **zod** | - | Form state + schema validation |
| HTTP Client | **axios** or **ky** | - | API calls to FastAPI backend |
| Icons | **Lucide React** | latest | Consistent icon set |
| Date Utils | **date-fns** | 3.x | Date formatting |
| State | **@tanstack/react-query** | 5.x | Server state management, caching |

#### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | **Docker** + **Docker Compose** | Production deployment |
| Reverse Proxy | **Nginx** (in Docker) | Serve frontend + proxy API |
| Video | **ffmpeg** | Demo recording |

---

## 3. Module Specifications

### 3.1 Module: Authentication & Authorization

**Source**: PRD Section 8.1 (Field Worker UX Constraint), Org Chart PRD (RBAC)

#### 3.1.1 Backend Implementation

- `POST /api/auth/login` — accepts email + password, returns JWT access token + refresh token
- `POST /api/auth/refresh` — refresh expired access token
- `GET /api/auth/me` — returns current user profile with role
- JWT payload: `{user_id, email, role, employee_id, exp}`
- Access token expiry: 1 hour; Refresh token: 30 days
- Password hashing: bcrypt via passlib
- FastAPI dependency injection: `get_current_user()`, `require_role()`

#### 3.1.2 Demo Users (Pre-loaded)

| Username | Password | Role | Persona | Access Scope |
|----------|----------|------|---------|-------------|
| `admin@lumber.com` | `LumberAdmin2026!` | ADMIN | IT Ian | Full system access |
| `hr@lumber.com` | `LumberHR2026!` | HR_MANAGER | HR Helen | All HR features, all employees |
| `pm@lumber.com` | `LumberPM2026!` | PROJECT_MANAGER | Project Paula | Org chart, performance (own projects), analytics (limited) |
| `foreman@lumber.com` | `LumberForeman2026!` | FOREMAN | Foreman Francisco | Crew view, performance (own crew), own training |
| `worker@lumber.com` | `LumberWorker2026!` | EMPLOYEE | Tradesman Tony | Own profile, own reviews, own training |

#### 3.1.3 Role Permission Matrix

| Feature | ADMIN | HR_MANAGER | PROJECT_MANAGER | FOREMAN | EMPLOYEE |
|---------|-------|------------|-----------------|---------|----------|
| View Dashboard | ✅ Full | ✅ Full | ✅ Project scope | ✅ Crew scope | ✅ Personal |
| Manage Employees | ✅ CRUD all | ✅ CRUD all | 👁️ View only | 👁️ View crew | 👁️ Own profile |
| Org Chart | ✅ Full edit | ✅ Full edit | ✅ Project view | ✅ Crew view | 👁️ Read-only |
| Performance Reviews | ✅ All | ✅ All | ✅ Own team | ✅ Own crew | 👁️ Own reviews |
| Create Reviews | ✅ | ✅ | ✅ Direct reports | ✅ Direct reports | ❌ Self-review only |
| Goals (CRUD) | ✅ All | ✅ All | ✅ Team | ✅ Crew | ✅ Own |
| Incidents | ✅ All | ✅ All | ✅ Report + view | ✅ Report + view | 👁️ Own |
| Commendations | ✅ All | ✅ All | ✅ Give + view | ✅ Give + view | 👁️ Received |
| PIPs | ✅ All | ✅ All | ✅ Own team | ❌ View only | 👁️ Own |
| LMS Admin | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Training | ✅ All | ✅ All | ✅ Team | ✅ Crew | ✅ Own |
| Assign Training | ✅ | ✅ | ✅ Team | ❌ | ❌ |
| Certifications | ✅ All | ✅ All | ✅ Team | ✅ Crew | ✅ Own |
| Analytics | ✅ Full | ✅ Full | ✅ Limited | ❌ | ❌ |
| System Settings | ✅ | ❌ | ❌ | ❌ | ❌ |

#### 3.1.4 Frontend Auth Flow

- Login page with Lumber branding (mint green accent, dark nav)
- JWT stored in httpOnly cookie (or localStorage for simplicity in demo)
- Axios interceptor for automatic token refresh
- React context provider: `AuthProvider` with `useAuth()` hook
- Route guards: `<ProtectedRoute requiredRole={...}>`
- Role-based UI: conditional rendering of menu items, buttons, actions
- "Access Denied" page for unauthorized routes
- Logout clears token + redirects to login

---

### 3.2 Module: Dashboard

**Source**: PRD Section 4.5, Capabilities Analysis, Prototype v5 subpage "dashboard"

#### 3.2.1 API Endpoints

- `GET /api/dashboard/kpis` — returns all KPI values for current user's scope
- `GET /api/dashboard/charts` — returns chart data (headcount, trends, etc.)
- `GET /api/dashboard/activity` — returns recent activity feed

#### 3.2.2 KPI Cards (Admin/HR View)

| KPI | Calculation | Visual |
|-----|------------|--------|
| Total Headcount | `COUNT(employees WHERE status=ACTIVE)` | Number + trend vs last month |
| Open Positions | `COUNT(positions WHERE filled=false)` | Number + warning color |
| Pending Reviews | `COUNT(reviews WHERE status IN (DRAFT, IN_PROGRESS))` | Number + urgency |
| Expiring Certifications | `COUNT(certs WHERE expiration <= NOW()+30d)` | Number + red/yellow |
| Turnover Rate (YTD) | `terminations_ytd / avg_headcount × 100` | Percentage |
| Average Tenure | `AVG(NOW() - hire_date)` | Years + months |
| Training Compliance | `valid_required_certs / total_required_certs × 100` | % + progress bar |
| Active Projects | `COUNT(projects WHERE status=ACTIVE)` | Number |

#### 3.2.3 Charts (Recharts)

1. **Headcount by Department** — Horizontal bar chart (BarChart)
2. **Headcount Trend (12-month)** — Area/Line chart (AreaChart)
3. **Employee Type Distribution** — Donut chart (PieChart)
4. **Certification Compliance by Dept** — Stacked bar (BarChart)
5. **Recent Activity Feed** — Scrollable list component

#### 3.2.4 Role-Specific Dashboard Views

| Role | What they see |
|------|--------------|
| **Admin/HR** | Full KPIs, all charts, all activity |
| **Project Manager** | Project headcount, project performance summary, crew compliance |
| **Foreman** | Crew headcount, crew certs, pending crew reviews, recent incidents |
| **Employee** | Own training progress, upcoming reviews, personal cert status |

---

### 3.3 Module: Employee Management

**Source**: TSG "Core HR Records" (25 requirements), PRD Section 2, Prototype v5 subpage "employees"

#### 3.3.1 API Endpoints

```
GET    /api/employees              — List with search, filter, sort, pagination
GET    /api/employees/{id}         — Single employee with all relations
POST   /api/employees              — Create new employee
PUT    /api/employees/{id}         — Update employee
PATCH  /api/employees/{id}/status  — Change employment status
GET    /api/employees/{id}/history — Job history timeline
GET    /api/employees/{id}/audit   — Audit trail
DELETE /api/employees/{id}         — Soft delete (set status=TERMINATED)
GET    /api/employees/export       — CSV export with current filters
GET    /api/departments            — List all departments with hierarchy
GET    /api/divisions              — List all divisions
GET    /api/locations              — List all locations
```

#### 3.3.2 Employee List View (Frontend)

- `@tanstack/react-table` with server-side operations
- **Search**: Full-text search by name, employee number, email, job title
- **Filters** (sidebar or dropdown):
  - Department (multi-select)
  - Division (multi-select)
  - Employee Type (Full-time / Part-time / Contractor / Casual)
  - Status (Active / On Leave / Suspended / Terminated)
  - Trade (multi-select)
  - Union Status (Union / Non-union)
  - Location (multi-select)
- **Columns**: Avatar, Full Name, Employee #, Department, Job Title, Trade, Location, Status badge, Hire Date
- **Sort**: Click any column header
- **Pagination**: 25/50/100 per page with page navigation
- **Actions**: View Profile, Edit, Quick Status Change
- **Bulk**: Export CSV, Export PDF
- **Quick-add**: "New Employee" button (opens form)

#### 3.3.3 Employee Profile Page (Frontend)

Tabbed layout (following BambooHR pattern):

**Tab 1: Overview**
- Header: Avatar, Name, Title, Department badge, Status badge, Tenure
- Quick stats: Reports to (link), Direct reports count, Projects assigned
- Contact: Email, Phone, Address

**Tab 2: Employment**
- Job Title, Department, Division, Location
- Employee Type, Pay Rate, Pay Type
- Hire Date, Original Hire Date, Tenure (calculated)
- Cost Center, Bonus Eligible
- Reports To (with link)
- Direct Reports list (with links)

**Tab 3: Job History**
- Timeline visualization (vertical timeline)
- Each entry: Date range, Title, Department, Salary, Reason for change

**Tab 4: Union & Compliance**
- Union Name, Local, Seniority Date, Trade/Classification, CBA ref
- I-9 Status, Veteran Status, EEO Category
- Work Authorization details

**Tab 5: Performance**
- Mini-view of recent reviews (links to full review)
- Active goals with progress bars
- Recent incidents/commendations

**Tab 6: Training & Certs**
- Active certifications with expiry status (green/yellow/red)
- Training assignments with status
- Training transcript

**Tab 7: Audit Trail**
- Table: Timestamp, User, Field, Old Value, New Value
- Filterable by date range and field

#### 3.3.4 Employee Create/Edit Form

- Multi-step form or single long form with sections
- Validation via Pydantic (backend) + zod (frontend)
- Auto-generate Employee Number (format: `SCG-XXXXX`)
- Required fields marked, optional fields clearly indicated
- SSN masked input (last 4 visible to HR/Admin only)
- Department/Division/Location dropdowns populated from API
- "Reports To" searchable employee selector
- Photo upload (or default avatar by initials)

#### 3.3.5 TSG Requirements Coverage

All 25 Core HR Records requirements mapped:
- ✅ #1: PII storage with masking (SSN)
- ✅ #2: Multiple geographies/locations/divisions
- ✅ #3: Department cost centers
- ✅ #5: Employee hierarchy (reportsTo)
- ✅ #6: Multiple employee types (enum)
- ✅ #7: Auto-generated unique identifiers (SCG-XXXXX)
- ✅ #8: Job/salary/status history (JobHistory model)
- ✅ #9, #11: Union tracking (dedicated fields)
- ✅ #10: Tenure calculation (computed from hireDate)
- ✅ #12: Historic job details (JobHistory)
- ✅ #14: Configurable status codes (enum)
- ✅ #15: Notes field (open text)
- ✅ #17: Demographics (gender, ethnicity, veteran)
- ✅ #18: Life change support (status changes with effective dates)
- ✅ #19, #20: Employee self-service (EMPLOYEE role sees own profile)
- ✅ #21: Audit trail (AuditLog model)
- ✅ #22: Mass updates (bulk export/import)
- ✅ #23: Custom fields (bonusEligible, perDiem, travelAuth, vehicleAllowance)
- ✅ #24: Compliance records (i9, veteran, workAuth)

---

### 3.4 Module: Org Chart

**Source**: Lumber Org Chart PRD, TSG "Organizational Structure" (9 requirements), Prototype v5 subpage "orgchart"

#### 3.4.1 API Endpoints

```
GET /api/org-chart/corporate    — Full corporate hierarchy tree
GET /api/org-chart/projects     — Project/crew tree structure
GET /api/org-chart/node/{id}    — Single node with children
GET /api/org-chart/search       — Search employees in org context
GET /api/org-chart/span         — Span of control analytics
```

#### 3.4.2 Implementation: d3-org-chart Library

Using `d3-org-chart` (bumbeishvili) — the most feature-complete D3-based org chart library. It provides OUT OF THE BOX:
- ✅ Pan and zoom (mouse drag + scroll wheel)
- ✅ Click-to-expand/collapse branches with animation
- ✅ Custom node content (HTML templates)
- ✅ Search and highlight
- ✅ Fullscreen mode
- ✅ Export (PNG, SVG)
- ✅ Minimap navigation
- ✅ Fit-to-screen
- ✅ Horizontal/vertical layout toggle
- ✅ Paging for large datasets
- ✅ React integration

**What we add on top**:
- Custom node cards matching Lumber prototype design
- Corporate vs Project/Crew view toggle
- Span-of-control color coding
- Cert status indicators on nodes
- Click-to-open employee profile
- Breadcrumb navigation

#### 3.4.3 Node Card Design (matching Prototype v5)

```
┌──────────────────────────┐
│  [Photo]  Name           │
│           Job Title      │
│           Department     │
│  ─────────────────────── │
│  Trade Badge  | 👥 12    │
│  🟢 Certs OK | ⬛ Span:8│
└──────────────────────────┘
```

- Photo/avatar (40px circle)
- Full name (bold)
- Job title + department
- Trade badge (colored)
- Direct reports count
- Cert status indicator (🟢 valid, 🟡 expiring, 🔴 expired)
- Span of control indicator (green ≤8, yellow 9-12, red >12)

#### 3.4.4 Two Views (per Prototype v5)

**1. Corporate Hierarchy** (`renderCorp()` in prototype):
```
Summit Construction Group
├── CEO
├── Heavy Civil Division VP
│   ├── Bridge & Structures Director
│   │   ├── Superintendent
│   │   │   ├── Foreman → Workers
│   │   │   └── Foreman → Workers
│   │   └── Superintendent ...
│   ├── Highway & Roads Director ...
│   └── Utilities Director ...
├── Building Division VP ...
├── Specialty Division VP ...
└── Corporate (CFO, VP HR, etc.)
```

**2. Project/Crew View** (`renderProject()` in prototype):
```
Active Projects
├── Downtown Office Tower
│   ├── Crew A (Concrete) — Foreman: J. Martinez
│   │   ├── Worker 1
│   │   └── Worker 2 ...
│   ├── Crew B (Electrical) — Foreman: R. Johnson
│   └── Crew C (HVAC) — Foreman: M. Chen
├── I-95 Bridge Rehabilitation
│   ├── Crew A (Ironwork) ...
│   └── Crew B (Concrete) ...
└── ...
```

#### 3.4.5 Features from TSG Requirements

- ✅ TSG #1: Corporate hierarchy visualization
- ✅ TSG #2: Project/crew hierarchy visualization
- ✅ TSG #3: Drill-down by click (expand/collapse)
- ✅ TSG #4: Historical snapshots ("As of" date picker)
- ✅ TSG #5: Supervisor history (click node → see history)
- ✅ TSG #6: Delegate indicators (badge on nodes)
- ✅ TSG #9: Export as PNG, PDF, CSV

#### 3.4.6 Bilingual Support (Org Chart PRD)

- EN/ES toggle button in toolbar
- All labels, navigation, and tooltips translated
- Node cards respect language setting

---

### 3.5 Module: Performance Management

**Source**: Performance Management PRD, TSG "Performance Management" (15 requirements), Prototype v5 tabs: dashboard, cycles, review-form, incidents, commends

#### 3.5.1 API Endpoints

```
# Reviews
GET    /api/performance/reviews              — List reviews (filtered by scope/role)
GET    /api/performance/reviews/{id}         — Single review with all criteria
POST   /api/performance/reviews              — Create new review
PUT    /api/performance/reviews/{id}         — Update review
PATCH  /api/performance/reviews/{id}/sign    — Sign off (employee or manager)
PATCH  /api/performance/reviews/{id}/status  — Change review status

# Review Cycles
GET    /api/performance/cycles               — List review cycles
POST   /api/performance/cycles               — Create new cycle

# Goals
GET    /api/performance/goals                — List goals (filtered)
POST   /api/performance/goals                — Create goal
PUT    /api/performance/goals/{id}           — Update goal (progress, status)
DELETE /api/performance/goals/{id}           — Delete goal

# Incidents
GET    /api/performance/incidents            — List incidents
POST   /api/performance/incidents            — Log new incident
PUT    /api/performance/incidents/{id}       — Update incident (resolution)

# Commendations
GET    /api/performance/commendations        — List commendations
POST   /api/performance/commendations        — Create commendation

# PIPs
GET    /api/performance/pips                 — List PIPs
POST   /api/performance/pips                 — Create PIP
PUT    /api/performance/pips/{id}            — Update PIP
PATCH  /api/performance/pips/{id}/milestones — Update milestone status

# Calibration
GET    /api/performance/calibration          — 9-box grid data
```

#### 3.5.2 Performance Dashboard Tab

- Current review cycle status (% complete, overdue count)
- Performance rating distribution (histogram via Recharts)
- Goal completion rate by department
- Recent incidents summary
- Top commendation recipients

#### 3.5.3 Review Cycles Tab

- Table of review cycles: Name, Type, Period, Status, Progress bar, Due date
- "Create Cycle" modal: Select type (Annual/Mid-Year/30-60-90/Project Closeout), date range, departments included
- Cycle status: Draft → Active → In Progress → Completed
- Batch actions: Send reminders, export results

#### 3.5.4 Review Form Tab

**Review Types** (TSG #4):
1. Annual Review — comprehensive, all competencies
2. Mid-Year Check-in — lighter, progress focus
3. 30/60/90 Day Review — probationary, simplified
4. Project Closeout — project-specific evaluation
5. PIP Review — remediation tracking

**Form Sections** (matching Prototype v5):

**Section 1: Core Competencies** (TSG #8, #9 — configurable, weighted)
| Competency | Weight | Rating (1-5) | Comments |
|------------|--------|-------------|----------|
| Safety Compliance | 25% | ⭐⭐⭐⭐☆ | Text area |
| Quality of Work | 25% | ⭐⭐⭐⭐⭐ | Text area |
| Productivity & Efficiency | 20% | ⭐⭐⭐☆☆ | Text area |
| Teamwork & Communication | 15% | ⭐⭐⭐⭐☆ | Text area |
| Reliability & Attendance | 15% | ⭐⭐⭐⭐☆ | Text area |

Rating scale: 1=Unsatisfactory, 2=Needs Improvement, 3=Meets Expectations, 4=Exceeds Expectations, 5=Exceptional

**Section 2: Goal Achievement** — auto-populated from active goals with completion %

**Section 3: Overall Rating** — auto-calculated from weighted competency scores (TSG #9)

**Section 4: Manager Comments** — rich text area (TSG #7)

**Section 5: Employee Comments** — response text area

**Section 6: Development Plan** — recommended training, career path notes (TSG #12)

**Section 7: Signatures** — electronic sign-off with timestamps (TSG #6)
- Manager signs first
- Employee reviews and signs (or "Disagree" option with comment)
- Both signatures locked after submission

#### 3.5.5 Incidents Tab (matching Prototype v5 `modal-log-incident`)

- Incident list with filters: type, severity, date range, department, status
- "Log Incident" modal:
  - Employee selector (search)
  - Type: Safety Violation, Attendance Issue, Quality Issue, Conduct Issue
  - Severity: Minor, Moderate, Major, Critical (color-coded)
  - Date, Location, Description (text area)
  - Witnesses (text)
  - Status: Open → Investigating → Resolved → Closed
- Incident detail view with resolution workflow

#### 3.5.6 Commendations Tab (matching Prototype v5 `modal-log-commend`)

- Commendation feed (card layout, most recent first)
- "Give Commendation" modal:
  - Employee selector
  - Category: Safety, Quality, Teamwork, Above & Beyond
  - Star rating (1-5) (from `setCommendStars()` in prototype)
  - Description
  - Public/Private toggle
- Public commendations visible to all; private only to employee + HR

#### 3.5.7 Goals Management

- Goal list with progress bars and status badges
- "Create Goal" form:
  - Title, Description
  - Category: Safety / Quality / Productivity / Development / Leadership
  - Target Date, Weight (for review scoring)
  - Parent Goal (for cascading: company → dept → individual) (TSG #2)
- Inline progress update (slider 0-100%)
- Status transitions: Not Started → In Progress → At Risk → Completed/Deferred

#### 3.5.8 PIP Management

- PIP list with status and timeline
- PIP creation wizard:
  1. Issue description
  2. Improvement targets (checklist)
  3. Timeline (start date, end date)
  4. Check-in dates (milestones)
  5. Supporting documentation
- Milestone tracking: each milestone has title, due date, status (Pending/Completed/Missed)
- Outcome: Completed (employee improved), Extended, Failed (may lead to termination)

#### 3.5.9 Calibration View (9-Box Grid)

- 3×3 matrix: Performance (X) vs Potential (Y)
- Each cell shows employee cards (draggable)
- Filters: Department, Review Cycle
- Distribution percentages per cell
- Side-by-side comparison of similar roles

#### 3.5.10 TSG Requirements Coverage

All 15 Performance Management requirements:
- ✅ #1: Date-effective goals with version history
- ✅ #2: Cascading goals (company → dept → individual)
- ✅ #3: Goal tracking with % completion
- ✅ #4: Multiple review types (5 types)
- ✅ #5: Configurable intervals
- ✅ #6: Workflow with sign-off
- ✅ #7: Evidence/attachment support
- ✅ #8: Customizable criteria with weights
- ✅ #9: Weighted scoring calculation
- ✅ #10: Performance history timeline
- ✅ #11: Summary and detailed reporting
- ✅ #12: Development plan in review form
- ✅ #13: Performance → training link
- ✅ #14: PIP management
- ✅ #15: Performance → pay link (merit matrix)

---

### 3.6 Module: Learning Management System (LMS)

**Source**: PRD Section 4.3, TSG "Learning & Development" (25 requirements), Prototype v5 tabs: catalog, worker, manager, rules

#### 3.6.1 API Endpoints

```
# Courses
GET    /api/lms/courses                      — Course catalog (filtered)
GET    /api/lms/courses/{id}                 — Course detail
POST   /api/lms/courses                      — Create course (HR/Admin)
PUT    /api/lms/courses/{id}                 — Update course

# Certifications
GET    /api/lms/certifications               — List all certs (filtered)
GET    /api/lms/certifications/dashboard     — Compliance dashboard data
GET    /api/lms/certifications/expiring      — Expiring within 30/60/90 days
POST   /api/lms/certifications               — Add certification record

# Training Assignments
GET    /api/lms/assignments                  — List assignments (filtered)
POST   /api/lms/assignments                  — Assign training (single or bulk)
PATCH  /api/lms/assignments/{id}/status      — Update assignment status/completion

# Training Rules
GET    /api/lms/rules                        — List training rules
POST   /api/lms/rules                        — Create rule (auto-assign)

# Reports
GET    /api/lms/transcript/{employee_id}     — Employee training transcript
GET    /api/lms/compliance-gap               — Gap analysis report
```

#### 3.6.2 Catalog Tab (Prototype v5 `setLmsTab('catalog')`)

- Grid or list view of all courses
- Filter by: Category, Format, Trade, Required/Elective
- Course card: Title, Category badge, Format icon, Duration, Required indicator
- Click to open course detail:
  - Description, Prerequisites, Duration, Format
  - Certification granted upon completion
  - Provider information
  - Enrollment stats (completed/in-progress/total)

**Course Categories** (construction-specific):
- OSHA Safety (OSHA 10, OSHA 30, Confined Spaces, Fall Protection, Excavation Safety)
- Trade Certifications (Welding AWS D1.1, Crane Operation NCCCO, Rigging & Signaling)
- Equipment Operation (Forklift, Aerial Lift, Excavator, Boom Truck)
- Compliance (First Aid/CPR, Hazmat, Silica Awareness, Lead Abatement)
- Professional Development (Supervision Skills, Blueprint Reading, Estimating Basics)
- Company Policies (Drug & Alcohol Policy, Harassment Prevention, Code of Conduct)

#### 3.6.3 Worker Tab (Prototype v5 `setLmsTab('worker')`)

Employee-centric view:
- My Certifications: card list with status (🟢 valid, 🟡 expiring, 🔴 expired)
- My Training Assignments: table with status, due date, progress
- My Training Transcript: complete history of completed training
- Enrollment: self-enroll in elective courses

#### 3.6.4 Manager Tab (Prototype v5 `setLmsTab('manager')`)

Team oversight view:
- Team Certification Matrix: employees × required certs (✅/🟡/🔴/❌)
- Assign Training: select employees (individual or bulk), select course, set due date
- Team Compliance Rate: % bar
- Overdue Assignments: action list

#### 3.6.5 Rules Tab (Prototype v5 `setLmsTab('rules')`, `modal-new-rule`)

Auto-assignment rules:
- "When employee is hired in [department/trade] → assign [courses]"
- "When cert [name] expires in [days] → assign renewal [course]"
- "When review rating < [threshold] → assign [development courses]"
- Rules table: Name, Trigger, Action, Active toggle

#### 3.6.6 Certification Tracking Dashboard

- Overall compliance rate (big number + progress ring)
- Expiring in 30 days / 60 days / 90 days (three KPI cards)
- Compliance by Department (heatmap table)
- Expired certifications alert list (sorted by urgency)
- Drill-down: click department → see per-employee cert status

---

### 3.7 Module: Analytics & Reporting

**Source**: PRD Section 4.5, Prototype v5 subpage "analytics"

#### 3.7.1 API Endpoints

```
GET /api/analytics/workforce          — Headcount, turnover, tenure data
GET /api/analytics/performance        — Rating distributions, trends, completion rates
GET /api/analytics/training           — Compliance rates, training hours, cert forecasts
GET /api/analytics/organization       — Span of control, vacancies, hierarchy stats
```

#### 3.7.2 Four Dashboard Sections

**1. Workforce Overview**
- Headcount by department (horizontal BarChart)
- Headcount trend 12-month (AreaChart)
- Employee type distribution (PieChart/Donut)
- Average tenure by department (BarChart)
- Turnover rate by department (BarChart, with voluntary/involuntary split)
- New hires vs terminations over time (dual BarChart)

**2. Performance Analytics**
- Rating distribution histogram (BarChart)
- Performance trends by department over cycles (LineChart)
- Goal completion rates (BarChart)
- Review completion: on-time vs overdue (stacked BarChart)
- Incident frequency by type, department, month (BarChart, heatmap)

**3. Training & Compliance**
- Certification compliance rate by department (BarChart with threshold line)
- Training hours per employee (BarChart)
- Course completion rates (BarChart)
- Expiring certifications forecast 30/60/90 days (grouped BarChart)
- Top 10 courses by enrollment (BarChart)

**4. Organizational Health**
- Span of control distribution (histogram)
- Vacancy/fill rate by department (BarChart)
- Employee distribution by grade/level (PieChart)
- Cost center headcount analysis (table + chart)

#### 3.7.3 Chart Interactions & Export

- Hover tooltips on all charts
- Click to drill down (department → employees)
- Date range selector (all dashboards)
- Department filter (all dashboards)
- Export: CSV (data), PNG (chart image), PDF (full report)

---

## 4. Database Schema

### 4.1 SQLAlchemy Models (Unified Employee Data Model — Rippling pattern)

Employee is the CENTRAL entity. Everything connects to Employee.

```
Company ──< Division ──< Department ──< Employee (central)
                                            │
Location ──────────────────────────────────>│
                                            │
              ┌─────────────────────────────┤
              │         │         │         │         │
         JobHistory  Review   Goal    Certification  TrainingAssignment
                       │                                    │
                  ReviewCriteria                         Course
                       │
                   Signature
              │         │
          Incident  Commendation
              │
             PIP ──< PIPMilestone
              │
          AuditLog
              │
           Project ──< ProjectAssignment >── Employee
```

### 4.2 Model Definitions (Pydantic + SQLAlchemy)

**User** (auth only):
- id: UUID (primary key)
- email: str (unique, indexed)
- password_hash: str
- role: Enum(ADMIN, HR_MANAGER, PROJECT_MANAGER, FOREMAN, EMPLOYEE)
- employee_id: FK → Employee (nullable for admin-only users)
- is_active: bool
- created_at, updated_at: datetime

**Employee** (central entity):
- id: UUID
- employee_number: str (unique, auto-gen: "SCG-XXXXX")
- first_name, last_name: str
- email: str (unique)
- phone: str (nullable)
- address, city, state, zip: str (nullable)
- date_of_birth: date (nullable)
- ssn_encrypted: str (nullable, AES encrypted, only last 4 visible)
- gender: Enum(MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY) (nullable)
- ethnicity: str (nullable)
- veteran_status: bool (default false)
- photo_url: str (nullable)
- employee_type: Enum(FULL_TIME, PART_TIME, CONTRACTOR, CASUAL)
- status: Enum(ACTIVE, ON_LEAVE, SUSPENDED, TERMINATED)
- hire_date: date
- original_hire_date: date (nullable, for rehires)
- termination_date: date (nullable)
- termination_reason: str (nullable)
- department_id: FK → Department
- division_id: FK → Division
- location_id: FK → Location (nullable)
- job_title: str
- job_level: str (nullable, e.g., "Journeyman", "Apprentice", "Foreman", "Superintendent")
- trade: str (nullable, e.g., "Electrical", "Carpentry", "Plumbing")
- pay_rate: Decimal
- pay_type: Enum(HOURLY, SALARY)
- reports_to_id: FK → Employee (self-referential, nullable)
- union_name: str (nullable)
- union_local: str (nullable)
- union_seniority_date: date (nullable)
- cost_center: str (nullable)
- bonus_eligible: bool (default false)
- per_diem_eligible: bool (default false)
- travel_auth_level: str (nullable)
- vehicle_allowance: bool (default false)
- eeo_category: str (nullable)
- i9_status: str (nullable)
- work_auth_expiry: date (nullable)
- notes: text (nullable)
- emergency_contact_name: str (nullable)
- emergency_contact_phone: str (nullable)
- emergency_contact_relation: str (nullable)
- created_at, updated_at: datetime

**Company**: id, name, code, address, city, state, zip

**Division**: id, name, code, company_id (FK)

**Department**: id, name, code, division_id (FK), cost_center, manager_id (FK → Employee, nullable)

**Location**: id, name, address, city, state, type: Enum(OFFICE, FIELD, WAREHOUSE)

**Project**: id, name, code, status: Enum(ACTIVE, COMPLETED, PLANNED), location_id (FK), start_date, end_date, project_manager_id (FK → Employee)

**ProjectAssignment**: id, project_id (FK), employee_id (FK), role, crew_name, start_date, end_date

**JobHistory**: id, employee_id (FK), job_title, department_name, location_name, start_date, end_date, reason, salary, changed_by_id (FK → User)

**PerformanceReview**: id, employee_id (FK), reviewer_id (FK → Employee), review_cycle_id (FK), type: Enum(ANNUAL, MID_YEAR, THIRTY_SIXTY_NINETY, PROJECT_CLOSEOUT, PIP), status: Enum(DRAFT, SELF_REVIEW, MANAGER_REVIEW, PENDING_SIGN_OFF, COMPLETED, CANCELLED), period_start, period_end, due_date, overall_rating: Float (nullable), manager_comments, employee_comments, development_plan, completed_at, created_at

**ReviewCycle**: id, name, type, period_start, period_end, status: Enum(DRAFT, ACTIVE, IN_PROGRESS, COMPLETED), departments (JSON array of dept IDs)

**ReviewCriteria**: id, review_id (FK), name, category, weight: Float, rating: Int (1-5, nullable), comments

**Goal**: id, employee_id (FK), parent_goal_id (FK → Goal, nullable for cascading), title, description, category: Enum(SAFETY, QUALITY, PRODUCTIVITY, DEVELOPMENT, LEADERSHIP), target_date, weight: Float, percent_complete: Int (0-100), status: Enum(NOT_STARTED, IN_PROGRESS, AT_RISK, COMPLETED, DEFERRED), created_at, updated_at

**Incident**: id, employee_id (FK), reported_by_id (FK → Employee), type: Enum(SAFETY, ATTENDANCE, QUALITY, CONDUCT), severity: Enum(MINOR, MODERATE, MAJOR, CRITICAL), description, incident_date, location, witnesses, status: Enum(OPEN, INVESTIGATING, RESOLVED, CLOSED), resolution, created_at

**Commendation**: id, employee_id (FK), awarded_by_id (FK → Employee), category: Enum(SAFETY, QUALITY, TEAMWORK, ABOVE_AND_BEYOND), stars: Int (1-5), description, is_public: bool, created_at

**Course**: id, title, description, category, format: Enum(E_LEARNING, INSTRUCTOR_LED, TOOLBOX_TALK), duration_hours: Float, prerequisites (JSON), certification_granted: str (nullable), provider, is_required: bool, trade_specific: str (nullable), created_at

**TrainingAssignment**: id, employee_id (FK), course_id (FK), assigned_by_id (FK → User), status: Enum(ASSIGNED, IN_PROGRESS, COMPLETED, OVERDUE), due_date, completed_date (nullable), score: Float (nullable), created_at

**Certification**: id, employee_id (FK), name, issuing_body, cert_number, issue_date, expiration_date (nullable), status: Enum(VALID, EXPIRING_SOON, EXPIRED, REVOKED), attachment_url (nullable), course_id (FK, nullable), created_at

**TrainingRule**: id, name, trigger_type: Enum(NEW_HIRE, CERT_EXPIRING, LOW_REVIEW_SCORE), trigger_config (JSON), action_course_ids (JSON), is_active: bool, created_at

**PIP**: id, employee_id (FK), created_by_id (FK → User), issue_description, improvement_targets (JSON), start_date, end_date, status: Enum(ACTIVE, COMPLETED, EXTENDED, FAILED), outcome, created_at

**PIPMilestone**: id, pip_id (FK), title, description, due_date, completed_date (nullable), status: Enum(PENDING, COMPLETED, MISSED)

**AuditLog**: id, entity_type: str, entity_id: UUID, action: Enum(CREATE, UPDATE, DELETE), field: str (nullable), old_value: str (nullable), new_value: str (nullable), user_id (FK → User), timestamp: datetime

---

## 5. Seed Data Specification

### 5.1 Company Structure: Summit Construction Group

```
Summit Construction Group (SCG)
├── Heavy Civil Division (VP: Robert "Bob" Anderson)
│   ├── Bridge & Structures Dept (45 employees)
│   │   Director: Sarah Chen | Supts: 3 | Foremans: 6 | Workers: 35
│   ├── Highway & Roads Dept (52 employees)
│   │   Director: Marcus Williams | Supts: 3 | Foremans: 7 | Workers: 41
│   └── Utilities Dept (38 employees)
│       Director: Patricia Gonzalez | Supts: 2 | Foremans: 5 | Workers: 30
├── Building Division (VP: Jennifer "Jen" Thompson)
│   ├── Commercial Construction Dept (48 employees)
│   │   Director: David Kim | Supts: 3 | Foremans: 6 | Workers: 38
│   ├── Industrial Construction Dept (35 employees)
│   │   Director: Michael O'Brien | Supts: 2 | Foremans: 5 | Workers: 27
│   └── Renovation & Retrofit Dept (28 employees)
│       Director: Lisa Patel | Supts: 2 | Foremans: 4 | Workers: 21
├── Specialty Division (VP: James "Jim" Rodriguez)
│   ├── Electrical Dept (32 employees)
│   │   Director: Carlos Martinez | Supts: 2 | Foremans: 4 | Workers: 25
│   ├── Mechanical/HVAC Dept (28 employees)
│   │   Director: Amanda Foster | Supts: 2 | Foremans: 4 | Workers: 21
│   └── Plumbing & Fire Protection Dept (22 employees)
│       Director: Kevin Washington | Supts: 1 | Foremans: 3 | Workers: 17
└── Corporate (COO: Thomas "Tom" Mitchell)
    ├── Executive Office (8) — CEO: Richard Sterling
    ├── Human Resources (12) — VP HR: Sandra Lopez
    ├── Finance & Accounting (10) — CFO: Daniel Park
    ├── Safety & Compliance (8) — Dir: Frank Murphy
    ├── Estimating (6) — Dir: Rachel Torres
    └── IT & Technology (5) — Dir: Brian Chang
```

**Total: ~377 employees**

### 5.2 Projects (8 active)

| Project | Division | Type | Workers | Crews |
|---------|----------|------|---------|-------|
| Downtown Office Tower | Building/Commercial | New construction | 45 | 4 |
| I-95 Bridge Rehabilitation | Heavy Civil/Bridge | Rehabilitation | 38 | 3 |
| Municipal Water Treatment | Heavy Civil/Utilities | Infrastructure | 30 | 3 |
| Amazon Distribution Center | Building/Industrial | New construction | 35 | 3 |
| Hospital Wing Addition | Building/Commercial | Addition | 28 | 3 |
| Highway 301 Widening | Heavy Civil/Highway | Expansion | 40 | 4 |
| Solar Farm Electrical | Specialty/Electrical | New construction | 22 | 2 |
| Residential Complex HVAC | Specialty/Mechanical | New construction | 18 | 2 |

### 5.3 Demographics Distribution

- Gender: 85% male, 15% female (construction industry realistic)
- Job levels: 60% journeyman, 20% apprentice, 10% foreman, 5% superintendent, 5% admin/mgmt
- Union: 40% union, 60% non-union
- Type: 70% full-time, 15% part-time, 15% contractor
- Tenure: 30% <1yr, 30% 1-5yr, 25% 5-15yr, 15% >15yr
- Trades: Carpentry, Electrical, Plumbing, Ironwork, Concrete, Welding, Heavy Equipment, HVAC, Pipe Fitting, Painting, Roofing, Drywall

### 5.4 Performance Data (pre-seeded)

- 1 completed annual review cycle (Q4 2025) — ~300 reviews with varied ratings (bell curve: 5% rating=1, 15% rating=2, 50% rating=3, 25% rating=4, 5% rating=5)
- 1 active mid-year cycle (Q2 2026, in progress) — ~50 reviews in various states
- 45 active goals spread across ~30 employees
- 12 incidents (3 safety, 4 attendance, 3 quality, 2 conduct; mixed severity)
- 25 commendations (8 safety, 7 quality, 6 teamwork, 4 above & beyond)
- 3 active PIPs with milestones
- 8 recent 30/60/90 day reviews for new hires

### 5.5 Training & Certification Data (pre-seeded)

- 35 courses in catalog across all categories
- 600+ training assignments (70% completed, 20% in-progress, 10% overdue)
- 450+ certifications:
  - 75% valid (expiration > 90 days)
  - 12% expiring soon (30-90 days)
  - 8% expiring critical (< 30 days)
  - 5% expired
- All field workers: OSHA 10 cert
- All superintendents/foremen: OSHA 30 cert
- Trade-specific: welding certs (AWS D1.1), crane (NCCCO), rigging, confined space, aerial lift
- 5 active training rules (new hire auto-assign, cert renewal, etc.)

---

## 6. UI/UX Specifications

### 6.1 Branding (Lumber — Exact from Prototype v5)

CSS custom properties extracted from `lumber_hris_prototype_v5.html`:

```css
:root {
  --nav-bg: #1e2d3b;         /* Dark blue-gray sidebar/header */
  --nav-text: #c8d6e2;       /* Light text on nav */
  --nav-hover: rgba(255,255,255,.08);
  --nav-active: #7aecb4;     /* MINT GREEN — Lumber accent */
  --page-bg: #f0f2f5;        /* Light gray page background */
  --white: #ffffff;
  --border: #e2e6ea;
  --border2: #d0d5dd;
  --t1: #111827;              /* Text primary */
  --t2: #374151;              /* Text secondary */
  --t3: #6b7280;              /* Text tertiary */
  --t4: #9ca3af;              /* Text muted */
  --mint: #7aecb4;            /* Primary accent */
  --mint2: #5dd4a0;           /* Darker mint */
  --mint-bg: rgba(122,236,180,.1);
  --blue: #2563eb;            /* Secondary accent */
  --blue-bg: rgba(37,99,235,.08);
  --red: #dc2626;             /* Danger/alert */
  --red-bg: rgba(220,38,38,.07);
  --yellow: #d97706;          /* Warning */
  --yellow-bg: rgba(217,119,6,.07);
  --orange: #ea580c;
  --purple: #7c3aed;
  --nav-h: 52px;              /* Top nav height */
  --sub-h: 44px;              /* Sub-nav/tabs height */
}
```

### 6.2 Layout (matching Prototype v5 structure)

```
┌────────────────────────────────────────────────────────────────┐
│ [🪵] Lumber HRIS    [🔍 Search...]           [🔔 3] [👤 HR Helen ▼] │
├────────────┬───────────────────────────────────────────────────┤
│            │ ┌─ Sub-nav tabs ──────────────────────────────┐  │
│  Dashboard │ │ Dashboard | Employees | OrgChart | Perf ... │  │
│  Time      │ └────────────────────────────────────────────┘  │
│  Pay       │                                                  │
│  HRIS ◄──  │       Main Content Area                         │
│  Scheduler │       (scrollable)                               │
│  Resources │                                                  │
│  Reports   │       Charts, Tables, Forms, etc.               │
│            │                                                  │
│ ────────── │                                                  │
│  ⚙️ Settings│                                                  │
│            │                                                  │
└────────────┴──────────────────────────────────────────────────┘
```

**Navigation hierarchy** (from Prototype v5):
- Top-level sidebar: Module selector (HRIS, Time, Pay, Scheduler, Resources, Reports)
- Sub-nav bar: Subpages within HRIS (Dashboard, Employees, Org Chart, Performance, LMS, Analytics)
- For Performance: additional tab bar (Dashboard, Cycles, Review Form, Incidents, Commendations)
- For LMS: additional tab bar (Catalog, Worker, Manager, Rules)

### 6.3 Component Library (shadcn/ui)

Required components from shadcn/ui:
- **Layout**: Sidebar, Tabs, Breadcrumb, Separator
- **Data Display**: Table, Card, Badge, Avatar, Calendar, Progress
- **Forms**: Input, Select, Textarea, Checkbox, RadioGroup, DatePicker, Switch, Slider
- **Feedback**: Alert, Toast, Dialog/Modal, Tooltip, Skeleton (loading)
- **Navigation**: Button, DropdownMenu, Command (search), NavigationMenu

### 6.4 Responsive Design

- Desktop-first (HR admin primary use case)
- Tablet: sidebar collapses to icons, tables scroll horizontally
- Mobile: stacked layouts, hamburger menu, touch targets ≥44px

---

## 7. Development Phases & Checkpoints

### CRITICAL RULE: Opus Quality Gates

After **EVERY phase**, Opus will:
1. **Read all generated code** files in the phase
2. **Run the application** and verify it works
3. **Check against PRD requirements** (specific requirement IDs)
4. **Verify UI** matches Lumber prototype colors and structure
5. **Test edge cases** and error handling
6. **Log checkpoint results** (PASS/FAIL with details)
7. **Only proceed** to next phase if checkpoint PASSES

If checkpoint FAILS → fix issues → re-verify → only then proceed.

---

### Phase 1: Project Scaffolding + Database + Seed Data
**Duration**: 60-90 min
**Checkpoint**: SETUP_01

**Backend Tasks**:
1.1. Create project structure: `backend/` directory with FastAPI app
1.2. Install dependencies to `.pylibs/`: fastapi, uvicorn, sqlalchemy, pydantic, python-jose, passlib, bcrypt, aiofiles, python-multipart, alembic
1.3. Define all SQLAlchemy models (Section 4.2)
1.4. Define all Pydantic schemas (request/response)
1.5. Create database initialization (SQLite for dev)
1.6. Build comprehensive seed script (Section 5)
1.7. Verify: run seed, check 377+ employees created, all relations correct

**Frontend Tasks**:
1.8. Initialize Vite + React + TypeScript project: `frontend/` directory
1.9. Install dependencies: react-router, shadcn/ui, tailwind, axios, recharts, @tanstack/react-table, react-hook-form, zod, d3-org-chart, lucide-react, date-fns, @tanstack/react-query
1.10. Configure Tailwind with Lumber colors (Section 6.1)
1.11. Set up project structure (pages, components, hooks, lib, types)
1.12. Verify: `npm run dev` starts without errors

**Checkpoint SETUP_01 Criteria**:
- [ ] FastAPI app starts (`uvicorn main:app`)
- [ ] All SQLAlchemy models compile and create tables
- [ ] Database seeded: 377+ employees, 9 departments, 8 projects, 35 courses, 450+ certs
- [ ] All demo users created with correct roles
- [ ] Frontend dev server starts (`npm run dev`)
- [ ] Tailwind configured with Lumber colors
- [ ] API docs accessible at `/docs` (Swagger)

---

### Phase 2: Authentication + App Shell
**Duration**: 45-60 min
**Checkpoint**: AUTH_01

**Backend Tasks**:
2.1. Implement auth endpoints: `POST /api/auth/login`, `/refresh`, `GET /api/auth/me`
2.2. JWT token generation with role in payload
2.3. Password verification with bcrypt
2.4. FastAPI dependency: `get_current_user()` with role checking
2.5. CORS configuration for frontend origin

**Frontend Tasks**:
2.6. Create Login page with Lumber branding
2.7. Implement AuthContext + useAuth hook
2.8. Axios interceptor for JWT token management
2.9. Build AppShell layout: sidebar + header + sub-nav + content area
2.10. Implement sidebar navigation (matching prototype modules)
2.11. Implement sub-nav tabs for HRIS subpages
2.12. Role-based menu visibility
2.13. User dropdown (name, role, logout)
2.14. Protected route wrapper component
2.15. "Access Denied" page

**Checkpoint AUTH_01 Criteria**:
- [ ] All 5 demo users can log in successfully
- [ ] Invalid credentials show error message
- [ ] JWT token returned and stored
- [ ] Protected routes redirect to login when not authenticated
- [ ] Role-based menu items: Admin sees everything, Employee sees limited
- [ ] Sidebar matches prototype style (dark bg, mint accent)
- [ ] Sub-nav tabs appear for HRIS module
- [ ] User menu shows name and role
- [ ] Logout clears session and redirects
- [ ] Swagger docs show auth endpoints working

---

### Phase 3: Employee Management
**Duration**: 75-90 min
**Checkpoint**: EMP_01

**Backend Tasks**:
3.1. Employee CRUD endpoints (all from Section 3.3.1)
3.2. Search: full-text across name, employee_number, email, job_title
3.3. Filter: department, division, status, type, trade, union, location
3.4. Pagination: offset/limit with total count
3.5. Sort: any field, ascending/descending
3.6. Employee detail with all relations loaded (department, reports_to, direct_reports)
3.7. Job history endpoint
3.8. Audit trail logging on every CREATE/UPDATE/DELETE
3.9. CSV export endpoint with current filters applied
3.10. Status change endpoint with effective date and reason

**Frontend Tasks**:
3.11. Employee List page with @tanstack/react-table
3.12. Search bar (debounced, server-side)
3.13. Filter panel (sidebar or dropdown, multi-select)
3.14. Column sorting (click headers)
3.15. Pagination controls
3.16. Employee Profile page with tabs (Section 3.3.3)
3.17. Job History timeline component
3.18. Create Employee form with validation
3.19. Edit Employee form (pre-populated)
3.20. Status Change modal
3.21. Audit Trail table (Tab 7)
3.22. CSV Export button
3.23. Employee role self-service view (limited profile)

**Checkpoint EMP_01 Criteria**:
- [ ] Employee list loads 377+ employees
- [ ] Search finds employees by name, ID, email
- [ ] All 7 filters work correctly
- [ ] Pagination shows correct page counts
- [ ] Sorting works on all columns
- [ ] Employee profile shows all data across tabs
- [ ] Job history timeline renders correctly
- [ ] Create employee works with validation errors displayed
- [ ] Edit employee saves changes with audit trail entry
- [ ] Status change creates JobHistory entry
- [ ] CSV export downloads valid file
- [ ] Employee role user sees only own profile (self-service)
- [ ] HR role user sees all employees
- [ ] API docs show all employee endpoints

---

### Phase 4: Org Chart
**Duration**: 60-75 min
**Checkpoint**: ORG_01

**Backend Tasks**:
4.1. Corporate hierarchy endpoint (returns tree structure from reports_to chain)
4.2. Project/crew endpoint (returns projects → crews → workers)
4.3. Node detail endpoint
4.4. Search endpoint (find employee in org context)
4.5. Span of control analytics endpoint

**Frontend Tasks**:
4.6. Integrate d3-org-chart library
4.7. Custom node template matching Lumber design (Section 3.4.3)
4.8. Corporate Hierarchy view (default)
4.9. Project/Crew view (toggle)
4.10. View toggle button with animated transition
4.11. Search overlay: type name → zoom to employee
4.12. Breadcrumb navigation
4.13. Span-of-control color indicators on nodes
4.14. Cert status indicators on nodes (green/yellow/red dot)
4.15. Click node → open employee profile (navigate or side panel)
4.16. Fullscreen toggle
4.17. Zoom controls (fit, zoom in/out, reset)
4.18. Export toolbar (PNG, CSV)
4.19. EN/ES language toggle

**Checkpoint ORG_01 Criteria**:
- [ ] Org chart renders full hierarchy (377 nodes)
- [ ] Pan and zoom work smoothly (no lag)
- [ ] Expand/collapse branches with animation
- [ ] Corporate view shows correct department hierarchy
- [ ] Project view shows correct crew assignments
- [ ] View toggle switches smoothly
- [ ] Search finds employee and centers on them
- [ ] Breadcrumbs update correctly
- [ ] Node cards show: photo, name, title, dept, reports count, cert status
- [ ] Span of control colors: green ≤8, yellow 9-12, red >12
- [ ] Click node opens employee profile
- [ ] Export PNG produces valid image
- [ ] EN/ES toggle translates labels
- [ ] No performance issues (smooth at 377 nodes)

---

### Phase 5: Performance Management
**Duration**: 90-120 min (most complex module)
**Checkpoint**: PERF_01

**Backend Tasks**:
5.1. Review CRUD endpoints (Section 3.5.1)
5.2. Review cycle management
5.3. Weighted scoring calculation engine
5.4. Goal CRUD with cascading support
5.5. Incident CRUD with severity/type filtering
5.6. Commendation CRUD with star ratings
5.7. PIP CRUD with milestone management
5.8. Sign-off workflow (manager + employee)
5.9. Calibration data endpoint (9-box grid aggregation)
5.10. Performance history endpoint (timeline data)

**Frontend Tasks**:
5.11. Performance Dashboard tab (charts, metrics)
5.12. Review Cycles tab (table, create cycle modal)
5.13. Review Form (full multi-section form matching Section 3.5.4)
5.14. Competency rating component (star/slider + weight display)
5.15. Overall rating auto-calculation display
5.16. Sign-off workflow UI (manager sign → employee sign)
5.17. Goals management page (cards with progress bars)
5.18. Goal create/edit modal
5.19. Incidents tab (table + log incident modal)
5.20. Incident detail view with resolution form
5.21. Commendations tab (card feed + give commendation modal)
5.22. PIP management page (list + create wizard)
5.23. PIP milestone tracker
5.24. Performance history timeline (per employee)
5.25. Calibration 9-box grid view

**Checkpoint PERF_01 Criteria**:
- [ ] Performance dashboard shows correct metrics
- [ ] Review cycles list with correct statuses
- [ ] Create review cycle works
- [ ] Review form renders all 7 sections
- [ ] Competency ratings save correctly with weights
- [ ] Overall rating auto-calculates from weighted scores
- [ ] Manager sign-off captures signature/timestamp
- [ ] Employee sign-off works (with agree/disagree)
- [ ] Goals CRUD: create, update progress, complete
- [ ] Goal cascading displays (parent → child)
- [ ] Incident logging works with all fields
- [ ] Incident resolution workflow
- [ ] Commendation stars work (1-5)
- [ ] PIP creation wizard (all steps)
- [ ] PIP milestones track completion
- [ ] Performance timeline renders correctly
- [ ] Calibration 9-box grid shows correct placement
- [ ] FOREMAN sees only own crew's reviews
- [ ] EMPLOYEE sees only own reviews and self-review

---

### Phase 6: LMS (Learning Management)
**Duration**: 60-75 min
**Checkpoint**: LMS_01

**Backend Tasks**:
6.1. Course CRUD endpoints
6.2. Certification CRUD with status calculation (auto-set EXPIRING_SOON/EXPIRED)
6.3. Compliance dashboard aggregation endpoint
6.4. Training assignment CRUD (individual + bulk)
6.5. Training rules engine (auto-assign on triggers)
6.6. Employee training transcript endpoint
6.7. Compliance gap analysis endpoint

**Frontend Tasks**:
6.8. Catalog tab (grid/list view with filters)
6.9. Course detail view
6.10. Worker tab (my certs, my training, transcript)
6.11. Manager tab (team cert matrix, assign training, compliance)
6.12. Rules tab (rules table, create rule modal)
6.13. Certification status cards (green/yellow/red)
6.14. Compliance dashboard (progress ring, KPI cards, dept breakdown)
6.15. Training assignment form (single + bulk)
6.16. Expiring certs alert list
6.17. Gap analysis view (employees × required certs)

**Checkpoint LMS_01 Criteria**:
- [ ] Course catalog shows 35 courses
- [ ] Filters: category, format, trade, required
- [ ] Course detail shows all info
- [ ] Worker tab: employee sees own certs and training
- [ ] Manager tab: cert matrix renders correctly
- [ ] Assign training works (individual employee, set due date)
- [ ] Bulk assign works (by department/trade)
- [ ] Certification status colors correct (green/yellow/red based on expiry)
- [ ] Compliance dashboard: correct percentages
- [ ] Expiring certs list sorted by urgency
- [ ] Training transcript complete for seeded data
- [ ] Rules table shows 5 rules
- [ ] Create new rule modal works
- [ ] Gap analysis shows missing required certs

---

### Phase 7: Dashboard & Analytics
**Duration**: 45-60 min
**Checkpoint**: ANALYTICS_01

**Backend Tasks**:
7.1. Dashboard KPI aggregation endpoint
7.2. Workforce analytics endpoint (headcount, turnover, tenure)
7.3. Performance analytics endpoint (ratings, trends, completion)
7.4. Training analytics endpoint (compliance, hours, forecasts)
7.5. Organization analytics endpoint (span, vacancies, distribution)
7.6. All endpoints support date range and department filters

**Frontend Tasks**:
7.7. Dashboard page: KPI cards row (Section 3.2.2)
7.8. Headcount by Department chart (horizontal BarChart)
7.9. Headcount Trend 12-month (AreaChart)
7.10. Employee Type Distribution (PieChart/Donut)
7.11. Certification Compliance by Dept (stacked BarChart)
7.12. Recent Activity Feed component
7.13. Analytics page: 4 dashboard sections
7.14. Performance distribution histogram
7.15. Turnover analysis chart
7.16. Training compliance forecast chart
7.17. Date range picker filter (global)
7.18. Department filter (global)
7.19. Export: CSV data download, PNG chart capture
7.20. Role-specific dashboard views (foreman=crew, employee=personal)

**Checkpoint ANALYTICS_01 Criteria**:
- [ ] Dashboard KPIs show correct numbers (verified against DB)
- [ ] All Recharts charts render with correct data
- [ ] Charts have hover tooltips
- [ ] Date range filter updates all charts
- [ ] Department filter works across all charts
- [ ] CSV export produces valid data
- [ ] Admin sees full dashboard
- [ ] Foreman sees crew-scoped dashboard
- [ ] Employee sees personal dashboard
- [ ] Analytics page loads all 4 sections
- [ ] No performance issues with large dataset
- [ ] Activity feed shows recent events

---

### Phase 8: Docker, Polish & Cross-Module Integration
**Duration**: 45-60 min
**Checkpoint**: DOCKER_01

**Tasks**:
8.1. Backend Dockerfile (Python, multi-stage, production)
8.2. Frontend Dockerfile (Node build + Nginx serve)
8.3. docker-compose.yml (frontend + backend + PostgreSQL + Nginx)
8.4. PostgreSQL configuration + init script
8.5. .env.example with all variables documented
8.6. start-dev.sh script (SQLite, local development)
8.7. README.md with complete setup + usage instructions
8.8. Cross-module navigation testing:
  - Employee profile → Org Chart (show in tree)
  - Employee profile → Performance tab (reviews, goals)
  - Employee profile → Training tab (certs, assignments)
  - Review form → Employee profile
  - Org chart node → Employee profile
  - LMS cert → Employee profile
  - Performance incident → Employee profile
8.9. Loading states (skeleton/spinner on all data fetches)
8.10. Empty states (friendly messages when no data)
8.11. Error states (error boundaries, API error handling)
8.12. Final UI polish pass:
  - Alignment and spacing consistency
  - Color consistency with prototype
  - Button styles, badge styles, status colors
  - Responsive check (tablet/mobile)
8.13. Console error cleanup

**Checkpoint DOCKER_01 Criteria**:
- [ ] Backend Dockerfile builds successfully
- [ ] Frontend Dockerfile builds successfully
- [ ] docker-compose.yml is syntactically valid
- [ ] README has clear step-by-step instructions
- [ ] .env.example documents all variables
- [ ] start-dev.sh works on a clean checkout
- [ ] All cross-module links navigate correctly
- [ ] All pages have loading states
- [ ] All empty tables show "No data" message
- [ ] API errors show user-friendly messages
- [ ] No console errors in browser
- [ ] Responsive on tablet viewport

---

### Phase 9: Video Demo
**Duration**: 30-45 min
**Checkpoint**: FINAL

**Tasks**:
9.1. Write demo script with timestamps (Section 9.2)
9.2. Start app and prepare demo data view
9.3. Record screen + narrate in English (using ffmpeg)
9.4. Add background music (from TOOLS.md settings)
9.5. Export final video
9.6. Send to Franco via WhatsApp (after approval)

**Demo Script** (English narration):

| Time | Scene | Narration |
|------|-------|-----------|
| 0:00 | Login page | "Welcome to Lumber HRIS, a complete human resource management system built for the construction industry." |
| 0:20 | Login as HR Helen | "Let's log in as Helen, our HR Manager." |
| 0:30 | Dashboard | "The dashboard shows key workforce metrics at a glance: headcount, pending reviews, expiring certifications, turnover rate." |
| 1:00 | Dashboard charts | "Charts provide visual breakdowns by department, employee type, and compliance status." |
| 1:30 | Employee list | "The employee directory manages over 375 employees with search, filters, and sorting." |
| 2:00 | Employee profile | "Each employee profile has comprehensive tabs: employment details, job history, union information, performance, training, and audit trail." |
| 2:30 | Create employee | "Creating a new employee with validation and auto-generated ID." |
| 3:00 | Org Chart corporate | "The interactive org chart shows the corporate hierarchy. Pan, zoom, expand, collapse, and search for any employee." |
| 3:30 | Org Chart project | "Switch to project view to see crews organized by construction project." |
| 4:00 | Org Chart features | "Each node shows the employee's trade, certification status, and span of control." |
| 4:30 | Performance dashboard | "Performance management tracks review cycles, goals, incidents, and commendations." |
| 5:00 | Review form | "Reviews use weighted competencies with automatic overall score calculation." |
| 5:30 | Goals + Incidents | "Goals cascade from company to department to individual. Incidents are logged with severity and resolution tracking." |
| 6:00 | Calibration grid | "The 9-box calibration grid helps calibrate ratings across the organization." |
| 6:30 | LMS catalog | "The learning management system has 35+ courses including OSHA safety, trade certifications, and equipment operation." |
| 7:00 | Cert tracking | "Certification tracking shows compliance rates and alerts for expiring certifications." |
| 7:30 | LMS manager view | "Managers can view their team's certification matrix and assign training." |
| 8:00 | Analytics | "Analytics provides four dashboards: workforce, performance, training compliance, and organizational health." |
| 8:30 | Login as Foreman | "Logging in as Foreman Francisco shows a crew-scoped view — he only sees his own team." |
| 9:00 | Login as Employee | "And as Tradesman Tony, the employee portal shows personal information, own reviews, and training status." |
| 9:15 | Closing | "Lumber HRIS — built for construction, powered by modern technology. FastAPI backend, React frontend, fully dockerized." |

---

## 8. File Structure

```
lumber-hris/
├── PLAN.md                           # This document
├── README.md                         # Setup & usage instructions
├── docker-compose.yml                # Production deployment
├── start-dev.sh                      # Local development script
├── .env.example                      # Environment variables
│
├── backend/
│   ├── Dockerfile                    # Python production build
│   ├── requirements.txt              # Python dependencies
│   ├── main.py                       # FastAPI app entry point
│   ├── config.py                     # Settings (DB URL, JWT secret, etc.)
│   ├── database.py                   # SQLAlchemy engine + session
│   ├── seed.py                       # Seed data script
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                   # User model
│   │   ├── employee.py               # Employee model (central)
│   │   ├── organization.py           # Company, Division, Department, Location
│   │   ├── project.py                # Project, ProjectAssignment
│   │   ├── performance.py            # Review, ReviewCriteria, Goal, ReviewCycle
│   │   ├── incident.py               # Incident, Commendation
│   │   ├── pip.py                    # PIP, PIPMilestone
│   │   ├── lms.py                    # Course, TrainingAssignment, Certification, TrainingRule
│   │   ├── audit.py                  # AuditLog
│   │   └── job_history.py            # JobHistory
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                   # Login, Token, UserResponse
│   │   ├── employee.py               # EmployeeCreate, EmployeeUpdate, EmployeeResponse, etc.
│   │   ├── organization.py           # Department, Division, Location schemas
│   │   ├── performance.py            # Review, Goal, Incident, Commendation, PIP schemas
│   │   ├── lms.py                    # Course, Certification, Assignment, Rule schemas
│   │   └── analytics.py              # Dashboard KPIs, chart data schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                   # /api/auth/*
│   │   ├── employees.py              # /api/employees/*
│   │   ├── departments.py            # /api/departments/*
│   │   ├── org_chart.py              # /api/org-chart/*
│   │   ├── performance.py            # /api/performance/*
│   │   ├── lms.py                    # /api/lms/*
│   │   ├── analytics.py              # /api/analytics/*
│   │   └── dashboard.py              # /api/dashboard/*
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py           # JWT, password hashing
│   │   ├── employee_service.py       # Employee business logic
│   │   ├── performance_service.py    # Review scoring, calibration
│   │   ├── lms_service.py            # Cert status calc, compliance
│   │   └── analytics_service.py      # Aggregation queries
│   └── utils/
│       ├── __init__.py
│       ├── dependencies.py           # FastAPI deps (get_current_user, require_role)
│       ├── audit.py                  # Audit trail helper
│       └── helpers.py                # Misc utilities
│
├── frontend/
│   ├── Dockerfile                    # Node build + Nginx
│   ├── nginx.conf                    # Nginx config (serve + proxy API)
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts            # Lumber brand colors
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx                  # React entry
│   │   ├── App.tsx                   # Router + providers
│   │   ├── api/
│   │   │   ├── client.ts             # Axios instance with interceptors
│   │   │   ├── auth.ts               # Auth API calls
│   │   │   ├── employees.ts          # Employee API calls
│   │   │   ├── org-chart.ts          # Org chart API calls
│   │   │   ├── performance.ts        # Performance API calls
│   │   │   ├── lms.ts                # LMS API calls
│   │   │   └── analytics.ts          # Analytics API calls
│   │   ├── hooks/
│   │   │   ├── useAuth.ts            # Auth context + hook
│   │   │   ├── useEmployees.ts       # React Query hooks for employees
│   │   │   └── ...                   # More React Query hooks per module
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── employees/
│   │   │   │   ├── EmployeeList.tsx
│   │   │   │   ├── EmployeeProfile.tsx
│   │   │   │   └── EmployeeForm.tsx
│   │   │   ├── org-chart/
│   │   │   │   └── OrgChart.tsx
│   │   │   ├── performance/
│   │   │   │   ├── PerformanceDashboard.tsx
│   │   │   │   ├── ReviewCycles.tsx
│   │   │   │   ├── ReviewForm.tsx
│   │   │   │   ├── Goals.tsx
│   │   │   │   ├── Incidents.tsx
│   │   │   │   ├── Commendations.tsx
│   │   │   │   ├── PIPs.tsx
│   │   │   │   └── Calibration.tsx
│   │   │   ├── lms/
│   │   │   │   ├── Catalog.tsx
│   │   │   │   ├── WorkerView.tsx
│   │   │   │   ├── ManagerView.tsx
│   │   │   │   └── Rules.tsx
│   │   │   ├── analytics/
│   │   │   │   └── Analytics.tsx
│   │   │   └── AccessDenied.tsx
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── layout/
│   │   │   │   ├── AppShell.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── SubNav.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── employees/
│   │   │   │   ├── EmployeeTable.tsx
│   │   │   │   ├── ProfileTabs.tsx
│   │   │   │   ├── JobHistoryTimeline.tsx
│   │   │   │   └── AuditTrail.tsx
│   │   │   ├── org-chart/
│   │   │   │   ├── OrgChartCanvas.tsx
│   │   │   │   ├── OrgChartControls.tsx
│   │   │   │   └── NodeCard.tsx
│   │   │   ├── performance/
│   │   │   │   ├── CompetencyRating.tsx
│   │   │   │   ├── GoalCard.tsx
│   │   │   │   ├── IncidentForm.tsx
│   │   │   │   ├── CommendationCard.tsx
│   │   │   │   ├── PIPWizard.tsx
│   │   │   │   ├── CalibrationGrid.tsx
│   │   │   │   └── PerformanceTimeline.tsx
│   │   │   ├── lms/
│   │   │   │   ├── CourseCard.tsx
│   │   │   │   ├── CertStatusBadge.tsx
│   │   │   │   ├── CertMatrix.tsx
│   │   │   │   └── ComplianceDashboard.tsx
│   │   │   ├── analytics/
│   │   │   │   ├── KPICard.tsx
│   │   │   │   └── ChartCard.tsx
│   │   │   └── shared/
│   │   │       ├── DataTable.tsx
│   │   │       ├── SearchInput.tsx
│   │   │       ├── FilterPanel.tsx
│   │   │       ├── StatusBadge.tsx
│   │   │       ├── ExportButton.tsx
│   │   │       └── EmptyState.tsx
│   │   ├── lib/
│   │   │   ├── utils.ts              # Tailwind merge, formatters
│   │   │   └── constants.ts          # Colors, roles, enums
│   │   ├── types/
│   │   │   └── index.ts              # All TypeScript interfaces
│   │   └── styles/
│   │       └── globals.css            # Tailwind directives + custom CSS
│   └── public/
│       ├── lumber-logo.svg
│       └── favicon.ico
│
└── nginx/
    └── default.conf                   # Docker Nginx config
```

---

## 9. Execution Timeline

| Phase | Duration | Checkpoint | Cumulative |
|-------|----------|------------|-----------|
| 1. Scaffolding + DB + Seed | 60-90 min | SETUP_01 | ~1.5h |
| 2. Auth + App Shell | 45-60 min | AUTH_01 | ~2.5h |
| 3. Employee Management | 75-90 min | EMP_01 | ~4h |
| 4. Org Chart | 60-75 min | ORG_01 | ~5h |
| 5. Performance Management | 90-120 min | PERF_01 | ~7h |
| 6. LMS | 60-75 min | LMS_01 | ~8.5h |
| 7. Dashboard & Analytics | 45-60 min | ANALYTICS_01 | ~9.5h |
| 8. Docker & Polish | 45-60 min | DOCKER_01 | ~10.5h |
| 9. Video Demo | 30-45 min | FINAL | ~11h |

**Total estimated: ~11 hours** (realistic with quality gates)

---

## 10. Risk Register

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| pip install --target fails for some packages | Low | High | Already tested: works ✅ |
| d3-org-chart React integration issues | Medium | Medium | Library has React examples; fallback to raw D3 |
| SQLite concurrent writes | Low | Low | Single-threaded dev use; PostgreSQL for production |
| Seed data generation too slow | Low | Medium | Batch inserts, pre-computed data |
| Performance module complexity overrun | Medium | High | Strict timeboxing; core features first, polish later |
| Frontend build too large | Low | Low | Code splitting, lazy routes |
| Video recording quality | Low | Medium | Proven ffmpeg approach from SimulAI project |

---

## 11. Requirements Traceability

### TSG HRIS Requirements Coverage

| Sheet | Requirements | Covered | Coverage |
|-------|-------------|---------|----------|
| Core HR Records | 25 | 24 | 96% |
| Organizational Structure | 9 | 9 | 100% |
| Performance Management | 15 | 15 | 100% |
| Learning & Development | 25 | 21 | 84% |
| Position Management | 12 | 10 | 83% |
| Payroll | 22 | N/A | Existing Lumber module |
| Benefits | 25 | N/A | Phase 4 per PRD |
| Time & Attendance | 18 | N/A | Existing Lumber module |
| Leave Management | 17 | N/A | Existing Lumber module |
| Scheduling | 25 | N/A | Existing Lumber module |
| Onboarding/Offboarding | 11 | 5 | 45% (basic) |
| Succession Planning | 14 | 4 | 29% (via calibration) |
| Compensation Mgmt | 15 | 3 | 20% (via perf→pay) |
| Workforce Planning | 10 | N/A | Phase 3 per PRD |

**Note**: Payroll, Benefits, Time & Attendance, Leave Management, and Scheduling are existing Lumber modules per the Capabilities Analysis — they are OUT OF SCOPE for this HRIS build.
