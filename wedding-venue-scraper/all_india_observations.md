# All-India Wedding Venue Data — Detailed Observations

> **Scope:** All-India national dataset | **Dataset:** Second scraping phase (full national run)
> **Total Venues:** 13,211 | **States:** 10 | **Sources:** WedMeGood (12,909) + VenueLook (302)
> **Charts:** `output/charts/all_india/` (10 charts)

---

## 1. Overview & Pipeline Context

After validating the pipeline on Rajasthan (~2,036 venues), the scraper was extended to all 10 approved Indian states: Rajasthan, Maharashtra, Karnataka, Tamil Nadu, West Bengal, Delhi NCR, Uttarakhand, Goa, Kerala, and Himachal Pradesh.

Raw records scraped: **~26,982** (WedMeGood alone)
After deduplication: **13,211** final records
Duplicates removed: **~13,771 (51%)** — higher dedup rate than Rajasthan pilot because VenueLook overlap was higher across dense metro cities
Processing time: Rajasthan + national runs combined

The national dataset is stored in `output/dataset/wedding_venues_india.csv` (13,211 rows × 17 columns) and the all-India charts are in `output/charts/all_india/`.

---

## 2. Geographic Distribution — State Level

### State-Wise Venue Counts

| State | Venues | % of Total | Median Price (₹) | Avg Rating | Avg Max Capacity |
|---|---|---|---|---|---|
| Maharashtra | 3,692 | 27.9% | 640 | 1.4 | 605 |
| Rajasthan | 2,036 | 15.4% | 700 | 1.2 | 859 |
| Karnataka | 1,749 | 13.2% | 550 | 1.4 | 583 |
| Tamil Nadu | 1,244 | 9.4% | 450 | 1.4 | 549 |
| West Bengal | 1,053 | 8.0% | 700 | 1.3 | 422 |
| Delhi NCR | 1,046 | 7.9% | 1,000 | 1.4 | 527 |
| Uttarakhand | 949 | 7.2% | 1,050 | 1.0 | 517 |
| Goa | 774 | 5.9% | 700 | 0.8 | 422 |
| Kerala | 368 | 2.8% | 600 | 0.5 | 517 |
| Himachal Pradesh | 300 | 2.3% | 875 | 0.9 | 307 |

**Key observations:**

- **Maharashtra dominates** (27.9%) — driven entirely by Mumbai, Pune, Thane, Navi Mumbai, and satellite cities. This is a metro-driven volume, not a destination wedding market.
- **Rajasthan second (15.4%)** — entirely destination wedding focused. Its 2,036 venues represent premium intent; Maharashtra's 3,692 are largely local function halls.
- **Karnataka third (13.2%)** — almost entirely Bangalore. The city is India's third-largest metro and has a huge local wedding market.
- **Kerala and Himachal Pradesh are underrepresented** (2.8% and 2.3%) — both are major destination wedding markets but may have fewer listings on WedMeGood or city slugs not yet configured in `cities.json`.
- **Himachal Pradesh has the lowest median capacity** (307 guests avg max) — reflecting smaller hill resort properties vs. large urban banquet halls.
- **Delhi NCR has the highest median price** (₹1,000 per plate) among all states — reflecting the premium purchasing power of the NCR market.

---

## 3. Top 20 Cities Nationally

| Rank | City | State | Venues | Median Price (₹) | Avg Rating |
|---|---|---|---|---|---|
| 1 | Bangalore | Karnataka | 1,520 | 550 | 1.5 |
| 2 | Mumbai | Maharashtra | 1,418 | 650 | 1.8 |
| 3 | Chennai | Tamil Nadu | 1,144 | 450 | 1.5 |
| 4 | Jaipur | Rajasthan | 1,085 | 650 | 1.4 |
| 5 | Kolkata | West Bengal | 913 | 700 | 1.4 |
| 6 | Pune | Maharashtra | 895 | 600 | 1.5 |
| 7 | Goa | Goa | 774 | 700 | 0.8 |
| 8 | Gurgaon | Delhi NCR | 585 | 1,000 | 1.5 |
| 9 | Udaipur | Rajasthan | 431 | 800 | 1.0 |
| 10 | Dehradun | Uttarakhand | 321 | 800 | 1.3 |
| 11 | Noida | Delhi NCR | 292 | 1,000 | 1.1 |
| 12 | Jodhpur | Rajasthan | 290 | 600 | 0.6 |
| 13 | Navi Mumbai | Maharashtra | 278 | 600 | 1.1 |
| 14 | Rishikesh | Uttarakhand | 249 | 1,200 | 0.6 |
| 15 | Pimpri-Chinchwad | Maharashtra | 243 | 550 | 1.1 |
| 16 | Thane | Maharashtra | 227 | 649 | 1.4 |
| 17 | Jim Corbett | Uttarakhand | 202 | 1,600 | 1.2 |
| 18 | Kochi | Kerala | 187 | 600 | 0.3 |
| 19 | Lonavala | Maharashtra | 177 | 1,200 | 0.9 |
| 20 | Ernakulam | Kerala | 154 | 550 | 0.6 |

