# MARINA INTELLIGENCE
> **Complete Football Performance Analytics & Tactical Intelligence Platform**  
> *Initial Club: Chennaiyin FC | Competition: Indian Super League (ISL) 2026–27*

---

## 1. Executive Platform Overview

**MARINA INTELLIGENCE** is an integrated, enterprise-grade football intelligence platform engineered for technical directors, performance analysts, tactical coaches, and recruitment departments.

Built upon strict empirical data integrity, the platform guarantees that every calculation, visual element, and tactical dossier is grounded in verified match events, official fixture records, and club squad registries without data fabrication or artificial score generation.

---

## 2. Integrated Application Modules

MARINA INTELLIGENCE delivers 8 fully integrated, end-to-end operational modules:

| Module | Title | URL Route | Core Functionality |
|---|---|---|---|
| **01** | **Season Overview Dashboard** | `/` | Dynamic league table, points, goal differential, form sequence, home/away splits, upcoming fixtures. |
| **02** | **Team Analytics** | `/teams` | Attacking conversion, defensive duel success, possession circulation, half-by-half trends, squad leadership overview. |
| **03** | **Player Intelligence** | `/players` & `/players/[id]` | Individual player dossiers, verified physical attributes, per-90 indicators ($\ge 45\text{ min}$ threshold), senior council tags. |
| **04** | **Match Centre** | `/matches` & `/matches/[id]` | Match logs distinguishing `FINISHED` from `SCHEDULED`, starting XI, substitutes, timeline events, and match reports. |
| **05** | **Tactical Intelligence** | `/tactical` | Formation structure, vertical third distribution, flank attacks, pressing PPDA, and evidence-grounded recommendations. |
| **06** | **Advanced Football Analytics** | `/intelligence` | Expected Goals ($xG$), pitch shot map geometry, passing network degree centrality, spatial defending distributions. |
| **07** | **AI Football Analyst** | `/analyst` | Deterministic natural language query interpreter producing 6-part structured analytical dossiers. |
| **08** | **Administration & Governance** | `/settings` & `/data-quality` | Role-based access control (RBAC) matrix (Owner, Administrator, Analyst, Viewer), database health diagnostics, data sync logs. |

---

## 3. Project Demonstration

A complete end-to-end video walkthrough demonstrating MARINA INTELLIGENCE's match centre logs, tactical pitch models, player performance dossiers, and AI analyst workflows:

