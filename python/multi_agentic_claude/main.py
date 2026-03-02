"""
Entry point for the Multi-Agent Weather Query System.
Demonstrates the full pipeline with the sample query.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from config.settings import settings
from orchestrator.weather_orchestrator import WeatherOrchestrator

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

SAMPLE_QUERY = "What will be the temperature in New York on 5th February 5 pm"


async def main(query: str | None = None) -> None:
    query = query or SAMPLE_QUERY
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")

    try:
        settings.validate()
    except ValueError as exc:
        print(f"[CONFIG ERROR] {exc}")
        print("Please copy .env.example to .env and fill in your API keys.")
        sys.exit(1)

    orchestrator = WeatherOrchestrator()
    result = await orchestrator.run(query)

    if not result.success:
        print("[ERRORS]")
        for err in result.errors:
            print(f"  • {err}")
        sys.exit(1)

    print("📍 Location   :", result.city)
    print(f"🌐 Coordinates: {result.latitude:.4f}°N, {result.longitude:.4f}°W")
    print(f"🕔 Target Time: {result.date_str} {result.time_str} ({result.timezone})")
    print(f"🌡  Temperature: {result.temperature_celsius:.1f}°C / {result.temperature_fahrenheit:.1f}°F")
    print(f"⛅ Conditions : {result.weather_description}")
    print(f"\n💬 Answer:\n   {result.natural_language_answer}\n")


if __name__ == "__main__":
    user_query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    asyncio.run(main(user_query))