**Key observations:**

- **Bangalore leads nationally (1,520 venues)** — more than Mumbai. This is surprising and reflects WedMeGood's strong penetration in the Bangalore market (tech-savvy user base actively listing venues).
- **Jim Corbett (₹1,600 median) and Rishikesh (₹1,200 median) are the most expensive cities per plate** nationally — these are premium eco-resort and adventure destination markets with no budget segment at all.
- **Chennai has the lowest median (₹450)** despite being the third-largest city by venue count — reflecting Tamil Nadu's highly competitive, locally-priced banquet market.
- **Goa at rank 7 (774 venues) appears with median ₹700** — deceptively in the middle, but Goa has very high beach/resort venue pricing mixed with many smaller local halls.
- **The top 3 cities (Bangalore, Mumbai, Chennai) are all metro local-wedding markets** — not destination markets. The first true destination city is Jaipur (rank 4).

---

## 4. Venue Type Distribution — National

### Overall

| Type | Count | % of Total | % of Classified |
|---|---|---|---|
| Banquet Hall | 6,437 | 48.7% | 55.7% |
| Hotel | 2,436 | 18.4% | 21.1% |
| Resort | 1,738 | 13.2% | 15.0% |
| Farmhouse | 778 | 5.9% | 6.7% |
| Palace | 356 | 2.7% | 3.1% |
| Beach | 83 | 0.6% | 0.7% |
| **Unclassified (NaN)** | **1,383** | **10.5%** | — |

**Banquet halls are the majority (48.7%) at the national level** — far higher than Rajasthan's 36%. This reflects the national dataset being dominated by Maharashtra, Karnataka, and Tamil Nadu, all of which have massive local banquet hall markets.

### State-Wise Type Distribution (Unique Insights)

| State | Dominant Type | Notable |
|---|---|---|
| Maharashtra | Banquet Hall (2,140) | 58% of all Maharashtra venues are banquet halls |
| Rajasthan | Banquet Hall (626) but Palace (216) is uniquely concentrated | Has 60.7% of all national palaces |
| Karnataka | Banquet Hall (953) | Many are Kalyana Mantapas — a culturally specific South Indian wedding hall |
| Tamil Nadu | Banquet Hall (888) | Many listed as "Kalyana Mandapam" — the Tamil equivalent |
| West Bengal | Banquet Hall (810) | Community halls and AC banquet spaces dominate |
| Delhi NCR | Farmhouse (281, 26.9%) | Second highest farmhouse count after Maharashtra — Delhi's "farmhouse wedding" culture |
| Goa | Resort (229, 29.6%) | Highest resort proportion nationally — reflects destination wedding focus |
| Himachal Pradesh | Resort (126, 42.0%) | Highest % of resorts of any state — mountain eco-resort market |
| Uttarakhand | Resort (321, 33.8%) | Mix of river-camp resorts (Rishikesh) + hill resorts (Dehradun, Mussoorie) |
| Kerala | Banquet Hall (173, 47%) | Lower than national avg; backwater resorts exist but appear as "resort" or unclassified |

**Rajasthan holds 60.7% of all 356 palace venues nationally** (216 of 356) — making it uniquely the "palace wedding" state of India.

**Delhi NCR has the highest farmhouse proportion (26.9%)** — the "Delhi farmhouse wedding" is a culturally specific format. Gurgaon and Noida peripheral farmhouses serve as semi-outdoor alternatives to urban banquet halls.

---

## 5. Capacity Analysis — National

**Field coverage:** 13,193 of 13,211 (99.9%) — nearly perfect.

| Segment | Threshold | Count | % |
|---|---|---|---|
| Boutique | < 100 guests | 660 | 5.0% |
| Medium | 100–499 guests | 7,208 | 54.6% |
| Large | 500–999 guests | 2,864 | 21.7% |
| Mega | ≥ 1,000 guests | 2,461 | 18.6% |

