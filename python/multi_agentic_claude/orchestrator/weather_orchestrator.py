"""
Weather Orchestrator — coordinates the multi-agent pipeline using Semantic Kernel.

Flow:
  1. SK LLM extracts (city, date_str, time_str) from natural language query
  2. GeolocationAgent resolves city → coordinates
  3. TimeAgent parses date/time → datetime
  4. TemperatureAgent fetches forecast
  5. SK LLM generates final natural language answer
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_prompt_execution_settings import (
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory

from agents.base_agent import AgentContext
from agents.geolocation_agent import GeolocationAgent
from agents.temperature_agent import TemperatureAgent
from agents.time_agent import TimeAgent
from config.settings import Settings, settings as default_settings
from services.geocoding_service import GeocodingServiceProtocol
from services.datetime_service import DatetimeServiceProtocol
from services.weather_service import WeatherServiceProtocol

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    raw_query: str
    city: str
    date_str: str
    time_str: str
    latitude: float
    longitude: float
    temperature_celsius: float
    temperature_fahrenheit: float
    weather_description: str
    timezone: str
    natural_language_answer: str
    errors: list[str]

    @property
    def success(self) -> bool:
        return not self.errors


EXTRACTION_PROMPT = """
You are a query parser. Extract the city, date, and time from the user query.
Return ONLY a JSON object with keys: "city", "date_str", "time_str".
If time is not specified, use "time_str": null.

Examples:
Query: "What will be the temperature in New York on 5th February 5 pm"
Output: {"city": "New York", "date_str": "5th February", "time_str": "5 pm"}

Query: "Temperature in London tomorrow morning"
Output: {"city": "London", "date_str": "tomorrow", "time_str": "morning"}

Query: "Will it be cold in Tokyo on December 25?"
Output: {"city": "Tokyo", "date_str": "December 25", "time_str": null}
"""

ANSWER_PROMPT = """
You are a weather assistant. Given the following weather data, provide a concise, 
friendly, natural language answer to the user's query.

User query: {query}
City: {city}
Target time: {datetime}
Temperature: {celsius}°C ({fahrenheit}°F)
Conditions: {description}
Timezone: {timezone}

Provide a 2-3 sentence friendly response.
"""


class WeatherOrchestrator:
    """
    Orchestrates the multi-agent pipeline for weather queries.
    Uses Semantic Kernel for NLU (query parsing) and response generation.
    Agents handle the domain logic in a clean pipeline.
    """

    def __init__(
        self,
        app_settings: Settings | None = None,
        geocoding_service: GeocodingServiceProtocol | None = None,
        datetime_service: DatetimeServiceProtocol | None = None,
        weather_service: WeatherServiceProtocol | None = None,
    ) -> None:
        self._settings = app_settings or default_settings
        self._geo_agent = GeolocationAgent(geocoding_service)
        self._time_agent = TimeAgent(datetime_service)
        self._temp_agent = TemperatureAgent(weather_service)
        self._kernel = self._build_kernel()

    def _build_kernel(self) -> sk.Kernel:
        kernel = sk.Kernel()
        kernel.add_service(
            OpenAIChatCompletion(
                service_id="chat",
                ai_model_id=self._settings.openai_model,
                api_key=self._settings.openai_api_key,
            )
        )
        return kernel

    async def _extract_query_parts(self, query: str) -> dict:
        """Use SK + LLM to extract city, date, time from natural language query."""
        chat_service = self._kernel.get_service("chat")
        settings = OpenAIChatPromptExecutionSettings(temperature=0.0, max_tokens=200)

        history = ChatHistory()
        history.add_system_message(EXTRACTION_PROMPT)
        history.add_user_message(f"Query: {query}")

        response = await chat_service.get_chat_message_content(
            chat_history=history,
            settings=settings,
            kernel=self._kernel,
        )

        raw = str(response).strip()
        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("LLM returned non-JSON: %s", raw)
            # Fallback: return empty dict; caller handles missing fields
            return {}

    async def _generate_answer(self, context: AgentContext) -> str:
        """Use SK + LLM to generate a natural language response."""
        chat_service = self._kernel.get_service("chat")
        exec_settings = OpenAIChatPromptExecutionSettings(temperature=0.7, max_tokens=200)

        dt_str = (
            context.target_datetime.strftime("%A, %B %-d, %Y at %-I:%M %p")
            if context.target_datetime
            else "unknown time"
        )

        prompt = ANSWER_PROMPT.format(
            query=context.raw_query,
            city=context.city,
            datetime=dt_str,
            celsius=f"{context.temperature_celsius:.1f}",
            fahrenheit=f"{context.temperature_fahrenheit:.1f}",
            description=context.weather_description,
            timezone=context.timezone,
        )

        history = ChatHistory()
        history.add_user_message(prompt)

        response = await chat_service.get_chat_message_content(
            chat_history=history,
            settings=exec_settings,
            kernel=self._kernel,
        )
        return str(response).strip()

    async def run(self, query: str) -> QueryResult:
        """
        Execute the full multi-agent pipeline for a weather query.

        Args:
            query: Natural language query (e.g. "What's the temp in NY on April 5 at 5 pm?")

        Returns:
            QueryResult with all resolved data and natural language answer.
        """
        logger.info("Orchestrator received query: %s", query)

        # Step 1: Extract structured intent from NL query via SK/LLM
        parts = await self._extract_query_parts(query)
        city = parts.get("city", "")
        date_str = parts.get("date_str", "")
        time_str = parts.get("time_str")

        # Step 2: Build shared context and run agent pipeline
        context = AgentContext(
            raw_query=query,
            city=city,
            date_str=date_str,
            time_str=time_str,
        )

        # Agent pipeline (sequential — each enriches context)
        context = await self._geo_agent(context)
        context = await self._time_agent(context)
        context = await self._temp_agent(context)

        if context.has_errors:
            return QueryResult(
                raw_query=query,
                city=city,
                date_str=date_str,
                time_str=time_str or "",
                latitude=context.latitude or 0.0,
                longitude=context.longitude or 0.0,
                temperature_celsius=0.0,
                temperature_fahrenheit=0.0,
                weather_description="",
                timezone="",
                natural_language_answer="",
                errors=context.errors,
            )

        # Step 3: Generate NL answer via SK/LLM
        answer = await self._generate_answer(context)

        return QueryResult(
            raw_query=query,
            city=context.city or "",
            date_str=date_str,
            time_str=time_str or "",
            latitude=context.latitude,
            longitude=context.longitude,
            temperature_celsius=context.temperature_celsius,
            temperature_fahrenheit=context.temperature_fahrenheit,
            weather_description=context.weather_description,
            timezone=context.timezone,
            natural_language_answer=answer,
            errors=[],
        )
