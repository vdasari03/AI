"""
Geolocation Agent — resolves a city name to geographic coordinates.
Depends on GeocodingServiceProtocol (injected).
"""

from __future__ import annotations

import logging

from agents.base_agent import AgentContext, BaseAgent
from services.geocoding_service import GeocodingServiceProtocol, NominatimGeocodingService

logger = logging.getLogger(__name__)


class GeolocationAgent(BaseAgent):
    """
    Enriches AgentContext with latitude/longitude for the requested city.
    """

    def __init__(self, geocoding_service: GeocodingServiceProtocol | None = None) -> None:
        self._service: GeocodingServiceProtocol = (
            geocoding_service or NominatimGeocodingService()
        )

    @property
    def name(self) -> str:
        return "GeolocationAgent"

    async def process(self, context: AgentContext) -> AgentContext:
        if not context.city:
            context.add_error("GeolocationAgent: 'city' not set in context.")
            return context

        try:
            coords = await self._service.resolve(context.city)
            context.latitude = coords.latitude
            context.longitude = coords.longitude
            logger.info(
                "Resolved '%s' → lat=%.4f, lon=%.4f",
                context.city,
                context.latitude,
                context.longitude,
            )
        except Exception as exc:
            context.add_error(f"GeolocationAgent error: {exc}")

        return context
