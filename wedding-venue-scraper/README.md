# Indian Wedding Destination Intelligence Dataset
 
A web scraping, data engineering, and analytics pipeline that builds a structured dataset of wedding venues across India and transforms it into actionable intelligence through visualisations and reports effect.

---

## What It Does

1. **Scrapes** verified wedding venue sources (WedMeGood, VenueLook) across 10 Indian states and 25+ cities
2. **Cleans & normalises** raw data — price strings, capacity ranges, venue types, area extraction
3. **Deduplicates** across sources using fuzzy matching
4. **Exports** a validated CSV + multi-sheet Excel workbook
5. **Generates** 10 static charts (PNG) + an interactive HTML dashboard + a markdown summary report

**Pilot run result:** 2,036 unique validated venues from Rajasthan alone (5 cities), scraped in ~10 minutes.

---

## Project Structure

```
wedding-venue-scraper/
├── main.py                        # Pipeline entry point
├── requirements.txt
├── config/
│   ├── settings.py                # Paths, rate limits, thresholds, constants
│   ├── cities.json                # 10 states, 25+ cities, 50+ micro-areas
│   └── selectors.json             # CSS selectors per source (reference)
├── src/
│   ├── scrapers/
│   │   ├── base.py                # HTTP session, SQLite cache, backoff, retry
│   │   ├── wedmegood.py           # Tier 1 — extracts from __INITIAL_STATE__ JSON
│   │   ├── venuelook.py           # Tier 1 — extracts from JSON-LD + comparison table
│   │   ├── shaadisaga.py          # Tier 1 — Selenium headless Chrome (JS-rendered)
│   │   ├── weddingwire.py         # Tier 2 — enrichment/cross-validation only
│   │   └── tourism.py             # Tier 2 — official name validation
│   ├── cleaning/
│   │   ├── normalizer.py          # Price regex, capacity, rating, venue type, area
│   │   ├── validator.py           # PRD §8 validation rules + QualityReport
│   │   └── deduplicator.py        # Fuzzy dedup (fuzzywuzzy), city-gated merge
│   └── analytics/
│       ├── charts.py              # 10 Matplotlib/Seaborn charts → PNG
│       ├── dashboard.py           # Plotly tabbed interactive HTML dashboard
│       └── report.py              # Markdown summary + luxury clusters + micro-locations
├── data/
│   ├── raw/                       # Per-source CSV dumps
│   ├── processed/                 # venues_clean.csv (post-normalise + dedup)
│   └── cache/                     # SQLite URL cache (7-day TTL)
├── output/
│   ├── dataset/                   # wedding_venues_india.csv + .xlsx
│   ├── charts/                    # 01_state_ranking.png … 10_source_coverage.png
│   ├── dashboard/                 # wedding_venues_dashboard.html
│   └── report/                    # wedding_venues_summary.md
└── tests/
    ├── test_normalizer.py          # 40+ price format tests, capacity, rating, area
    ├── test_validator.py           # All PRD §8 rules, median imputation
    └── test_deduplicator.py        # Fuzzy match, merge, rate calculation
```

---

## Setup

### Requirements

- Python 3.10+
- Google Chrome (only needed for ShaadiSaga / Selenium)

### Install

```bash
git clone <repo-url>
cd wedding-venue-scraper
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP fetching (Tier 1 & 2 static sources) |
| `beautifulsoup4` + `lxml` | HTML parsing |
| `selenium` | Headless Chrome for JS-rendered pages (ShaadiSaga) |
| `pandas` + `numpy` | Data processing, dedup, export |
| `openpyxl` | Excel workbook generation |
| `fuzzywuzzy` + `python-Levenshtein` | Cross-source fuzzy deduplication |
| `matplotlib` + `seaborn` | Static chart generation |
| `plotly` | Interactive HTML dashboard |
| `pytest` | Test runner |

---

## Usage

### Full pipeline (scrape + clean + export + analytics)

```bash
# All states, default sources (WedMeGood + VenueLook)
python main.py

# Target specific states
python main.py --states "Rajasthan" "Goa" "Kerala"

