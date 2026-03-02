"""
Semantic Kernel Plugin — Temperature.
Wraps TemperatureAgent as an SK-native kernel function.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from semantic_kernel.functions import kernel_function

from agents.temperature_agent import TemperatureAgent
from agents.base_agent import AgentContext
from services.weather_service import WeatherServiceProtocol

logger = logging.getLogger(__name__)


class TemperaturePlugin:
    """SK plugin exposing temperature forecast as a kernel function."""

    def __init__(self, weather_service: WeatherServiceProtocol | None = None) -> None:
        self._agent = TemperatureAgent(weather_service)

    @kernel_function(
        name="get_temperature",
        description="Gets the temperature forecast for a location at a specific datetime.",
    )
    async def get_temperature(
        self,
        latitude: str,
        longitude: str,
        iso_datetime: str,
    ) -> str:
        """
        Get temperature forecast for lat/lon at a given datetime.

        Args:
            latitude: Latitude as string float
            longitude: Longitude as string float
            iso_datetime: ISO 8601 datetime string

        Returns:
            JSON with temperature in Celsius and Fahrenheit plus weather description.
        """
        try:
            lat = float(latitude)
            lon = float(longitude)
            target_dt = datetime.fromisoformat(iso_datetime)
        except ValueError as exc:
            return json.dumps({"error": str(exc)})

        context = AgentContext(
            raw_query=f"temperature at {lat},{lon} on {iso_datetime}",
            latitude=lat,
            longitude=lon,
            target_datetime=target_dt,
        )
        context = await self._agent(context)

        if context.has_errors:
            return json.dumps({"error": context.errors})

        return json.dumps({
            "temperature_celsius": context.temperature_celsius,
            "temperature_fahrenheit": context.temperature_fahrenheit,
            "weather_description": context.weather_description,
            "timezone": context.timezone,
        })
