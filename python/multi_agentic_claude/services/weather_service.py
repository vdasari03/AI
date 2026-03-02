"""
Weather service — wraps Open-Meteo API (free, no key required).
Responsible only for fetching temperature forecasts.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import httpx

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TemperatureForecast:
    latitude: float
    longitude: float
    target_time: datetime
    temperature_celsius: float
    temperature_fahrenheit: float
    weather_description: str
    timezone: str

    @classmethod
    def from_celsius(
        cls,
        latitude: float,
        longitude: float,
        target_time: datetime,
        celsius: float,
        weather_description: str = "",
        timezone: str = "UTC",
    ) -> "TemperatureForecast":
        return cls(
            latitude=latitude,
            longitude=longitude,
            target_time=target_time,
            temperature_celsius=celsius,
            temperature_fahrenheit=celsius * 9 / 5 + 32,
            weather_description=weather_description,
            timezone=timezone,
        )


class WeatherServiceProtocol(Protocol):
    async def get_forecast(
        self, latitude: float, longitude: float, target_time: datetime
    ) -> TemperatureForecast: ...


# WMO Weather Codes mapping (subset)
WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Icy fog",
    51: "Light drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    80: "Rain showers",
    95: "Thunderstorm",
}


class OpenMeteoWeatherService:
    """
    Free weather forecast via Open-Meteo API.
    Fetches hourly temperature data and finds the closest hour to target_time.
    """

    def __init__(
        self,
        base_url: str = "https://historical-forecast-api.open-meteo.com/v1/forecast",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url
        self._client = http_client

    async def get_forecast(
        self, latitude: float, longitude: float, target_time: datetime
    ) -> TemperatureForecast:
        logger.info(
        "Fetching forecast for lat=%.4f, lon=%.4f at %s",
        latitude, longitude, target_time.isoformat(),
    )
        from datetime import date, timezone as tz
        today = date.today()
        target_date = target_time.date()
        days_diff = (target_date - today).days

        if days_diff < 0:
            # Historical: use archive API
            base_url = "https://archive-api.open-meteo.com/v1/archive"
        elif days_diff <= 16:
            # Within forecast window
            base_url = f"{self._base_url}/forecast"
        else:
            # Beyond 16-day window: use historical forecast API
            base_url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

        date_str = target_date.isoformat()
        # date_str = target_time.strftime("%Y-%m-%d")
        # params = {
        #     "latitude": latitude,
        #     "longitude": longitude,
        #     "hourly": "temperature_2m,weathercode",
        #     "start_date": date_str,
        #     "end_date": date_str,
        #     "timezone": "auto",
        # }

        params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,weather_code",  # Fixed: was "weathercode"
        "start_date": date_str,
        "end_date": date_str,
        "timezone": "auto",
        }

        async with (self._client or httpx.AsyncClient()) as client:
            response = await client.get(base_url, params=params, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            
        hourly = data.get("hourly", {})
        times: list[str] = hourly.get("time", [])
        temps: list[float] = hourly.get("temperature_2m", [])
        codes: list[int] = hourly.get("weathercode", [])
        timezone: str = data.get("timezone", "UTC")

        if not times:
            raise ValueError("No forecast data returned from Open-Meteo.")

        # Find closest hour to target_time
        target_hour = target_time.hour
        best_idx = min(range(len(times)), key=lambda i: abs(int(times[i].split("T")[1][:2]) - target_hour))

        celsius = temps[best_idx]
        code = codes[best_idx] if httpx.codes else 0
        description = WMO_CODES.get(code, "Unknown")

        forecast = TemperatureForecast.from_celsius(
            latitude=latitude,
            longitude=longitude,
            target_time=target_time,
            celsius=celsius,
            weather_description=description,
            timezone=timezone,
        )

        logger.info(
        "Forecast: %.1f°C / %.1f°F — %s",
        forecast.temperature_celsius,
        forecast.temperature_fahrenheit,
        forecast.weather_description,
    )
        
        return forecast
