"""
Unit tests for src/cleaning/deduplicator.py
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cleaning.deduplicator import deduplicate, deduplicate_within_source, report_duplicate_rate


def _venue(name: str, city: str, rating: float = 4.0, source: str = "wedmegood", **kwargs) -> dict:
    return {
        "venue_id": f"id-{name[:6]}",
        "venue_name": name,
        "city": city,
        "state": "Rajasthan",
        "rating": rating,
        "source": source,
        "source_url": f"https://example.com/{name.replace(' ', '-').lower()}",
        **kwargs
    }


# ── Core deduplication ────────────────────────────────────────────────────────

class TestDeduplicate:
    def test_no_duplicates_unchanged(self):
        records = [
            _venue("The Grand Palace", "Udaipur"),
            _venue("Lake View Resort", "Jaipur"),
            _venue("Desert Camp Jaisalmer", "Jaisalmer"),
        ]
        result, dup_count = deduplicate(records)
        assert len(result) == 3
        assert dup_count == 0

    def test_exact_duplicates_removed(self):
        records = [
            _venue("The Grand Palace", "Udaipur", rating=4.5),
            _venue("The Grand Palace", "Udaipur", rating=4.2),
        ]
        result, dup_count = deduplicate(records)
        assert len(result) == 1
        assert dup_count == 1

    def test_highest_rated_kept_as_primary(self):
        records = [
            _venue("Taj Lake Palace", "Udaipur", rating=3.0, min_price=None),
            _venue("Taj Lake Palace Hotel", "Udaipur", rating=4.8, min_price=2_000_000),
        ]
        result, _ = deduplicate(records)
        assert result[0]["rating"] == 4.8

    def test_fields_merged_from_secondary(self):
        # Primary has no area; secondary does — secondary field should be merged
        records = [
            _venue("Heritage Palace Hotel", "Udaipur", rating=4.5, area=None),
            _venue("Heritage Palace", "Udaipur", rating=3.8, area="Lake Pichola"),
        ]
        result, _ = deduplicate(records)
        assert result[0]["area"] == "Lake Pichola"

    def test_similar_but_different_city_not_deduped(self):
        records = [
            _venue("Taj Hotel", "Udaipur"),
            _venue("Taj Hotel", "Jaipur"),
        ]
        result, dup_count = deduplicate(records)
        assert len(result) == 2
        assert dup_count == 0

    def test_fuzzy_near_match_deduped(self):
        records = [
            _venue("The Oberoi Udaivilas", "Udaipur"),
            _venue("Oberoi Udaivilas Hotel", "Udaipur"),
        ]
        result, dup_count = deduplicate(records)
        assert len(result) == 1
        assert dup_count == 1

    def test_completely_different_venues_not_deduped(self):
        records = [
            _venue("Rambagh Palace", "Jaipur"),
            _venue("Umaid Bhawan Palace", "Jodhpur"),
        ]
        result, dup_count = deduplicate(records)
        assert len(result) == 2

    def test_empty_input(self):
        result, dup_count = deduplicate([])
        assert result == []
        assert dup_count == 0

    def test_single_record(self):
        result, dup_count = deduplicate([_venue("Test Palace", "Udaipur")])
        assert len(result) == 1
        assert dup_count == 0


# ── Within-source deduplication ───────────────────────────────────────────────

class TestDeduplicateWithinSource:
    def test_removes_exact_duplicates(self):
        records = [
            _venue("Lake View Resort", "Udaipur"),
            _venue("Lake View Resort", "Udaipur"),
            _venue("Lake View Resort", "Udaipur"),
        ]
        result = deduplicate_within_source(records)
        assert len(result) == 1

    def test_different_venues_kept(self):
        records = [
            _venue("Palace A", "Udaipur"),
            _venue("Palace B", "Udaipur"),
            _venue("Palace C", "Jaipur"),
        ]
        result = deduplicate_within_source(records)
        assert len(result) == 3


# ── Duplicate rate reporting ──────────────────────────────────────────────────

class TestReportDuplicateRate:
    def test_rate_calculation(self):
        rate = report_duplicate_rate(original_count=100, deduped_count=92)
        assert abs(rate - 0.08) < 1e-9

    def test_no_duplicates(self):
        assert report_duplicate_rate(100, 100) == 0.0

    def test_zero_original(self):
        assert report_duplicate_rate(0, 0) == 0.0

    def test_target_below_5_percent(self):
        # PRD success criterion: deduplication < 5% overlap
        rate = report_duplicate_rate(1000, 955)
        assert rate < 0.05
