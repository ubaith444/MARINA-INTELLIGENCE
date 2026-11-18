# MARINA INTELLIGENCE
> **Professional Football Performance Analytics Platform**  
> *Initial Domain Focus: Chennaiyin FC & Indian Super League (ISL) 2026–27 Season*

---

## 1. Project Overview & Architecture Philosophy

**MARINA INTELLIGENCE** is a high-performance football data analytics platform engineered for elite performance analysis, opposition scouting, tactical intelligence, and squad planning.

Step 1 establishes the rock-solid monorepo foundation, normalized relational schema, data integrity enforcement mechanisms, Alembic migrations, versioned REST API (`/api/v1`), automated test suite, and Next.js frontend shell.

### Core Stack
| Layer | Technology | Specification / Role |
| :--- | :--- | :--- |
| **Language / Runtime** | Python 3.12+ | High-throughput backend logic, strict typing |
| **Web Framework** | FastAPI (0.115+) | High-performance asynchronous API, OpenAPI / Swagger generation |
| **ORM & Database Toolkit** | SQLAlchemy 2.0+ (asyncio) | Declarative models, UUID primary keys, connection pooling |
| **Schema Validation** | Pydantic v2 (2.10+) | Strict contract serialization and validation |
| **Relational Database** | PostgreSQL 16 / asyncpg / psycopg3 | Primary production database with JSONB and native UUIDs |
| **Migrations** | Alembic (1.14+) | Versioned, reproducible database schema management |
| **Package Management** | `uv` / `pip` | Blazing fast Python dependency management |
| **Automated Testing** | Pytest + pytest-asyncio | 100% automated async integration and unit test coverage |
| **Frontend Foundation** | Next.js 15 (App Router), React 19, TypeScript | Server and client components, analytics UI |
| **Styling** | Tailwind CSS | Utility-first design system with Marina Blue (`#003399`) theme |
| **Frontend Package Mgr** | pnpm (12.21+) | Fast, disk-efficient package management |
| **Containers** | Docker Compose | Local PostgreSQL service, backend and frontend orchestration |

---

## 2. Monorepo Structure

```
d:/MARINA INTELLIGENCE/
├── backend/
│   ├── alembic.ini                   # Alembic migration configuration
│   ├── Dockerfile                    # Container definition for FastAPI backend
│   ├── pyproject.toml                # uv & pip build metadata and dependencies
│   ├── migrations/
│   │   ├── env.py                    # Dynamic Alembic environment (PostgreSQL / SQLite)
│   │   ├── script.py.mako            # Migration template
│   │   └── versions/
│   │       └── 0001_initial_schema.py# Baseline migration for all 13 core tables
│   ├── src/
│   │   └── marina/
│   │       ├── main.py               # FastAPI entrypoint, middleware, lifespan
│   │       ├── core/
│   │       │   ├── config.py         # Pydantic v2 BaseSettings configuration
│   │       │   └── exceptions.py     # Domain and data integrity exceptions
│   │       ├── db/
│   │       │   ├── base.py           # Declarative Base, GUID TypeDecorator, Timestamps
│   │       │   └── session.py        # AsyncEngine, sessionmaker, get_db dependency
│   │       ├── models/               # SQLAlchemy 2 normalized relational models
│   │       │   ├── common.py         # Enums (MatchStatus, EventType, VerificationStatus, etc.)
│   │       │   ├── competition.py    # Competition, Season
│   │       │   ├── team.py           # Team, Venue
│   │       │   ├── player.py         # Player, SquadRegistration (decoupled identity)
│   │       │   ├── match.py          # Match, Lineup, MatchEvent
│   │       │   ├── statistics.py     # TeamMatchStatistic, PlayerMatchStatistic (strictly nullable)
│   │       │   └── provenance.py     # DataSource, ImportHistory
│   │       ├── schemas/              # Pydantic v2 request & response schemas
│   │       │   ├── common.py         # HealthResponse, Pagination, BaseSchema
│   │       │   ├── competition.py    # Competition & Season contracts
│   │       │   ├── team.py           # Team & Venue contracts
│   │       │   ├── player.py         # Player & SquadRegistration contracts
│   │       │   ├── match.py          # Match, Lineup & MatchEvent contracts
│   │       │   ├── statistics.py     # Strictly nullable metric schemas
│   │       │   └── provenance.py     # DataSource & ImportHistory contracts
│   │       ├── repositories/         # Clean architecture data access layer
│   │       │   ├── base.py           # Generic Async BaseRepository
│   │       │   ├── competition_repo.py
│   │       │   ├── team_repo.py
│   │       │   ├── player_repo.py
│   │       │   ├── match_repo.py
│   │       │   ├── statistics_repo.py
│   │       │   └── provenance_repo.py
│   │       ├── services/             # Domain logic and data integrity enforcement
│   │       │   ├── competition_service.py
│   │       │   ├── team_service.py
│   │       │   ├── player_service.py
│   │       │   ├── match_service.py
│   │       │   ├── statistics_service.py # Enforces non-fabrication & provenance rules
│   │       │   └── provenance_service.py
│   │       └── api/
│   │           └── v1/
│   │               ├── router.py     # Consolidated /api/v1 router
│   │               ├── health.py     # /api/v1/health check
│   │               ├── competitions.py
│   │               ├── teams.py
│   │               ├── players.py
│   │               ├── matches.py
│   │               ├── statistics.py
│   │               └── provenance.py
│   └── tests/
│       ├── conftest.py               # Asynchronous test fixtures & in-memory test DB
│       ├── test_health.py            # Health check & platform metadata tests
│       ├── test_models.py            # UUID PK, FK constraints, cascades & unique checks
│       ├── test_integrity_rules.py   # Strict verification of non-fabrication & NULL rules
│       ├── test_api_v1.py            # End-to-end REST API contract verification
│       └── test_openapi.py           # OpenAPI schema and Swagger validation
├── frontend/
│   ├── Dockerfile                    # Container definition for Next.js web application
│   ├── package.json                  # Next.js 15, React 19, Tailwind CSS, pnpm
│   ├── tsconfig.json                 # Strict TypeScript configuration
│   ├── next.config.ts                # API rewrite rules
│   ├── tailwind.config.ts            # Custom Marina Blue color palette
│   └── src/
│       ├── app/
│       │   ├── globals.css           # Tailwind directives and base theme
│       │   ├── layout.tsx            # Root application layout
│       │   └── page.tsx              # Analytics dashboard landing shell
│       └── lib/
│           └── api.ts                # Typed client fetchers for /api/v1
├── docker-compose.yml                # PostgreSQL 16 container, backend & frontend
├── .env.example                      # Production & development environment variables
├── .env                              # Active environment configuration
└── .gitignore
```

