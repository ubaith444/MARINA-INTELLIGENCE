# MARINA INTELLIGENCE — Analytics & Metric Formulas Specification

**Document Version:** 1.2.0  
**Target Environment:** Indian Super League (ISL) 2026–27 | Chennaiyin FC  
**Architecture Layer:** Step 3 & Step 5 — Football Analytics & Season Calculation Engine  

---

## 1. Principles of Mathematical Integrity

1. **Strict Preservation of Unavailable Data:**
   - If an advanced metric (such as Expected Goals $xG$, Expected Assists $xA$, or Possession %) is not tracked for a match or competition, it **MUST remain `None` (`NULL`)**.
   - Under no circumstances is missing data coerced or imputed to `0` or `0.0`.
2. **Prevention of Division-by-Zero (`safe_divide`):**
   - All rate, ratio, and percentage calculations use the guarded function:
     $$\text{safe\_divide}(a, b) = \begin{cases} \text{round}\left(\frac{a}{b}, 2\right) & \text{if } b > 0 \\ \text{None} & \text{if } b = 0 \text{ or } a \text{ is None} \end{cases}$$
3. **Completed Fixtures Only:**
   - All season-level analytics, form streaks, goal tallies, and rolling indicators filter strictly for completed fixtures (`MatchStatus.FINISHED`). Incomplete, scheduled, or postponed fixtures are excluded.
4. **Sample Size Validation for Rates:**
   - Per-90 standardizations are only computed if a player meets the minimum playing time threshold (default: $\ge 45$ minutes). Sub-threshold values return `None` with `has_sufficient_minutes = False` to prevent small sample distortions.
5. **Benchmark Isolation:**
   - Open-source benchmark data (e.g., StatsBomb Open Data) is strictly restricted to algorithmic validation and test suites. It is never mixed into Chennaiyin FC production tables.

---

## 2. Module 1: Team Performance & Seasonal Form Engine

### 2.1 Points and Match Record
- **Points:**  
  $$\text{Points} = (\text{Wins} \times 3) + (\text{Draws} \times 1)$$
- **Goal Difference ($GD$):**  
  $$GD = \text{Goals For} - \text{Goals Against}$$
- **Points Per Match ($PPM$):**  
  $$PPM = \frac{\text{Points}}{\text{Matches Played}}$$
- **Win Percentage ($Win\%$):**  
  $$Win\% = \left(\frac{\text{Wins}}{\text{Matches Played}}\right) \times 100$$
- **Goals Scored Per Match:**  
  $$\text{GPM} = \frac{\text{Goals For}}{\text{Matches Played}}$$
- **Goals Conceded Per Match:**  
  $$\text{GCPM} = \frac{\text{Goals Against}}{\text{Matches Played}}$$
- **Average Possession Percentage:**  
  $$\text{Avg Possession } \% = \frac{\sum_{i=1}^M \text{Possession}_i}{M} \quad \text{where } M = \text{matches with tracked possession}$$

### 2.2 Venue Splits & Home Advantage Index
Computed independently for fixtures where `Match.home_team_id == team_id` versus `Match.away_team_id == team_id`.
- **Home to Away Point Ratio:**  
  $$\text{Ratio}_{\text{H:A}} = \frac{\text{Home Points}}{\text{Away Points}}$$
- **Win Percentage Delta:**  
  $$\Delta Win\% = HomeWin\% - AwayWin\%$$
- **Home Advantage Index ($HAI$):**  
  $$HAI = \left(\frac{\text{Home Points}}{\text{Home Points} + \text{Away Points}}\right) \times 100$$

### 2.3 Recent Form Sequence
Calculated over the most recent $N$ finished matches (default: $N = 5$), ordered chronologically by `scheduled_kickoff`:
$$\text{Result} = \begin{cases} \mathbf{W} & \text{if Goals For} > \text{Goals Against} \\ \mathbf{D} & \text{if Goals For} = \text{Goals Against} \\ \mathbf{L} & \text{if Goals For} < \text{Goals Against} \end{cases}$$

---

## 3. Module 2: Attacking Analytics & Shot Quality

### 3.1 Shooting Accuracy & Conversion
- **Shooting Accuracy Percentage:**  
  $$\text{Shooting Accuracy } \% = \left(\frac{\text{Shots on Target}}{\text{Shots Total}}\right) \times 100$$
- **Shot Conversion Rate:**  
  $$\text{Conversion Rate } \% = \left(\frac{\text{Goals}}{\text{Shots Total}}\right) \times 100$$

