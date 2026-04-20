# Rajasthan Wedding Venue Data — Detailed Observations

> **Scope:** Rajasthan-only extract | **Dataset:** First scraping phase (Rajasthan pilot run)
> **Total Venues:** 2,036 | **Cities:** 12 | **Sources:** WedMeGood (1,969) + VenueLook (67)

---

## 1. Overview & Pipeline Context

This dataset was the **first phase of the project** — a deliberate pilot run restricted to Rajasthan before scaling to all of India. The decision was correct: Rajasthan is India's most prominent destination wedding state, and using it as a pilot allowed validation of all pipeline components (scraping, normalization, deduplication, analytics) on a manageable but meaningful dataset.

Raw records scraped: **~5,942**
After within-source deduplication: **2,433**
After cross-source fuzzy deduplication: **2,036**
Duplicates removed: **397 (16.3%)**
Processing time: **~10 minutes**

The 10 static charts in `output/charts/` and the Plotly dashboard in `output/dashboard/` all correspond to this Rajasthan dataset.

---

## 2. Geographic Distribution

### City-Level Venue Count

| City | Venues | % of Total |
|---|---|---|
| Jaipur | 1,085 | 53.3% |
| Udaipur | 431 | 21.2% |
| Jodhpur | 290 | 14.2% |
| Pushkar | 121 | 5.9% |
| Jaisalmer | 92 | 4.5% |
| Ajmer | 9 | 0.4% |
| Kumbhalgarh | 3 | 0.1% |
| Alwar | 1 | <0.1% |
| Dungarpur | 1 | <0.1% |
| Neemrana | 1 | <0.1% |
| Nagaur | 1 | <0.1% |
| Jamshedpur | 1 | <0.1% |

**Key observation:** Jaipur alone accounts for **53.3% of all Rajasthan venues** — making it a clear hub. Udaipur (21.2%) and Jodhpur (14.2%) form the secondary tier. The remaining 9 cities together contribute only 6.9%. This extreme concentration is expected: these three cities are Rajasthan's most active tourism and wedding destinations.

**Anomaly flagged:** Jamshedpur and Nagaur appear in the dataset — both are incorrectly geotagged to Rajasthan. Jamshedpur is in Jharkhand. This is a **source-side data quality issue** (WedMeGood geographic tagging error) that the scraper inherited. These 2 venues should be excluded from Rajasthan analysis.

**Underrepresented cities:** Neemrana (1 venue), Kumbhalgarh (3 venues), Alwar (1 venue) — all well-known wedding destinations — suggest that the `cities.json` configuration had limited slug coverage for these cities, causing the scraper to miss most of their listings. Expanding city slugs would recover these venues in a future run.

---

## 3. Source Distribution

| Source | Venues | % |
|---|---|---|
| WedMeGood | 1,969 | 96.7% |
| VenueLook | 67 | 3.3% |

**The dataset is almost entirely WedMeGood data.** VenueLook contributed only 67 venues (3.3%). This creates a **source bias**: WedMeGood's pricing model, listing conventions, and venue type classifications dominate the entire dataset. Any systematic error in WedMeGood's data (e.g., their per-plate vs. per-function price labeling — discussed in Section 7) propagates to 96.7% of the records.

ShaadiSaga (Tier-1, JavaScript-rendered) was available as a source but was either not run for Rajasthan or produced zero results in this pilot phase.

---

## 4. Venue Type Distribution

| Type | Count | % of Classified |
|---|---|---|
| Banquet Hall | 626 | 36.0% |
| Hotel | 431 | 24.8% |
| Resort | 356 | 20.5% |
| Palace | 216 | 12.4% |
| Farmhouse | 107 | 6.1% |
| Beach | 4 | 0.2% |
| **Unclassified (NaN)** | **296** | **—** |

296 venues (14.5%) have no venue type assigned — the keyword classifier found no match in their name or description. This is the most common data gap after price.

