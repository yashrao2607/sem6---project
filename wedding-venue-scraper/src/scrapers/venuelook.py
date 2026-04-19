"""
VenueLook scraper — Tier 1 source.
Extracts from two complementary page structures:
  - Schema.org JSON-LD script: venue name, URL, address (30 per page)
  - Comparison table <td>: capacity and price-per-plate (same 30, same order)
Pagination: ?page=N; total pages from resp.data[0].total_pages
URL pattern: https://www.venuelook.com/wedding-venues-in-{city}?page=N
"""
import json
import logging
import re
from bs4 import BeautifulSoup

from .base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.venuelook.com"
LISTING_TPL = "/wedding-venues-in-{city}"

_RE_JSONLD = re.compile(r'\[.*?"@type"\s*:\s*"LocalBusiness".*?\]', re.DOTALL)


class VenueLookScraper(BaseScraper):
    source_name = "venuelook"

    def scrape_city(self, city_slug: str, state: str, city_display: str) -> list[dict]:
        logger.info("[VenueLook] Scraping city: %s (%s)", city_display, state)
        path = LISTING_TPL.format(city=city_slug)
        first_url = BASE_URL + path

        html = self.fetch(first_url)
        if not html:
            logger.warning("[VenueLook] No response for %s", first_url)
            return []

        total_pages = self._detect_total_pages(html)
        logger.info("  %s: %d pages", city_display, total_pages)

        all_venues: list[dict] = []
        all_venues.extend(self._parse_listing_page(html, city_slug, state, city_display))

        for page in range(2, total_pages + 1):
            page_url = f"{BASE_URL}{path}?page={page}"
            page_html = self.fetch(page_url)
            if not page_html:
                continue
            venues = self._parse_listing_page(page_html, city_slug, state, city_display)
            all_venues.extend(venues)
            logger.info("  Page %d -> %d venues", page, len(venues))

        logger.info("[VenueLook] %s -> %d total venues", city_display, len(all_venues))
        return all_venues

    # ── Page parsing ──────────────────────────────────────────────────────────

    def _parse_listing_page(self, html: str, _city_slug: str,
                             state: str, city_display: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")

        # 1. Parse JSON-LD for name, URL, address
        jsonld_items = self._extract_jsonld(html)

        # 2. Parse comparison table for capacity and price
        table_rows = self._extract_table_rows(soup)

        results: list[dict] = []
        for i, item in enumerate(jsonld_items):
            name = item.get("name", "").strip()
            if not name:
                continue
            source_url = item.get("url", "").strip()
            if not source_url:
                continue

            address = item.get("address", {})
            address_raw = address.get("streetAddress", "")
            area_hint  = address.get("addressLocality", "")

            # Merge table data by position
            cap_raw   = None
            price_raw = None
            if i < len(table_rows):
                cap_raw, price_raw = table_rows[i]

            results.append({
                "venue_id":       self.make_id(),
                "venue_name":     name,
                "state":          state,
                "city":           city_display,
                "address_raw":    address_raw,
                "area_hint":      area_hint,
                "capacity_raw":   cap_raw,
                "price_raw":      price_raw,
                "venue_type_raw": None,
                "source":         self.source_name,
                "source_url":     source_url,
                "scraped_at":     self.scraped_at,
            })

        return results

    def _extract_jsonld(self, html: str) -> list[dict]:
        """Extract the Schema.org LocalBusiness JSON-LD array."""
        for s in BeautifulSoup(html, "html.parser").find_all("script"):
            txt = s.string or ""
            if 5000 < len(txt) < 60000:
                m = re.search(r'(\[.+\])', txt, re.DOTALL)
                if m:
                    try:
                        arr = json.loads(m.group(1))
                        if arr and isinstance(arr[0], dict) and arr[0].get("@type") == "LocalBusiness":
                            return arr
                    except json.JSONDecodeError:
                        pass
        return []

    def _extract_table_rows(self, soup: BeautifulSoup) -> list[tuple]:
        """
        Extract (capacity_raw, price_raw) tuples from the comparison table.
        Returns list aligned with JSON-LD index.
        """
        table = soup.find("table")
        if not table:
            return []
        rows = table.find_all("tr")
        result = []
        for row in rows[1:]:  # skip header
            cells = row.find_all(["td", "th"])
            cap   = cells[1].get_text(strip=True) if len(cells) > 1 else None
            price = cells[2].get_text(strip=True) if len(cells) > 2 else None
            result.append((cap, price))
        return result

    def _detect_total_pages(self, html: str) -> int:
        """Read total_pages from the embedded resp.data JSON script."""
        soup = BeautifulSoup(html, "html.parser")
        for s in soup.find_all("script"):
            txt = s.string or ""
            if '"total_pages"' in txt and len(txt) > 500:
                try:
                    d = json.loads(txt)
                    resp_items = (d.get("props", {})
                                   .get("pageProps", {})
                                   .get("resp", {})
                                   .get("data", []))
                    if resp_items:
                        return int(resp_items[0].get("total_pages", 1))
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass
        # Fallback: count pagination links
        soup2 = BeautifulSoup(html, "html.parser")
        nums = []
        for a in soup2.select("a[href*='page=']"):
            m = re.search(r"page=(\d+)", a.get("href", ""))
            if m:
                nums.append(int(m.group(1)))
        return max(nums) if nums else 1

    # ── Unused abstract stubs ─────────────────────────────────────────────────

    def _parse_detail_page(self, _html: str, partial: dict) -> dict:
        return partial  # listing page already has all needed fields