**Overall stats:** Min 25 guests | Max 9,000 guests | Mean 589 | Median 350

**Rajasthan had a higher median capacity (500) than the national median (350)** — confirming that Rajasthan caters to larger-format destination weddings, while the national average is pulled down by small urban banquet halls in South India.

**Mega venues (1,000+ guests) at 18.6% nationally** — primarily in Maharashtra (large function grounds), Rajasthan (palace courtyards), and Tamil Nadu (large community mandapams).

**Himachal Pradesh has the smallest venues** (avg max capacity 307) — hill stations have physical space constraints; properties are boutique by necessity.

---

## 6. Rating Analysis — National

**Field coverage:** 12,909 of 13,211 (97.7%) — high coverage.

| Rating Range | Count | % |
|---|---|---|
| Exactly 0.0 (no reviews) | 9,338 | 72.3% |
| > 0.0 and ≤ 4.0 | 615 | 4.8% |
| > 4.0 | 2,958 | 22.9% |
| No rating (null) | 302 | 2.3% |

**National mean rating: 1.27** | **Median rating: 0.00**

The pattern mirrors Rajasthan exactly: **72.3% of all national venues have a rating of 0.0**, meaning no reviews — not poor performance. This is a structural property of WedMeGood's platform where listings default to 0.0 rather than NULL.

**State-level rating quality (among non-zero rated venues):**

| State | Avg Rating (all incl. 0) | Meaningful (excl. 0) |
|---|---|---|
| Maharashtra | 1.4 | Most reviewed nationally |
| Karnataka | 1.4 | Active review culture (Bangalore) |
| Tamil Nadu | 1.4 | Similar to Karnataka |
| Rajasthan | 1.2 | Destination venues, fewer local reviews |
| Uttarakhand | 1.0 | Eco-resorts — less review-active |
| Goa | 0.8 | Very low — many unreviewed beach listings |
| Kerala | 0.5 | Lowest nationally — WedMeGood penetration lower in Kerala |

**Implication:** Kerala and Goa data should be used with extreme caution for any rating-based analysis. Maharashtra and metro South India have the most reliable rating signal.

---

## 7. ⚠️ Price Misclassification — National Analysis (THE MOST CRITICAL FINDING)

### The Root Problem

The same misclassification present in the Rajasthan dataset exists at the national level — **amplified by 6.5×** due to the larger dataset. This is not a bug in the code; it is a **semantic design gap**: `min_price` stores two different pricing concepts in the same column.

### Price Column Statistics

**`min_price` (13,203 venues — 99.9% coverage):**

| Bucket | Count | % | What it likely represents |
|---|---|---|---|
| ≤ ₹100 | 3 | 0.02% | Data entry errors / test listings |
| ₹101 – ₹500 | 3,009 | 22.8% | Per-plate prices, budget segment |
| ₹501 – ₹1,000 | 6,182 | 46.8% | Per-plate prices, standard segment |
| ₹1,001 – ₹5,000 | 2,636 | 20.0% | Per-plate prices, premium per-plate |
| ₹5,001 – ₹10,000 | 36 | 0.3% | Ambiguous — could be per-plate (luxury) or per-function (very small event) |
| ₹10,001 – ₹50,000 | 394 | 3.0% | Ambiguous — per-plate for ultra-luxury OR very small package |
| ₹50,001 – ₹1,00,000 | 429 | 3.3% | Almost certainly per-function pricing |
| ₹1,00,001 – ₹5,00,000 | 436 | 3.3% | Per-function, mid-tier packages |
| ₹5,00,001 – ₹10,00,000 | 56 | 0.4% | Per-function, premium packages |
| ₹10,00,001 – ₹95,00,000 | 22 | 0.2% | Per-function, luxury packages (e.g., Amanbagh ₹95L) |

**`price_per_plate` (9,920 venues — 75.1% coverage):**

| Bucket | Count | % |
|---|---|---|
| ≤ ₹500 | 2,822 | 28.4% |
| ₹501 – ₹1,000 | 4,744 | 47.8% |
| ₹1,001 – ₹5,000 | 2,238 | 22.6% |
| ₹5,001 – ₹10,000 | 32 | 0.3% |
| ₹10,001 – ₹50,000 | 67 | 0.7% |
| > ₹50,000 | 17 | 0.2% |

`price_per_plate` max is ₹50,000 (the hard cap enforced by the validator). Range is entirely within plausible per-plate territory for Indian weddings (₹175–₹50,000).

### The Duplication Problem

