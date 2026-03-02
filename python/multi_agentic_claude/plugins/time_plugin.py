"""
Semantic Kernel Plugin — Time.
Wraps TimeAgent as an SK-native kernel function.
"""

from __future__ import annotations

import json
import logging

from semantic_kernel.functions import kernel_function

from agents.time_agent import TimeAgent
from agents.base_agent import AgentContext
from services.datetime_service import DatetimeServiceProtocol

logger = logging.getLogger(__name__)


class TimePlugin:
    """SK plugin exposing datetime parsing as a kernel function."""

    def __init__(self, datetime_service: DatetimeServiceProtocol | None = None) -> None:
        self._agent = TimeAgent(datetime_service)

    @kernel_function(
        name="parse_datetime",
        description="Parses a date and optional time string into an ISO datetime.",
    )
    async def parse_datetime(self, date_str: str, time_str: str = "") -> str:
        """
        Parse a date and optional time into an ISO format datetime.

        Args:
            date_str: Date expression (e.g. '5th April', '2025-04-05')
            time_str: Optional time (e.g. '5 pm', '17:00')

        Returns:
            JSON with iso_datetime and human_readable strings.
        """
        from services.datetime_service import DatetimeService

        context = AgentContext(
            raw_query=f"{date_str} {time_str}",
            date_str=date_str,
            time_str=time_str or None,
        )
        context = await self._agent(context)

        if context.has_errors:
            return json.dumps({"error": context.errors})

        svc = DatetimeService()
        return json.dumps({
            "iso_datetime": context.target_datetime.isoformat(),
            "human_readable": svc.format_for_display(context.target_datetime),
        })
