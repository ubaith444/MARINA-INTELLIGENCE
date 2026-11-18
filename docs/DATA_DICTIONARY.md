# MARINA INTELLIGENCE: Data Dictionary & Provenance Specification

This document details the schema definitions, normalization standards, and verification rules for all 13 core relational entities in **MARINA INTELLIGENCE**.

---

## 1. Relational Entities Specification

### 1.1 `competitions`
Registry of sanctioned leagues and cup competitions.
- `id` (UUID, Primary Key): Unique platform identifier.
- `code` (VARCHAR(32), Unique, Indexed): e.g. `ISL`, `SUPER_CUP`, `DURAND_CUP`.
- `name` (VARCHAR(128)): Official competition name (e.g., `Indian Super League`).
- `country` (VARCHAR(64)): Host nation (`India`).
- `federation` (VARCHAR(64)): Governing body (`AIFF`).
- `tier` (INTEGER): Pyramid level (`1` for ISL).
- `competition_type` (VARCHAR(32)): `LEAGUE`, `KNOCKOUT_CUP`, or `HYBRID`.
- `is_active` (BOOLEAN): Status flag.

### 1.2 `seasons`
Individual editions of a competition.
- `id` (UUID, Primary Key).
- `competition_id` (UUID, FK -> `competitions.id`, ON DELETE CASCADE).
- `name` (VARCHAR(64)): Human-readable label (e.g. `2026–27`).
- `slug` (VARCHAR(64), Indexed): Unique per competition (e.g. `isl-2026-27`).
- `start_date` / `end_date` (DATE, Nullable): Official calendar bounds.
- `is_current` (BOOLEAN): Active operational target season.
- `is_completed` (BOOLEAN): True when all matchdays have finished.

### 1.3 `venues`
Stadium infrastructure registry.
- `id` (UUID, Primary Key).
- `name` (VARCHAR(128), Unique): e.g. `Jawaharlal Nehru Stadium (Marina Arena)`.
- `city` (VARCHAR(64)): e.g. `Chennai`.
- `state` (VARCHAR(64), Nullable): e.g. `Tamil Nadu`.
- `country` (VARCHAR(64)): `India`.
- `capacity` (INTEGER, Nullable): Seating capacity (e.g. `40000`).
- `surface` (VARCHAR(32)): `Natural Grass`, `Hybrid`, or `Artificial`.

### 1.4 `teams`
Football club franchises.
- `id` (UUID, Primary Key).
- `name` (VARCHAR(128), Unique): Official registered name (`Chennaiyin FC`).
- `short_name` (VARCHAR(32)): Official abbreviation (`CFC`).
- `slug` (VARCHAR(64), Unique): URL-friendly slug (`chennaiyin-fc`).
- `founded_year` (INTEGER, Nullable): Club establishment (`2014`).
- `primary_venue_id` (UUID, FK -> `venues.id`, ON DELETE SET NULL).
- `primary_color` (VARCHAR(16)): Primary club hex code (e.g. `#003399` Marina Blue).
- `secondary_color` (VARCHAR(16)): Secondary hex code (`#FFFFFF`).

### 1.5 `players` (Decoupled Player Identity)
Intrinsic biological human identity, completely decoupled from temporary club contracts.
- `id` (UUID, Primary Key).
- `slug` (VARCHAR(128), Unique): Canonical identifier (e.g. `farukh-choudhary`).
- `first_name` (VARCHAR(64)).
- `last_name` (VARCHAR(64)).
- `known_name` (VARCHAR(128), Nullable): Display/jersey name (`Farukh Choudhary`).
- `date_of_birth` (DATE, Nullable).
- `nationality` (VARCHAR(64)): Primary sporting nationality (`India`).
- `primary_position` (ENUM): Tactical position (`PlayerPosition.LW`).
- `secondary_position` (ENUM, Nullable).
- `preferred_foot` (VARCHAR(16), Nullable): `LEFT`, `RIGHT`, `BOTH`.

### 1.6 `squad_registrations`
Official seasonal registration binding a player to a club team.
- `id` (UUID, Primary Key).
- `player_id` (UUID, FK -> `players.id`, ON DELETE CASCADE).
- `team_id` (UUID, FK -> `teams.id`, ON DELETE CASCADE).
- `season_id` (UUID, FK -> `seasons.id`, ON DELETE CASCADE).
- `jersey_number` (INTEGER, Nullable): Official squad number (1-99).
- `squad_status` (ENUM): `FIRST_TEAM`, `RESERVES`, `ACADEMY`, `ON_LOAN`.
- `registered_at` / `deregistered_at` (DATE, Nullable).
- *Constraint*: `UniqueConstraint(season_id, team_id, player_id)`.

