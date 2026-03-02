from llm_adapter import LLMAdapter
from shell_integration import detect_commands


class Processor:
    def __init__(self, repo, llm_mode=None):
        self.repo = repo
        self.llm = LLMAdapter(repo, mode=llm_mode)

    def process_texts(self, texts):
        results = []
        for t in texts:
            # First, detect any explicit shell-style commands in the text.
            cmds = detect_commands(t)
            if cmds:
                # Convert commands to high-confidence signals
                for c in cmds:
                    results.append({
                        "symbol": c["symbol"],
                        "company": (self.repo.get(c["symbol"]) or {}).get("name"),
                        "sentiment_score": 2.0 if c["action"] == "BUY" else -2.0,
                        "confidence": 0.99,
                        "evidence": c.get("raw"),
                        "timestamps": [],
                    })
            else:
                res = self.llm.analyze_text(t)
                results.extend(res)

        # Aggregate sentiment per symbol with confidences and timestamps
        agg = {}
        for r in results:
            s = r["symbol"]
            if s not in agg:
                agg[s] = {
                    "symbol": s,
                    "company": r.get("company"),
                    "sentiment_score": 0.0,
                    "confidence": 0.0,
                    "evidence": [],
                    "timestamps": [],
                }
            agg[s]["sentiment_score"] += r.get("sentiment_score", 0.0) * r.get("confidence", 1.0)
            agg[s]["confidence"] = min(1.0, agg[s]["confidence"] + r.get("confidence", 0.0) * 0.5)
            agg[s]["evidence"].append(r.get("evidence"))
            if r.get("timestamp"):
                agg[s]["timestamps"].append(r.get("timestamp"))

        # Convert to list
        out = []
        for v in agg.values():
            out.append(v)
        return out