### 3.2 Expected Goals ($xG$) and Shot Efficiency
- **Expected Goals Per Match ($xG/M$):**  
  $$xG/M = \frac{\sum xG}{\text{Matches with } xG \text{ tracked}}$$
- **Shot Efficiency (Goals vs. $xG$ Overperformance):**  
  $$\text{Shot Efficiency} = \text{Goals Scored} - \text{Expected Goals}$$

### 3.3 Goal Timing & Competition Phase Breakdown
- **Phase Breakdown:**  
  - First Half Goals: $\text{count}(e \in \text{Goals} \mid \text{period} = \text{FIRST\_HALF})$
  - Second Half Goals: $\text{count}(e \in \text{Goals} \mid \text{period} = \text{SECOND\_HALF})$
  - Extra Time Goals: $\text{count}(e \in \text{Goals} \mid \text{period} \in \{\text{EXTRA\_FIRST}, \text{EXTRA\_SECOND}\})$
- **Goals by Match & Goals by Player:**  
  Chronological match goal series and individual player goals + assists contributions.

---

## 4. Module 3: Defensive Resilience & Disciplinary Engine

### 4.1 Clean Sheets & Defensive Success
- **Clean Sheet Percentage:**  
  $$\text{Clean Sheet } \% = \left(\frac{\text{Matches with 0 Goals Conceded}}{\text{Matches Played}}\right) \times 100$$
- **Tackle Success Percentage:**  
  $$\text{Tackle Success } \% = \left(\frac{\text{Tackles Won}}{\text{Tackles Total}}\right) \times 100$$
- **Total Defensive Actions ($TDA$):**  
  $$TDA = \text{Tackles} + \text{Interceptions} + \text{Clearances} + \text{Blocked Shots}$$
- **Defensive Actions Per Match:**  
  $$TDA/M = \frac{TDA}{\text{Matches Played}}$$

### 4.2 Disciplinary Index
Standardized tactical penalty scoring to measure squad disciplinary risk:
$$\text{Discipline Index} = (\text{Yellow Cards} \times 1) + (\text{Red Cards} \times 3)$$

### 4.3 Match-by-Match Defensive Record
Tracks goals conceded, clean sheet boolean, tackles won/total, interceptions, clearances, saves, and cards for every fixture.

---

## 5. Module 4: Passing & Possession Analytics Engine

### 5.1 Passing Metrics & Volume
- **Total Passes:** $\sum \text{passes\_total}$ across completed matches.
- **Successful Passes:** $\sum \text{passes\_completed}$ across completed matches.
- **Failed Passes:**  
  $$\text{Failed Passes} = \text{Total Passes} - \text{Successful Passes}$$
- **Passing Accuracy Percentage:**  
  $$\text{Pass Accuracy } \% = \left(\frac{\text{Successful Passes}}{\text{Total Passes}}\right) \times 100$$

### 5.2 Match-by-Match Passing
Per-fixture breakdown including `passes_total`, `passes_completed`, `failed_passes`, `pass_accuracy_pct`, and `possession_pct`. Explicitly distinguishes aggregate provider feeds from granular telemetry.

---

## 6. Module 5: Performance Trends & Chronological Trajectory Engine

### 6.1 Last 5 Fixtures & Full Match History
Extracts the latest 5 completed matches with date, opponent, venue, final score, outcome ("W"/"D"/"L"), and points earned.

### 6.2 Monthly Output Aggregation
Aggregates goals scored and conceded grouped by year-month (`"YYYY-MM"`):
$$\text{Monthly GF}[Y\text{-}M] = \sum_{m \in M_{Y\text{-}M}} \text{Goals For}_m, \quad \text{Monthly GA}[Y\text{-}M] = \sum_{m \in M_{Y\text{-}M}} \text{Goals Against}_m$$

### 6.3 Points Progression
Chronological progression recording match number, date, opponent, points earned, and cumulative points to date.

### 6.4 Rolling Performance Trends
Computes rolling moving averages over a sliding window of $W$ matches (default: $W = 3$):
- **Rolling Goals For Avg:** $\frac{1}{k} \sum_{j=\max(0, i-W+1)}^i \text{GF}_j$
- **Rolling Goals Against Avg:** $\frac{1}{k} \sum_{j=\max(0, i-W+1)}^i \text{GA}_j$
- **Rolling Points Per Match:** $\frac{1}{k} \sum_{j=\max(0, i-W+1)}^i \text{Points}_j$
*(where $k$ is the actual number of matches in the window slice).*

