"""Base Data Extractor with Rate Limiting, Retries, and Provenance Metadata."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import httpx

logger = logging.getLogger("marina.ingestion.extractor")


class BaseExtractor(ABC):
    """Abstract base class for all football data extractors."""

    def __init__(
        self,
        source_code: str,
        source_name: str,
        base_url: str,
        rate_limit_delay_sec: float = 1.0,
        timeout_sec: float = 20.0,
        user_agent: Optional[str] = None,
    ) -> None:
        self.source_code = source_code
        self.source_name = source_name
        self.base_url = base_url.rstrip("/")
        self.rate_limit_delay_sec = rate_limit_delay_sec
        self.timeout_sec = timeout_sec
        self.user_agent = (
            user_agent
            or "MarinaIntelligenceBot/1.0 (+https://github.com/marina-intelligence; football-analytics)"
        )
        self._last_request_time: float = 0.0

    async def _throttle(self) -> None:
        """Enforces respectful rate limiting between external network requests."""
        loop = asyncio.get_running_loop()
        now = loop.time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit_delay_sec:
            await asyncio.sleep(self.rate_limit_delay_sec - elapsed)
        self._last_request_time = loop.time()

    async def fetch(
        self,
        endpoint_or_url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retries: int = 3,
        backoff_factor: float = 1.5,
    ) -> httpx.Response:
        """Executes an HTTP GET request with retries, exponential backoff, and throttling."""
        url = endpoint_or_url if endpoint_or_url.startswith("http") else f"{self.base_url}/{endpoint_or_url.lstrip('/')}"
        req_headers = {"User-Agent": self.user_agent, "Accept": "application/json, text/html, */*"}
        if headers:
            req_headers.update(headers)

        attempt = 0
        current_delay = 1.0
        while attempt < retries:
            await self._throttle()
            try:
                async with httpx.AsyncClient(timeout=self.timeout_sec, follow_redirects=True) as client:
                    response = await client.get(url, params=params, headers=req_headers)
                    response.raise_for_status()
                    return response
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                attempt += 1
                logger.warning(
                    "Fetch attempt %d/%d failed for %s: %s. Retrying in %.1fs...",
                    attempt,
                    retries,
                    url,
                    str(exc),
                    current_delay,
                )
                if attempt >= retries:
                    raise
                await asyncio.sleep(current_delay)
                current_delay *= backoff_factor

        raise RuntimeError(f"Unexpected termination in fetch loop for {url}")

    @abstractmethod
    async def extract_fixtures(self, season_code: str = "2026-27") -> Dict[str, Any]:
        """Extract fixtures and scheduled matches for designated season."""
        pass

    @abstractmethod
    async def extract_results(self, season_code: str = "2026-27") -> Dict[str, Any]:
        """Extract completed match results and scores."""
        pass