# Add ShaadiSaga (requires Chrome + ChromeDriver)
python main.py --sources wedmegood venuelook shaadisaga --states "Rajasthan"
```

### Analytics only (skip scraping, use existing cleaned data)

```bash
python main.py --skip-scraping
```

### Load from a custom CSV

```bash
python main.py --skip-scraping --input-csv path/to/your.csv
```

### Invalidate URL cache and re-scrape

```bash
python main.py --invalidate-cache --states "Goa"
```

### Run tests

```bash
pytest tests/ -v
# 84 tests, all passing
```

---

## Data Sources

| Source | Tier | Method | Data Available |
|---|---|---|---|
| [WedMeGood](https://www.wedmegood.com) | 1 | `__INITIAL_STATE__` JSON | Name, city, locality, price, capacity, rating, reviews, venue type |
| [VenueLook](https://www.venuelook.com) | 1 | JSON-LD + HTML table | Name, URL, address, capacity, price per plate |
| [ShaadiSaga](https://www.shaadisaga.com) | 1 | Selenium (JS-rendered) | Name, featured status, pricing |
| [WeddingWire India](https://www.weddingwire.in) | 2 | BeautifulSoup | Cross-validation: reviews + pricing |
| [Rajasthan Tourism](https://tourism.rajasthan.gov.in) | 2 | Requests | Heritage property name validation |
| [Goa Tourism](https://www.goatourism.gov.in) | 2 | Requests | Beach area name validation |

> **Tier 2 sources** are enrichment/validation only — not used for bulk discovery.

---

## Dataset Schema

Every record represents one venue. All prices are in INR (float).

| Field | Type | Description |
|---|---|---|
| `venue_id` | string | UUID |
| `venue_name` | string | Venue name |
| `state` | string | Indian state |
| `city` | string | City |
| `area` | string | Micro-location / locality |
| `venue_type` | enum | `palace` \| `resort` \| `beach` \| `farmhouse` \| `hotel` \| `banquet_hall` |
| `min_price` | float | Minimum price in INR |
| `max_price` | float | Maximum price in INR |
| `price_per_plate` | float | Per-plate cost in INR |
| `capacity_min` | int | Minimum guest capacity |
| `capacity_max` | int | Maximum guest capacity |
| `rating` | float | Rating (0.0–5.0) |
| `review_count` | int | Number of reviews |
| `source` | string | `wedmegood` \| `venuelook` \| `shaadisaga` |
| `source_url` | string | Direct URL to venue listing |
| `scraped_at` | datetime | ISO 8601 timestamp |

### Price normalisation

All raw price strings are converted to INR floats:

```
"₹5 Lakhs"          → min_price: 500000
"₹2L – ₹10L"        → min_price: 200000, max_price: 1000000
"₹2,500 per plate"   → price_per_plate: 2500
"₹1.5 Crore"         → min_price: 15000000
"₹50K – ₹200K"       → min_price: 50000, max_price: 200000
```

---

## Output Files

| File | Description |
|---|---|
| `output/dataset/wedding_venues_india.csv` | Final flat dataset |
| `output/dataset/wedding_venues_india.xlsx` | Excel: raw data + state pivot + city pivot + quality sheet |
| `output/charts/01_state_ranking.png` | Venues per state, sorted |
| `output/charts/02_city_heatmap.png` | Venue density: state × city heatmap |
| `output/charts/03_cost_distribution.png` | Price box plots by state and city |
| `output/charts/04_venue_type_pie.png` | Venue type distribution |
| `output/charts/05_capacity_histogram.png` | Guest capacity distribution |
| `output/charts/06_price_vs_rating.png` | Price vs. rating scatter with trend |
| `output/charts/07_luxury_segmentation.png` | Budget/mid/premium/luxury tier breakdown |
| `output/charts/08_micro_hotspots.png` | Top 20 areas by venue count |
| `output/charts/09_cost_location_matrix.png` | Median price heatmap: state × venue type |
| `output/charts/10_source_coverage.png` | Field fill rates per source |
| `output/dashboard/wedding_venues_dashboard.html` | Plotly interactive tabbed dashboard |
| `output/report/wedding_venues_summary.md` | Written findings + luxury clusters + top micro-locations |

---

## Pipeline Architecture

```
Phase 1 — Scraping
  └── Discover pagination → fetch listing pages → parse vendor JSON/HTML
      └── Cache every URL in SQLite (7-day TTL, bypasses on re-run)