[![MARINA INTELLIGENCE Demonstration Video](https://img.shields.io/badge/YouTube-Video%20Demonstration-red?style=for-the-badge&logo=youtube)](https://youtu.be/NEil_gDGzdo)

> **Demonstration Video Link:**  
> `https://www.youtube.com/watch?v=REPLACE_WITH_YOUR_YOUTUBE_VIDEO_ID`  
> *(https://youtu.be/NEil_gDGzdo)*

---

## 4. Application Screenshots & Visual Walkthrough

The high-resolution captures below showcase MARINA INTELLIGENCE running in production on genuine Chennaiyin FC ISL 2026–27 datasets:

### 1. Executive Season Overview Dashboard
> Central command console presenting dynamic league standings, 5-match form trajectories, goal scoring trends, senior leadership group council, and verified next match countdown.

![Main Dashboard](docs/media/01-main-dashboard.png)

### 2. Match Centre & Fixture Intelligence
> Comprehensive fixture timeline distinguishing completed match logs (`FINISHED`) from upcoming fixtures (`SCHEDULED`) with verified dual-entry scorelines.

![Match Centre](docs/media/02-match-centre.png)

### 3. Match Detail & Starting XI Lineup
> Single-match tactical breakdown featuring official starting XI pitch formation layout, substitutes bench, match events timeline, and dual-party referee verification.

![Match Detail](docs/media/03-match-detail.png)

### 4. Player Performance Analytics
> Squad-wide performance evaluation grid standardizing per-90 indicators, goal involvements, passing volume, defensive contributions, and senior council badges.

![Player Performance Analytics](docs/media/04-player-performance-analytics.png)

### 5. Player Profile & Tactical Radar Visualizer
> Deep individual player dossier featuring normalized multi-dimensional radar metrics, physical attributes, discipline logs, and position-specific KPIs.

![Player Profile Detail](docs/media/05-player-profile-detail.png)

### 6. Tactical Intelligence & Average Lineup
> Starting XI average player positioning, vertical third spatial distributions, horizontal flank attack channels, field tilt %, and defensive pressing intensity (PPDA).

![Tactical Analysis](docs/media/06-tactical-analysis.png)

### 7. Advanced Football Analytics (Shot Maps & xG)
> Pitch shot map coordinate geometry ($1050 \times 680$ normalized canvas), logistic regression Expected Goals ($xG$) modeling, cumulative match momentum, and passing network centrality.

![Advanced Football Analytics](docs/media/07-advanced-intelligence.png)

### 8. AI Football Analyst & Natural Language Query Engine
> Deterministic query interpreter generating structured 6-part analytical dossiers (Executive Summary, Tactical Query Context, Performance Evidence, Football Interpretation, Measurement Limitations, Final Assessment) without LLM hallucinations.

![AI Football Analyst](docs/media/08-ai-football-analyst.png)

### 9. Multi-Tier System Architecture & Core Pipelines
> End-to-end data pipeline architecture illustrating multi-provider ingestion, relational database constraints (23 relational tables), analytical calculation engines, and responsive Next.js presentation tier.

![System Architecture](docs/media/09-system-architecture.png)

---

## 5. Technology Stack & Multi-Tier Architecture

### Frontend
- **Framework:** Next.js 15.5.29 (React 19, App Router)
- **Language:** TypeScript 5+ (Strict mode)
- **Styling:** Tailwind CSS with a strict sports analytics light aesthetic:
  - Canvas Background: `#FFFFFF` (pure white) and `#F4F8F4` (light turf grey-green).
  - Primary Pitch Accent: `#246B45` (pitch emerald green).
  - Core Brand Identity: `#174B32` (deep club pine green).
  - High-Contrast Text: `#26332B` (dark turf charcoal) and `#718078` (muted operational slate).
- **Pitch Visualizations:** `FootballPitch.tsx` with normalized coordinate mapping ($1050 \times 680$ SVG canvas).
- **Charts:** Apache ECharts (`RadarChart.tsx`, `GoalTrendChart.tsx`) and Recharts.

### Backend
- **Framework:** FastAPI with asynchronous ASGI execution (Python 3.12+).
- **ORM:** SQLAlchemy 2.0 (Asyncio).
- **Validation:** Pydantic V2 with strict type validation.
- **Analytics:** NumPy, Pandas, Scikit-learn, SciPy.

### Database
- **Engine:** PostgreSQL 16 (production) / SQLite (`marina.db`) with 23 relational tables and foreign keys.

---

## 6. Documentation Suite

MARINA INTELLIGENCE provides 11 technical guides in `docs/`:

1. [PROJECT_ARCHITECTURE.md](docs/PROJECT_ARCHITECTURE.md) — Multi-tier architecture, data flow, and component breakdown.
2. [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) — 23 relational tables, foreign key relations, constraints, and audit fields.
3. [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) — REST API catalog, query parameters, request/response payloads.
4. [FOOTBALL_METRICS_DICTIONARY.md](docs/FOOTBALL_METRICS_DICTIONARY.md) — Operational definitions, formulas, per-90 rates, and division guards.
5. [DATA_SOURCES.md](docs/DATA_SOURCES.md) — Authoritative feeds (`ISL_OFFICIAL`, `CFC_OFFICIAL`, `AIFF_OFFICIAL`, `MANUAL_CURATION`).
6. [DATA_VALIDATION.md](docs/DATA_VALIDATION.md) — Validation pipelines, duplicate detection, and discrepancy preservation.
7. [ANALYTICS_METHODOLOGY.md](docs/ANALYTICS_METHODOLOGY.md) — $xG$ logistic regression, passing networks, PPDA, and position weights.
8. [TESTING_GUIDE.md](docs/TESTING_GUIDE.md) — Backend Pytest, frontend Vitest, test coverage, and execution commands.
9. [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) — Docker Compose, production build, environment variables, and healthchecks.
10. [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) — Milestone tracking and future enhancements.
11. [METRICS_FORMULAS.md](docs/METRICS_FORMULAS.md) — Mathematical reference guide.

---

## 7. Verification & Testing

The platform maintains automated test coverage across backend and frontend:

- **Backend Pytest:** **137 / 137 tests passing** (`python -m pytest backend/tests`).
- **Frontend Vitest:** **39 / 39 tests passing** across 12 test files (`pnpm test`).
- **Production Compilation:** Next.js `pnpm build` generates **17 / 17 routes** with 100% type safety.

---

## 8. Getting Started

### Local Quickstart

```powershell
# 1. Start Backend Server
$env:PYTHONPATH="backend\src"
python -m uvicorn marina.main:app --host 127.0.0.1 --port 8000 --reload

# 2. Start Frontend Web Client
cd frontend
pnpm dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### Docker Deployment

```bash
docker compose up -d --build
```
Access the platform at `http://localhost:3000` and API documentation at `http://localhost:8000/docs`.
