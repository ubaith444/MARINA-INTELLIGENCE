# MARINA INTELLIGENCE — Relational Database Schema Specification

**Document Version:** 4.0.0  
**Database Engine:** PostgreSQL 16 / SQLite Engine (`marina.db`)  
**ORM Framework:** SQLAlchemy 2.0 (Async)  
**Total Tables:** 23  

---

## 1. Schema Design Principles

1. **Strict Referential Integrity:** Foreign keys link every player appearance, lineup, event, and statistic to stable parent entities (`matches`, `teams`, `seasons`, `players`).
2. **Season & Matchday Isolation:** Historical records are immutable. Upcoming fixtures remain flagged `SCHEDULED` without fabricated scores or synthetic events.
3. **Audit Provenance:** All entities store `created_at`, `updated_at`, and data provenance linkages to `data_sources`.
4. **Discrepancy Preservation:** Ingestion conflicts between multiple providers are flagged and preserved in `data_verification` rather than silently overwritten.

---

## 2. Entity Relationship Overview

```
 [competitions] ──< [seasons] ──< [matches] ──< [match_events]
                          │             │       ├──< [match_shots]
                          │             │       └──< [match_passes]
                          │             ├──< [match_lineups]
                          │             ├──< [match_substitutes]
                          │             ├──< [player_match_statistics]
                          │             └──< [team_match_statistics]
                          │
 [teams] ───────────────< [matches] (home_team_id / away_team_id)
    │
    ├──< [team_squad_memberships] >── [players]
    ├──< [squad_registrations]    >── [players]
    └──< [season_leadership_members] >── [players]
```

---

## 3. Comprehensive Table Catalog

### 3.1 Core Competition & Scheduling
- **`competitions`**: League registry (`id`, `name`, `code`, `country`, `tier`).
- **`seasons`**: Season lifecycle (`id`, `competition_id`, `name`, `start_date`, `end_date`, `is_current`).
- **`venues`**: Stadium metadata (`id`, `name`, `city`, `capacity`, `surface`, `coordinates`).
- **`matches`**: Fixture & match record (`id`, `season_id`, `home_team_id`, `away_team_id`, `venue_id`, `match_number`, `scheduled_kickoff`, `actual_kickoff`, `match_status`, `home_score`, `away_score`, `fixture_leg`, `verification_status`, `has_discrepancy`).

### 3.2 Clubs, Players & Squad Management
- **`teams`**: Club identity (`id`, `name`, `short_name`, `slug`, `city`, `founded_year`).
- **`players`**: Individual master player registry (`id`, `slug`, `first_name`, `last_name`, `known_name`, `date_of_birth`, `nationality`, `secondary_nationality`, `primary_position`, `secondary_position`, `height_cm`, `weight_kg`, `preferred_foot`, `squad_number`, `joined_date`, `previous_club`, `contract_expiry`, `market_value_inr`).
- **`squad_registrations`**: Official seasonal league registration roster.
- **`team_squad_memberships`**: Active and historical club contract memberships.
- **`season_leadership_members`**: Dedicated senior leadership group council table scoped to `season_id` and `team_id` with `unique(season_id, team_id, player_id)`.

### 3.3 Matchday Lineups & Substitutions
- **`lineups`**: Historical import registry.
- **`match_lineups`**: Starting XI designations (`id`, `match_id`, `player_id`, `team_id`, `shirt_number`, `position`, `grid_x`, `grid_y`, `is_captain`).
- **`match_substitutes`**: Bench registrations, tactical substitutions, and substitution minute logs.

### 3.4 Match Events & Telemetry
- **`match_events`**: Granular timestamped event timeline (`id`, `match_id`, `team_id`, `primary_player_id`, `secondary_player_id`, `event_type`, `period`, `minute`, `stoppage_minute`, `description`, `is_verified`).
- **`match_shots`**: Spatial shot event coordinates (`id`, `match_id`, `team_id`, `player_id`, `minute`, `outcome`, `shot_type`, `x_coord`, `y_coord`, `expected_goals`).
- **`match_passes`**: Passing sequence logs.

### 3.5 Aggregated Performance Statistics
- **`player_match_statistics`**: Granular player performance record per match (`id`, `match_id`, `player_id`, `minutes_played`, `goals`, `assists`, `shots_total`, `shots_on_target`, `expected_goals`, `expected_assists`, `tackles_total`, `tackles_won`, `interceptions`, `clearances`, `blocks`, `passes_total`, `passes_completed`, `fouls_committed`, `yellow_cards`, `red_cards`, `saves`, `goals_conceded`, `clean_sheet`).
- **`team_match_statistics`**: Aggregated team match stats (`id`, `match_id`, `team_id`, `possession_pct`, `shots_total`, `shots_on_target`, `expected_goals`, `passes_total`, `passes_completed`, `tackles_total`, `interceptions`, `corners`, `fouls_committed`).

### 3.6 Data Governance & Ingestion Auditing
- **`data_sources`**: Registered providers (`ISL_OFFICIAL`, `CFC_OFFICIAL`, `AIFF_OFFICIAL`, `MANUAL_CURATION`).
- **`data_sync_logs`**: Sync run executions and records updated.
- **`data_verification`**: Multi-provider conflict and dispute preservation.
- **`import_history`**: CSV/JSON ingestion audit logs.
- **`squad_import_history`**: Roster synchronization archives.
