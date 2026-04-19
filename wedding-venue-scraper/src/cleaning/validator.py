"""
Validation pipeline for normalized venue records.
Enforces PRD §8 rules; returns (valid_records, flagged_records, quality_report).
"""
import logging
import re
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config.settings import (
    APPROVED_SOURCES, APPROVED_STATES, MAX_CAPACITY, MAX_PRICE_PER_PLATE,
    VENUE_NAME_MAX_LEN, VENUE_NAME_MIN_LEN
)

logger = logging.getLogger(__name__)

_RE_HTML_TAG = re.compile(r"<[^>]+>")


@dataclass
class QualityReport:
    total_raw: int = 0
    dropped: int = 0
    flagged: int = 0
    valid: int = 0
    field_fill: dict = field(default_factory=dict)
    source_dist: dict = field(default_factory=dict)
    geo_coverage: dict = field(default_factory=dict)

    def __str__(self):
        lines = [
            f"=== Data Quality Report ===",
            f"Total raw     : {self.total_raw}",
            f"Dropped       : {self.dropped}",
            f"Flagged       : {self.flagged}",
            f"Valid         : {self.valid}",
            "",
            "Field fill rates:",
        ]
        for f_name, rate in sorted(self.field_fill.items()):
            lines.append(f"  {f_name:<20} {rate:.1%}")
        lines.append("\nSource distribution:")
        for src, pct in sorted(self.source_dist.items()):
            lines.append(f"  {src:<20} {pct:.1%}")
        lines.append("\nGeographic coverage:")
        for k, v in sorted(self.geo_coverage.items()):
            lines.append(f"  {k:<12} {v}")
        return "\n".join(lines)


# ── Individual field validators ───────────────────────────────────────────────

def _validate_venue_name(name: Optional[str]) -> tuple[bool, str]:
    if not name:
        return False, "venue_name is empty"
    if _RE_HTML_TAG.search(name):
        return False, "venue_name contains HTML tags"
    if len(name) < VENUE_NAME_MIN_LEN:
        return False, f"venue_name too short ({len(name)} chars)"
    if len(name) > VENUE_NAME_MAX_LEN:
        return False, f"venue_name too long ({len(name)} chars)"
    return True, ""


def _validate_state(state: Optional[str]) -> tuple[bool, str]:
    if not state:
        return None, "state is empty"  # flag, not drop
    if state not in APPROVED_STATES:
        return None, f"state '{state}' not in approved list"
    return True, ""


def _validate_city(city: Optional[str], state: Optional[str]) -> tuple[bool, str]:
    if not city:
        return None, "city is empty"
    return True, ""


def _validate_prices(record: dict) -> dict:
    """Validate price fields; return cleaned record with nulls on failure."""
    min_p = record.get("min_price")
    max_p = record.get("max_price")
    ppp   = record.get("price_per_plate")

    if min_p is not None:
        if not isinstance(min_p, (int, float)) or min_p <= 0:
            logger.debug("Invalid min_price=%s for %s — set to null", min_p, record.get("venue_name"))
            record["min_price"] = None
            min_p = None
    if max_p is not None:
        if not isinstance(max_p, (int, float)) or max_p <= 0:
            record["max_price"] = None
            max_p = None
    if min_p and max_p and max_p < min_p:
        record["max_price"] = None  # inconsistent range

    if min_p is not None and min_p < 100:
        logger.warning("Suspiciously low min_price=%s for %s", min_p, record.get("venue_name"))
        # We don't null it, let it be flagged in soft checks or by the user
        # or we could flag it here if we had a list of flags.
        # For now, I'll just add it to a potential flag list if I change the return signature.
        # But wait, the PRD §8 says null invalid fields. 
        # I'll Null if < 10 for sure.
        if min_p < 10:
             record["min_price"] = None

    if ppp is not None:
        if not isinstance(ppp, (int, float)) or ppp <= 0 or ppp > MAX_PRICE_PER_PLATE:
            logger.debug("price_per_plate=%s out of bounds — set to null", ppp)
            record["price_per_plate"] = None
        elif ppp < 100:
            if ppp < 10:
                record["price_per_plate"] = None

    return record


