"""
Shared pytest fixtures for the multi-agent weather system.
Uses dependency injection to replace all external I/O with mocks.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.base_agent import AgentContext
from services.geocoding_service import Coordinates
from services.weather_service import TemperatureForecast


# ─── Shared Data Fixtures ────────────────────────────────────────────────────

@pytest.fixture
def new_york_coords() -> Coordinates:
    return Coordinates(
        city="New York",
        latitude=40.7128,
        longitude=-74.0060,
        display_name="New York, NY, USA",
    )


@pytest.fixture
def april_5_5pm() -> datetime:
    return datetime(2025, 4, 5, 17, 0, 0)


@pytest.fixture
def sample_forecast(april_5_5pm) -> TemperatureForecast:
    return TemperatureForecast.from_celsius(
        latitude=40.7128,
        longitude=-74.0060,
        target_time=april_5_5pm,
        celsius=15.5,
        weather_description="Partly cloudy",
        timezone="America/New_York",
    )


# ─── Mock Services ─────────────────────────────────────────────────────────

@pytest.fixture
def mock_geocoding_service(new_york_coords):
    service = AsyncMock()
    service.resolve = AsyncMock(return_value=new_york_coords)
    return service


@pytest.fixture
def mock_weather_service(sample_forecast):
    service = AsyncMock()
    service.get_forecast = AsyncMock(return_value=sample_forecast)
    return service


@pytest.fixture
def mock_datetime_service(april_5_5pm):
    service = MagicMock()
    service.parse = MagicMock(return_value=april_5_5pm)
    return service


# ─── Context Fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def base_context() -> AgentContext:
    return AgentContext(
        raw_query="What will be the temperature in New York on 5th April 5 pm",
        city="New York",
        date_str="5th April",
        time_str="5 pm",
    )


@pytest.fixture
def populated_context(base_context, april_5_5pm) -> AgentContext:
    """Context already enriched by geo + time agents."""
    ctx = base_context
    ctx.latitude = 40.7128
    ctx.longitude = -74.0060
    ctx.target_datetime = april_5_5pm
    return ctx
