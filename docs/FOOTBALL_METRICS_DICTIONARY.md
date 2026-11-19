# MARINA INTELLIGENCE — Football Metrics & Mathematical Formulations Dictionary

**Document Version:** 4.0.0  
**Standard Compliance:** Opta / StatsBomb Analytical Standards  
**Safety Protocol:** Zero Division-by-Zero (`safe_divide`), Strict Null Preservation  

---

## 1. Mathematical Guarantees & Integrity Protocols

1. **Guarded Division (`safe_divide`):**
   $$\text{safe\_divide}(a, b) = \begin{cases} \text{round}\left(\frac{a}{b}, 2\right) & \text{if } b > 0 \\ \text{None} & \text{if } b = 0 \text{ or } a \text{ is None} \end{cases}$$
2. **Standardized Per-90 Rate Threshold:**
   Per-90 metrics are computed **strictly** when a player has recorded $\ge 45$ competitive minutes. If minutes $< 45$, the rate returns `None` with `has_sufficient_minutes = False` to prevent small sample inflation.
3. **Null Preservation:** Missing tracking or optical telemetry remains `None` / `NULL` and is **never** coerced to `0`.

---

## 2. Core Performance Metrics

### 2.1 Seasonal Team Performance
- **Points:**  
  $$\text{Points} = (\text{Wins} \times 3) + (\text{Draws} \times 1)$$
- **Goal Difference ($GD$):**  
  $$GD = \text{Goals For} - \text{Goals Against}$$
- **Win Percentage ($Win\%$):**  
  $$Win\% = \text{safe\_divide}(\text{Wins}, \text{Matches Played}) \times 100$$
- **Goals Per Match ($GPM$):**  
  $$GPM = \text{safe\_divide}(\text{Goals For}, \text{Matches Played})$$
- **Home Advantage Index ($HAI$):**  
  $$HAI = \text{safe\_divide}(\text{Home Points}, \text{Home Points} + \text{Away Points}) \times 100$$

### 2.2 Individual Player Metrics
- **Goals Per 90 ($G_{90}$):**  
  $$G_{90} = \text{safe\_divide}(\text{Goals} \times 90, \text{Minutes Played}) \quad (\text{Minutes} \ge 45)$$
- **Assists Per 90 ($A_{90}$):**  
  $$A_{90} = \text{safe\_divide}(\text{Assists} \times 90, \text{Minutes Played}) \quad (\text{Minutes} \ge 45)$$
- **Pass Completion Rate (%):**  
  $$\text{Pass Accuracy } \% = \text{safe\_divide}(\text{Completed Passes}, \text{Attempted Passes}) \times 100$$
- **Tackle Win Percentage (%):**  
  $$\text{Tackle Win } \% = \text{safe\_divide}(\text{Tackles Won}, \text{Attempted Tackles}) \times 100$$
- **Save Percentage (%):**  
  $$\text{Save } \% = \text{safe\_divide}(\text{Saves}, \text{Saves} + \text{Goals Conceded}) \times 100$$

---

## 3. Advanced Tactical Metrics

### 3.1 Expected Goals ($xG$)
Logistic regression model estimating probability of a shot resulting in a goal based on geometric and situational features:
$$\text{Log-odds} = \beta_0 + \beta_1(\text{Distance}) + \beta_2(\text{Visible Angle}) + \beta_3(\text{Is Inside Box}) + \beta_4(\text{Header})$$
$$xG = \frac{1}{1 + e^{-\text{Log-odds}}}$$
- **Visible Goal Angle ($\theta$):**
  Trigonometric angle subtended by goalposts $(y_1 = 30.66, y_2 = 37.34)$ from shooter coordinate $(x, y)$:
  $$\theta = \arctan\left(\frac{7.32 \cdot x}{x^2 + y^2 - (7.32/2)^2}\right)$$

### 3.2 Expected Assists ($xA$)
Attributed to the creating pass as the resulting shot's calculated $xG$ value.

### 3.3 Passes Allowed per Defensive Action (PPDA)
Measures pressing intensity in the opposition's defensive two-thirds:
$$\text{PPDA} = \frac{\text{Opponent Passes in Defensive Two-Thirds}}{\text{Tackles} + \text{Interceptions} + \text{Fouls Committed in Zone}}$$
*A lower PPDA value signifies higher pressing intensity.*

### 3.4 Field Tilt (%)
Measures territorial dominance through final-third passing share:
$$\text{Field Tilt } \% = \frac{\text{Team Final-Third Passes}}{\text{Team Final-Third Passes} + \text{Opponent Final-Third Passes}} \times 100$$

### 3.5 Passing Network Centrality
Graph-theoretic degree centrality measuring player involvement in ball circulation:
$$C_D(v) = \frac{\text{deg}(v)}{N - 1}$$
where $\text{deg}(v)$ is the number of active passing connections and $N = 11$ starting players.