---

## 7. Module 6: Player Intelligence & Per-90 Standardizer

### 7.1 Per-90 Standardization
Standardizes volume statistics across varying minutes played:
$$\text{Metric Per 90} = \left(\frac{\text{Metric Total}}{\text{Minutes Played}}\right) \times 90$$

**Standardized Per-90 Metrics:**
- `goals_per_90`
- `assists_per_90`
- `goal_contributions_per_90`
- `shots_per_90`
- `shots_on_target_per_90`
- `expected_goals_per_90`
- `expected_assists_per_90`
- `passes_completed_per_90`
- `tackles_per_90`
- `interceptions_per_90`

### 7.2 Tactical Radar Dimensions (0–100 Scale)
Computes 5 normalized tactical dimensions for head-to-head comparison:
1. **Scoring Threat:**  
   $$\text{Score} = \min\left(100.0, \max\left(0.0, \frac{\text{Goals Per 90}}{0.80} \times 100\right)\right)$$
2. **Shot Volume:**  
   $$\text{Score} = \min\left(100.0, \max\left(0.0, \frac{\text{Shots Per 90}}{3.50} \times 100\right)\right)$$
3. **Playmaking / Assists:**  
   $$\text{Score} = \min\left(100.0, \max\left(0.0, \frac{\text{Assists Per 90}}{0.50} \times 100\right)\right)$$
4. **Passing Output:**  
   $$\text{Score} = \min\left(100.0, \max\left(0.0, \frac{\text{Passes Completed Per 90}}{55.0} \times 100\right)\right)$$
5. **Defensive Ball Winning:**  
   $$\text{Score} = \min\left(100.0, \max\left(0.0, \frac{\text{Tackles Per 90} + \text{Interceptions Per 90}}{4.50} \times 100\right)\right)$$

---

## 8. Step 5 REST API Endpoint Catalog

| Method | Endpoint | Description | Key Response Fields |
|---|---|---|---|
| `GET` | `/api/v1/analytics/season` | Season Overview (default CFC) | `matches_played`, `points`, `ppm`, `average_possession_pct` |
| `GET` | `/api/v1/analytics/season/{season_id}` | Season Overview by Season ID | `matches_played`, `wins`, `points`, `goal_difference` |
| `GET` | `/api/v1/analytics/team/{team_id}` | Team Season Overview | `matches_played`, `home_record`, `away_record`, `recent_form` |
| `GET` | `/api/v1/analytics/team/{team_id}/attacking` | Attacking & Shot Analytics | `goals_scored`, `total_assists`, `goals_by_match`, `goals_by_player` |
| `GET` | `/api/v1/analytics/team/{team_id}/defensive` | Defensive Resilience & Duel Analytics | `goals_conceded`, `clean_sheets`, `discipline_index`, `defensive_by_match` |
| `GET` | `/api/v1/analytics/team/{team_id}/passing` | Passing & Possession Analytics | `total_passes`, `successful_passes`, `failed_passes`, `passing_accuracy_pct` |
| `GET` | `/api/v1/analytics/team/{team_id}/home-away` | Home vs Away Venue Performance | `home_record`, `away_record`, `point_ratio_home_to_away`, `home_advantage_index` |
| `GET` | `/api/v1/analytics/team/{team_id}/trends` | Chronological Performance Trends | `last_five_matches`, `monthly_goals_scored`, `points_progression`, `rolling_trends` |

---

## 9. Summary of Data Integrity Guarantees

| Metric | Handling when Missing | Division-by-Zero Guard | Minimum Minutes Required |
|---|---|---|---|
| Expected Goals ($xG$) | Strictly `None` (Never `0.0`) | N/A | None |
| Expected Assists ($xA$) | Strictly `None` (Never `0.0`) | N/A | None |
| Possession % | Strictly `None` (Never `0.0`) | N/A | None |
| Shooting Accuracy % | `None` when shots = 0 | Yes | None |
| Passing Accuracy % | `None` when passes = 0 | Yes | None |
| Shot Efficiency | `None` when $xG$ is `None` | N/A | None |
| Per-90 Statistics | `None` when minutes < threshold | Yes | $\ge 45$ min (default) |
| Radar Dimensions | Default score = 0.0 | Yes | Inherited from Per-90 |
| Home Advantage Index | `None` when total points = 0 | Yes | None |