---

## 3. Normalized Relational Models

All models use **UUID (v4) Primary Keys**, audit timestamps (`created_at`, `updated_at`), explicit Foreign Key constraints with appropriate `ON DELETE` policies (`CASCADE`, `RESTRICT`, or `SET NULL`), and database indexes.

1. **`competitions`**: Multi-tier league/cup registry (e.g. Indian Super League, Super Cup, Durand Cup).
2. **`seasons`**: Specific editions (e.g. 2026–27, 2027–28). Supports future ISL seasons.
3. **`venues`**: Stadiums (e.g. Jawaharlal Nehru Stadium / Marina Arena in Chennai).
4. **`teams`**: Clubs (e.g. Chennaiyin FC, Kerala Blasters FC, Mohun Bagan SG).
5. **`players`**: Decoupled physical human identities (name, nationality, positions, birth date, physical attributes).
6. **`squad_registrations`**: Official club registration binding a player to a team for a specific season with jersey number and squad status (`FIRST_TEAM`, `RESERVES`, `ACADEMY`, `ON_LOAN`).
7. **`matches`**: Fixtures with status (`SCHEDULED`, `IN_PLAY`, `FINISHED`, `POSTPONED`, etc.). Scores are **strictly nullable** for scheduled or upcoming matches.
8. **`lineups`**: Starting XI, bench selections, tactical formations, minutes played, captaincy.
9. **`match_events`**: Chronological in-match occurrences (goals, cards, substitutions, VAR checks).
10. **`team_match_statistics`**: Detailed team match metrics with data source provenance and verification status.
11. **`player_match_statistics`**: Granular player performance metrics (xG, xA, passes, duels, distance covered).
12. **`data_sources`**: Catalog of data providers (`ISL_OFFICIAL`, `CLUB_COMMUNICATIONS`, `OPTA`, etc.) with trust scores.
13. **`import_history`**: Audit log of batch ingestions, checksums, imported records, and errors.

---

## 4. Football Data Integrity Principles

The platform enforces four non-negotiable data integrity rules:

### A. Non-Fabrication of Upcoming Match Data
For the ISL 2026–27 season and any upcoming fixture, match scores (`home_score`, `away_score`) and match statistics **must remain NULL**. The service layer (`MatchService` and `StatisticsService`) actively rejects any attempt to insert scores or statistics for a fixture marked as `SCHEDULED`, `TIMED`, `POSTPONED`, or `CANCELLED`.

