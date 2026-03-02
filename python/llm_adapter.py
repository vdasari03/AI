import os
from datetime import datetime

try:
    from llm_mock import LLMMock
except Exception:
    LLMMock = None


class LLMAdapter:
    """Adapter that selects between the mock LLM and a real provider if configured.

    By default uses the deterministic `LLMMock`. If `OPENAI_API_KEY` is set and
    the `openai` package is installed, this adapter will attempt to call OpenAI's
    completion API (simple example). This is optional and guarded so tests stay
    deterministic.
    """

    def __init__(self, repo, mode=None):
        self.repo = repo
        self.mode = mode or os.getenv("LLM_MODE", "mock")
        if self.mode == "mock":
            if LLMMock is None:
                raise RuntimeError("LLMMock not available")
            self.impl = LLMMock(repo)
        elif self.mode == "openai":
            try:
                import openai
            except Exception:
                raise RuntimeError("openai package required for openai mode")
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError("OPENAI_API_KEY not set")
            openai.api_key = key
            self.impl = _OpenAIWrapper(openai, repo)
        else:
            raise ValueError(f"Unknown LLM mode: {self.mode}")

    def analyze_text(self, text):
        # normalize output of underlying impl to standard schema
        out = self.impl.analyze_text(text)
        # attach timestamp if missing
        for item in out:
            if "timestamp" not in item:
                item["timestamp"] = datetime.utcnow().isoformat() + "Z"
            if "confidence" not in item:
                # default confidence mapped from sentiment_score
                score = item.get("sentiment_score", 0)
                item["confidence"] = min(1.0, 0.5 + abs(score) * 0.15)
        return out


class _OpenAIWrapper:
    def __init__(self, openai, repo):
        self.openai = openai
        self.symbols = set(repo.list_symbols())

    def analyze_text(self, text):
        # Minimal example: send prompt and expect structured JSON back.
        prompt = f"Extract stock symbols and sentiment from the text:\n{text}\n\nRespond as JSON list with fields symbol, sentiment_score, evidence."
        resp = self.openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=150)
        # For safety, we do not rely on parsing complex outputs here in the prototype.
        # Attempt a rudimentary parse if the model returned JSON.
        raw = resp.choices[0].text
        try:
            import json

            data = json.loads(raw)
            return data
        except Exception:
            # Fallback: simple symbol search
            found = []
            text_lower = text.lower()
            for s in self.symbols:
                if s.lower() in text_lower:
                    found.append({"symbol": s, "sentiment_score": 0, "evidence": text})
            return found
