"""
Unit tests for src/cleaning/validator.py
Covers all PRD §8 validation rules.
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cleaning.validator import validate_records, apply_median_imputation


def _make_venue(**kwargs) -> dict:
    defaults = {
        "venue_id": "test-uuid",
        "venue_name": "Test Palace Hotel",
        "state": "Rajasthan",
        "city": "Udaipur",
        "area": None,
        "venue_type": "palace",
        "min_price": 500_000.0,
        "max_price": 1_500_000.0,
        "price_per_plate": None,
        "capacity_min": 100,
        "capacity_max": 500,
        "rating": 4.2,
        "review_count": 120,
        "source": "wedmegood",
        "source_url": "https://wedmegood.com/venue/123",
        "scraped_at": "2026-04-01T10:00:00",
    }
    defaults.update(kwargs)
    return defaults


# ── venue_name rules ──────────────────────────────────────────────────────────

class TestVenueName:
    def test_valid_name_passes(self):
        valid, flagged, report = validate_records([_make_venue()])
        assert len(valid) == 1

    def test_empty_name_drops(self):
        valid, flagged, report = validate_records([_make_venue(venue_name="")])
        assert len(valid) == 0
        assert report.dropped == 1

    def test_html_in_name_drops(self):
        valid, flagged, report = validate_records([_make_venue(venue_name="<b>Test</b>")])
        assert len(valid) == 0

    def test_too_short_drops(self):
        valid, flagged, report = validate_records([_make_venue(venue_name="AB")])
        assert report.dropped == 1

    def test_too_long_drops(self):
        valid, flagged, report = validate_records([_make_venue(venue_name="A" * 201)])
        assert report.dropped == 1


# ── source_url rules ──────────────────────────────────────────────────────────

class TestSourceUrl:
    def test_valid_url_passes(self):
        valid, _, _ = validate_records([_make_venue()])
        assert len(valid) == 1

    def test_missing_url_drops(self):
        _, _, report = validate_records([_make_venue(source_url="")])
        assert report.dropped == 1

    def test_invalid_url_drops(self):
        _, _, report = validate_records([_make_venue(source_url="not-a-url")])
        assert report.dropped == 1


# ── state rules ───────────────────────────────────────────────────────────────

class TestStateValidation:
    def test_approved_state_passes(self):
        valid, flagged, _ = validate_records([_make_venue(state="Rajasthan")])
        assert len(valid) == 1
        assert len(flagged) == 0

    def test_unknown_state_flags(self):
        valid, flagged, _ = validate_records([_make_venue(state="UnknownState")])
        assert len(flagged) == 1
        assert "_flags" in flagged[0]

    def test_empty_state_flags(self):
        _, flagged, _ = validate_records([_make_venue(state="")])
        assert len(flagged) == 1


# ── Price validation ──────────────────────────────────────────────────────────

class TestPriceValidation:
    def test_valid_prices_pass_through(self):
        valid, _, _ = validate_records([_make_venue(min_price=200_000, max_price=500_000)])
        assert valid[0]["min_price"] == 200_000

    def test_negative_price_set_to_null(self):
        valid, _, _ = validate_records([_make_venue(min_price=-100)])
        assert valid[0]["min_price"] is None

    def test_max_less_than_min_clears_max(self):
        valid, _, _ = validate_records([_make_venue(min_price=500_000, max_price=100_000)])
        assert valid[0]["max_price"] is None

    def test_price_per_plate_over_cap_nulled(self):
        valid, _, _ = validate_records([_make_venue(price_per_plate=100_000)])
        assert valid[0]["price_per_plate"] is None

    def test_valid_per_plate(self):
        valid, _, _ = validate_records([_make_venue(price_per_plate=2500)])
        assert valid[0]["price_per_plate"] == 2500


# ── Capacity validation ───────────────────────────────────────────────────────

class TestCapacityValidation:
    def test_valid_capacity_passes(self):
        valid, _, _ = validate_records([_make_venue(capacity_min=100, capacity_max=500)])
        assert valid[0]["capacity_max"] == 500

    def test_capacity_over_limit_nulled(self):
        valid, _, _ = validate_records([_make_venue(capacity_max=20_000)])
        assert valid[0]["capacity_max"] is None

    def test_capacity_max_less_than_min_clears_max(self):
        valid, _, _ = validate_records([_make_venue(capacity_min=500, capacity_max=100)])
        assert valid[0]["capacity_max"] is None


# ── Rating validation ─────────────────────────────────────────────────────────

class TestRatingValidation:
    def test_valid_rating(self):
        valid, _, _ = validate_records([_make_venue(rating=4.5)])
        assert valid[0]["rating"] == 4.5

    def test_rating_over_5_nulled(self):
        valid, _, _ = validate_records([_make_venue(rating=6.0)])
        assert valid[0]["rating"] is None

    def test_negative_rating_nulled(self):
        valid, _, _ = validate_records([_make_venue(rating=-1.0)])
        assert valid[0]["rating"] is None


# ── Quality report ────────────────────────────────────────────────────────────

class TestQualityReport:
    def test_report_totals(self):
        records = [_make_venue(), _make_venue(venue_name=""), _make_venue(state="Badstate")]
        valid, flagged, report = validate_records(records)
        assert report.total_raw == 3
        assert report.dropped == 1
        assert report.flagged == 1
        assert report.valid == 1

    def test_fill_rates_computed(self):
        _, _, report = validate_records([_make_venue()])
        assert "rating" in report.field_fill
        assert 0.0 <= report.field_fill["rating"] <= 1.0


# ── Median imputation ─────────────────────────────────────────────────────────

class TestMedianImputation:
    def test_imputes_missing_price(self):
        records = [
            _make_venue(min_price=500_000, city="Udaipur"),
            _make_venue(min_price=300_000, city="Udaipur"),
            _make_venue(min_price=None, city="Udaipur"),
        ]
        result = apply_median_imputation(records)
        imputed = [r for r in result if r.get("_imputed_min_price")]
        assert len(imputed) == 1
        assert imputed[0]["min_price"] == 400_000  # median of [300k, 500k]

    def test_no_imputation_for_different_city(self):
        records = [
            _make_venue(min_price=500_000, city="Udaipur"),
            _make_venue(min_price=None, city="Jaipur"),
        ]
        result = apply_median_imputation(records)
        jaipur = [r for r in result if r["city"] == "Jaipur"][0]
        assert jaipur["min_price"] is None  # no data for Jaipur
