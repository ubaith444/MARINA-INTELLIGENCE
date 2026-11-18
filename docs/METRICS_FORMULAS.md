# MARINA INTELLIGENCE — Analytics & Metric Formulas Specification

**Document Version:** 1.0.0  
**Target Environment:** Indian Super League (ISL) 2026–27 | Chennaiyin FC  
**Architecture Layer:** Step 3 — Football Analytics & Performance Intelligence Engine  

---

## 1. Principles of Mathematical Integrity

1. **Strict Preservation of Unavailable Data:**
   - If an advanced metric (such as Expected Goals $xG$, Expected Assists $xA$, or Distance Covered) is not tracked for a match or competition, it **MUST remain `None` (`NULL`)**.
   - Under no circumstances is missing data coerced or imputed to `0` or `0.0`.
2. **Prevention of Division-by-Zero (`safe_divide`):**
   - All rate, ratio, and percentage calculations use the guarded function:
     $$\text{safe\_divide}(a, b) = \begin{cases} \text{round}\left(\frac{a}{b}, 2\right) & \text{if } b > 0 \\ \text{None} & \text{if } b = 0 \text{ or } a \text{ is None} \end{cases}$$
3. **Sample Size Validation for Rates:**
   - Per-90 standardizations are only computed if a player meets the minimum playing time threshold (default: $\ge 45$ minutes). Sub-threshold values return `None` with `has_sufficient_minutes = False` to prevent small sample distortions.
4. **Benchmark Isolation:**
   - Open-source benchmark data (e.g., StatsBomb Open Data) is strictly restricted to algorithmic validation and test suites. It is never mixed into Chennaiyin FC production tables.

---

## 2. Module 1: Team Performance & Form Analytics

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

### 2.2 Venue Split (Home vs. Away)
Computed independently for fixtures where `Match.home_team_id == team_id` versus `Match.away_team_id == team_id`.

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
  *Positive values indicate finishing efficiency beyond baseline probabilistic expectations; negative values indicate underperformance.*

### 3.3 Goal Timing Distribution
- **First-Half Goal Ratio:**  
  $$\text{First Half } \% = \left(\frac{\text{Goals (1st Half)}}{\text{Total Goals}}\right) \times 100$$
- **Second-Half Goal Ratio:**  
  $$\text{Second Half } \% = \left(\frac{\text{Goals (2nd Half)}}{\text{Total Goals}}\right) \times 100$$

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

---

## 5. Module 4: Player Intelligence & Per-90 Standardizer

### 5.1 Per-90 Standardization
Standardizes volume statistics across varying minutes played to enable fair comparisons between regular starters, rotational players, and substitutes:
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

### 5.2 Tactical Radar Dimensions (0–100 Scale)
Computes 5 normalized tactical dimensions for head-to-head comparison, scaled against elite Indian Super League positional benchmarks:
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

## 6. Module 5: Match Intelligence & Tactical Reports

### 6.1 Match Tactical Report
Aggregates side-by-side performance indicators for home and away squads:
- Possession %
- Total shots, on target, off target, blocked
- Passing efficiency: passes total, passes completed, pass accuracy %
- Duels: tackles total, tackles won, tackle success %
- Set pieces: corner kicks, fouls committed, disciplinary sanctions

### 6.2 Half-by-Half Analysis
Splits match statistics into `FIRST_HALF` and `SECOND_HALF` phases to identify tactical adjustments, fatigue patterns, and momentum swings.

### 6.3 Head-to-Head ($H2H$) History
Aggregates all historical fixtures between two specific clubs:
- Total matches played
- Team A wins, Team B wins, Draws
- Cumulative goals scored by each club

---

## 7. Module 6: Tactical Analytics & Spatial Intelligence

### 7.1 Pitch Coordinate System
Standard FIFA / ISL pitch dimension model via `mplsoccer`:
- **Length:** $105.0\text{ meters}$ ($X \in [0, 105]$)
- **Width:** $68.0\text{ meters}$ ($Y \in [0, 68]$)
- **Goal Center:** $(105.0, 34.0)$
- **Goal Width:** $7.32\text{ meters}$ (Posts located at $Y = 30.34$ and $Y = 37.66$)

### 7.2 Shot Distance and Shooting Angle
- **Distance to Goal Center:**  
  $$d = \sqrt{(105.0 - x)^2 + (34.0 - y)^2}$$
- **Visible Goal Angle ($\theta$):**  
  Angle subtended by the goalposts from position $(x, y)$:
  $$\vec{v}_1 = (105.0 - x, 30.34 - y), \quad \vec{v}_2 = (105.0 - x, 37.66 - y)$$
  $$\cos\theta = \frac{\vec{v}_1 \cdot \vec{v}_2}{\|\vec{v}_1\| \|\vec{v}_2\|}$$
  $$\theta = \arccos(\text{clip}(\cos\theta, -1.0, 1.0)) \times \frac{180}{\pi}$$

### 7.3 Progressive Passes (Opta / Wyscout Standard)
A pass from $(x_1, y_1)$ to $(x_2, y_2)$ is classified as **Progressive** if and only if:
1. It originates outside the defensive 40% of the pitch:
   $$x_1 \ge 105.0 \times 0.40 = 42.0\text{ meters}$$
2. And satisfies at least one of the following criteria:
   - Moves the ball at least $10.0\text{ meters}$ closer to the opponent's goal center:
     $$\text{dist}(x_1, y_1) - \text{dist}(x_2, y_2) \ge 10.0\text{ meters}$$
   - Penetrates into the opponent penalty box:
     $$x_2 \ge 88.5 \quad \text{and} \quad 13.84 \le y_2 \le 54.16 \quad (\text{from outside the box})$$

### 7.4 Passing Network Graph Density
Measures structural team connectivity:
- **Potential Edges:**  
  $$E_{\text{potential}} = \frac{N(N - 1)}{2} \quad \text{where } N = \text{number of nodes}$$
- **Network Density:**  
  $$\text{Density} = \frac{|E_{\text{actual}}|}{E_{\text{potential}}}$$

### 7.5 Field Tilt (Territorial Dominance)
Measures territorial control by comparing attacking third activity:
$$\text{Field Tilt } \% = \left(\frac{\text{Team Final Third Passes}}{\text{Team Final Third Passes} + \text{Opponent Final Third Passes}}\right) \times 100$$

**Territorial Dominance Categories:**
- $\ge 60.0\%$: `HIGH` (Dominant territorial pressure)
- $45.0\% - 59.9\%$: `BALANCED` (Contested midfield territory)
- $< 45.0\%$: `DEFENSIVE` (Pinned in defensive/middle zones)

---

## 8. Summary of Data Integrity Guarantees

| Metric | Handling when Missing | Division-by-Zero Guard | Minimum Minutes Required |
|---|---|---|---|
| Expected Goals ($xG$) | Strictly `None` (Never `0.0`) | N/A | None |
| Expected Assists ($xA$) | Strictly `None` (Never `0.0`) | N/A | None |
| Shooting Accuracy % | `None` when shots = 0 | Yes | None |
| Shot Efficiency | `None` when $xG$ is `None` | N/A | None |
| Per-90 Statistics | `None` when minutes < threshold | Yes | $\ge 45$ min (default) |
| Field Tilt % | `None` when total passes = 0 | Yes | None |
| Radar Dimensions | Default score = 0.0 | Yes | Inherited from Per-90 |