```
Both min_price and price_per_plate non-null: 9,920 venues
Of these, identical values: 9,856 (99.4%)
```

For **99.4% of venues where both columns are populated, they contain identical values.** This means `min_price` is simply a copy of `price_per_plate` for those venues. The two columns are not independent — they are the same data in two fields.

The 64 venues (0.6%) where they differ are the "conflict" cases described below.

### Conflict Cases: Venues With Both Package AND Per-Plate Prices

37 venues nationally have `min_price > ₹50,000` AND `price_per_plate` populated. These venues list both a venue package fee AND a separate catering per-plate charge:

**State distribution of conflicts:**

| State | Conflict Venues | Example |
|---|---|---|
| Rajasthan | 7 | Varmala Resort: ₹2L package + ₹2,500 per plate |
| Maharashtra | 4 | The Royal Atlantis: ₹2.45L package + ₹750 per plate |
| Karnataka | 5 | Sri Krishna Kalyana Mantapa: ₹4.5L package + ₹500 per plate |
| Tamil Nadu | 8 | Wings Convention Centre: ₹4L package + ₹499 per plate |
| Uttarakhand | 5 | Raga on the Ganges: ₹31L package + ₹2,000 per plate |
| Delhi NCR | 4 | Five Elements: ₹5L package + ₹900 per plate |
| West Bengal | 3 | Mandap Banquet: ₹1.5L package + ₹550 per plate |
| Goa | 1 | — |
| Kerala | 0 | — |
| Himachal Pradesh | 0 | — |

The **Raga on the Ganges (Uttarakhand)** case is the most extreme: `min_price = ₹31,00,000` and `price_per_plate = ₹2,000`. These are two completely different pricing dimensions for the same venue — the package fee for using the riverside resort, and the per-person catering cost on top of it. Both are real and correct, but storing them in adjacent columns without a `pricing_model` flag creates analytical confusion.

### State-Wise Count of Package-Price Venues (min_price > ₹1,00,000)

| State | High-Price Venues | % of State | Interpretation |
|---|---|---|---|
| Rajasthan | 102 | 5.0% | Heritage palaces, luxury resorts |
| Karnataka | 89 | 5.1% | Kalyana Mantapas with hall + catering package |
| Maharashtra | 84 | 2.3% | Mumbai farmhouses + luxury halls |
| Uttarakhand | 48 | 5.1% | River camp resorts (Rishikesh), Corbett resorts |
| Tamil Nadu | 44 | 3.5% | Large Tamil convention halls + mandapams |
| West Bengal | 29 | 2.8% | Kolkata banquet halls with fixed packages |
| Delhi NCR | 25 | 2.4% | Noida/Gurgaon farmhouses |
| Goa | 8 | 1.0% | Luxury beach resorts |
| Kerala | 7 | 1.9% | Backwater resorts |
| Himachal Pradesh | 4 | 1.3% | Mountain retreats |
| **Total** | **440** | **3.3%** | |

### Impact on the National Charts

- **Chart 03 (Cost Distribution — All India):** Shows state-level box plots where the "whiskers" extend to ₹95L for Rajasthan. This is not a meaningful distribution — it mixes ₹650/plate Jaipur banquet halls with ₹95L Amanbagh resort packages.
- **Chart 07 (Luxury Segmentation):** The "Luxury (>₹10L)" tier contains only the 22 venues priced ₹10L–₹95L. These are not "luxury in the same category as ₹9L venues" — they are qualitatively different products.
- **Chart 06 (Price vs. Rating):** 440 package-price venues appear as extreme outliers on the price axis. The trend line across all venues is distorted by these outliers.
- **Reported national median of ₹699 (from summary):** This is the median per-plate price of the 75% of venues quoting per-plate. The actual median all-event cost for a 300-guest wedding would be ₹699 × 300 = ₹2,09,700 — a very different number.

### What the Data Is Telling You (Correctly)

The data is correct. The pipeline scraped it correctly. The normalizer handled it correctly. The issue is **analytical framing**:

- **₹175–₹5,000 range (90% of venues):** These venues quote in "per plate" = per person for food. To get event cost: multiply by guest count.
- **₹1,00,000–₹95,00,000 range (3.3% of venues):** These venues quote as "per function" = entire event, food + venue + services bundled. Per-guest cost: divide by capacity.
- **₹5,000–₹1,00,000 (borderline, ~6.6%):** Unknown model; could be either high-end per-plate or low-end per-function.

### Recommended Additions to the Dataset

