"""
Unit tests for agents layer.
Services are fully mocked — agents tested in isolation.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.base_agent import AgentContext
from agents.geolocation_agent import GeolocationAgent
from agents.time_agent import TimeAgent
from agents.temperature_agent import TemperatureAgent
from services.geocoding_service import Coordinates
from services.weather_service import TemperatureForecast


# ─── GeolocationAgent ────────────────────────────────────────────────────────

class TestGeolocationAgent:

    @pytest.mark.asyncio
    async def test_resolves_city_to_coordinates(self, mock_geocoding_service, base_context):
        agent = GeolocationAgent(mock_geocoding_service)
        result = await agent(base_context)

        assert result.latitude == pytest.approx(40.7128)
        assert result.longitude == pytest.approx(-74.0060)
        assert not result.has_errors

    @pytest.mark.asyncio
    async def test_missing_city_adds_error(self, mock_geocoding_service):
        context = AgentContext(raw_query="test", city=None)
        agent = GeolocationAgent(mock_geocoding_service)
        result = await agent(context)

        assert result.has_errors
        assert "city" in result.errors[0].lower()
        mock_geocoding_service.resolve.assert_not_called()

    @pytest.mark.asyncio
    async def test_service_error_adds_error(self):
        failing_service = AsyncMock()
        failing_service.resolve = AsyncMock(side_effect=ConnectionError("timeout"))
        context = AgentContext(raw_query="test", city="New York")
        agent = GeolocationAgent(failing_service)
        result = await agent(context)

        assert result.has_errors
        assert "timeout" in result.errors[0]

    @pytest.mark.asyncio
    async def test_agent_name(self, mock_geocoding_service):
        agent = GeolocationAgent(mock_geocoding_service)
        assert agent.name == "GeolocationAgent"


# ─── TimeAgent ───────────────────────────────────────────────────────────────

class TestTimeAgent:

    @pytest.mark.asyncio
    async def test_parses_date_and_time(self, mock_datetime_service, base_context, april_5_5pm):
        agent = TimeAgent(mock_datetime_service)
        result = await agent(base_context)

        assert result.target_datetime == april_5_5pm
        assert not result.has_errors

    @pytest.mark.asyncio
    async def test_missing_date_str_adds_error(self, mock_datetime_service):
        context = AgentContext(raw_query="test", date_str=None)
        agent = TimeAgent(mock_datetime_service)
        result = await agent(context)

        assert result.has_errors
        assert "date_str" in result.errors[0]
        mock_datetime_service.parse.assert_not_called()

    @pytest.mark.asyncio
    async def test_parse_error_adds_error(self):
        bad_service = MagicMock()
        bad_service.parse = MagicMock(side_effect=ValueError("Unparseable"))
        context = AgentContext(raw_query="test", date_str="gibberish date")
        agent = TimeAgent(bad_service)
        result = await agent(context)

        assert result.has_errors
        assert "Unparseable" in result.errors[0]

    @pytest.mark.asyncio
    async def test_agent_name(self, mock_datetime_service):
        agent = TimeAgent(mock_datetime_service)
        assert agent.name == "TimeAgent"

    @pytest.mark.asyncio
    async def test_time_str_passed_to_service(self, mock_datetime_service, base_context):
        agent = TimeAgent(mock_datetime_service)
        await agent(base_context)
        mock_datetime_service.parse.assert_called_once_with("5th April", "5 pm")


# ─── TemperatureAgent ────────────────────────────────────────────────────────

class TestTemperatureAgent:

    @pytest.mark.asyncio
    async def test_fetches_temperature(self, mock_weather_service, populated_context):
        agent = TemperatureAgent(mock_weather_service)
        result = await agent(populated_context)

        assert result.temperature_celsius == pytest.approx(15.5)
        assert result.temperature_fahrenheit == pytest.approx(59.9)
        assert result.weather_description == "Partly cloudy"
        assert result.timezone == "America/New_York"
        assert not result.has_errors

    @pytest.mark.asyncio
    async def test_missing_latitude_adds_error(self, mock_weather_service, populated_context):
        populated_context.latitude = None
        agent = TemperatureAgent(mock_weather_service)
        result = await agent(populated_context)

        assert result.has_errors
        assert "latitude" in result.errors[0]
        mock_weather_service.get_forecast.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_longitude_adds_error(self, mock_weather_service, populated_context):
        populated_context.longitude = None
        agent = TemperatureAgent(mock_weather_service)
        result = await agent(populated_context)

        assert result.has_errors

    @pytest.mark.asyncio
    async def test_missing_datetime_adds_error(self, mock_weather_service, populated_context):
        populated_context.target_datetime = None
        agent = TemperatureAgent(mock_weather_service)
        result = await agent(populated_context)

        assert result.has_errors

    @pytest.mark.asyncio
    async def test_service_error_adds_error(self, populated_context):
        failing_service = AsyncMock()
        failing_service.get_forecast = AsyncMock(side_effect=RuntimeError("API down"))
        agent = TemperatureAgent(failing_service)
        result = await agent(populated_context)

        assert result.has_errors
        assert "API down" in result.errors[0]

    @pytest.mark.asyncio
    async def test_agent_name(self, mock_weather_service):
        agent = TemperatureAgent(mock_weather_service)
        assert agent.name == "TemperatureAgent"

    @pytest.mark.asyncio
    async def test_calls_service_with_correct_args(
        self, mock_weather_service, populated_context, april_5_5pm
    ):
        agent = TemperatureAgent(mock_weather_service)
        await agent(populated_context)

        mock_weather_service.get_forecast.assert_called_once_with(
            latitude=40.7128,
            longitude=-74.0060,
            target_time=april_5_5pm,
        )
