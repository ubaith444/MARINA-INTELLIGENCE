# MARINA INTELLIGENCE: Data Acquisition & Ingestion Pipeline Architecture

This document describes the design, execution stages, and data integrity safeguards of the Step 2 data pipeline.

---

## 1. High-Level Ingestion Flow

```
+-------------------------------------------------------------------------------+
|                             DATA SOURCES                                      |
|  ISL Official (Tier 1) · Chennaiyin FC (Tier 1) · AIFF (Tier 1) · Manual CSV |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
| 01. EXTRACT                                                                   |
| BaseExtractor · HTTPX (throttling, retries, custom user agent) · BeautifulSoup |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
| 02. RAW DATA ARCHIVE                                                          |
| RawArchiveStorage: Immutable raw files · SHA-256 Checksums · Sidecar metadata |
| Path: data/raw_archive/{source_code}/{entity_type}/{YYYYMMDD}/{batch}_{hash}  |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
| 03. TRANSFORM & NORMALIZE                                                     |
| FootballNormalizer: Canonical team mapping · Player slug & name splitting     |
| IST to UTC conversion · Strict preservation of NULL for unmeasured metrics    |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
| 04. VALIDATE & CONFLICT DETECTION                                             |
| Pandera DataFrame Schemas · Pydantic v2 Models · ConflictDetector             |
| Detects score discrepancies, duplicate fixtures, and illegal scheduled scores |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
| 05. IDEMPOTENT UPSERT & AUDIT                                                 |
| PostgreSQL / SQLAlchemy 2 Async Engine · Atomic transactions                  |
| Idempotent merges · Ingestion batch logging in import_history                 |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
| 06. ANALYTICS API & CLI                                                       |
| FastAPI /api/v1 Endpoints · Click CLI · Automated Data Quality Reporting     |
+-------------------------------------------------------------------------------+
```

---

## 2. Ingestion Stages

### Stage 1: Acquisition & Throttling
- Custom user agent: `MarinaIntelligenceBot/1.0 (+https://github.com/marina-intelligence; football-analytics)`.
- Respectful rate limiting with configurable delay between calls (default: 1.0 second).
- Exponential backoff retry handler for network interruptions.

### Stage 2: Immutable Raw Archive
- Payloads are written to disk with SHA-256 validation.
- Files cannot be mutated once written.
- Structured sidecar metadata stores batch ID, timestamp, and byte size.

### Stage 3: Normalization & Entity Matching
- **Teams**: Canonical mapping from over 35 aliases and acronyms to standard slugs (e.g. `chennaiyin-fc`, `east-bengal-fc`).
- **Players**: Decoupled biological individual (`Player`) vs club registration (`SquadRegistration`).
- **Dates**: Indian Standard Time (`+05:30`) strings converted to timezone-aware UTC.
- **Metrics**: Unmeasured values are converted to `None`, preserving database `NULL`.

### Stage 4: Validation & Conflict Detection
- **Pandera**: Validates tabular column datatypes, value ranges, and relational invariants (e.g. `home_team != away_team`).
- **Pydantic**: Validates individual record schemas.
- **ConflictDetector**:
  - Compares existing match scores with incoming reports.
  - If a discrepancy occurs (e.g., existing 5–3 vs incoming 4–3), the match is flagged as `DISPUTED` and logged in audit records; it is **never silently overwritten**.
  - Rejects scores assigned to `SCHEDULED` or unplayed fixtures.

### Stage 5: Idempotent Persistence
- Upserts check uniqueness constraints before updating.
- Running the pipeline multiple times (`ingest-all`) does not create duplicate fixtures, duplicate squad numbers, or duplicate statistics.
