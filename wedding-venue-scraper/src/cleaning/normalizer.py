"""
Price and field normalization for raw scraped venue records.
Converts heterogeneous raw text into typed, analytics-ready fields.
"""
import re
import uuid
from datetime import datetime
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config.settings import VENUE_TYPES, VENUE_TYPE_KEYWORDS

# ── Price regex patterns (from PRD §15.1) ────────────────────────────────────

_RE_LAKHS = re.compile(
    r"[^0-9\s,.]*\s*([\d,]+(?:\.\d+)?)\s*(?:L|Lakh|Lakhs?|Lac|Lacs?)",
    re.IGNORECASE
)
_RE_CRORE = re.compile(
    r"[^0-9\s,.]*\s*([\d,]+(?:\.\d+)?)\s*(?:Cr|Crore?s?)",
    re.IGNORECASE
)
_RE_PER_PLATE = re.compile(
    r"[^0-9\s,.]*\s*([\d,]+(?:\.\d+)?)\s*(?:/\s*plate|per\s*plate|pp)",
    re.IGNORECASE
)
_RE_RANGE = re.compile(
    r"[^0-9\s,.]*\s*([\d,]+(?:\.\d+)?)\s*[-–—to]+\s*[^0-9\s,.]*\s*([\d,]+(?:\.\d+)?)",
    re.IGNORECASE
)
_RE_PLAIN = re.compile(r"[^0-9\s,.]*\s*([\d,]+(?:\.\d+)?)")
_RE_K = re.compile(
    r"[^0-9\s,.]*\s*([\d,]+(?:\.\d+)?)\s*[Kk](?:\b|$)"
)

# ── Capacity regex ────────────────────────────────────────────────────────────

_RE_CAP_RANGE = re.compile(r"(\d+)\s*[-–—to]+\s*(\d+)")
_RE_CAP_SINGLE = re.compile(r"(\d+)\s*(?:guests?|pax|people|persons?)?", re.IGNORECASE)

# ── Rating regex ──────────────────────────────────────────────────────────────

_RE_RATING = re.compile(r"(\d+\.?\d*)\s*(?:/\s*5)?")

# ── Review count regex ────────────────────────────────────────────────────────

_RE_REVIEWS = re.compile(r"(\d+)\s*(?:reviews?|ratings?)?", re.IGNORECASE)


def _clean_num(s: str) -> float:
    """Strip commas and convert to float."""
    return float(s.replace(",", ""))


# ── Public functions ──────────────────────────────────────────────────────────

def normalize_price(raw: Optional[str]) -> dict:
    """
    Parse a raw price string into typed INR numeric fields.
    Returns a dict with keys: min_price, max_price, price_per_plate.
    All values are float or None.
    """
    if not raw or not isinstance(raw, str):
        return {"min_price": None, "max_price": None, "price_per_plate": None}

    text = raw.strip()
    result = {"min_price": None, "max_price": None, "price_per_plate": None}

    # 1. Per-plate price
    m = _RE_PER_PLATE.search(text)
    if m:
        result["price_per_plate"] = _clean_num(m.group(1))

    # 2. Lakhs range (e.g. "₹2L – ₹10L")
    lakhs_matches = list(_RE_LAKHS.finditer(text))
    if len(lakhs_matches) >= 2:
        vals = sorted([_clean_num(m.group(1)) * 100_000 for m in lakhs_matches])
        result["min_price"], result["max_price"] = vals[0], vals[-1]
        return result
    if len(lakhs_matches) == 1:
        val = _clean_num(lakhs_matches[0].group(1)) * 100_000
        result["min_price"] = val
        return result

    # 3. Crore
    m = _RE_CRORE.search(text)
    if m:
        val = _clean_num(m.group(1)) * 10_000_000
        result["min_price"] = val
        return result

    # 4. Thousands (K notation)
    k_matches = list(_RE_K.finditer(text))
    if len(k_matches) >= 2:
        vals = sorted([_clean_num(m.group(1)) * 1000 for m in k_matches])
        result["min_price"], result["max_price"] = vals[0], vals[-1]
        return result
    if len(k_matches) == 1:
        result["min_price"] = _clean_num(k_matches[0].group(1)) * 1000
        return result

    # 5. Plain numeric range (e.g. "₹2,500 – ₹7,500")
    m = _RE_RANGE.search(text)
    if m:
        lo, hi = _clean_num(m.group(1)), _clean_num(m.group(2))
        result["min_price"], result["max_price"] = min(lo, hi), max(lo, hi)
        return result

    # 6. Single plain value
    m = _RE_PLAIN.search(text)
    if m:
        val = _clean_num(m.group(1))
        if val > 0:
            result["min_price"] = val
        return result

    return result


def normalize_capacity(raw: Optional[str]) -> dict:
    """Parse raw capacity text → {capacity_min, capacity_max}."""
    if not raw or not isinstance(raw, str):
        return {"capacity_min": None, "capacity_max": None}

    m = _RE_CAP_RANGE.search(raw)
    if m:
        c1, c2 = int(m.group(1)), int(m.group(2))
        return {"capacity_min": min(c1, c2), "capacity_max": max(c1, c2)}

    m = _RE_CAP_SINGLE.search(raw)
    if m:
        val = int(m.group(1))
        if 10 < val < 10_000:
            return {"capacity_min": val, "capacity_max": val}

    return {"capacity_min": None, "capacity_max": None}


