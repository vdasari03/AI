"""
Integration-style unit tests for WeatherOrchestrator.
The SK kernel and all external services are mocked.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.base_agent import AgentContext
from orchestrator.weather_orchestrator import WeatherOrchestrator, QueryResult
from services.geocoding_service import Coordinates
from services.weather_service import TemperatureForecast


MOCK_LLM_EXTRACTION = '{"city": "New York", "date_str": "5th April", "time_str": "5 pm"}'
MOCK_LLM_ANSWER = "On April 5th at 5 PM, New York will be partly cloudy at 15.5°C (59.9°F). Bring a light jacket!"


def make_mock_kernel(extraction_response: str, answer_response: str):
    """Build a mock SK kernel that returns preset LLM responses."""
    mock_response = MagicMock()
    mock_response.__str__ = MagicMock(side_effect=[extraction_response, answer_response])

    mock_chat_service = AsyncMock()
    mock_chat_service.get_chat_message_content = AsyncMock(return_value=mock_response)

    mock_kernel = MagicMock()
    mock_kernel.get_service = MagicMock(return_value=mock_chat_service)
    return mock_kernel


class TestWeatherOrchestrator:

    def _make_orchestrator(
        self,
        geocoding_service=None,
        datetime_service=None,
        weather_service=None,
        extraction=MOCK_LLM_EXTRACTION,
        answer=MOCK_LLM_ANSWER,
    ):
        """Helper to build orchestrator with mocked kernel and services."""
        mock_settings = MagicMock()
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4o"

        with patch(
            "orchestrator.weather_orchestrator.OpenAIChatCompletion",
            return_value=MagicMock(),
        ):
            orch = WeatherOrchestrator(
                app_settings=mock_settings,
                geocoding_service=geocoding_service,
                datetime_service=datetime_service,
                weather_service=weather_service,
            )

        orch._kernel = make_mock_kernel(extraction, answer)
        return orch

    @pytest.mark.asyncio
    async def test_run_returns_successful_result(
        self,
        mock_geocoding_service,
        mock_datetime_service,
        mock_weather_service,
    ):
        orch = self._make_orchestrator(
            geocoding_service=mock_geocoding_service,
            datetime_service=mock_datetime_service,
            weather_service=mock_weather_service,
        )

        result = await orch.run(
            "What will be the temperature in New York on 5th February 5 pm"
        )

        assert isinstance(result, QueryResult)
        assert result.success
        assert result.city == "New York"
        assert result.temperature_celsius == pytest.approx(15.5)
        assert result.temperature_fahrenheit == pytest.approx(59.9)
        assert result.natural_language_answer != ""

    @pytest.mark.asyncio
    async def test_run_propagates_geolocation_error(
        self,
        mock_datetime_service,
        mock_weather_service,
    ):
        failing_geo = AsyncMock()
        failing_geo.resolve = AsyncMock(side_effect=ValueError("City not found"))

        orch = self._make_orchestrator(
            geocoding_service=failing_geo,
            datetime_service=mock_datetime_service,
            weather_service=mock_weather_service,
        )

        result = await orch.run("What is the temp in ZZZ on 5th April 5 pm")
        assert not result.success
        assert result.errors

    @pytest.mark.asyncio
    async def test_run_propagates_weather_error(
        self,
        mock_geocoding_service,
        mock_datetime_service,
    ):
        failing_weather = AsyncMock()
        failing_weather.get_forecast = AsyncMock(side_effect=RuntimeError("API down"))

        orch = self._make_orchestrator(
            geocoding_service=mock_geocoding_service,
            datetime_service=mock_datetime_service,
            weather_service=failing_weather,
        )

        result = await orch.run("What is the temp in New York on 5th April 5 pm")
        assert not result.success

    @pytest.mark.asyncio
    async def test_run_handles_malformed_llm_extraction(
        self,
        mock_geocoding_service,
        mock_datetime_service,
        mock_weather_service,
    ):
        """If LLM returns non-JSON, orchestrator handles gracefully."""
        orch = self._make_orchestrator(
            geocoding_service=mock_geocoding_service,
            datetime_service=mock_datetime_service,
            weather_service=mock_weather_service,
            extraction="This is not JSON at all!",
        )

        # Should not raise — just results in empty city/date fallback
        result = await orch.run("garbage query")
        # city will be "" (empty from malformed JSON), causing agent errors
        assert isinstance(result, QueryResult)

    @pytest.mark.asyncio
    async def test_query_result_success_property(self):
        result = QueryResult(
            raw_query="q",
            city="NYC",
            date_str="April 5",
            time_str="5 pm",
            latitude=40.7,
            longitude=-74.0,
            temperature_celsius=15.0,
            temperature_fahrenheit=59.0,
            weather_description="Clear",
            timezone="UTC",
            natural_language_answer="Nice day!",
            errors=[],
        )
        assert result.success

        result_with_error = QueryResult(
            raw_query="q", city="", date_str="", time_str="",
            latitude=0, longitude=0, temperature_celsius=0,
            temperature_fahrenheit=0, weather_description="",
            timezone="", natural_language_answer="", errors=["something failed"],
        )
        assert not result_with_error.success
