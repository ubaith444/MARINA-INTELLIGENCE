# MARINA INTELLIGENCE — Authoritative Data Sources & Provenance Catalog

**Document Version:** 4.0.0  
**Target Environment:** Indian Super League (ISL) 2026–27  
**Entity:** Chennaiyin FC  

---

## 1. Primary Authoritative Feeds

MARINA INTELLIGENCE establishes four discrete data source levels to guarantee auditability and eliminate fabricated data:

| Source Code | Source Name | Source Category | Trust Rating | Scope & Coverage |
|---|---|---|---|---|
| `ISL_OFFICIAL` | Indian Super League Official Match Centre | League Management | **100/100** | Official fixture schedule, kickoff times, venues, match referees, published scorelines |
| `CFC_OFFICIAL` | Chennaiyin FC Official Communications | Club Operations | **100/100** | Squad registry, contract expiries, market valuations, leadership group announcements |
| `AIFF_OFFICIAL` | All India Football Federation Competitions Registry | National Federation | **95/100** | Player birth dates, domestic registration status, historical appearances |
| `MANUAL_CURATION` | Tactical Video Analyst Tagging Pipeline | Internal Performance Dept | **90/100** | Spatial shot coordinates $(x, y)$, defensive action coordinates, passing connections |

---

## 2. Ingestion Files & Provenance Mapping

The platform includes verified raw datasets in `backend/src/marina/data/`:

### 2.1 `chennaiyin_fc_2026_27_fixtures.csv` (and `.json`)
- **Records:** 24 regular season ISL fixtures.
- **Coverage:**
  - Matches 1 to 5: `FINISHED` official matches with home/away designation, verified scores, and match events.
  - Matches 6 to 24: `SCHEDULED` unplayed fixtures with confirmed kickoffs, venues, and opponent names.
- **Discrepancy Flags:**
  - Match 7 (vs Mumbai City FC) includes recorded discrepancy notes (`Schedule discrepancy: CFC announcement lists Mumbai City away 30 Nov, while ISL lists Chennaiyin home 28 Nov`).

### 2.2 `chennaiyin_fc_2026_27_squad.csv` (and `.json`)
- **Records:** 28 officially registered first-team players.
- **Attributes:** Squad number, player name, position, verified birth date, nationality, height, preferred foot, previous club, contract expiry, and market valuation.

---

## 3. Coordinate Systems & Normalization

All spatial event coordinates (shots, passes, touches, defensive actions) are ingested and normalized according to international standards:

- **Pitch Dimensions:** $105.0\text{ m}$ (length) $\times 68.0\text{ m}$ (width).
- **Normalized Coordinate Range:** $x \in [0.0, 100.0]$, $y \in [0.0, 100.0]$.
  - $x = 0$: Defending goal line.
  - $x = 100$: Opponent attacking goal line.
  - $y = 0$: Left touchline.
  - $y = 100$: Right touchline.
- **SVG Viewport Space:** Mapped directly to $1050 \times 680$ pixels on `FootballPitch.tsx` with zero distortion.
