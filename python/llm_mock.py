from typing import List, Dict, Any
from datetime import datetime


class LLMMock:
    """Deterministic LLM mock: extracts symbols and scores text with keyword matching.

    Returns a list of dicts containing: symbol, company, sentiment_score, confidence, evidence, timestamp
    """

    def __init__(self, repo) -> None:
        self.symbols = set(repo.list_symbols())
        # map symbols to company names for basic entity linking
        self.name_map = {s: (repo.get(s) or {}).get("name", "") for s in self.symbols}

    def analyze_text(self, text: str) -> List[Dict[str, Any]]:
        text_lower = text.lower()
        found: List[Dict[str, Any]] = []
        pos_words = ["buy", "bullish", "long", "beats", "strong", "positive"]
        neg_words = ["sell", "bearish", "short", "weak", "trouble", "regulatory", "miss"]
        for sym in self.symbols:
            if sym.lower() in text_lower:
                score = 0
                for w in pos_words:
                    if w in text_lower:
                        score += 1
                for w in neg_words:
                    if w in text_lower:
                        score -= 1
                # add confidence and entity-linked name and timestamp
                confidence = min(1.0, 0.5 + abs(score) * 0.15)
                found.append({
                    "symbol": sym,
                    "company": self.name_map.get(sym, ""),
                    "sentiment_score": float(score),
                    "confidence": confidence,
                    "evidence": text,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
        return found
