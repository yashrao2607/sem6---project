"""
WedMeGood scraper — Tier 1 primary source.
Data is embedded as window.__INITIAL_STATE__ JSON in SSR HTML.
URL pattern: https://www.wedmegood.com/vendors/{city}/wedding-venues/?page=N
"""
import json
import logging
import re
from typing import Optional
from urllib.parse import urljoin

from .base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.wedmegood.com"
LISTING_TPL = "/vendors/{city}/wedding-venues/"

_RE_STATE = re.compile(
    r'window\.__INITIAL_STATE__\s*=\s*(\{.+?\});\s*</script>', re.DOTALL
)


def _extract_state(html: str) -> Optional[dict]:
    m = _RE_STATE.search(html)
    if not m:
        return None
    raw = m.group(1).replace(":undefined", ":null")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("__INITIAL_STATE__ JSON parse error: %s", e)
        return None


class WedMeGoodScraper(BaseScraper):
    source_name = "wedmegood"

    # ── Public API ────────────────────────────────────────────────────────────

    def scrape_city(self, city_slug: str, state: str, city_display: str) -> list[dict]:
        logger.info("[WedMeGood] Scraping city: %s (%s)", city_display, state)
        path = LISTING_TPL.format(city=city_slug)
        first_url = BASE_URL + path

        # Fetch first page to determine total pages
        html = self.fetch(first_url)
        if not html:
            logger.warning("[WedMeGood] No response for %s", first_url)
            return []

        data = _extract_state(html)
        if not data:
            logger.warning("[WedMeGood] No __INITIAL_STATE__ on %s", first_url)
            return []

        vl = data.get("vendorList", {})
        num_pages = vl.get("numPages", 1) or 1
        logger.info("  %s: %d total venues across %d pages",
                    city_display, vl.get("totalVendors", 0), num_pages)

        venues: list[dict] = []
        venues.extend(self._extract_vendors(vl, state, city_display, city_slug))

        for page in range(2, num_pages + 1):
            page_url = f"{BASE_URL}{path}?page={page}"
            page_html = self.fetch(page_url)
            if not page_html:
                continue
            page_data = _extract_state(page_html)
            if not page_data:
                continue
            page_vl = page_data.get("vendorList", {})
            extracted = self._extract_vendors(page_vl, state, city_display, city_slug)
            venues.extend(extracted)
            logger.info("  Page %d -> %d venues", page, len(extracted))

        logger.info("[WedMeGood] %s -> %d total venues", city_display, len(venues))
        return venues

    # ── Vendor extraction ─────────────────────────────────────────────────────

    def _extract_vendors(self, vl: dict, state: str, city_display: str, _city_slug: str) -> list[dict]:
        vendors_array = vl.get("vendorsArray", [])
        results = []
        for v in vendors_array:
            rec = self._parse_vendor(v, state, city_display)
            if rec:
                results.append(rec)
        return results

    def _parse_vendor(self, v: dict, state: str, city_display: str) -> Optional[dict]:
        name = v.get("name", "").strip()
        if not name:
            return None

        slug = v.get("new_slug", "")
        source_url = urljoin(BASE_URL, slug) if slug else None
        if not source_url:
            return None

        # Price
        price_raw = None
        vp = v.get("vendor_price")
        vp_sub = v.get("vendor_price_subtext", "")
        dest_price = v.get("destination_price")
        if vp and str(vp).strip():
            price_raw = f"\u20b9{vp} {vp_sub}".strip()
        elif dest_price:
            price_raw = dest_price

        # Capacity
        cap_raw = None
        gc = v.get("num_guest_count")
        if gc and isinstance(gc, list) and gc:
            c = gc[0]
            lo, hi = c.get("min_value"), c.get("max_value")
            if lo and hi:
                cap_raw = f"{lo} - {hi}"
            elif hi:
                cap_raw = str(hi)

        # Venue type
        vtype_raw = None
        vt = v.get("venue_type")
        if isinstance(vt, list) and vt:
            vtype_raw = vt[0]
        elif isinstance(vt, str):
            vtype_raw = vt

        # Rating / reviews
        rating = v.get("vendor_rating") or v.get("best_rating")
        review_count = v.get("reviews_count")

        # Area / locality
        area_raw = (v.get("primary_locality") or v.get("locality") or "").strip()
        address_raw = v.get("address", "").strip()

        return {
            "venue_id":       self.make_id(),
            "venue_name":     name,
            "state":          state,
            "city":           v.get("base_city") or v.get("city") or city_display,
            "address_raw":    address_raw or area_raw,
            "area_hint":      area_raw,   # passed to normalizer for area extraction
            "venue_type_raw": vtype_raw,
            "price_raw":      price_raw,
            "capacity_raw":   cap_raw,
            "rating":         rating,
            "review_count_raw": str(review_count) if review_count else None,
            "source":         self.source_name,
            "source_url":     source_url,
            "scraped_at":     self.scraped_at,
        }

    # ── Abstract stubs (not used — data comes from JSON, not HTML parsing) ────

    def _parse_listing_page(self, html: str, _city_slug: str) -> list[dict]:
        data = _extract_state(html)
        if not data:
            return []
        vl = data.get("vendorList", {})
        return self._extract_vendors(vl, "", "", _city_slug)

    def _parse_detail_page(self, _html: str, partial: dict) -> dict:
        return partial  # listing JSON already contains all needed fields