**Surprising finding:** Banquet halls dominate even in Rajasthan, which is typically associated with palaces and heritage properties in tourism marketing. This reflects that the **WedMeGood listing base is dominated by local/budget venues** (family function halls, community centers), not just the luxury destination wedding properties that appear in travel media.

**Palace at 12.4% (216 venues)** is actually very high by national standards — Rajasthan uniquely concentrates heritage properties. By comparison, Goa has only 9 palaces in the national dataset.

**Beach at 0.2% (4 venues)** is expected — Rajasthan is landlocked, so these 4 beach-classified venues are likely misclassified (possibly lakeside venues where "lake" was not a keyword, but "shore" or "coastal" matched).

---

## 5. Capacity Analysis

**Field coverage:** 2,034 of 2,036 venues (99.9%) — excellent.

| Segment | Threshold | Count | % |
|---|---|---|---|
| Boutique | < 100 guests | 78 | 3.8% |
| Medium | 100–499 guests | 866 | 42.5% |
| Large | 500–999 guests | 420 | 20.6% |
| Mega | ≥ 1,000 guests | 670 | 32.9% |

**Average max capacity:** 859 guests
**Median max capacity:** 500 guests
**Minimum max capacity:** 50 guests
**Maximum max capacity:** 8,000 guests

**Key observation:** 32.9% of Rajasthan venues have a maximum capacity of 1,000+ guests — a remarkably high proportion. This reflects two things: (1) Rajasthan's preference for large format Indian weddings (Baraat + multiple functions), and (2) many "venues" listed are open-air grounds or palace lawns that accommodate very large gatherings.

The **53.6% of venues hosting 500+ guests** (1,090 of 2,034) means the majority of the Rajasthan market targets medium-to-large weddings. Boutique (under 100 guests) is only 3.8% — destination micro-weddings are a niche.

**Capacity vs. venue type:**
- Resorts average **1,164 guests max** — highest among all types (likely include multiple indoor + outdoor event spaces)
- Palace venues average **844 guests max**
- Banquet halls average **736 guests max** — these are purpose-built function venues
- Farmhouses average **704 guests max**

---

## 6. Rating Analysis

**Field coverage:** 1,969 of 2,036 venues have a rating value (96.7%). However:

| Rating Value | Count | % |
|---|---|---|
| 0.0 (no reviews yet) | 1,471 | 72.3% |
| 0.1 – 4.0 | 64 | 3.1% |
| > 4.0 | 434 | 21.3% |
| No rating (null) | 67 | 3.3% |

**Mean rating: 1.17** | **Median rating: 0.00**

The mean of 1.17 and median of 0.00 are deeply misleading as summary statistics. **72.3% of venues (1,471) have a rating of exactly 0.0** — this means zero reviews on WedMeGood, not a poor rating. WedMeGood stores unrated venues as 0.0 rather than null, and the scraper faithfully captures this value.

The **correct interpretation** of Rajasthan ratings:
- **1,471 venues (72.3%):** No reviews at all — new listings, inactive venues, or venues that don't solicit platform reviews
- **434 venues (21.3%):** Well-reviewed — avg rating in the 4.0–5.0 range
- **64 venues (3.1%):** Actively reviewed with mixed to good scores

**For any analysis using ratings, the 0.0 values should be treated as null (no data), not as poor ratings.** This is a critical interpretation error that would skew any correlation analysis (e.g., "price vs. rating" chart) because 72% of the x-axis values are meaningless zeros.

**Notable high-rated micro-locations:**
- Kumbhalgarh: 3 venues, avg rating 5.0 (all top-rated)
- Sajjangarh (Udaipur): 3 venues, avg rating 5.0
- Umaid Bhawan (Jodhpur): 1 venue, rating 5.0 — the iconic Umaid Bhawan Palace

---

## 7. ⚠️ Price Misclassification — The Core Data Quality Issue

