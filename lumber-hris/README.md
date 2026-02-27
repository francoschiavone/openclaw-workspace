# 🪵 Lumber HRIS

**Human Resources Information System for Summit Construction Group**

Full-stack HRIS application built with FastAPI + React, designed for the construction industry. Features organizational management, performance tracking, LMS & training compliance, credential management (BuilderFax), and workforce analytics.

## Quick Start

```bash
cd lumber-hris
bash start.sh
# → http://localhost:8000
```

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Administrator | admin@lumber.com | LumberAdmin2026! |
| HR Manager | hr@lumber.com | LumberHR2026! |
| Project Manager | pm@lumber.com | LumberPM2026! |
| Foreman | foreman@lumber.com | LumberForeman2026! |
| Employee | worker@lumber.com | LumberWorker2026! |

## Stack

**Backend:**
- Python 3.11 + FastAPI 0.133
- SQLAlchemy 2.0 + SQLite (dev) / PostgreSQL (prod)
- JWT authentication (python-jose)
- 8 API routers, 45+ endpoints

**Frontend:**
- React 19 + TypeScript
- Vite 7 (build tooling)
- Tailwind CSS (CDN)
- Recharts, Lucide Icons, d3
- React Query, React Router

## Architecture

```
lumber-hris/
├── backend/
│   ├── main.py              # FastAPI app, CORS, static serving
│   ├── models/database.py   # 22 SQLAlchemy tables
│   ├── seed.py              # Data generator (375 employees)
│   └── routers/
│       ├── auth.py          # JWT login, refresh, role-based access
│       ├── employees.py     # CRUD, search, pagination, audit
│       ├── departments.py   # Department/Division/Location
│       ├── org_chart.py     # Corporate hierarchy + project crews
│       ├── performance.py   # Reviews, goals, incidents, PIPs, 9-box
│       ├── lms.py           # Courses, certs, assignments, compliance
│       ├── analytics.py     # Workforce/performance/training/org
│       ├── dashboard.py     # KPIs, charts, activity feed
│       └── static.py        # SPA serving (catch-all)
├── frontend/
│   ├── src/
│   │   ├── pages/           # 9 page components
│   │   ├── components/      # AppShell layout
│   │   ├── context/         # AuthContext
│   │   └── lib/             # API client (axios + JWT)
│   └── dist/                # Built frontend (served by FastAPI)
├── requirements/            # Original PRD documents
├── start.sh                 # Single-command startup
└── lumber_hris.db           # SQLite database
```

## Modules

### Dashboard
- Real-time KPIs: headcount, certifications, reviews, compliance
- Projects overview with crew/worker counts
- Upcoming certification renewals
- Headcount by department (bar chart) + type distribution (pie chart)

### Employees
- Full CRUD with search, filters, pagination
- 375 employees across 15 departments
- Role-based filtering (workers see only self)
- Employee profile with complete details

### Org Chart
- **Corporate mode**: Interactive tree with zoom/pan, SVG connectors
- **Project/Crew mode**: View teams organized by project and crew
- Click-to-detail side panel
- Status indicators (active/on leave/terminated)

### Performance
- Review cycles (Annual, Mid-Year, 30/60/90)
- Goal tracking with progress bars
- Incidents & commendations
- 9-box calibration grid

### LMS & Training
- Course catalog (35 courses, 5 categories)
- Training assignments (932 active)
- Certification tracking (835 certs)
- Expiring certification alerts
- Auto-enrollment rules
- Compliance dashboard

### BuilderFax (Credential Management)
- All certifications view with search/filter
- Expiring soon alerts
- Compliance rate tracking

### Analytics
- Workforce demographics and distribution
- Performance rating distributions
- Training completion trends
- Organization structure analysis

## API Endpoints

All endpoints under `/api/*`. Full Swagger docs at `/docs`.

| Group | Endpoints | Auth |
|-------|-----------|------|
| Auth | login, refresh, me | Public / Bearer |
| Employees | list, detail, create, update, delete, search | Bearer |
| Departments | list | Bearer |
| Org Chart | corporate, flat, projects | Bearer |
| Performance | reviews, cycles, goals, incidents, commendations, PIPs, 9-box | Bearer |
| LMS | courses, certifications, assignments, compliance, expiring, rules | Bearer |
| Analytics | workforce, performance, training, organization | Bearer |
| Dashboard | KPIs, charts, activity | Bearer |

## Seed Data

- **Company**: Summit Construction Group
- **Employees**: 375 across 3 divisions + corporate
- **Departments**: 15 (Safety, Concrete, Carpentry, Electrical, etc.)
- **Projects**: 7 active construction projects
- **Certifications**: 835 (OSHA, First Aid, crane, welding, etc.)
- **Training**: 35 courses, 932 assignments
- **Reviews**: 25 performance reviews, 53 goals
- **Demographics**: 85% male / 15% female, 40% union

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | sqlite:///./lumber_hris.db | Database connection |
| SECRET_KEY | (hardcoded) | JWT signing key |
| PORT | 8000 | Server port |

## Requirements PRDs

Based on 4 Product Requirements Documents from Lumber/TSG:
- Lumber HRIS PRD v0.2 (master)
- Org Chart PRD (Executive Branded)
- Performance Management PRD (Executive Branded)
- Onboarding PRD (Workforce Management)
