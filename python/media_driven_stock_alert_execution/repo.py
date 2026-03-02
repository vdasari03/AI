from typing import Dict, Optional


class StockRepository:
    """In-memory stock repository used for tests and prototyping."""

    def __init__(self) -> None:
        # sample in-memory repository of stocks
        self.stocks: Dict[str, Dict[str, float]] = {
            "AAPL": {"name": "Apple Inc.", "price": 150.0},
            "TSLA": {"name": "Tesla Inc.", "price": 200.0},
            "GOOG": {"name": "Alphabet Inc.", "price": 120.0},
            "AMZN": {"name": "Amazon.com Inc.", "price": 90.0},
            "NFLX": {"name": "Netflix Inc.", "price": 350.0},
        }

    def list_symbols(self) -> list[str]:
        return list(self.stocks.keys())

    def get(self, symbol: str) -> Optional[Dict[str, float]]:
        return self.stocks.get(symbol)