This is the most important finding from this dataset. **The `min_price` and `price_per_plate` columns contain two fundamentally different pricing models mixed together without distinction.**

### What the columns actually store

**`price_per_plate` (1,539 Rajasthan venues):**
This correctly stores **per-person catering cost** for venues that quote pricing this way.
- Range: ₹175 – ₹50,000
- Median: ₹650 per person
- Typical banquet hall: ₹400–₹800 per plate

**`min_price` (2,034 Rajasthan venues):**
This is where the confusion lives. It stores **two completely different things**:

1. **Per-plate prices** (for 75% of venues): identical to `price_per_plate`
   - Range: ₹175 – ₹5,000
   - Example: Hotel O Rasuj, Jaipur — `min_price = 650, price_per_plate = 650`

2. **Total venue package prices** (for 102 Rajasthan venues, 5%): the cost for the entire venue for one wedding event, quoted in raw string as "per function"
   - Range: ₹1,00,000 – ₹95,00,000
   - Example: Amanbagh, Jaipur — `min_price = 9,500,000 (₹95 Lakhs), price_per_plate = NULL`
   - Example: Dream Hill Resort, Udaipur — `min_price = 750,000 (₹7.5 Lakhs), price_per_plate = NULL`

### How the misclassification happened

WedMeGood's platform allows venues to list pricing in two formats:
- **"₹650 per plate"** → correctly parsed as per-plate
- **"₹7,50,000 per function"** → the normalizer's regex detects the large number and places it in `min_price`, but correctly **does not** place it in `price_per_plate` (since it's clearly not a per-plate figure)

The normalizer handled this correctly at the field level — it never confused a ₹7.5L function price for a per-plate price. **The misclassification is at the column semantic level**: `min_price` was designed to be a floor price in any unit, but the analytics and charts treat it as a comparable metric across all venues. Comparing ₹650 (per plate, per-person) against ₹7,50,000 (per function, entire event) in the same price distribution chart or heatmap produces **misleading results**.

### Evidence of the issue

```
Same value in min_price and price_per_plate: 1,514 of 1,539 (98.4%)
```
For 98.4% of Rajasthan venues where both columns are populated, they have identical values — confirming `min_price` is storing the per-plate value for these venues.

**Conflict cases (37 across all India, ~7 in Rajasthan):** Venues where `min_price` is very high (package price) but `price_per_plate` also exists (separate per-plate quote):

| Venue | min_price | price_per_plate | What this means |
|---|---|---|---|
| Varmala Resort and Banquet, Jaipur | ₹2,00,000 | ₹2,500 | Package ₹2L + per-plate ₹2,500 catering |
| Shiv Shakti Marriage Garden, Jaipur | ₹1,50,000 | ₹500 | Package ₹1.5L + per-plate ₹500 |
| Ganesh Paradise, Jaipur | ₹2,50,000 | ₹550 | Package ₹2.5L + per-plate ₹550 |
| Jaisalmer Desert Resort | ₹5,00,000 | ₹600 | Package ₹5L + per-plate ₹600 |

These are actually **correctly scraped** — these venues have a venue booking fee (package) plus a separate catering per-plate cost. The data is right; the column naming is misleading.

### Impact on charts

- **Chart 03 (Cost Distribution box plot):** The box for Rajasthan shows median ~₹700 and max ~₹95L — these two numbers are not comparable. The ₹700 is per-plate, the ₹95L is per-function. The chart is technically accurate but semantically invalid as a single distribution.
- **Chart 06 (Price vs. Rating scatter):** All 102 package-price venues appear as extreme outliers in the upper range of the price axis, compressing the rest of the chart.
- **Chart 07 (Luxury Segmentation):** The ₹10L+ "Luxury" tier is entirely composed of package-price venues. These should be a separate category, not a price tier within the same axis.
- **Median price of ₹700 for Rajasthan** reported in the summary is the median per-plate price for the 75% of venues quoting per-plate — misleadingly presented as "Rajasthan median venue price."

