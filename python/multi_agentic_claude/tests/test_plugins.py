"""
Unit tests for Semantic Kernel plugins.
Plugins delegate to agents; agents are tested separately.
Here we verify the JSON serialization contract of each plugin.
"""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins.geolocation_plugin import GeolocationPlugin
from plugins.time_plugin import TimePlugin
from plugins.temperature_plugin import TemperaturePlugin
from services.geocoding_service import Coordinates
from services.weather_service import TemperatureForecast


class TestGeolocationPlugin:

    @pytest.mark.asyncio
    async def test_resolve_location_returns_json(self, mock_geocoding_service):
        plugin = GeolocationPlugin(mock_geocoding_service)
        result = await plugin.resolve_location("New York")
        data = json.loads(result)

        assert data["city"] == "New York"
        assert data["latitude"] == pytest.approx(40.7128)
        assert data["longitude"] == pytest.approx(-74.0060)

    @pytest.mark.asyncio
    async def test_resolve_location_error_returns_error_json(self):
        failing_service = AsyncMock()
        failing_service.resolve = AsyncMock(side_effect=ValueError("City not found: 'ZZZZZ'"))
        plugin = GeolocationPlugin(failing_service)
        result = await plugin.resolve_location("ZZZZZ")
        data = json.loads(result)

        assert "error" in data


class TestTimePlugin:

    @pytest.mark.asyncio
    async def test_parse_datetime_returns_json(self, mock_datetime_service):
        plugin = TimePlugin(mock_datetime_service)
        result = await plugin.parse_datetime("5th April", "5 pm")
        data = json.loads(result)

        assert "iso_datetime" in data
        assert "human_readable" in data
        assert "2025-04-05" in data["iso_datetime"]

    @pytest.mark.asyncio
    async def test_parse_datetime_error_returns_error_json(self):
        bad_service = MagicMock()
        bad_service.parse = MagicMock(side_effect=ValueError("Bad date"))
        plugin = TimePlugin(bad_service)
        result = await plugin.parse_datetime("not a date")
        data = json.loads(result)

        assert "error" in data


class TestTemperaturePlugin:

    @pytest.mark.asyncio
    async def test_get_temperature_returns_json(self, mock_weather_service):
        plugin = TemperaturePlugin(mock_weather_service)
        result = await plugin.get_temperature(
            latitude="40.7128",
            longitude="-74.006",
            iso_datetime="2025-04-05T17:00:00",
        )
        data = json.loads(result)

        assert data["temperature_celsius"] == pytest.approx(15.5)
        assert data["temperature_fahrenheit"] == pytest.approx(59.9)
        assert data["weather_description"] == "Partly cloudy"

    @pytest.mark.asyncio
    async def test_invalid_latitude_returns_error_json(self, mock_weather_service):
        plugin = TemperaturePlugin(mock_weather_service)
        result = await plugin.get_temperature(
            latitude="not-a-float",
            longitude="-74.006",
            iso_datetime="2025-04-05T17:00:00",
        )
        data = json.loads(result)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_invalid_datetime_returns_error_json(self, mock_weather_service):
        plugin = TemperaturePlugin(mock_weather_service)
        result = await plugin.get_temperature(
            latitude="40.7",
            longitude="-74.0",
            iso_datetime="not-a-datetime",
        )
        data = json.loads(result)
        assert "error" in data
