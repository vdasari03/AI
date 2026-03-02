import json
from processor import Processor
from repo import StockRepository
from alert_engine import AlertEngine
from execution_engine import ExecutionEngine


def sample_texts():
    return [
        "Breaking: AAPL beats earnings, analysts bullish — buy now!",
        "Rumors of regulatory trouble hit TSLA; some say sell.",
        "GOOG launching new product; long-term positive.",
        "Weak guidance for AMZN, consider selling or hedge.",
        "NFLX strong subscriber growth, consider BUY."
    ]


def main():
    repo = StockRepository()
    texts = sample_texts()
    processor = Processor(repo)
    signals = processor.process_texts(texts)
    exec_engine = ExecutionEngine()
    engine = AlertEngine(repo, execution_engine=exec_engine)
    # pass execute=True to simulate placing orders
    recommendations = engine.generate_recommendations(signals, execute=True)
    print(json.dumps(recommendations, indent=2))


if __name__ == "__main__":
    main()