### Correct interpretation of prices

| Segment | Count | Price Range | Pricing Unit |
|---|---|---|---|
| Budget per-plate venues | ~1,200 | ₹175 – ₹700 | Per person |
| Mid-tier per-plate | ~700 | ₹700 – ₹5,000 | Per person |
| Ambiguous (borderline) | ~232 | ₹5,000 – ₹1,00,000 | Unknown — could be either |
| Package-price luxury | 102 | ₹1,00,000 – ₹95,00,000 | Entire event cost |

### Recommended fix

Add a `pricing_model` column:
- `"per_plate"` — venues where `min_price <= 50,000` and equals `price_per_plate`
- `"per_function"` — venues where `min_price > 1,00,000` and `price_per_plate` is null
- `"both"` — 37 venues with both columns populated at different scales
- `"unknown"` — 232 borderline venues (₹5K–₹1L range, ambiguous)

Then stratify all price charts by `pricing_model`.

---

## 8. Micro-Location Analysis (from Composite Scoring)

The micro-location composite score (density 40% + avg rating 30% + price diversity 30%) ranked:

| Rank | Area | City | Score | Venues | Avg Rating | Notes |
|---|---|---|---|---|---|---|
| 1 | Mansarovar | Jaipur | 0.62 | 81 | 1.8 | Highest density; rating low (many unreviewed) |
| 2 | Amer | Jaipur | 0.49 | 55 | 2.5 | Near Amer Fort; mix of heritage + budget |
| 3 | Vaishali Nagar | Jaipur | 0.44 | 63 | 1.6 | Dense local market, budget segment |
| 4 | Pushkar Lake | Pushkar | 0.42 | 8 | 3.0 | Highest avg rating among top 10 |
| 5 | Bani Park | Jaipur | 0.37 | 52 | 1.4 | Dense; many mid-tier banquet halls |
| 6 | Khuri | Jaisalmer | 0.32 | 5 | 0.0 | Desert camp area; all unreviewed |
| 7 | Sajjangarh | Udaipur | 0.31 | 3 | 5.0 | Only 3 venues but all perfectly rated |
| 8 | Umaid Bhawan | Jodhpur | 0.30 | 1 | 5.0 | Iconic palace; single venue |
| 9 | Sam Sand Dunes | Jaisalmer | 0.24 | 7 | 0.0 | All unreviewed |
| 10 | C-Scheme | Jaipur | 0.17 | 4 | 2.5 | Central Jaipur, premium location |

**Important observation:** The composite scoring is dominated by **venue density** (40% weight), which explains why Mansarovar (81 venues, mostly unreviewed banquet halls) scores above Sajjangarh (3 venues, all 5-star rated). This is a methodology limitation — the score favors volume over quality. Rebalancing weights (e.g., 25% density + 45% rating + 30% diversity) would surface Sajjangarh and Umaid Bhawan as the true luxury hotspots.

**Undervalued destinations detected:** Neemrana and Kumbhalgarh — below-median prices with above-median review satisfaction. Kumbhalgarh has only 3 venues but avg 5.0 rating — this is a hidden gem with near-zero pipeline coverage.

**Luxury corridor detection:** Insufficient area-level data to form clusters (reported in the summary). The area extraction field (`area`) is populated for only ~62% of venues — below the minimum needed for DBSCAN-style geographic clustering. This is a gap for the next run.

---

## 9. Data Completeness Summary

| Field | Populated | Coverage |
|---|---|---|
| venue_name | 2,036/2,036 | 100% |
| city | 2,036/2,036 | 100% |
| capacity_min | 2,036/2,036 | 100% |
| capacity_max | 2,034/2,036 | 99.9% |
| min_price (any value) | 2,034/2,036 | 99.9% |
| min_price (excluding imputed) | 1,726/2,036 | 84.8% |
| rating (any, including 0) | 1,969/2,036 | 96.7% |
| rating (meaningful, >0) | 498/2,036 | 24.5% |
| price_per_plate | 1,539/2,036 | 75.6% |
| venue_type | 1,740/2,036 | 85.5% |
| area/micro-location | ~1,262/2,036 | ~62% |
| source_url | 2,036/2,036 | 100% |
| review_count | ~1,867/2,036 | ~91.7% |

