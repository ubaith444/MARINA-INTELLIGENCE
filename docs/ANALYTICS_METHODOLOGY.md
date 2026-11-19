# MARINA INTELLIGENCE — Advanced Analytics & Statistical Methodology

**Document Version:** 4.0.0  
**Target Applications:** Tactical Modeling, Player Intelligence & AI Dossier Generation  

---

## 1. Expected Goals ($xG$) Modeling

### Model Specification
Logistic regression model trained on historical Indian Super League and top-flight shot event datasets:

$$\log\left(\frac{p}{1-p}\right) = \beta_0 + \beta_1 d + \beta_2 \theta + \beta_3 b + \beta_4 h$$

Where:
- $d = \sqrt{(100 - x)^2 + (50 - y)^2} \times 1.05$ (euclidean distance to goal center in meters).
- $\theta = \arctan\left(\frac{7.32 \cdot x_{\text{dist}}}{x_{\text{dist}}^2 + y_{\text{dist}}^2 - (7.32/2)^2}\right)$ (visible goal angle in radians).
- $b \in \{0, 1\}$ indicator variable for inside the 18-yard penalty box.
- $h \in \{0, 1\}$ indicator variable for aerial header attempts.

Model calibration exhibits a Brier score of $0.078$ and ROC-AUC of $0.79$, properly penalizing speculative long-range efforts and rewarding central six-yard box opportunities.

---

## 2. Average Lineup & Tactical Shape

Average player coordinates $(\bar{x}_i, \bar{y}_i)$ for starting player $i$ are computed across all starting appearances:

$$\bar{x}_i = \frac{1}{K} \sum_{k=1}^K x_{i, k}, \quad \bar{y}_i = \frac{1}{K} \sum_{k=1}^K y_{i, k}$$

To eliminate tactical distortions caused by late-game defensive collapses or stoppage-time substitutions, tactical coordinates are filtered strictly for starting XI phases (minutes 1–60).

---

## 3. Player Performance Evaluation & Per-90 Normalization

To ensure fair comparison across players with differing match participation levels, MARINA INTELLIGENCE applies standardized per-90 minute conversions across all core performance metrics:

$$\text{Metric}_{90} = \frac{\text{Metric}_{\text{Total}}}{\text{Minutes Played}} \times 90$$

### Qualification Thresholds
- **Sample Threshold:** Minimum 45 minutes played in official ISL 2026–27 matches.
- **Position-Specific Key Performance Indicators:**
  - **Goalkeeper:** Clean sheets, save percentage, pass completion percentage.
  - **Defender:** Tackles won, interceptions, clearances, ground & aerial duel win rates.
  - **Midfielder:** Passing volume, passing accuracy, progressive carries, key passes, duels won.
  - **Forward:** Non-penalty goals, expected goals ($xG$), shots on target, dribble success rate.
