"""
Time Agent — parses the requested date and time into a datetime object.
Depends on DatetimeServiceProtocol (injected).
"""

from __future__ import annotations

import logging

from agents.base_agent import AgentContext, BaseAgent
from services.datetime_service import DatetimeService, DatetimeServiceProtocol

logger = logging.getLogger(__name__)


class TimeAgent(BaseAgent):
    """
    Enriches AgentContext with a resolved target_datetime from date_str and time_str.
    """

    def __init__(self, datetime_service: DatetimeServiceProtocol | None = None) -> None:
        self._service: DatetimeServiceProtocol = datetime_service or DatetimeService()

    @property
    def name(self) -> str:
        return "TimeAgent"

    async def process(self, context: AgentContext) -> AgentContext:
        if not context.date_str:
            context.add_error("TimeAgent: 'date_str' not set in context.")
            return context

        try:
            context.target_datetime = self._service.parse(
                context.date_str, context.time_str
            )
            logger.info("Resolved target datetime: %s", context.target_datetime.isoformat())
        except Exception as exc:
            context.add_error(f"TimeAgent error: {exc}")

        return context
