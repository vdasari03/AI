class AlertEngine:
    def __init__(self, repo, execution_engine=None):
        self.repo = repo
        from execution_engine import ExecutionEngine

        self.execution = execution_engine or ExecutionEngine()

    def generate_recommendations(self, signals, execute=False):
        recs = []
        executions = []
        for s in signals:
            score = s.get("sentiment_score", 0)
            # thresholded decision
            if score >= 1.0:
                action = "BUY"
            elif score <= -1.0:
                action = "SELL"
            else:
                action = "HOLD"

            stock = self.repo.get(s["symbol"]) or {}
            price = stock.get("price", 100.0)
            size = self._mock_size(price, score)

            rec = {
                "symbol": s["symbol"],
                "company": s.get("company"),
                "action": action,
                "score": round(score, 4),
                "confidence": round(s.get("confidence", 0.0), 4),
                "size": size,
                "evidence": s.get("evidence", []),
                "timestamps": s.get("timestamps", []),
            }

            if execute and action in ("BUY", "SELL") and size > 0:
                exec_rec = self.execution.place_order(s["symbol"], action, size, price)
                rec["execution"] = exec_rec
                executions.append(exec_rec)

            recs.append(rec)

        return {"recommendations": recs, "executions": executions, "meta": {"generated_by": "LLM-adapter", "version": "0.2"}}

    def _mock_size(self, price, score):
        base = 1000
        multiplier = min(5, max(0, abs(score)))
        dollars = base * multiplier
        qty = int(dollars / max(1, price))
        return qty