Phase 2 — Cleaning
  ├── normalize_record()   — price regex, capacity parsing, venue type classification
  ├── deduplicate_within_source()  — exact URL / name+city match per source
  ├── validate_records()   — PRD §8 rules, null invalid fields, flag soft failures
  ├── deduplicate()        — cross-source fuzzy match (threshold 85, city-gated)
  └── apply_median_imputation()  — fill missing prices with city median

Phase 3 — Export
  └── CSV + Excel (raw data, state pivot, city pivot, quality sheet)

Phase 4 — Analytics
  ├── generate_all_charts()  — 10 Matplotlib/Seaborn PNGs
  ├── build_dashboard()      — Plotly interactive HTML
  └── generate_report()      — Markdown with luxury clusters, micro-location ranking
```

### Rate limiting

- **1.5–3.0 s** randomised delay between requests
- **Exponential backoff** on HTTP 429 (30 s base, max 5 retries)
- **Session rotation** every 50 requests (fresh User-Agent)
- **Sequential only** — no concurrent requests

---

## Pilot Run Results (Rajasthan, 2 sources)

| Metric | Value |
|---|---|
| Raw records scraped | 5,942 |
| After within-source dedup | 2,433 |
| After cross-source dedup | **2,036** |
| Duplicates removed | 397 (16.3%) |
| Capacity coverage | 100% |
| Rating coverage | 94.4% |
| Price coverage | 83.8% |
| Venue type coverage | 83.2% |
| Cities covered | 12 (5 Rajasthan cities × 2 sources) |
| Run time | ~10 minutes |

---

## Extending to More States

The Goa slugs in `cities.json` need updating — WedMeGood uses `goa` (not `north-goa`), and VenueLook uses `goa` too. Update [config/cities.json](config/cities.json) city slugs, then run:

```bash
python main.py --sources wedmegood venuelook --states "Goa" "Kerala" "Maharashtra"
```

To scrape all 10 states for the full 500–2,000 venue target:

```bash
python main.py --sources wedmegood venuelook
```

Estimated full run time: ~90 minutes (rate-limited; cached on subsequent runs).

---

## Target Geography

| State | Cities | Key Micro-Locations |
|---|---|---|
| Rajasthan | Udaipur, Jaipur, Jodhpur, Jaisalmer, Pushkar | Lake Pichola, Amer, Mehrangarh, Sam Sand Dunes |
| Goa | North Goa, South Goa, Panjim | Candolim, Calangute, Vagator, Cavelossim |
| Kerala | Kochi, Alleppey, Munnar, Kovalam | Fort Kochi, Kumarakom, Vembanad Lake |
| Maharashtra | Mumbai, Pune, Lonavala, Mahabaleshwar | Juhu, Alibaug, Lavasa |
| Karnataka | Bangalore, Mysore, Coorg | Whitefield, Kabini, Madikeri |
| Uttarakhand | Dehradun, Mussoorie, Jim Corbett, Rishikesh | Mall Road, Laxman Jhula |
| Tamil Nadu | Chennai, Mahabalipuram, Pondicherry | ECR Road, White Town, Auroville |
| Himachal Pradesh | Shimla, Manali, Dharamsala | The Ridge, Old Manali, McLeodganj |
| Delhi NCR | New Delhi, Gurgaon, Noida | Chattarpur, MG Road, Sector 29 |
| West Bengal | Kolkata | Park Street, Alipore, Rajarhat |

---

## Advanced Analytics (from `report.py`)

- **Luxury Wedding Corridors** — clusters where avg price > ₹10L with 3+ venues in same area
- **Cost vs. Popularity Curve** — classifies cities as overpriced / undervalued / balanced
- **Top 10 Micro-Locations** — composite score: venue density × avg rating × price diversity

---

## Success Criteria (PRD §14)

| Criterion | Status |
|---|---|
| ≥ 500 unique validated venues | **2,036 (Rajasthan pilot)** |
| ≥ 3 Tier 1 sources scraped (>80% fill rate) | **2 sources; capacity 100%, rating 94%** |
| All 10 visualisations generated | **10 / 10** |
| Price data for >60% venues | **83.8%** |
| Capacity data for >50% venues | **100%** |
| Deduplication overlap <5% (within final set) | **16.3% cross-source removed** |
| All advanced insights delivered | **Luxury clusters, cost curve, top micro-locations** |
| Complete documentation | **This README** |
