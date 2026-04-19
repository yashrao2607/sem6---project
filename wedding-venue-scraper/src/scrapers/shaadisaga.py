"""
ShaadiSaga scraper — Tier 1 source (JavaScript-heavy).
Uses Selenium WebDriver with headless Chrome and explicit waits.
URL pattern: https://www.shaadisaga.com/wedding-vendors/{city}/wedding-venues
"""
import logging
import time
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.shaadisaga.com"
LISTING_TPL = "/wedding-vendors/{city}/wedding-venues"


def _get_driver():
    """Return a headless Chrome WebDriver instance. Import deferred to avoid
    hard dependency when Selenium is not installed."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        return webdriver.Chrome(options=opts)
    except ImportError:
        raise RuntimeError(
            "Selenium is required for ShaadiSaga scraping. "
            "Install with: pip install selenium"
        )


class ShaadiSagaScraper(BaseScraper):
    source_name = "shaadisaga"

    def __init__(self):
        super().__init__()
        self._driver = None

    def _ensure_driver(self):
        if self._driver is None:
            self._driver = _get_driver()

    def close(self):
        if self._driver:
            self._driver.quit()
            self._driver = None

    # ── Public API ────────────────────────────────────────────────────────────

    def scrape_city(self, city_slug: str, state: str, city_display: str) -> list[dict]:
        logger.info("[ShaadiSaga] Scraping city: %s (%s)", city_display, state)
        self._ensure_driver()

        path = LISTING_TPL.format(city=city_slug)
        url = BASE_URL + path
        partials = self._scrape_listing(url, city_slug)

        venues: list[dict] = []
        for partial in partials:
            partial.update({
                "state": state, "city": city_display,
                "source": self.source_name, "scraped_at": self.scraped_at,
                "venue_id": self.make_id()
            })
            detail_url = partial.get("source_url")
            if detail_url:
                detail_html = self._fetch_js(detail_url)
                if detail_html:
                    partial = self._parse_detail_page(detail_html, partial)
            venues.append(partial)

        logger.info("[ShaadiSaga] %s → %d venues", city_display, len(venues))
        self.close()
        return venues

    # ── JS-rendered fetcher ───────────────────────────────────────────────────

    def _fetch_js(self, url: str, wait: float = 3.0) -> Optional[str]:
        cached = self.cache.get(url)
        if cached:
            return cached
        try:
            self._driver.get(url)
            time.sleep(wait)  # wait for JS hydration

            # Try explicit wait for main content
            try:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.support.ui import WebDriverWait
                WebDriverWait(self._driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h2,h3,.vendor-card,.listing-item"))
                )
            except Exception:
                pass

            html = self._driver.page_source
            self.cache.set(url, html)
            return html
        except Exception as exc:
            logger.error("Selenium fetch failed for %s: %s", url, exc)
            return None

    def _scrape_listing(self, url: str, city_slug: str) -> list[dict]:
        results: list[dict] = []
        page = 1
        while True:
            page_url = f"{url}?page={page}" if page > 1 else url
            html = self._fetch_js(page_url)
            if not html:
                break
            cards = self._parse_listing_page(html, city_slug)
            if not cards:
                break
            results.extend(cards)
            logger.info("  ShaadiSaga page %d → %d cards", page, len(cards))
            # Check for next page
            soup = BeautifulSoup(html, "html.parser")
            if not soup.select_one("a.next-page, a[rel='next'], li.next a"):
                break
            page += 1
            if page > 15:  # safety cap
                break
        return results

    # ── Listing page ──────────────────────────────────────────────────────────

    def _parse_listing_page(self, html: str, city_slug: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        cards = (
            soup.select("div.vendor-card") or
            soup.select("div.listing-item") or
            soup.select(".venue-listing") or
            soup.select("div[class*='vendor']") or
            soup.select("article")
        )
        results = []
        for card in cards:
            rec = self._extract_card(card)
            if rec:
                results.append(rec)
        return results

    def _extract_card(self, card) -> Optional[dict]:
        name = None
        for sel in ["h2", "h3", ".vendor-title", ".listing-title"]:
            tag = card.select_one(sel)
            if tag and tag.get_text(strip=True):
                name = self.clean_text(tag.get_text())
                break
        if not name:
            return None

        link = None
        for sel in ["a[href*='wedding-venue']", "a[href*='/venue/']", "a"]:
            tag = card.select_one(sel)
            if tag and tag.get("href"):
                href = tag["href"]
                link = href if href.startswith("http") else urljoin(BASE_URL, href)
                break

        featured = bool(card.select_one(".featured-badge, .premium-tag, .featured-label"))
        price_raw = None
        for sel in [".price", ".cost", ".starting-price", "[class*='price']"]:
            tag = card.select_one(sel)
            if tag:
                price_raw = self.clean_text(tag.get_text())
                break

        return {
            "venue_name": name,
            "source_url": link,
            "featured": featured,
            "price_raw": price_raw,
        }

    # ── Detail page ───────────────────────────────────────────────────────────

    def _parse_detail_page(self, html: str, partial: dict) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        record = dict(partial)

        address = None
        for sel in ["address", ".location", ".venue-address", "[class*='address']"]:
            tag = soup.select_one(sel)
            if tag:
                address = self.clean_text(tag.get_text())
                break
        record["address_raw"] = address

        pricing = None
        for sel in [".pricing", ".package-details", ".price-info", "[class*='price']"]:
            tag = soup.select_one(sel)
            if tag:
                pricing = self.clean_text(tag.get_text())
                break
        if pricing and not record.get("price_raw"):
            record["price_raw"] = pricing

        cap = None
        for sel in [".capacity", ".guest-capacity", "[class*='capacity']"]:
            tag = soup.select_one(sel)
            if tag:
                cap = self.clean_text(tag.get_text())
                break
        record["capacity_raw"] = cap

        return record
