"""
Semantic Kernel Plugin — Geolocation.
Wraps GeolocationAgent as an SK-native kernel function.
"""

from __future__ import annotations

import logging

from semantic_kernel.functions import kernel_function

from agents.geolocation_agent import GeolocationAgent
from agents.base_agent import AgentContext
from services.geocoding_service import GeocodingServiceProtocol

logger = logging.getLogger(__name__)


class GeolocationPlugin:
    """SK plugin exposing geolocation as a kernel function."""

    def __init__(self, geocoding_service: GeocodingServiceProtocol | None = None) -> None:
        self._agent = GeolocationAgent(geocoding_service)

    @kernel_function(
        name="resolve_location",
        description="Resolves a city name to its latitude and longitude coordinates.",
    )
    async def resolve_location(self, city: str) -> str:
        """
        Resolve a city to coordinates.

        Args:
            city: Name of the city (e.g. 'New York')

        Returns:
            JSON string with latitude, longitude, and city name.
        """
        import json

        context = AgentContext(raw_query=city, city=city)
        context = await self._agent(context)

        if context.has_errors:
            return json.dumps({"error": context.errors})

        return json.dumps({
            "city": context.city,
            "latitude": context.latitude,
            "longitude": context.longitude,
        })
