"""
Cross-source deduplication using fuzzy string matching.
PRD §8: fuzzy match score > 85% on name+city triggers a duplicate flag.
Keeps highest-rated record; merges complementary fields.
"""
import logging

try:
    from fuzzywuzzy import fuzz
except ImportError:
    try:
        from rapidfuzz import fuzz  # faster drop-in replacement
    except ImportError:
        raise ImportError(
            "fuzzywuzzy or rapidfuzz is required for deduplication. "
            "Install with: pip install fuzzywuzzy python-Levenshtein"
        )

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import DEDUP_THRESHOLD

logger = logging.getLogger(__name__)


def _dedup_key(record: dict) -> str:
    """Build a normalised comparison string from venue_name + city."""
    name = (record.get("venue_name") or "").lower().strip()
    city = (record.get("city") or "").lower().strip()
    return f"{name} {city}"


def _score(a: dict, b: dict) -> int:
    """
    Return fuzzy match score (0–100) between two records.
    City must match exactly; only then compare venue names.
    This prevents cross-city false positives (e.g. "Taj Hotel" Udaipur
    vs "Taj Hotel" Jaipur are distinct venues).
    """
    city_a = (a.get("city") or "").lower().strip()
    city_b = (b.get("city") or "").lower().strip()
    if city_a != city_b:
        return 0  # different cities → never a duplicate
    name_a = (a.get("venue_name") or "").lower().strip()
    name_b = (b.get("venue_name") or "").lower().strip()
    return fuzz.token_set_ratio(name_a, name_b)


def _merge(primary: dict, secondary: dict) -> dict:
    """
    Merge two records: primary wins on non-null fields;
    secondary fills in any null fields in primary.
    """
    merged = dict(primary)
    for key, val in secondary.items():
        if merged.get(key) is None and val is not None:
            merged[key] = val
    return merged


def _best(a: dict, b: dict) -> tuple[dict, dict]:
    """Return (primary, secondary) preferring higher-rated or more complete record."""
    rating_a = a.get("rating") or 0.0
    rating_b = b.get("rating") or 0.0
    if rating_a >= rating_b:
        return a, b
    return b, a


def deduplicate(records: list[dict]) -> tuple[list[dict], int]:
    """
    Deduplicate a list of venue records.

    Algorithm:
    1. For each record, compare against all already-accepted records.
    2. If fuzzy score > DEDUP_THRESHOLD, treat as duplicate.
    3. Merge fields from duplicate into primary; keep primary.

    Returns:
        deduped   — list of unique records with merged fields
        dup_count — number of duplicates removed
    """
    accepted: list[dict] = []
    dup_count = 0

    for record in records:
        matched = False
        for i, existing in enumerate(accepted):
            score = _score(record, existing)
            if score >= DEDUP_THRESHOLD:
                primary, secondary = _best(existing, record)
                accepted[i] = _merge(primary, secondary)
                dup_count += 1
                matched = True
                logger.debug(
                    "Dedup: '%s' ↔ '%s' (score=%d) — merged",
                    record.get("venue_name"), existing.get("venue_name"), score
                )
                break
        if not matched:
            accepted.append(record)

    dup_rate = dup_count / len(records) if records else 0
    logger.info("Deduplication: %d → %d records (removed %d, %.1f%%)",
                len(records), len(accepted), dup_count, dup_rate * 100)
    return accepted, dup_count


def deduplicate_within_source(records: list[dict]) -> list[dict]:
    """
    Dedup for records from a single source.

    Within a single source, two records are duplicates only when:
    - They share the same source_url (same page scraped twice), OR
    - They have exactly the same name+city key (no fuzzy — scrapers can
      produce slightly different name variants for genuinely different venues).
    """
    result: list[dict] = []
    seen_keys: set = set()
    seen_urls: set = set()

    for rec in records:
        key = _dedup_key(rec)
        url = (rec.get("source_url") or "").strip()

        # Exact URL match → definite duplicate
        if url and url in seen_urls:
            continue
        # Exact name+city match → duplicate
        if key in seen_keys:
            continue

        seen_keys.add(key)
        if url:
            seen_urls.add(url)
        result.append(rec)

    return result


def report_duplicate_rate(original_count: int, deduped_count: int) -> float:
    """Return the cross-source duplicate percentage."""
    if original_count == 0:
        return 0.0
    return (original_count - deduped_count) / original_count