**2,104 records (across all-India) have imputed min_price** — of these, 308 are Rajasthan records where the original listing had "Price on Request" and the city-level median (₹700 for most Rajasthan cities) was substituted. These are marked `_imputed_min_price = True`.

---

## 10. Key Rajasthan Findings

1. **Jaipur is the undisputed capital of Rajasthan wedding venues** — 53% market share, 1,085 venues, the widest price range (₹175–₹95L), and the only city with multiple luxury palace options at the ₹10L+ tier.

2. **Udaipur commands the highest average price** (₹31,026 avg vs. ₹30,431 for Jaipur) with a smaller but more premium-skewed venue mix — most high-price package venues (>₹1L) are concentrated in Udaipur.

3. **Jaisalmer has the highest median price** (₹850) and the second-highest average (₹37,223 distorted by desert resorts) — a niche, premium market.

4. **Jodhpur is undervalued relative to its tourism profile** — median price ₹600, similar to budget cities, yet it hosts Umaid Bhawan Palace (rated 5.0) and multiple heritage properties. Its price distribution is depressed by a large number of local budget banquet halls.

5. **Banquet halls dominate by volume (36%) but resorts dominate by average price (₹72,005 avg)** — the market is bifurcated: a large budget segment and a small but high-value luxury segment.

6. **72% of venues have zero reviews** — only 24.5% of venues have meaningful engagement on WedMeGood's review system. The platform's review penetration is low, making star ratings unreliable as a quality proxy for 75% of the dataset.

7. **Price data is bimodal**: most venues cluster at ₹400–₹1,000 per plate (local weddings), while 102 venues (5%) have package prices of ₹1L–₹95L (destination weddings). These two segments should never be analyzed in the same price distribution.

8. **The max_price column is entirely empty (null)** — the scraper captured no upper price bounds. All range information was collapsed to `min_price` only. This means "₹2L–₹10L" ranges are stored as ₹2L, losing the upper bound entirely.

---

## 11. Charts Generated for Rajasthan

All 10 charts in `output/charts/` correspond to this Rajasthan dataset:

| Chart | File | What It Shows | Limitation |
|---|---|---|---|
| State Ranking | 01_state_ranking.png | Only Rajasthan (trivial for single-state run) | No comparative value alone |
| City Heatmap | 02_city_heatmap.png | Venue density across 12 cities | Jaipur visually dominates all other cities |
| Cost Distribution | 03_cost_distribution.png | Box plots by state + top cities | Mixed per-plate and per-function prices in same axis |
| Venue Type Pie | 04_venue_type_pie.png | 6 venue types + unclassified | 14.5% unclassified is invisible in pie |
| Capacity Histogram | 05_capacity_histogram.png | Log-scale distribution | Bimodal: boutique vs mega |
| Price vs Rating | 06_price_vs_rating.png | Scatter with trend line | 72% of rating axis = meaningless zeros |
| Luxury Segmentation | 07_luxury_segmentation.png | 4 price tiers by state | Tier thresholds mix per-plate and per-function |
| Micro Hotspots | 08_micro_hotspots.png | Top 20 areas by count | Dominated by density; missing quality signal |
| Cost-Location Matrix | 09_cost_location_matrix.png | State × venue type heatmap | Only 1 state; shows type-level price differences |
| Source Coverage | 10_source_coverage.png | Field fill rates by source | Reveals WedMeGood dominance |

---

*Rajasthan pilot observations — first scraping phase of the Indian Wedding Venue Intelligence Project*
