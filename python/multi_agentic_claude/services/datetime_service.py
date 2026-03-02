"""
Datetime service — parses and validates natural language / structured date-time strings.
Single Responsibility: datetime resolution only.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Protocol

from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

# Common named times
NAMED_TIMES: dict[str, int] = {
    "midnight": 0,
    "noon": 12,
    "morning": 8,
    "afternoon": 14,
    "evening": 18,
    "night": 20,
}


class DatetimeServiceProtocol(Protocol):
    def parse(self, date_str: str, time_str: str | None = None) -> datetime: ...


class DatetimeService:
    """
    Parses flexible date/time expressions into datetime objects.
    Supports ISO format, natural language like '5th April 5 pm'.
    """

    def parse(self, date_str: str, time_str: str | None = None) -> datetime:
        """
        Parse date and optional time into a datetime.

        Args:
            date_str: Date expression (e.g. "5th April", "2025-04-05", "April 5")
            time_str: Optional time (e.g. "5 pm", "17:00", "noon")

        Returns:
            Resolved datetime object (current year assumed if not specified)
        """
        combined = f"{date_str} {time_str}" if time_str else date_str
        logger.info("Parsing datetime expression: '%s'", combined)

        try:
            dt = dateutil_parser.parse(combined, default=self._default_dt())
            logger.info("Parsed datetime: %s", dt.isoformat())
            return dt
        except (ValueError, OverflowError) as exc:
            raise ValueError(
                f"Unable to parse date/time expression: '{combined}'. Error: {exc}"
            ) from exc

    @staticmethod
    def _default_dt() -> datetime:
        """Default base: current date at midnight."""
        now = datetime.now()
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    def format_for_display(self, dt: datetime) -> str:
        return dt.strftime("%A, %B %-d, %Y at %-I:%M %p")