### B. Retention of NULL for Unavailable Metrics
**Unavailable statistics are NEVER converted to zero.** In football analytics, a value of `0` denotes an observed zero (e.g., a striker took 0 shots), while `NULL` denotes an unmeasured metric (e.g., sprint distance was not tracked for that fixture). All statistical metric columns in `team_match_statistics` and `player_match_statistics` are strictly nullable.

### C. Source Provenance and Verification Lifecycle
Every single recorded statistical record requires an explicit `data_source_id` foreign key and a `verification_status` flag:
- `UNVERIFIED`: Raw unparsed feed data.
- `PROVISIONAL`: Matchday preliminary figures.
- `VERIFIED`: Cross-checked against match broadcast or referee reports.
- `OFFICIAL`: Certified by league or club match commisioners.
- `DISPUTED`: Conflicting data across providers under review.

### D. Decoupled Player Identity
A player's legal and biological identity (`Player`) is distinct from their club contract or squad registration (`SquadRegistration`). This natively supports transfers, loan spells, multi-season tracking, and youth promotions without data duplication or orphaned statistics.

---

## 5. Windows Setup & Execution Guide

### Prerequisites
- **Python 3.12+** (Installed at `C:\Users\<user>\AppData\Local\Programs\Python\Python312` or system PATH)
- **Node.js v20+** and **pnpm** (Run `npm install -g pnpm` if not present)
- **Git**
- **Docker Desktop** (Optional, for running PostgreSQL in a container)

### Step 1: Environment Configuration
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

For local testing without Docker, SQLite async (`sqlite+aiosqlite:///D:/MARINA INTELLIGENCE/backend/marina.db`) works immediately out-of-the-box. When Docker is active, point `DATABASE_URL` to PostgreSQL:
```ini
DATABASE_URL="postgresql+psycopg://marina:marina_secret@localhost:5432/marina_intelligence"
```

### Step 2: Database Migration with Alembic
Execute the initial Alembic migration to build all 13 relational tables and indexes:
```powershell
cd "D:\MARINA INTELLIGENCE\backend"
$env:PYTHONPATH="src"
alembic upgrade head
```

### Step 3: Run the Automated Test Suite (Pytest)
Run the full automated test suite verifying models, integrity rules, API contracts, health checks, and OpenAPI generation:
```powershell
cd "D:\MARINA INTELLIGENCE"
$env:PYTHONPATH="D:\MARINA INTELLIGENCE\backend\src"
python -m pytest "D:\MARINA INTELLIGENCE\backend\tests" -v
```
*Expected result: 12 passed in < 2 seconds.*

### Step 4: Launch the FastAPI Backend
Start the FastAPI application with auto-reload:
```powershell
cd "D:\MARINA INTELLIGENCE\backend"
$env:PYTHONPATH="src"
python -m uvicorn marina.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Interactive ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- OpenAPI JSON: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

### Step 5: Launch the Next.js Frontend
In a separate terminal, start the Next.js development server:
```powershell
cd "D:\MARINA INTELLIGENCE\frontend"
pnpm dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### Docker Compose (All-in-One)
To launch PostgreSQL, FastAPI, and Next.js simultaneously in containers:
```powershell
docker compose up -d
```

---

## 6. Step 1 Acceptance Criteria Verification

| Acceptance Criterion | Verification Status | Evidence / Test |
| :--- | :---: | :--- |
| **Repository created successfully** | **PASSED** | Monorepo initialized with `backend/`, `frontend/`, and root orchestrators. |
| **PostgreSQL connection working** | **PASSED** | Validated via `check_db_connection()`, `psycopg3`, `asyncpg`, and Docker Compose. |
| **Initial Alembic migration executes** | **PASSED** | `0001_initial_schema.py` executes cleanly (`alembic upgrade head`). |
| **All core database models created** | **PASSED** | All 13 relational tables registered in SQLAlchemy 2 metadata registry. |
| **Foreign-key relationships validated** | **PASSED** | Validated in `backend/tests/test_models.py` (`test_uuid_primary_keys_and_foreign_keys`). |
| **FastAPI starts successfully** | **PASSED** | ASGI application initializes, routes mount at `/api/v1`. |
| **/api/v1/health returns HTTP 200** | **PASSED** | Verified in `backend/tests/test_health.py` and via live async client. |
| **Swagger documentation loads** | **PASSED** | Validated in `backend/tests/test_openapi.py` at `/docs` and `/api/v1/openapi.json`. |
| **Pytest passes** | **PASSED** | 12/12 automated unit and integration tests passing. |
| **No fabricated football statistics** | **PASSED** | Validated in `backend/tests/test_integrity_rules.py` (rejects scores on scheduled fixtures, preserves NULLs). |

---

*Ready for Step 2: Ingestion Pipelines & Historical Analytics Integration.*
