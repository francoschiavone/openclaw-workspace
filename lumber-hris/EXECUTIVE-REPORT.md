# Lumber HRIS — Executive Status Report

**Date:** February 27, 2026  
**Author:** Franco Schiavone, AI Engineer  
**Repository:** `github.com/francoschiavone/openclaw-workspace/lumber-hris`

---

## Summary

Full-stack HRIS prototype for Summit Construction Group. Functional demo covering core HR modules with realistic seed data (374 employees, 15 departments, 8 projects). Built as a single-server deployment: FastAPI backend serving both API and React frontend.

---

## What's Built

### Modules — Functional

| Module | Status | Notes |
|--------|--------|-------|
| **Authentication** | ✅ Ready | JWT-based, 5 roles (Admin, HR Manager, PM, Foreman, Employee), role-based data filtering |
| **Dashboard** | ✅ Ready | Real-time KPIs, project overview, cert renewals, charts |
| **Employee Directory** | ✅ Ready | Full CRUD, search, pagination, department/status filters |
| **Employee Profile** | ✅ Ready | Contact info, employment details, compensation, certs, training, performance, projects |
| **Org Chart** | ✅ Ready | Interactive hierarchy with zoom/pan, 374 nodes, department grouping |
| **Performance Management** | ✅ Ready | Review cycles, 350 reviews, 53 goals, 12 incidents, 25 commendations, 9-box calibration |
| **LMS & Training** | ✅ Ready | 35 courses, 932 assignments, course catalog, my learning view, auto-enrollment rules |
| **BuilderFax** | ✅ Ready | 835 certifications tracked, expiration alerts, compliance metrics |
| **Analytics** | ✅ Ready | Workforce demographics, department breakdowns, interactive charts |

### Data Model

22 tables, fully seeded:

| Entity | Count |
|--------|-------|
| Employees | 374 |
| Departments | 15 |
| Certifications | 835 |
| Training Assignments | 932 |
| Performance Reviews | 350 |
| Courses | 35 |
| Goals | 53 |
| Projects | 8 |
| Users (login accounts) | 24 |

---

## What's NOT Production-Ready

| Gap | Severity | Detail |
|-----|----------|--------|
| **No PostgreSQL config** | High | Currently SQLite. Need Alembic migrations + PostgreSQL connection for production. |
| **No Docker deployment** | High | No Dockerfile or docker-compose. Single `uvicorn` process, no Gunicorn/workers. |
| **No file upload** | Medium | Employee photos, document attachments not implemented. |
| **No email/notifications** | Medium | No SMTP integration, no in-app notifications. |
| **No CSV/PDF export** | Medium | Analytics and employee reports not exportable. |
| **No audit trail UI** | Medium | Backend logs audit events, but no admin-facing audit log viewer. |
| **No employee create/edit forms** | Medium | API supports CRUD, but frontend only has list/view (no create/edit modals). |
| **No onboarding workflow** | Low | PRD-defined onboarding module not built. |
| **No employee surveys** | Low | PRD-defined survey module not built. |
| **No succession planning** | Low | PRD-defined module not built. |
| **No SSO/SAML** | Low | Auth is email+password only. No SSO integration. |
| **Security hardening** | High | No rate limiting, no CSRF protection, no input sanitization beyond Pydantic validation. CORS is wildcard. |
| **No automated tests** | Medium | Manual E2E test passed (45/45 endpoints), but no pytest suite committed. |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Client (Browser)               │
│              React 19 + TypeScript               │
│              Tailwind CSS (CDN)                  │
│              Recharts, Lucide Icons              │
└─────────────────┬───────────────────────────────┘
                  │ HTTP (JSON)
                  ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Application                 │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Auth     │  │ Employees│  │ Org Chart│      │
│  │ (JWT)    │  │ (CRUD)   │  │ (Flat)   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Performnce│  │ LMS      │  │ Analytics│      │
│  │(Reviews) │  │(Courses) │  │(Charts)  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐                     │
│  │ Dashboard│  │ Static   │ ← serves SPA       │
│  │ (KPIs)   │  │ (catch-  │   (index.html +    │
│  └──────────┘  │  all)    │    JS/CSS bundle)  │
│                └──────────┘                     │
│                                                  │
│  SQLAlchemy ORM ─── 22 tables ─── UUID PKs      │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
        ┌──────────────────┐
        │  SQLite (dev)    │
        │  PostgreSQL (prod)│
        └──────────────────┘
```

### Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI 0.133, SQLAlchemy 2.0, Uvicorn |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS (CDN), Recharts |
| **Auth** | JWT (python-jose), bcrypt via passlib |
| **Database** | SQLite (dev), PostgreSQL-ready (SQLAlchemy abstraction) |
| **Deployment** | Single-server: FastAPI serves API (`/api/*`) + SPA (catch-all) |

### Codebase

| Component | Lines |
|-----------|-------|
| Backend (Python) | ~3,400 |
| Frontend (TypeScript/TSX) | ~3,200 |
| **Total** | **~6,600** |

### API Endpoints

8 routers, 45+ endpoints:
- `POST /api/auth/login` — JWT token
- `GET/POST /api/employees` — CRUD with role-based filtering
- `GET /api/employees/{id}` — Full profile with certs, reviews, training
- `GET /api/org-chart/flat` — All 374 nodes for client-side tree
- `GET /api/performance/reviews` — Reviews with cycle tracking
- `GET /api/performance/goals` — 53 goals with progress
- `GET /api/performance/incidents` — Safety/conduct incidents
- `GET /api/performance/commendations` — Recognition awards
- `GET /api/performance/calibration/nine-box` — Talent grid
- `GET /api/lms/courses` — Course catalog
- `GET /api/lms/assignments` — Training tracking
- `GET /api/analytics/workforce` — Demographics
- `GET /api/dashboard/stats` — KPI summary

### Role-Based Access

| Role | Sees |
|------|------|
| Admin / HR Manager | All employees, all data |
| Project Manager | Project team members |
| Foreman | Crew members |
| Employee | Own profile only |

---

## To Move to Production

**Minimum viable:**
1. PostgreSQL + Alembic migrations
2. Dockerfile + docker-compose
3. Security: rate limiting, CORS lockdown, CSRF
4. Employee create/edit forms in frontend
5. Pytest suite

**Nice to have:**
6. File uploads (photos, documents)
7. CSV/PDF export
8. Email notifications
9. SSO/SAML integration
10. Onboarding workflow