```
pricing_model: "per_plate" | "per_function" | "both" | "unknown"
estimated_event_cost_300guests: min_price × 300 (for per_plate) or min_price (for per_function)
```

This single field would resolve all chart ambiguity without touching the existing data.

---

## 8. Imputed Prices — National

**2,104 records have imputed `min_price`** (16% of 13,211 total venues):

| State | Imputed Venues | % of State | Imputation Value |
|---|---|---|---|
| Maharashtra | 554 | 15.0% | City median (~₹640) |
| Rajasthan | 308 | 15.1% | City median (~₹700) |
| Karnataka | 280 | 16.0% | City median (~₹550) |
| Tamil Nadu | 219 | 17.6% | City median (~₹450) |
| Uttarakhand | 199 | 21.0% | City median (~₹1,050) |
| Delhi NCR | 170 | 16.3% | City median (~₹1,000) |
| West Bengal | 168 | 16.0% | City median (~₹700) |
| Goa | 117 | 15.1% | City median (~₹700) |
| Himachal Pradesh | 52 | 17.3% | City median (~₹875) |
| Kerala | 37 | 10.1% | City median (~₹600) |

These are all venues that listed "Price on Request" or had no price string at all. The city-level median substitution is reasonable for approximate analytics, but **any venue with `_imputed_min_price = True` should be excluded from pricing research** and treated only as a presence/count data point.

Uttarakhand has the highest imputation rate (21%) — many Rishikesh and Jim Corbett eco-resort camps intentionally obscure pricing on aggregator platforms to drive direct inquiries.

---

## 9. Anomalous & Erroneous Records

### Extremely Low Prices (min_price < ₹200)

| Venue | State | City | Price | Notes |
|---|---|---|---|---|
| Hotel Sonai Garden Restaurant | Maharashtra | Pune | ₹100 | Likely a restaurant with a banquet room; ₹100/plate is implausibly low |
| Sai Samata Mangal Karyalaya | Maharashtra | Pune | ₹100 | Community hall; possible subsidized rate |
| Various Ulhasnagar halls | Maharashtra | Ulhasnagar | ₹150–₹180 | Budget community halls; may be correct for this area |
| Om Niwas Suite Hotel | Rajasthan | Jaipur | ₹175 | Budget hotel banquet; minimum rate possible |

3 venues have `min_price < ₹100` — these should be flagged or removed. ₹100 per plate for a wedding function is implausible in 2024 India (even subsidized community halls charge ₹150+).

Maharashtra (Ulhasnagar, Badlapur, Virar) has a cluster of ₹150–₹180 venues — these are real, reflecting the city's working-class budget wedding market near Mumbai. They are **not errors**, just low-tier local pricing.

### Geographic Tagging Errors

- **Jamshedpur** appears tagged as "Rajasthan" — Jamshedpur is in Jharkhand. Source: WedMeGood city tagging error.
- **Nagaur** (Rajasthan) had 1 venue with no price data — data point is near-empty.
- Some Goa venues may be tagged to Goa (city) when they are in North Goa or South Goa sub-districts — the city field is too coarse for Goa's geography.

### Source Coverage Imbalance

| Source | Venues | % |
|---|---|---|
| WedMeGood | 12,909 | 97.7% |
| VenueLook | 302 | 2.3% |

**The national dataset is effectively a WedMeGood dataset.** VenueLook contributed only 302 records (2.3%) nationally vs. 302 records of a potential ~15,000+ VenueLook listings. This means either:
1. VenueLook scraping was partial (fewer cities scraped via VenueLook), or
2. VenueLook's cross-source deduplication removed its records in favor of WedMeGood's higher-rated entries

VenueLook's 302 venues are likely in Rajasthan only (the pilot run included VenueLook), and the national expansion used only WedMeGood. This is a significant coverage gap — VenueLook has different venue inventory than WedMeGood and adds ~15–20% unique coverage.

ShaadiSaga contributed **0 records** to the national dataset — either not run, failed, or all ShaadiSaga records were deduplicated as WedMeGood duplicates.

---

## 10. Deep-Dive: State-by-State Observations

### Maharashtra (3,692 venues — #1 nationally)

- Almost entirely Mumbai metro + Pune metro. The large count reflects urban population density, not wedding tourism.
- 2,140 banquet halls (58%) — the Mumbai/Pune wedding market runs on local function halls, not destination venues.
- 199 farmhouses (5.4%) — Mumbai periphery farmhouse market (Alibaug, Karjat, Lonavala area).
- 357 resorts — primarily Lonavala and Mahabaleshwar hill stations.
- Median price ₹640 — slightly below national median (₹699) reflecting the competitive local market.
- **Highest number of imputed prices (554)** — many Mumbai venues list "Package on Request."
- Notable: Ulhasnagar (near Thane) has an unusual cluster of ₹150–₹180 venues — the cheapest wedding market in India.

