# MARINA INTELLIGENCE — Data Validation & Quality Assurance Framework

**Document Version:** 4.0.0  
**Pipeline Layer:** Ingestion & Validation Middleware  

---

## 1. Automated Validation Rules

The backend executes a 7-stage validation pipeline on every dataset ingestion and sync operation:

1. **Entity Existence Verification:**
   - Fixtures must map to valid team GUIDs for both `home_team_id` and `away_team_id`.
   - Player statistics must reference valid player IDs in the master `players` table.
2. **Duplicate Detection:**
   - Matches: Enforced uniqueness on `(season_id, home_team_id, away_team_id, scheduled_kickoff)`.
   - Players: Slug and squad registration uniqueness.
   - Leadership Group: `unique(season_id, team_id, player_id)`.
3. **Score & Result Consistency:**
   - Match results must mathematically reconcile with `home_score` and `away_score`:
     - If Home Score > Away Score $\rightarrow$ Home Win, Away Loss.
     - If Home Score == Away Score $\rightarrow$ Draw.
4. **Minutes Played Bounds:**
   - Individual player `minutes_played` $\in [1, 120]$.
   - Team starting XI total minutes must not exceed match duration $\times 11$.
5. **Rate Safety & Division by Zero:**
   - All rates pass through `safe_divide`.
   - Zero minutes played returns `None` for rates.
6. **Per-90 Rate Threshold:**
   - Minimum sample size threshold: $\ge 45$ competitive minutes required.
7. **Discrepancy Preservation:**
   - Conflicting schedule feeds are flagged with `has_discrepancy = True` and preserved in `data_verification` for administrative review.

---

## 2. Data Availability Statuses

Every metric and report renders an explicit data availability classification:

- **`AVAILABLE`:** Required telemetry is present, validated, and directly observed.
- **`PARTIAL`:** Some matches lack granular spatial coordinates, but event totals are verified.
- **`ESTIMATED`:** Computed via an explicit statistical model (e.g. Expected Goals logistic regression).
- **`UNAVAILABLE`:** High-frequency optical tracking (e.g. sprint distance, top speed) does not exist; returns explicit missing disclosure rather than $0$.
