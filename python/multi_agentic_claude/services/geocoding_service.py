"""
Geocoding service — wraps Nominatim (OpenStreetMap) API.
Follows Single Responsibility Principle: only resolves city names to coordinates.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

import httpx

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Coordinates:
    city: str
    latitude: float
    longitude: float
    country: str = ""
    display_name: str = ""


class GeocodingServiceProtocol(Protocol):
    async def resolve(self, city: str) -> Coordinates: ...


class NominatimGeocodingService:
    """
    Free geocoding via OpenStreetMap Nominatim.
    No API key required. Respects usage policy (User-Agent required).
    """

    def __init__(
        self,
        base_url: str = "https://nominatim.openstreetmap.org",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url
        self._client = http_client  # injected for testability

    async def resolve(self, city: str) -> Coordinates:
        logger.info("Resolving coordinates for city: %s", city)
        params = {
            "q": city,
            "format": "json",
            "limit": 1,
        }
        headers = {"User-Agent": "MultiAgentWeatherSystem/1.0"}

        async with (self._client or httpx.AsyncClient()) as client:
            response = await client.get(
                f"{self._base_url}/search",
                params=params,
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            results = response.json()

        if not results:
            raise ValueError(f"City not found: '{city}'")

        result = results[0]
        coords = Coordinates(
            city=city,
            latitude=float(result["lat"]),
            longitude=float(result["lon"]),
            display_name=result.get("display_name", ""),
        )
        logger.info("Resolved %s → lat=%.4f, lon=%.4f", city, coords.latitude, coords.longitude)
        return coords
