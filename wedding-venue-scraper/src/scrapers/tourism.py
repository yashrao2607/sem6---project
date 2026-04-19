"""
Tourism website scrapers — Tier 2 validation-only sources.
Rajasthan Tourism: validates heritage palace names.
Goa Tourism: confirms beach venue area names and geographic accuracy.
"""
import logging
from typing import Optional

from bs4 import BeautifulSoup

from .base import BaseScraper

logger = logging.getLogger(__name__)

RAJASTHAN_URL = "https://tourism.rajasthan.gov.in"
GOA_URL = "https://www.goatourism.gov.in"


class RajasthanTourismScraper(BaseScraper):
    source_name = "tourism"

    def scrape_city(self, city_slug: str, state: str, city_display: str) -> list[dict]:
        """Fetch heritage property names from official Rajasthan Tourism portal."""
        logger.info("[RajasthanTourism] Fetching heritage properties for: %s", city_display)
        html = self.fetch(RAJASTHAN_URL + "/heritage-hotels")
        if not html:
            html = self.fetch(RAJASTHAN_URL)
        if not html:
            return []
        return self._parse_listing_page(html, city_slug)

    def _parse_listing_page(self, html: str, city_slug: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []
        # Look for hotel/property listings on the page
        for heading in soup.find_all(["h2", "h3", "h4"]):
            text = self.clean_text(heading.get_text())
            if not text or len(text) < 3:
                continue
            # Filter to properties matching our city
            if city_slug.replace("-", " ") in text.lower():
                results.append({
                    "venue_name": text,
                    "venue_type_raw": "heritage / palace",
                    "source": self.source_name,
                    "scraped_at": self.scraped_at,
                    "source_url": RAJASTHAN_URL,
                })
        return results

    def _parse_detail_page(self, html: str, partial: dict) -> dict:
        return partial

    def get_official_names(self) -> list[str]:
        """Return list of officially listed heritage property names."""
        html = self.fetch(RAJASTHAN_URL)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        return [
            self.clean_text(h.get_text())
            for h in soup.find_all(["h2", "h3", "h4"])
            if self.clean_text(h.get_text())
        ]


class GoaTourismScraper(BaseScraper):
    source_name = "tourism"

    def scrape_city(self, city_slug: str, state: str, city_display: str) -> list[dict]:
        logger.info("[GoaTourism] Fetching beach venue references for: %s", city_display)
        html = self.fetch(GOA_URL + "/beaches")
        if not html:
            html = self.fetch(GOA_URL)
        if not html:
            return []
        return self._parse_listing_page(html, city_slug)

    def _parse_listing_page(self, html: str, city_slug: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for heading in soup.find_all(["h2", "h3", "h4"]):
            text = self.clean_text(heading.get_text())
            if not text or len(text) < 3:
                continue
            results.append({
                "venue_name": text,
                "venue_type_raw": "beach",
                "source": self.source_name,
                "scraped_at": self.scraped_at,
                "source_url": GOA_URL,
            })
        return results

    def _parse_detail_page(self, html: str, partial: dict) -> dict:
        return partial

    def get_beach_area_names(self) -> list[str]:
        """Return list of official beach area names for geographic validation."""
        html = self.fetch(GOA_URL)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        return [
            self.clean_text(h.get_text())
            for h in soup.find_all(["h2", "h3", "h4"])
            if self.clean_text(h.get_text())
        ]
