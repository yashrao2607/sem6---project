"""
Unit tests for src/cleaning/normalizer.py
Covers all price format variants listed in PRD §15.1, capacity parsing,
rating normalization, and venue type classification.
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cleaning.normalizer import (
    normalize_price,
    normalize_capacity,
    normalize_rating,
    normalize_review_count,
    classify_venue_type,
    extract_area,
    normalize_record,
)


# ── Price normalization ───────────────────────────────────────────────────────

class TestNormalizePrice:
    def test_none_returns_all_null(self):
        r = normalize_price(None)
        assert r == {"min_price": None, "max_price": None, "price_per_plate": None}

    def test_empty_string(self):
        r = normalize_price("")
        assert r["min_price"] is None

    def test_lakhs_single(self):
        r = normalize_price("₹5 Lakhs")
        assert r["min_price"] == 500_000

    def test_lakhs_range(self):
        r = normalize_price("₹2L – ₹10L")
        assert r["min_price"] == 200_000
        assert r["max_price"] == 1_000_000

    def test_crore(self):
        r = normalize_price("₹1.5 Crore")
        assert r["min_price"] == 15_000_000

    def test_per_plate(self):
        r = normalize_price("₹2,500 per plate")
        assert r["price_per_plate"] == 2500.0

    def test_per_plate_slash(self):
        r = normalize_price("₹1500/plate")
        assert r["price_per_plate"] == 1500.0

    def test_plain_range(self):
        r = normalize_price("₹25,000 – ₹75,000")
        assert r["min_price"] == 25_000
        assert r["max_price"] == 75_000

    def test_starting_from_lakhs(self):
        r = normalize_price("Starting from ₹3.5 Lakhs")
        assert r["min_price"] == 350_000

    def test_k_notation(self):
        r = normalize_price("₹50K – ₹200K")
        assert r["min_price"] == 50_000
        assert r["max_price"] == 200_000

    def test_with_commas(self):
        r = normalize_price("₹1,00,000")
        assert r["min_price"] == 100_000.0

    def test_lacs_spelling(self):
        r = normalize_price("₹8 Lacs")
        assert r["min_price"] == 800_000

    def test_l_suffix(self):
        r = normalize_price("₹3L")
        assert r["min_price"] == 300_000

    def test_range_reversed_order_normalised(self):
        # max < min in raw string → should still be correct
        r = normalize_price("₹10L – ₹2L")
        assert r["min_price"] == 200_000
        assert r["max_price"] == 1_000_000

    def test_rupee_symbol_variants(self):
        r = normalize_price("Rs. 5,00,000")
        assert r["min_price"] == 500_000.0


# ── Capacity normalization ────────────────────────────────────────────────────

class TestNormalizeCapacity:
    def test_none(self):
        assert normalize_capacity(None) == {"capacity_min": None, "capacity_max": None}

    def test_range(self):
        r = normalize_capacity("100 – 500 guests")
        assert r["capacity_min"] == 100
        assert r["capacity_max"] == 500

    def test_single_value(self):
        r = normalize_capacity("200 guests")
        assert r["capacity_min"] == 200
        assert r["capacity_max"] == 200

    def test_to_range(self):
        r = normalize_capacity("50 to 300 people")
        assert r["capacity_min"] == 50
        assert r["capacity_max"] == 300

    def test_plain_number(self):
        r = normalize_capacity("500")
        assert r["capacity_max"] == 500

    def test_too_large_rejected(self):
        r = normalize_capacity("50000 guests")
        assert r["capacity_min"] is None

    def test_too_small_rejected(self):
        r = normalize_capacity("5")
        assert r["capacity_min"] is None


# ── Rating normalization ──────────────────────────────────────────────────────

class TestNormalizeRating:
    def test_none(self):
        assert normalize_rating(None) is None

    def test_float_in_range(self):
        assert normalize_rating(4.5) == 4.5

    def test_float_out_of_range(self):
        assert normalize_rating(6.0) is None

    def test_string_rating(self):
        assert normalize_rating("4.2/5") == 4.2

    def test_string_out_of_range(self):
        assert normalize_rating("5.5") is None

    def test_zero(self):
        assert normalize_rating(0.0) == 0.0


# ── Review count ──────────────────────────────────────────────────────────────

class TestNormalizeReviewCount:
    def test_none(self):
        assert normalize_review_count(None) is None

    def test_integer(self):
        assert normalize_review_count(42) == 42

    def test_string(self):
        assert normalize_review_count("123 reviews") == 123

    def test_string_bare(self):
        assert normalize_review_count("57") == 57


# ── Venue type classification ─────────────────────────────────────────────────

class TestClassifyVenueType:
    def test_palace_from_name(self):
        assert classify_venue_type(None, "City Palace Hotel") == "palace"

    def test_beach_from_raw(self):
        assert classify_venue_type("beach resort", None) == "beach"

    def test_farmhouse(self):
        assert classify_venue_type(None, "The Green Farmhouse") == "farmhouse"

    def test_hotel_chain(self):
        assert classify_venue_type(None, "Taj Lake Palace Hotel") == "palace"

    def test_banquet_hall(self):
        assert classify_venue_type("banquet hall", None) == "banquet_hall"

    def test_unknown_returns_none(self):
        assert classify_venue_type("xyz", "qrs venue") is None

    def test_none_returns_none(self):
        assert classify_venue_type(None, None) is None


# ── Area extraction ───────────────────────────────────────────────────────────

class TestExtractArea:
    def test_match_found(self):
        lookup = {"lake pichola": "Lake Pichola", "amer": "Amer"}
        area = extract_area("Near Lake Pichola, Udaipur, Rajasthan", "udaipur", lookup)
        assert area == "Lake Pichola"

    def test_no_match(self):
        lookup = {"lake pichola": "Lake Pichola"}
        area = extract_area("Some Random Colony, Udaipur", "udaipur", lookup)
        assert area is None

    def test_none_address(self):
        assert extract_area(None, "udaipur", {"lake pichola": "Lake Pichola"}) is None


# ── Full record normalization ─────────────────────────────────────────────────

class TestNormalizeRecord:
    def test_full_record(self):
        raw = {
            "venue_id": "abc",
            "venue_name": "The Grand Palace Resort",
            "state": "Rajasthan",
            "city": "Udaipur",
            "address_raw": "Near Lake Pichola, Udaipur",
            "price_raw": "₹5L – ₹15L",
            "capacity_raw": "100 – 800 guests",
            "rating": "4.3/5",
            "review_count_raw": "256 reviews",
            "source": "wedmegood",
            "source_url": "https://wedmegood.com/venue/123",
            "scraped_at": "2026-04-01T10:00:00",
        }
        area_lookup = {"lake pichola": "Lake Pichola"}
        result = normalize_record(raw, area_lookup)

        assert result["venue_name"] == "The Grand Palace Resort"
        assert result["min_price"] == 500_000
        assert result["max_price"] == 1_500_000
        assert result["capacity_min"] == 100
        assert result["capacity_max"] == 800
        assert result["rating"] == 4.3
        assert result["review_count"] == 256
        assert result["area"] == "Lake Pichola"
        assert result["venue_type"] in ["palace", "resort"]
