"""
Temperature Agent — fetches weather forecast for resolved coordinates and datetime.
Depends on WeatherServiceProtocol (injected).
"""

from __future__ import annotations

import logging

from agents.base_agent import AgentContext, BaseAgent
from services.weather_service import OpenMeteoWeatherService, WeatherServiceProtocol

logger = logging.getLogger(__name__)


class TemperatureAgent(BaseAgent):
    """
    Enriches AgentContext with temperature and weather description.
    Requires latitude, longitude, and target_datetime to be set.
    """

    def __init__(self, weather_service: WeatherServiceProtocol | None = None) -> None:
        self._service: WeatherServiceProtocol = weather_service or OpenMeteoWeatherService()

    @property
    def name(self) -> str:
        return "TemperatureAgent"

    async def process(self, context: AgentContext) -> AgentContext:
        missing = []
        if context.latitude is None:
            missing.append("latitude")
        if context.longitude is None:
            missing.append("longitude")
        if context.target_datetime is None:
            missing.append("target_datetime")

        if missing:
            context.add_error(f"TemperatureAgent: missing fields: {missing}")
            return context

        try:
            forecast = await self._service.get_forecast(
                latitude=context.latitude,
                longitude=context.longitude,
                target_time=context.target_datetime,
            )
            context.temperature_celsius = forecast.temperature_celsius
            context.temperature_fahrenheit = forecast.temperature_fahrenheit
            context.weather_description = forecast.weather_description
            context.timezone = forecast.timezone
            logger.info(
                "Temperature: %.1f°C / %.1f°F — %s",
                context.temperature_celsius,
                context.temperature_fahrenheit,
                context.weather_description,
            )
        except Exception as exc:
            context.add_error(f"TemperatureAgent error: {exc}")

        return context
