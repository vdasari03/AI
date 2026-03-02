"""
Abstract base agent — defines the contract all agents must fulfill.
Follows Interface Segregation and Open/Closed principles.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Shared context passed between agents in the pipeline."""
    raw_query: str
    city: str | None = None
    date_str: str | None = None
    time_str: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    target_datetime: Any = None  # datetime
    temperature_celsius: float | None = None
    temperature_fahrenheit: float | None = None
    weather_description: str | None = None
    timezone: str | None = None
    errors: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []

    def add_error(self, msg: str) -> None:
        logger.error("AgentContext error: %s", msg)
        self.errors.append(msg)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


class BaseAgent(ABC):
    """
    Abstract base for all agents.
    Each agent processes the shared AgentContext and enriches it.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent name."""

    @abstractmethod
    async def process(self, context: AgentContext) -> AgentContext:
        """
        Process the context and return enriched context.

        Args:
            context: Shared agent context

        Returns:
            Enriched AgentContext
        """

    async def __call__(self, context: AgentContext) -> AgentContext:
        logger.info("[%s] Starting", self.name)
        result = await self.process(context)
        logger.info("[%s] Completed", self.name)
        return result
