import re

COMMAND_PATTERNS = [
    # buy|sell 100 AAPL at 150 or buy 100 AAPL market
    re.compile(r"\b(?P<action>buy|sell)\s+(?P<qty>\d+)\s+(?P<symbol>[A-Z]{1,5})(?:\s+at\s+(?P<price>\d+(?:\.\d+)?))?(?:\s+(?P<price_type>market|limit))?\b", re.I),
    # AAPL buy 100 market
    re.compile(r"\b(?P<symbol>[A-Z]{1,5})\s+(?P<action>buy|sell)\s+(?P<qty>\d+)(?:\s+at\s+(?P<price>\d+(?:\.\d+)?))?(?:\s+(?P<price_type>market|limit))?\b", re.I),
]


def detect_commands(text):
    """Detect explicit trading commands in free text.

    Returns a list of parsed commands with normalized fields:
      - action: BUY/SELL
      - symbol
      - qty (int)
      - price (float or None)
      - price_type: 'market'|'limit' or None
      - raw: original matched text
    """
    out = []
    for pat in COMMAND_PATTERNS:
        for m in pat.finditer(text):
            gd = m.groupdict()
            action = gd.get("action")
            if not action:
                continue
            symbol = gd.get("symbol")
            qty = int(gd.get("qty")) if gd.get("qty") else 0
            price = float(gd.get("price")) if gd.get("price") else None
            price_type = (gd.get("price_type") or ("market" if price is None else "limit"))
            out.append({
                "action": action.upper(),
                "symbol": symbol.upper(),
                "qty": qty,
                "price": price,
                "price_type": price_type,
                "raw": m.group(0),
            })
    return out


if __name__ == "__main__":
    samples = [
        "Buy 100 AAPL at 150",
        "TSLA sell 50 market",
        "Consider buying 20 GOOG",
    ]
    for s in samples:
        print(s, detect_commands(s))
