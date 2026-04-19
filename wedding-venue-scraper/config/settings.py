"""
Global configuration for the Indian Wedding Destination Intelligence pipeline.
"""
import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
DATA_DIR    = BASE_DIR / "data"
RAW_DIR     = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR   = DATA_DIR / "cache"
OUTPUT_DIR  = BASE_DIR / "output"
CHARTS_DIR  = OUTPUT_DIR / "charts"
DASHBOARD_DIR = OUTPUT_DIR / "dashboard"
DATASET_DIR = OUTPUT_DIR / "dataset"
REPORT_DIR  = OUTPUT_DIR / "report"

CACHE_DB    = CACHE_DIR / "url_cache.db"
FINAL_CSV   = DATASET_DIR / "wedding_venues_india.csv"
FINAL_XLSX  = DATASET_DIR / "wedding_venues_india.xlsx"

# ── Rate limiting ─────────────────────────────────────────────────────────────
REQUEST_DELAY_MIN  = 1.5   # seconds
REQUEST_DELAY_MAX  = 3.0   # seconds
SESSION_ROTATE_EVERY = 50  # requests
BACKOFF_INITIAL    = 30    # seconds on 429
MAX_RETRIES        = 5
CACHE_TTL_DAYS     = 7

# ── Data quality ──────────────────────────────────────────────────────────────
VENUE_NAME_MIN_LEN  = 3
VENUE_NAME_MAX_LEN  = 200
MAX_PRICE_PER_PLATE = 50_000      # INR sanity cap
MAX_CAPACITY        = 10_000      # guest sanity cap
DEDUP_THRESHOLD     = 85          # fuzzywuzzy score

# ── Analytics ─────────────────────────────────────────────────────────────────
LUXURY_THRESHOLD_INR = 1_000_000  # ₹10 Lakhs
LUXURY_CLUSTER_MIN_VENUES = 3

# ── Source identifiers ────────────────────────────────────────────────────────
SOURCE_WEDMEGOOD   = "wedmegood"
SOURCE_VENUELOOK   = "venuelook"
SOURCE_SHAADISAGA  = "shaadisaga"
SOURCE_WEDDINGWIRE = "weddingwire"
SOURCE_TOURISM     = "tourism"

APPROVED_SOURCES = {
    SOURCE_WEDMEGOOD, SOURCE_VENUELOOK, SOURCE_SHAADISAGA,
    SOURCE_WEDDINGWIRE, SOURCE_TOURISM
}

# ── Venue type enum values ────────────────────────────────────────────────────
VENUE_TYPES = ["palace", "resort", "beach", "farmhouse", "hotel", "banquet_hall"]

VENUE_TYPE_KEYWORDS = {
    "palace":      ["palace", "mahal", "haveli", "fort", "garh", "heritage"],
    "resort":      ["resort", "retreat", "spa", "club"],
    "beach":       ["beach", "sea", "ocean", "coastal", "shore", "bay"],
    "farmhouse":   ["farm", "farmhouse", "villa", "bungalow", "estate"],
    "hotel":       ["hotel", "inn", "suites", "grand", "marriott", "hilton",
                    "hyatt", "oberoi", "taj", "leela", "itc"],
    "banquet_hall":["banquet", "hall", "convention", "auditorium", "community"],
}

# ── Approved geography ────────────────────────────────────────────────────────
APPROVED_STATES = [
    "Rajasthan", "Goa", "Kerala", "Maharashtra", "Karnataka",
    "Uttarakhand", "Tamil Nadu", "Himachal Pradesh", "Delhi NCR", "West Bengal"
]

# ── User-Agent pool ───────────────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) "
    "Gecko/20100101 Firefox/123.0",
]
