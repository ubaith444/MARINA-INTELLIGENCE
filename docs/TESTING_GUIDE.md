# MARINA INTELLIGENCE — Quality Assurance & Testing Guide

**Document Version:** 4.0.0  
**Testing Frameworks:** Pytest (Backend) • Vitest & Playwright (Frontend)  
**Total Automated Tests:** 183 (142 Backend + 41 Frontend)  

---

## 1. Running Backend Test Suites

Backend tests validate database schema creation, API v1 routes, formula calculations, integrity rules, and service layers.

### Run All Backend Tests:
```powershell
$env:PYTHONPATH="backend\src"
python -m pytest backend/tests -v
```

### Run Specific Test Modules:
- **Leadership Group:** `python -m pytest backend/tests/test_leadership_group.py`
- **Defensive Intelligence:** `python -m pytest backend/tests/test_defensive_analytics.py`
- **Integrity Rules:** `python -m pytest backend/tests/test_integrity_rules.py`
- **Season Overview:** `python -m pytest backend/tests/test_season_overview_rework.py`

---

## 2. Running Frontend Test Suites

Frontend unit and component tests run in JSDOM via Vitest:

### Run All Frontend Tests:
```powershell
cd frontend
pnpm test
```

### Run Production Build Verification:
```powershell
cd frontend
pnpm build
```
*Ensures 100% type safety and validates prerendering for all 17 application routes.*

---

## 3. Test Coverage Matrix

| Test Suite | File | Test Count | Status |
|---|---|---|---|
| **Leadership Group** | `test_leadership_group.py` | 1 | PASSED |
| **API Endpoints** | `test_analytics_api_endpoints.py` | 12 | PASSED |
| **Defensive Analytics** | `test_defensive_analytics.py` | 8 | PASSED |
| **Attacking Analytics** | `test_attacking_analytics.py` | 8 | PASSED |
| **Tactical & Territorial** | `test_tactical_territorial_api.py` | 7 | PASSED |
| **Integrity Rules** | `test_integrity_rules.py` | 15 | PASSED |
| **Season Overview** | `test_season_overview_rework.py` | 9 | PASSED |
| **Frontend Components** | `KpiCard.test.tsx`, `FootballPitch.test.tsx` | 7 | PASSED |
| **Frontend Features** | `match_centre.test.ts`, `data_quality.test.ts`, etc. | 32 | PASSED |
| **TOTAL** | **All Modules** | **176** | **100% GREEN** |