### Karnataka (1,749 venues — #3 nationally)

- 1,520 of 1,749 (86.9%) are in **Bangalore** — the dataset is essentially a Bangalore-only dataset for Karnataka.
- The **Kalyana Mantapa** (South Indian wedding hall) is the dominant venue type — many are listed generically and classified as banquet halls or left unclassified (the keyword "kalyana" is not in the classifier's vocabulary).
- 953 banquet halls but many have `venue_type = NaN` — the classifier likely missed "Kalyana Mantapa" and "Samudhaya Bhavana" naming patterns.
- 89 venues (5.1%) have package-price >₹1L — including several large convention Mantapas in Bangalore/Mysore that quote a hall-booking fee separate from catering.
- Median price ₹550 — second cheapest after Tamil Nadu (₹450). Bangalore has a very competitive mid-market.
- Average max capacity 583 guests — efficient use of urban hall space.

### Tamil Nadu (1,244 venues — #4 nationally)

- **Lowest median price nationally (₹450)** — Chennai's wedding market is extremely competitive with many Kalyana Mandapam options.
- 1,144 of 1,244 (92%) are in **Chennai** — near-total concentration.
- 888 banquet halls (71.4%) — "Mandapam" culture dominates Tamil Nadu.
- 44 venues with package prices >₹1L — several large convention mandapams in Chennai (e.g., Wings Convention Centre ₹4L, SVV Kalyana Mandapam ₹7.4L).
- Average max capacity 549 — mid-range.
- **Lowest average rating (1.4)** but this reflects the 0=unreviewed pattern, not actual quality.

### West Bengal (1,053 venues — #5 nationally)

- 913 of 1,053 (86.7%) are in **Kolkata** — near-total concentration.
- 810 banquet halls (76.9%) — the highest banquet hall proportion of any state.
- Kolkata's "AC Banquet + Catering" package culture means almost all venues are banquet halls with in-house catering.
- 29 venues with package prices >₹1L — some large Kolkata convention halls.
- Median price ₹700 — same as Rajasthan, but for very different products (local urban halls vs. destination palaces).
- The beach (3 venues) and farmhouse (13 venues) counts are minimal — West Bengal's destination wedding geography (Digha, Mandarmoni) is not yet captured by WedMeGood's listing base.

### Delhi NCR (1,046 venues — #6 nationally)

- 585 in Gurgaon, 292 in Noida, rest in Delhi + Faridabad + Ghaziabad.
- **Highest median price nationally (₹1,000 per plate)** — NCR couples pay the most per guest nationally.
- 281 farmhouses (26.9%) — highest farmhouse proportion of any state. The "Delhi farmhouse wedding" (Chhatarpur, Chhawla, Noida peripheral farms) is a culturally specific format.
- 263 hotels — Gurgaon's business hotel + banquet market.
- 379 banquet halls.
- 25 venues with package prices >₹1L — luxury Delhi farmhouses (Five Elements ₹5L, etc.).
- Average max capacity 527 — urban halls, not mega venues.

### Uttarakhand (949 venues — #7 nationally)

- **Highest average price (₹30,084 mean)** — driven by Jim Corbett resorts (median ₹1,600) and Rishikesh resorts.
- **Highest median price (₹1,050)** among all states — every sub-segment is more expensive than urban states.
- 3 sub-markets: Dehradun (321 venues, median ₹800), Rishikesh (249 venues, median ₹1,200), Jim Corbett (202 venues, median ₹1,600).
- 321 resorts (33.8%) — highest resort proportion after Himachal Pradesh. Uttarakhand is a resort-dominant market.
- 48 venues with package prices >₹1L — eco-resort camps that quote per-night or per-event pricing rather than per-plate. Raga on the Ganges at ₹31L is the most extreme.
- **Highest imputation rate (21%)** — many Rishikesh eco-camps intentionally hide pricing on aggregators.

### Goa (774 venues — #8 nationally)

- **All 774 venues are in "Goa" as city** — no sub-city (North Goa / South Goa / Panjim) differentiation. This is a `cities.json` configuration limitation.
- 229 resorts (29.6%) — highest resort proportion nationally by %. This matches Goa's identity as a beach resort destination.
- 200 banquet halls (25.9%) — local Goan community halls.
- 30 beach venues (36% of all national beach venues) — Goa contributes the most beach classifications.
- Median price ₹700 — mid-range, but the distribution is wide (local halls at ₹300 vs beach resorts at ₹3,000+).
- **Lowest average rating (0.8) nationally** — reflects high proportion of unreviewed listings (many new beach properties listing on WedMeGood).
- Only 8 venues with package prices >₹1L — Goa's luxury market (Taj Exotica, Park Hyatt etc.) may not be listed on WedMeGood or was not scraped.

### Kerala (368 venues — #9 nationally)

- Severely underrepresented — Kerala is a major destination wedding state (backwaters, houseboats, Kerala-style mandapams) but only 368 venues are captured.
- 187 in Kochi, 154 in Ernakulam (same urban area, two listings in the data).
- 173 banquet halls (47%) — Kochi's local hall market.
- 54 resorts — Munnar and backwater resorts; many not captured.
- 4 beach venues — Kerala's beach wedding market (Kovalam, Varkala) is essentially invisible in this dataset.
- **Lowest meaningful rating (0.5 avg)** — WedMeGood has the lowest penetration in Kerala. Most Kerala venues are listed on Kerala-specific platforms (Kerala.com, WedKingdom).
- **Lowest imputation rate (10%)** — fewer "Price on Request" listings; Kerala venues either have prices or don't list on WedMeGood.

### Himachal Pradesh (300 venues — #10 nationally)

- **Smallest state dataset** (300 venues, 2.3%).
- 126 resorts (42%) — the highest resort proportion of any state. Himachal is purely a resort market for weddings.
- 97 hotels (32.3%) — hill station hotels (Shimla, Manali, Dalhousie).
- 51 banquet halls — minimal local market.
- **Smallest average max capacity (307)** — hill properties are inherently boutique-scale. Manali and Shimla venues simply cannot accommodate 1,000-guest Indian-style weddings.
- Median price ₹875 — moderate, reflecting that hill resorts are premium but not in the Uttarakhand/NCR league.
- Only 4 venues with package prices >₹1L.

---

## 11. Comparative Summary: Rajasthan vs. National

| Metric | Rajasthan (Phase 1) | All-India (Phase 2) |
|---|---|---|
| Total venues | 2,036 | 13,211 |
| Median min_price | ₹700 | ₹699 |
| Avg min_price | ₹26,825 | ₹15,920 |
| % with price_per_plate | 75.6% | 75.1% |
| Avg max capacity | 859 guests | 589 guests |
| % Banquet Hall | 36% | 48.7% |
| % Palace | 12.4% | 2.7% |
| % Resort | 20.5% | 13.2% |
| % with 0 rating | 72.3% | 72.3% |
| Sources: WedMeGood % | 96.7% | 97.7% |
| Package-price venues (>₹1L) | 102 (5.0%) | 440 (3.3%) |
| Imputed prices | 308 (15.1%) | 2,104 (15.9%) |

**The national median (₹699) is identical to Rajasthan's (₹700)** — this is coincidental; the national median being equal to Rajasthan's means that WedMeGood's per-plate pricing is remarkably consistent across India (most venues price in the ₹500–₹800 range regardless of state).

**Rajasthan has a significantly higher average (₹26,825 vs. ₹15,920 national)** — pulled up by 102 luxury package-price venues (Amanbagh at ₹95L, Raffles Udaipur at ₹14L, etc.) that have no equivalent in urban states.

---

## 12. Data Quality Scorecard — National

| Dimension | Score | Notes |
|---|---|---|
| Completeness | **A** | venue_name 100%, capacity 99.9%, min_price 99.9% |
| Accuracy | **B** | Prices semantically ambiguous; 0-rating misrepresentation |
| Consistency | **B-** | 99.4% of dual-column records are identical (redundant); 37 conflict records |
| Uniqueness | **A-** | 16.3% cross-source duplicates removed; some within-source may remain |
| Validity | **B+** | Hard rules enforced; soft rules flagged; 3 price outliers below ₹100 |
| Timeliness | **A** | Scraped in single continuous session; all records within same week |
| Geographic accuracy | **B** | Jamshedpur wrongly in Rajasthan; Goa lacks sub-city resolution |
| Source diversity | **C** | 97.7% single source (WedMeGood); ShaadiSaga = 0 records |

---

## 13. Charts Generated for All-India

All 10 charts in `output/charts/all_india/` correspond to this national dataset:

| Chart | File | Key Insight | Limitation |
|---|---|---|---|
| State Ranking | 01_state_ranking.png | Maharashtra #1, Rajasthan #2 | Count-based; doesn't show quality difference |
| City Heatmap | 02_city_heatmap.png | Bangalore, Mumbai, Chennai cluster at top | Metro cities dominate; destination cities hidden |
| Cost Distribution | 03_cost_distribution.png | NCR and Uttarakhand highest; TN lowest | Per-plate and per-function mixed in same axis |
| Venue Type Pie | 04_venue_type_pie.png | Banquet hall 48.7% nationally | 10.5% unclassified; Kalyana Mantapa missed |
| Capacity Histogram | 05_capacity_histogram.png | Bimodal: 200–500 guests vs 1000+ guests | Large right tail from Rajasthan/Maharashtra mega venues |
| Price vs. Rating | 06_price_vs_rating.png | Weak positive trend | 72% of points at y=0 (unreviewed) — trend is unreliable |
| Luxury Segmentation | 07_luxury_segmentation.png | Rajasthan and Uttarakhand in ₹10L+ tier | Tier labels assume per-plate; package venues distort |
| Micro Hotspots | 08_micro_hotspots.png | Bangalore and Mumbai areas dominate by count | Area field ~40% null nationally; many areas invisible |
| Cost-Location Matrix | 09_cost_location_matrix.png | State × type median price grid | NCR farmhouses most expensive; Uttarakhand resorts premium |
| Source Coverage | 10_source_coverage.png | WedMeGood dominates at 97.7% | VenueLook essentially invisible at national scale |

---

## 14. Key National Findings & Recommendations

**Finding 1 — India's wedding venue market is bifurcated:**
There are two distinct markets in this dataset that should never be analyzed together: (a) 12,771 local urban venues (₹300–₹5,000/plate; banquet halls, mandapams, community halls), and (b) 440 destination/luxury venues (₹1L–₹95L per function; palaces, premium resorts, luxury farmhouses). All current charts mix both.

**Finding 2 — Metro cities dominate by volume, Rajasthan dominates by value:**
Bangalore (1,520), Mumbai (1,418), Chennai (1,144) lead in count. But for high-value destination weddings, Jaipur (1,085), Udaipur (431), and Goa (774) are the relevant markets.

**Finding 3 — South India is underclassified:**
The Kalyana Mantapa and Kalyana Mandapam naming patterns are not in the venue type classifier's vocabulary. Hundreds of Karnataka and Tamil Nadu venues are classified as banquet hall or left unclassified. A South India-specific keyword expansion would recover 200–400 correct classifications.

**Finding 4 — Rating data is effectively useless for 72% of the dataset:**
9,338 venues have rating = 0.0 (no reviews). Any correlation analysis, recommendation engine, or quality scoring using ratings must first exclude these records.

**Finding 5 — Kerala and Goa are significantly undercaptured:**
Kerala (368 venues) and Goa (774 venues) are prominent destination wedding states but are underrepresented. Backwater resorts, Kovalam beach properties, and premium Goa beach venues are largely absent. Expanding city slugs and adding Kerala-specific sources would double the coverage.

**Finding 6 — The max_price column is completely empty:**
0 of 13,211 records have a `max_price` value. Every price range ("₹2L–₹10L") was collapsed to only the minimum. The upper bound of every pricing range is lost. This means the "price range" (an important signal for negotiability) is entirely missing from the dataset.

**Finding 7 — 2,104 venues (16%) have imputed prices:**
These records cannot be used for any pricing analysis. They should be filtered out before any price-distribution computation, price vs. rating correlation, or luxury corridor detection.

**Recommendation 1:** Add `pricing_model` column to distinguish per-plate from per-function records before any further analysis.

**Recommendation 2:** Fix the normalizer to also capture `max_price` from range strings ("₹2L–₹10L" should produce `min_price=200000, max_price=1000000`).

**Recommendation 3:** Add `rating_is_meaningful` boolean (True where rating > 0) and use only this subset for any rating-based analysis.

**Recommendation 4:** Expand venue type keywords with South Indian terms: "mantapa", "mandapam", "karyalay", "karyalaya", "kalyan" to recover ~300–400 misclassified venues.

**Recommendation 5:** Re-run VenueLook and ShaadiSaga for all 10 states to reduce the 97.7% WedMeGood dependency and add cross-source validation.

---

*All-India national observations — second scraping phase of the Indian Wedding Venue Intelligence Project*
*Data reflects scraping as of the pipeline run date; prices and venue availability may change over time*
