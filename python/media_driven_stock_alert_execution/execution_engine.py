from datetime import datetime


class ExecutionEngine:
    """Simulated execution engine that records a deterministic fill.

    This is a deterministic simulator to keep tests repeatable.
    """

    def __init__(self):
        self.ledger = []
        self._next_id = 1

    def place_order(self, symbol, action, qty, price):
        # deterministic small price slippage derived from symbol/action
        key = f"{symbol}:{action}"
        slippage = (sum(ord(c) for c in key) % 7) / 100.0  # 0.00 - 0.06
        if action == "SELL":
            fill_price = round(price * (1 - slippage), 2)
        else:
            fill_price = round(price * (1 + slippage), 2)

        record = {
            "id": self._next_id,
            "symbol": symbol,
            "action": action,
            "qty": int(qty),
            "requested_price": price,
            "filled_qty": int(qty),
            "avg_fill_price": fill_price,
            "status": "FILLED",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        self._next_id += 1
        self.ledger.append(record)
        return record

    def list_ledger(self):
        return list(self.ledger)
