# MARINA INTELLIGENCE — REST API Specification & Endpoint Inventory

**Document Version:** 4.0.0  
**Base URL:** `http://127.0.0.1:8000/api/v1`  
**Protocol:** HTTP/1.1 REST • JSON Payload Format  

---

## 1. System Health & Diagnostics

### `GET /health`
Returns runtime server diagnostics and database connectivity status.
- **Response `200 OK`:**
  ```json
  {
    "status": "healthy",
    "version": "4.0.0",
    "database": "connected",
    "timestamp": "2026-11-19T05:30:00Z"
  }
  ```

---

## 2. Season & Team Analytics Endpoints

### `GET /season/overview`
Computes dynamic season-level table standings, record, clean sheets, and points for Chennaiyin FC.
- **Query Parameters:** `season_id` (optional GUID), `team_id` (optional GUID).
- **Response `200 OK`:** Returns `SeasonOverviewResponse` (matches played, wins, draws, losses, points, goal difference, clean sheets, goals per match).

### `GET /season/form`
Returns chronological sequence of finished matches with opponent names, results (W/D/L), and scores.

### `GET /season/home-away`
Computes home vs away performance splits, win percentages, and Home Advantage Index (HAI).

### `GET /teams/leadership-group`
Returns Chennaiyin FC's verified five-member senior leadership group council without synthetic hierarchy:
- Members: Nuno Reis (#4, Def), P. C. Laldinpuia (#3, Def), Nikola Stojanović (#8, Mid), Samik Mitra (#1, GK), Mohammad Nawaz (#13, GK).

---

## 3. Player Intelligence Endpoints

### `GET /players`
Lists registered players with pagination, position filtering, and nationality flags.
- **Query Parameters:** `offset`, `limit`, `position`, `is_indian`.

### `GET /players/{id}`
Returns complete individual player biographical and career registration dossier.

### `GET /players/statistics`
Returns computed season performance statistics for all players.
- **Guarded Rates:** Per-90 statistics are computed strictly when `minutes_played >= 45`.

### `GET /analytics/players/{id}/performance`
Computes granular radar dimensions, duel win percentages, pass accuracy, and defensive contributions.

---

## 4. Match Centre Endpoints

### `GET /matches`
Returns all competitive fixtures distinguishing `FINISHED` official matches from `SCHEDULED` upcoming ties.

### `GET /matches/{id}`
Returns detailed match centre dossier including starting XI, substitutes, event timeline, shooting analysis, and passing networks.

### `GET /analytics/matches/compare`
Compares performance metrics across two distinct matches (`match_a_id`, `match_b_id`).

---

## 5. Tactical & Advanced Intelligence Endpoints

### `GET /analytics/average-lineup`
Calculates empirical average player positions on the pitch using verified starting XI records.

### `GET /analytics/xg`
Returns calculated Expected Goals ($xG$) and Expected Goals Conceded ($xGA$) using logistic regression shot modeling.

### `GET /analytics/shots`
Returns verified shot events with pitch coordinates $(x, y)$, shot distance, goal angle, and outcome (`GOAL`, `SAVED`, `BLOCKED`, `MISSED`).

### `GET /analytics/tactical/passing-network`
Computes graph network topology: nodes (players with average touch positions) and edges (completed pass volume).

### `GET /analytics/tactical/territorial`
Returns field tilt percentage, vertical third touches, horizontal flank attacks, and pressing intensity (PPDA).

### `GET /analytics/defensive-intelligence`
Aggregates tackles attempted/won, interceptions, clearances, blocks, and spatial recovery coordinates.

---

## 6. AI Football Analyst

### `POST /analytics/ai-analyst/ask`
Interrogates database records using natural language queries.
- **Request Body:** `{"query": "Analyse our defensive performance"}`
- **Response `200 OK`:** Returns structured 6-part dossier:
  1. Executive Summary
  2. Key Statistics Table
  3. Performance Evidence
  4. Football Interpretation
  5. Measurement Limitations
  6. Final Assessment
