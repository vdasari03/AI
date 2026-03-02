"""
Unit tests for services layer.
All HTTP calls are intercepted with respx or unittest.mock.
"""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import respx

from services.geocoding_service import Coordinates, NominatimGeocodingService
from services.weather_service import OpenMeteoWeatherService, TemperatureForecast
from services.datetime_service import DatetimeService


# ─── GeocodingService ────────────────────────────────────────────────────────

class TestNominatimGeocodingService:

    NOMINATIM_RESPONSE = [
        {
            "lat": "40.7128",
            "lon": "-74.0060",
            "display_name": "New York, NY, USA",
        }
    ]

    @pytest.mark.asyncio
    @respx.mock
    async def test_resolve_returns_coordinates(self):
        respx.get("https://nominatim.openstreetmap.org/search").mock(
            return_value=httpx.Response(200, json=self.NOMINATIM_RESPONSE)
        )
        svc = NominatimGeocodingService()
        coords = await svc.resolve("New York")

        assert isinstance(coords, Coordinates)
        assert coords.latitude == pytest.approx(40.7128)
        assert coords.longitude == pytest.approx(-74.0060)
        assert coords.city == "New York"

    @pytest.mark.asyncio
    @respx.mock
    async def test_resolve_city_not_found_raises(self):
        respx.get("https://nominatim.openstreetmap.org/search").mock(
            return_value=httpx.Response(200, json=[])
        )
        svc = NominatimGeocodingService()
        with pytest.raises(ValueError, match="City not found"):
            await svc.resolve("UnknownCity123")

    @pytest.mark.asyncio
    @respx.mock
    async def test_resolve_http_error_raises(self):
        respx.get("https://nominatim.openstreetmap.org/search").mock(
            return_value=httpx.Response(500)
        )
        svc = NominatimGeocodingService()
        with pytest.raises(httpx.HTTPStatusError):
            await svc.resolve("New York")


# ─── WeatherService ──────────────────────────────────────────────────────────

OPEN_METEO_RESPONSE = {
    "timezone": "America/New_York",
    "hourly": {
        "time": ["2025-04-05T16:00", "2025-04-05T17:00", "2025-04-05T18:00"],
        "temperature_2m": [14.0, 15.5, 13.0],
        "weathercode": [2, 2, 3],
    },
}


class TestOpenMeteoWeatherService:

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_forecast_returns_correct_hour(self):
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=OPEN_METEO_RESPONSE)
        )
        svc = OpenMeteoWeatherService()
        target = datetime(2025, 4, 5, 17, 0)
        forecast = await svc.get_forecast(40.7128, -74.0060, target)

        assert isinstance(forecast, TemperatureForecast)
        assert forecast.temperature_celsius == pytest.approx(15.5)
        assert forecast.temperature_fahrenheit == pytest.approx(59.9)
        assert forecast.weather_description == "Partly cloudy"
        assert forecast.timezone == "America/New_York"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_forecast_empty_data_raises(self):
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json={"hourly": {}})
        )
        svc = OpenMeteoWeatherService()
        with pytest.raises(ValueError, match="No forecast data"):
            await svc.get_forecast(40.7, -74.0, datetime(2025, 4, 5, 17))

    def test_from_celsius_converts_to_fahrenheit(self):
        f = TemperatureForecast.from_celsius(
            latitude=0, longitude=0, target_time=datetime.now(),
            celsius=0.0, weather_description="Clear sky",
        )
        assert f.temperature_fahrenheit == pytest.approx(32.0)

    def test_from_celsius_100_degrees(self):
        f = TemperatureForecast.from_celsius(
            latitude=0, longitude=0, target_time=datetime.now(), celsius=100.0
        )
        assert f.temperature_fahrenheit == pytest.approx(212.0)


# ─── DatetimeService ─────────────────────────────────────────────────────────

class TestDatetimeService:

    def test_parse_explicit_iso(self):
        svc = DatetimeService()
        dt = svc.parse("2025-04-05", "17:00")
        assert dt.year == 2025
        assert dt.month == 4
        assert dt.day == 5
        assert dt.hour == 17

    def test_parse_natural_language(self):
        svc = DatetimeService()
        dt = svc.parse("5th April", "5 pm")
        assert dt.month == 4
        assert dt.day == 5
        assert dt.hour == 17

    def test_parse_date_only(self):
        svc = DatetimeService()
        dt = svc.parse("April 5")
        assert dt.month == 4
        assert dt.day == 5

    def test_parse_invalid_raises(self):
        svc = DatetimeService()
        with pytest.raises(ValueError):
            svc.parse("not a date at all xyzzy")

    def test_format_for_display(self):
        svc = DatetimeService()
        dt = datetime(2025, 4, 5, 17, 0)
        result = svc.format_for_display(dt)
        assert "April" in result
        assert "2025" in result
        assert "5:00 PM" in result
