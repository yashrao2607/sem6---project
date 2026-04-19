"""
WeddingWire India scraper — Tier 2 enrichment-only source.
Used exclusively to cross-validate pricing and add review depth.
Not used for bulk venue discovery.
"""
import logging
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.weddingwire.in"
LISTING_TPL = "/wedding-venues/{city}"


class WeddingWireScraper(BaseScraper):
    source_name = "weddingwire"

    def scrape_city(self, city_slug: str, state: str, city_display: str) -> list[dict]:
        """Scrape WeddingWire for enrichment data (reviews + pricing cross-validation)."""
        logger.info("[WeddingWire] Enrichment scrape for: %s", city_display)
        url = BASE_URL + LISTING_TPL.format(city=city_slug)
        html = self.fetch(url)
        if not html:
            return []
        return self._parse_listing_page(html, city_slug)

    def _parse_listing_page(self, html: str, city_slug: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        cards = (
            soup.select("div.vendor-tile") or
            soup.select("article.supplier-card") or
            soup.select("div[class*='vendor']")
        )
        results = []
        for card in cards:
            rec = self._extract_card(card)
            if rec:
                results.append(rec)
        return results

    def _extract_card(self, card) -> Optional[dict]:
        name = None
        for sel in ["h2.vendor-name", ".supplier-name", "h2", "h3"]:
            tag = card.select_one(sel)
            if tag and tag.get_text(strip=True):
                name = self.clean_text(tag.get_text())
                break
        if not name:
            return None

        link = None
        tag = card.select_one("a.vendor-link, a[href*='venue'], a")
        if tag and tag.get("href"):
            href = tag["href"]
            link = href if href.startswith("http") else urljoin(BASE_URL, href)

        review_count_raw = None
        tag = card.select_one(".review-count, [class*='review']")
        if tag:
            review_count_raw = self.clean_text(tag.get_text())

        price_raw = None
        tag = card.select_one(".budget-estimator, .price-estimate, [class*='price']")
        if tag:
            price_raw = self.clean_text(tag.get_text())

        return {
            "venue_name": name,
            "source_url": link,
            "review_count_raw": review_count_raw,
            "price_raw": price_raw,
            "source": self.source_name,
            "scraped_at": self.scraped_at,
        }

    def _parse_detail_page(self, html: str, partial: dict) -> dict:
        return partial  # enrichment only — detail pages not needed

    def enrich_venue(self, venue_name: str, city: str) -> dict:
        """Look up a specific venue by name for enrichment data."""
        city_slug = city.lower().replace(" ", "-")
        candidates = self.scrape_city(city_slug, "", city)
        for c in candidates:
            if venue_name.lower() in c.get("venue_name", "").lower():
                return c
        return {}