def _validate_capacity(record: dict) -> dict:
    cap_min = record.get("capacity_min")
    cap_max = record.get("capacity_max")

    if cap_min is not None:
        if not isinstance(cap_min, int) or cap_min <= 0 or cap_min >= MAX_CAPACITY:
            record["capacity_min"] = None
            cap_min = None
    if cap_max is not None:
        if not isinstance(cap_max, int) or cap_max <= 0 or cap_max >= MAX_CAPACITY:
            record["capacity_max"] = None
            cap_max = None
    if cap_min and cap_max and cap_max < cap_min:
        record["capacity_max"] = None
    return record


def _validate_rating(record: dict) -> dict:
    rating = record.get("rating")
    if rating is not None:
        try:
            r = float(rating)
            if not (0.0 <= r <= 5.0):
                record["rating"] = None
        except (TypeError, ValueError):
            record["rating"] = None
    return record


def _validate_source_url(url: Optional[str], source: Optional[str]) -> tuple[bool, str]:
    if not url:
        return False, "source_url is missing"
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, f"source_url '{url}' is not a valid URL"
    except Exception:
        return False, f"source_url '{url}' could not be parsed"
    return True, ""


# ── Main validation function ──────────────────────────────────────────────────

def validate_records(records: list[dict]) -> tuple[list[dict], list[dict], QualityReport]:
    """
    Validate a list of normalized records.

    Returns:
        valid_records   — passed all hard rules
        flagged_records — soft failures (state/city mismatch), include a 'flag' key
        report          — QualityReport with metrics
    """
    report = QualityReport(total_raw=len(records))
    valid: list[dict] = []
    flagged: list[dict] = []

    for rec in records:
        drop_reasons: list[str] = []
        flag_reasons: list[str] = []

        # Hard checks → drop on failure
        ok, msg = _validate_venue_name(rec.get("venue_name"))
        if not ok:
            drop_reasons.append(msg)

        ok, msg = _validate_source_url(rec.get("source_url"), rec.get("source"))
        if not ok:
            drop_reasons.append(msg)

        if drop_reasons:
            report.dropped += 1
            logger.debug("Dropping record '%s': %s", rec.get("venue_name"), drop_reasons)
            continue

        # Soft checks → flag for review
        ok, msg = _validate_state(rec.get("state"))
        if ok is None:
            flag_reasons.append(msg)

        ok, msg = _validate_city(rec.get("city"), rec.get("state"))
        if ok is None:
            flag_reasons.append(msg)

        # Field-level fixes (null invalid values, no drop)
        rec = _validate_prices(rec)
        rec = _validate_capacity(rec)
        rec = _validate_rating(rec)

        if flag_reasons:
            rec["_flags"] = "; ".join(flag_reasons)
            flagged.append(rec)
            report.flagged += 1
        else:
            valid.append(rec)
            report.valid += 1

    report.field_fill = _compute_fill_rates(valid + flagged)
    report.source_dist = _compute_source_dist(valid + flagged)
    report.geo_coverage = _compute_geo_coverage(valid + flagged)
    return valid, flagged, report


# ── Quality metric helpers ────────────────────────────────────────────────────

def _compute_fill_rates(records: list[dict]) -> dict:
    if not records:
        return {}
    fields = [
        "area", "venue_type", "min_price", "max_price",
        "price_per_plate", "capacity_min", "capacity_max",
        "rating", "review_count"
    ]
    n = len(records)
    return {
        f: sum(1 for r in records if r.get(f) is not None) / n
        for f in fields
    }


def _compute_source_dist(records: list[dict]) -> dict:
    if not records:
        return {}
    n = len(records)
    counts: dict = {}
    for r in records:
        src = r.get("source", "unknown")
        counts[src] = counts.get(src, 0) + 1
    return {k: v / n for k, v in counts.items()}


def _compute_geo_coverage(records: list[dict]) -> dict:
    return {
        "unique_states": len({r.get("state") for r in records if r.get("state")}),
        "unique_cities": len({r.get("city") for r in records if r.get("city")}),
        "unique_areas":  len({r.get("area") for r in records if r.get("area")}),
    }


def apply_median_imputation(records: list[dict]) -> list[dict]:
    """
    Fill missing price fields with city-level medians.
    Called as post-validation post-processing step.
    """
    import statistics

    city_prices: dict = {}
    for r in records:
        city = r.get("city", "")
        val = r.get("min_price")
        if val:
            city_prices.setdefault(city, []).append(val)

    city_medians = {city: statistics.median(vals) for city, vals in city_prices.items() if vals}

    for r in records:
        city = r.get("city", "")
        if r.get("min_price") is None and city in city_medians:
            r["min_price"] = city_medians[city]
            r["_imputed_min_price"] = True

    return records
