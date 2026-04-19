"""
Base scraper class with shared HTTP session, caching, rate limiting, and retry logic.
"""
import logging
import random
import sqlite3
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse

import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config.settings import (
    CACHE_DB, CACHE_TTL_DAYS, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX,
    SESSION_ROTATE_EVERY, BACKOFF_INITIAL, MAX_RETRIES, USER_AGENTS
)

logger = logging.getLogger(__name__)


class CacheDB:
    """SQLite-backed URL response cache."""

    def __init__(self, db_path=CACHE_DB):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS url_cache (
                url TEXT PRIMARY KEY,
                html TEXT NOT NULL,
                fetched_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def get(self, url: str) -> Optional[str]:
        cutoff = (datetime.utcnow() - timedelta(days=CACHE_TTL_DAYS)).isoformat()
        row = self.conn.execute(
            "SELECT html FROM url_cache WHERE url=? AND fetched_at>?",
            (url, cutoff)
        ).fetchone()
        return row[0] if row else None

    def set(self, url: str, html: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO url_cache (url, html, fetched_at) VALUES (?, ?, ?)",
            (url, html, datetime.utcnow().isoformat())
        )
        self.conn.commit()

    def invalidate(self, source_domain: str = None):
        if source_domain:
            self.conn.execute(
                "DELETE FROM url_cache WHERE url LIKE ?", (f"%{source_domain}%",)
            )
        else:
            self.conn.execute("DELETE FROM url_cache")
        self.conn.commit()


class BaseScraper(ABC):
    """
    Abstract base class for all source-specific scrapers.

    Provides:
    - HTTP session management with User-Agent rotation
    - SQLite-based response caching (7-day TTL)
    - Exponential backoff on HTTP 429 / 5xx
    - Randomised request delay for rate limiting
    """

    source_name: str = "base"

    def __init__(self):
        self.cache = CacheDB()
        self._session = self._new_session()
        self._request_count = 0
        self.scraped_at = datetime.utcnow().isoformat()

    # ── Session management ────────────────────────────────────────────────────

    def _new_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-IN,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        return session

    def _maybe_rotate_session(self):
        if self._request_count > 0 and self._request_count % SESSION_ROTATE_EVERY == 0:
            self._session = self._new_session()
            logger.debug("Rotated HTTP session after %d requests", self._request_count)

    # ── HTTP fetch with cache + backoff ───────────────────────────────────────

    def fetch(self, url: str, bypass_cache: bool = False) -> Optional[str]:
        if not bypass_cache:
            cached = self.cache.get(url)
            if cached:
                logger.debug("Cache hit: %s", url)
                return cached

        self._maybe_rotate_session()
        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        time.sleep(delay)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self._session.get(url, timeout=30)
                self._request_count += 1

                if resp.status_code == 200:
                    self.cache.set(url, resp.text)
                    return resp.text

                if resp.status_code == 429:
                    wait = BACKOFF_INITIAL * (2 ** (attempt - 1))
                    logger.warning("Rate limited on %s — waiting %ds (attempt %d)", url, wait, attempt)
                    time.sleep(wait)
                    continue

                if resp.status_code >= 500:
                    wait = BACKOFF_INITIAL * attempt
                    logger.warning("Server error %d on %s — retrying in %ds", resp.status_code, url, wait)
                    time.sleep(wait)
                    continue

                logger.error("Unexpected status %d for %s", resp.status_code, url)
                return None

            except requests.RequestException as exc:
                logger.error("Request failed for %s (attempt %d): %s", url, attempt, exc)
                if attempt < MAX_RETRIES:
                    time.sleep(BACKOFF_INITIAL * attempt)

        logger.error("Exhausted retries for %s", url)
        return None

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def make_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def clean_text(text: str) -> str:
        return " ".join(text.strip().split()) if text else ""

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def scrape_city(self, city_slug: str, state: str, city_display: str) -> list[dict]:
        """Scrape all venues for a given city and return a list of raw venue dicts."""
        ...

    @abstractmethod
    def _parse_listing_page(self, html: str, city_slug: str) -> list[dict]:
        """Parse a listing page HTML and return partial venue records."""
        ...

    @abstractmethod
    def _parse_detail_page(self, html: str, partial: dict) -> dict:
        """Enrich a partial record using the venue detail page HTML."""
        ...