### 1.7 `matches`
Competitive fixtures across their full lifecycle.
- `id` (UUID, Primary Key).
- `season_id` (UUID, FK -> `seasons.id`).
- `home_team_id` / `away_team_id` (UUID, FK -> `teams.id`).
- `venue_id` (UUID, FK -> `venues.id`, ON DELETE SET NULL).
- `scheduled_kickoff` / `actual_kickoff` (TIMESTAMP WITH TIME ZONE).
- `match_status` (ENUM): `SCHEDULED`, `TIMED`, `IN_PLAY`, `FINISHED`, `POSTPONED`, `CANCELLED`.
- `home_score` / `away_score` (INTEGER, STRICTLY NULLABLE):
  - **MANDATORY INTEGRITY RULE**: Must remain `NULL` for `SCHEDULED` and unplayed matches.

### 1.8 `lineups`
Tactical squad selections per fixture.
- `id` (UUID, Primary Key).
- `match_id` (UUID, FK -> `matches.id`, ON DELETE CASCADE).
- `team_id` / `player_id` (UUID, FKs).
- `lineup_role` (ENUM): `STARTER`, `BENCH`, `RESERVE`.
- `position` (ENUM, Nullable): Assigned match position.
- `tactical_formation` (VARCHAR(32), Nullable): e.g. `4-2-3-1`.
- `minutes_played` (INTEGER, Nullable): Pitch time.

### 1.9 `match_events`
Chronological discrete match events.
- `id` (UUID, Primary Key).
- `match_id` (UUID, FK -> `matches.id`, ON DELETE CASCADE).
- `event_type` (ENUM): `GOAL`, `PENALTY_GOAL`, `OWN_GOAL`, `SHOT`, `SAVE`, `YELLOW_CARD`, `RED_CARD`, `SUBSTITUTION`, `VAR_DECISION`.
- `period` (ENUM): `FIRST_HALF`, `SECOND_HALF`, `EXTRA_FIRST`, etc.
- `minute` (INTEGER): Match clock minute.
- `verification_status` (ENUM): `UNVERIFIED`, `PROVISIONAL`, `VERIFIED`, `OFFICIAL`, `DISPUTED`.

### 1.10 `team_match_statistics`
Aggregate team performance metrics.
- `id` (UUID, Primary Key).
- `match_id` (UUID, FK -> `matches.id`).
- `team_id` (UUID, FK -> `teams.id`).
- `data_source_id` (UUID, FK -> `data_sources.id`).
- `verification_status` (ENUM).
- **METRICS (STRICTLY NULLABLE)**:
  `possession_pct`, `shots_total`, `shots_on_target`, `expected_goals` (xG), `passes_total`, `pass_accuracy_pct`, `tackles_total`, `corners`, `fouls_committed`, `yellow_cards`, `red_cards`.
  - **MANDATORY INTEGRITY RULE**: Unmeasured metrics remain `NULL`. Never cast missing values to `0`.

### 1.11 `player_match_statistics`
Individual player performance metrics.
- `id` (UUID, Primary Key).
- `match_id`, `player_id`, `team_id`, `data_source_id` (UUID FKs).
- **METRICS (STRICTLY NULLABLE)**:
  `minutes_played`, `goals`, `assists`, `shots_total`, `expected_goals` (xG), `expected_assists` (xA), `passes_completed`, `tackles_won`, `interceptions`, `distance_covered_km`, `sprints_count`, `top_speed_kmh`.

### 1.12 `data_sources`
Catalog of authoritative data providers.
- `id` (UUID, Primary Key).
- `code` (VARCHAR(64), Unique): e.g. `ISL_OFFICIAL`, `CHENNAIYIN_FC_OFFICIAL`, `AIFF_OFFICIAL`, `STATSBOMB_OPEN_DATA`.
- `name` (VARCHAR(128)).
- `provider_type` (ENUM): `OFFICIAL_LEAGUE`, `CLUB_COMMUNICATIONS`, `FEDERATION`, `DATA_PROVIDER`, `MANUAL_CURATION`.
- `trust_score` (INTEGER, 1-100).

### 1.13 `import_history`
Audit and provenance tracking log.
- `id` (UUID, Primary Key).
- `data_source_id` (UUID, FK -> `data_sources.id`).
- `entity_type` (VARCHAR(64)): `FIXTURES`, `RESULTS`, `SQUAD`, `STATISTICS`.
- `batch_id` (VARCHAR(128), Indexed).
- `status` (ENUM): `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `PARTIAL`.
- `records_imported` / `records_failed` (INTEGER).
- `checksum_hash` (VARCHAR(128)): SHA-256 hash of immutable raw payload.
- `payload_path` (VARCHAR(512)): File path within `raw_data_archive/`.
- `source_url` (VARCHAR(512), Nullable).