def normalize_rating(raw) -> Optional[float]:
    """Parse rating to float 0.0–5.0."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw) if 0.0 <= float(raw) <= 5.0 else None
    m = _RE_RATING.search(str(raw))
    if m:
        try:
            v = float(m.group(1))
            return v if 0.0 <= v <= 5.0 else None
        except ValueError:
            pass
    return None


def normalize_review_count(raw) -> Optional[int]:
    """Parse review count text → int."""
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw
    m = _RE_REVIEWS.search(str(raw))
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return None


def classify_venue_type(raw: Optional[str], name: Optional[str] = None) -> Optional[str]:
    """
    Infer venue type from raw type label or venue name keywords.
    Returns one of the canonical venue type strings or None.

    Strategy: check the raw type label alone first (word-level), so an explicit
    label like "beach resort" is classified as "beach" (the first word), not
    "resort". Fall back to combined name+raw keyword search.
    """
    if not raw and not name:
        return None

    # Pass 1: check raw label's first meaningful word against type keywords
    if raw and isinstance(raw, str):
        raw_lower = raw.lower().strip()
        raw_words = raw_lower.split()
        for vtype, keywords in VENUE_TYPE_KEYWORDS.items():
            if any(raw_words[0] == kw or raw_words[0].startswith(kw) for kw in keywords):
                return vtype

    # Pass 2: scan combined text in declaration order
    # Simple fix:
    texts = []
    for x in [raw, name]:
        if x and isinstance(x, str):
            texts.append(x)
        elif isinstance(x, (int, float)) and x == x: # Simple NaN check
            texts.append(str(x))
    
    combined_text = " ".join(texts).lower()
    for vtype, keywords in VENUE_TYPE_KEYWORDS.items():
        if any(kw in combined_text for kw in keywords):
            return vtype
    return None


def extract_area(address_raw: Optional[str], city: str, area_lookup: dict,
                 area_hint: Optional[str] = None) -> Optional[str]:
    """
    Match address text against the pre-built area lookup for the given city.
    area_hint is a pre-parsed locality string from the scraper (e.g. WedMeGood's
    primary_locality field) — tried first before full address scan.
    area_lookup: {area_name_lower: area_display_name}
    """
    # Try the structured hint first
    if area_hint and isinstance(area_hint, str):
        hint_lower = area_hint.lower().strip()
        for area_lower, area_display in area_lookup.items():
            if area_lower in hint_lower or hint_lower in area_lower:
                return area_display

    if not address_raw or not isinstance(address_raw, str):
        return None
    addr_lower = address_raw.lower()
    for area_lower, area_display in area_lookup.items():
        if area_lower in addr_lower:
            return area_display
    return None


def normalize_record(raw: dict, area_lookup: dict = None) -> dict:
    """
    Apply all normalization to a raw scraped record.
    Returns a clean record conforming to the PRD schema.
    """
    area_lookup = area_lookup or {}

    # Prices
    price_raw = raw.get("price_raw") or raw.get("price_per_plate_raw")
    price_fields = normalize_price(price_raw)

    # Per-plate override if explicitly scraped
    ppp_raw = raw.get("price_per_plate_raw")
    if ppp_raw and not price_fields["price_per_plate"]:
        ppp_parsed = normalize_price(ppp_raw)
        if ppp_parsed["price_per_plate"]:
            price_fields["price_per_plate"] = ppp_parsed["price_per_plate"]
        elif ppp_parsed["min_price"]:
            price_fields["price_per_plate"] = ppp_parsed["min_price"]

    # Capacity
    cap_fields = normalize_capacity(raw.get("capacity_raw"))

    # Venue type
    vtype = classify_venue_type(
        raw.get("venue_type_raw"),
        raw.get("venue_name")
    )

    # Area
    area = extract_area(raw.get("address_raw"), raw.get("city", ""), area_lookup,
                        area_hint=raw.get("area_hint"))

    # Rating / reviews
    rating = normalize_rating(raw.get("rating"))
    review_count = normalize_review_count(raw.get("review_count_raw") or raw.get("review_count"))

    return {
        "venue_id":       raw.get("venue_id") or str(uuid.uuid4()),
        "venue_name":     raw.get("venue_name", "").strip(),
        "state":          raw.get("state", "").strip(),
        "city":           raw.get("city", "").strip(),
        "area":           area,
        "venue_type":     vtype,
        "min_price":      price_fields["min_price"],
        "max_price":      price_fields["max_price"],
        "price_per_plate":price_fields["price_per_plate"],
        "capacity_min":   cap_fields["capacity_min"],
        "capacity_max":   cap_fields["capacity_max"],
        "rating":         rating,
        "review_count":   review_count,
        "source":         raw.get("source", ""),
        "source_url":     raw.get("source_url", ""),
        "scraped_at":     raw.get("scraped_at", datetime.utcnow().isoformat()),
    }
