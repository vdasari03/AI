# Media Driven Stock Alert Execution System

## Specs-Driven Development Philosophy

This project follows **Specifications-Driven Development (SDD)**, where the architecture and behavior are:

1. **Test-First**: Tests define expected behavior before implementation
2. **Deterministic**: Output is reproducible and testable without external dependencies
3. **Modular**: Each component has a single responsibility with clear interfaces
4. **Observable**: System behavior can be traced and verified through structured outputs

### Core Principles

- **Separation of Concerns**: Text processing, signal generation, and execution are independent layers
- **Mock-First**: Default behavior uses deterministic mocks (no external API calls unless enabled)
- **Composability**: Components can be combined flexibly (e.g., different LLM modes)
- **Testability**: All components have unit and end-to-end test coverage

---

## Architecture Overview

```
Text Input
    ↓
Processor (combines NLP + command detection)
    ├→ detect_commands() [shell_integration]
    └→ LLMAdapter.analyze_text() [llm_adapter]
    ↓
Signals (structured sentiment/action data)
    ↓
AlertEngine (generates recommendations)
    ↓
ExecutionEngine (places orders deterministically)
    ↓
JSON Output (recommendations + executions)
```

---

## File-by-File Documentation

### **main.py**
- **Purpose**: Entry point for the stock alert system
- **Responsibility**: Orchestrates the full pipeline from text input to JSON output
- **Key Functions**:
  - `sample_texts()`: Provides example market news for demo
  - `main()`: Instantiates all components and produces recommendations
- **Output**: JSON-formatted recommendations and execution records
- **Specs**: Must output valid JSON with `recommendations`, `executions`, and `meta` fields

---

### **shell_integration.py**
- **Purpose**: Parses explicit trading commands from free-form text
- **Responsibility**: Regex-based command detection for structured trading instructions
- **Key Functions**:
  - `detect_commands(text)`: Extracts BUY/SELL commands from text
- **Supported Formats**:
  - `"Buy 100 AAPL at 150"` → action: BUY, symbol: AAPL, qty: 100, price: 150.0
  - `"TSLA sell 50 market"` → action: SELL, symbol: TSLA, qty: 50, price_type: market
- **Output**: List of normalized command dicts with fields: `action`, `symbol`, `qty`, `price`, `price_type`, `raw`
- **Specs**:
  - Case-insensitive matching (BUY/buy both work)
  - Price is optional; `price_type` can be 'market' or 'limit' or None
  - Returns empty list if no commands found

---

### **processor.py**
- **Purpose**: Aggregates signals from multiple sources (explicit commands + NLP analysis)
- **Responsibility**: Combine shell commands and LLM sentiment analysis into unified signals
- **Key Classes**:
  - `Processor`: Coordinates text processing pipeline
- **Key Methods**:
  - `process_texts(texts)`: Takes list of text snippets, returns aggregated signals
- **Aggregation Logic**:
  - Explicit commands get confidence=0.99, sentiment_score=±2.0
  - LLM analysis provides sentiment_score with lower confidence
  - Multiple signals per symbol are aggregated (averaged scores, combined evidence)
- **Specs**:
  - Input: list of strings (news articles, social media posts, etc.)
  - Output: dict per symbol with aggregated sentiment, confidence, evidence, timestamps
  - Symbol lookup uses `StockRepository`

---

### **llm_adapter.py**
- **Purpose**: Abstraction layer for LLM sentiment analysis (mock or real)
- **Responsibility**: Select and execute either mock or real LLM backend
- **Key Classes**:
  - `LLMAdapter`: Main adapter that selects implementation based on `LLM_MODE`
  - `LLMMock`: Deterministic mock using keyword matching
  - `_OpenAIWrapper`: Optional OpenAI integration (requires `openai` package and `OPENAI_API_KEY`)
- **Key Methods**:
  - `analyze_text(text)`: Returns list of dicts with sentiment analysis results
- **LLM Modes**:
  - `mock` (default): Keyword heuristics, always consistent, no API calls
  - `openai`: Calls OpenAI completion API (optional, requires configuration)
- **Specs**:
  - Output: list of dicts with fields: `symbol`, `company`, `sentiment_score`, `confidence`, `evidence`, `timestamp`
  - Default confidence calculation: `min(1.0, 0.5 + abs(sentiment_score) * 0.33)`
  - Missing timestamps are auto-filled with ISO format UTC time

---

### **llm_mock.py**
- **Purpose**: Deterministic NLP mock for reproducible testing
- **Responsibility**: Keyword-based sentiment extraction without external dependencies
- **Key Classes**:
  - `LLMMock`: Scores text by presence of positive/negative keywords
- **Key Methods**:
  - `analyze_text(text)`: Extracts symbols and scores sentiment via keyword matching
- **Positive Keywords**: buy, bullish, long, beats, strong, positive
- **Negative Keywords**: sell, bearish, short, weak, trouble, regulatory, miss
- **Specs**:
  - Sentiment score ranges from -1.0 to +1.0
  - Only detects symbols already in the repository
  - Confidence = min(1.0, 0.5 + abs(score) * 0.33)
  - Always returns consistent results for same input

---

### **alert_engine.py**
- **Purpose**: Generates trading recommendations based on signals
- **Responsibility**: Transform signals into actionable recommendations with optional execution
- **Key Classes**:
  - `AlertEngine`: Main recommendation engine
- **Key Methods**:
  - `generate_recommendations(signals, execute=False)`: Converts signals to trading recommendations
  - `_mock_size(score, symbol)`: Deterministic quantity calculator
- **Recommendation Logic**:
  - Score ≥ 0.5 → BUY action
  - Score ≤ -0.5 → SELL action
  - -0.5 < Score < 0.5 → HOLD action
  - Quantity calculated from confidence and score: `min(max(1, abs(score) * multiplier), 1000) * qty_rounds`
- **Specs**:
  - Output: dict with `recommendations`, `executions`, and `meta` (version, timestamp)
  - When `execute=True`, calls `ExecutionEngine.place_order()` for BUY/SELL actions
  - Execution results appended to recommendations

---

### **execution_engine.py**
- **Purpose**: Simulates deterministic trade execution
- **Responsibility**: Record orders with realistic slippage simulation
- **Key Classes**:
  - `ExecutionEngine`: In-memory order ledger
- **Key Methods**:
  - `place_order(symbol, action, qty, price)`: Simulates order fill with slippage
  - `list_ledger()`: Returns all executed orders
- **Execution Specs**:
  - Slippage = (sum of ASCII ord values of symbol + " " + action) / (100 * 100)
  - For SELL: `fill_price = requested_price * (1 - slippage)`
  - For BUY: `fill_price = requested_price * (1 + slippage)`
  - Status always "FILLED" (deterministic simulator)
  - Each order gets unique ID, timestamp, requested price, and filled quantity
- **Specs**:
  - Deterministic slippage ensures reproducible test results
  - Output: dict with `id`, `symbol`, `action`, `qty`, `requested_price`, `filled_qty`, `avg_fill_price`, `status`, `timestamp`

---

### **repo.py**
- **Purpose**: Stock repository with symbol/price lookup
- **Responsibility**: Provide canonical stock data for symbol resolution
- **Key Classes**:
  - `StockRepository`: In-memory stock data store
- **Key Methods**:
  - `list_symbols()`: Returns all available symbols
  - `get(symbol)`: Returns dict with `name` and `price` for symbol, or None
- **Data**:
  - AAPL: Apple Inc., $540.00
  - TSLA: Tesla Inc., $240.00
  - GOOG: Alphabet Inc., $94.00
  - AMZN: Amazon.com Inc., $175.00
  - NFLX: Netflix Inc., $480.00
- **Specs**:
  - Case-sensitive symbol matching
  - Returns dict or None (no exceptions for missing symbols)

---

### **cli_detect.py**
- **Purpose**: Command-line interface for direct command detection
- **Responsibility**: Standalone tool to test shell command parsing
- **Entry Point**: Can be run directly to demonstrate `detect_commands()` functionality
- **Specs**: Reads trading commands from stdin/arguments and outputs parsed structure

---

### **shell_hook.ps1**
- **Purpose**: PowerShell integration hook for shell integration
- **Responsibility**: Enables shell history processing and command detection
- **Usage**: Source this hook in PowerShell profile to integrate with alert system
- **Specs**: Integrates with PowerShell command execution pipeline

---

### **requirements.txt**
- **Purpose**: Python dependency specification
- **Current Status**: No external dependencies (uses Python standard library only)
- **Optional Dependencies**: `openai` (only if using `LLM_MODE=openai`)
- **Specs**: Minimal footprint for simplicity and testability

---

## Testing Approach

### Unit Tests
- **test_shell_integration.py**: Tests command parsing with various text formats
- **test_e2e.py**: End-to-end integration test covering full pipeline

### Test Strategy (Specs-Driven)
1. **Deterministic Input/Output**: All tests use fixed inputs with expected outputs
2. **No External Dependencies**: Tests never call real APIs
3. **Reproducible**: Run tests thousands of times with identical results
4. **Coverage**: Each module tested independently and in integration

### Running Tests
```bash
pytest python/media_driven_stock_alert_execution/tests/ -v
```

---

## Usage Examples

### Basic Usage
```python
from main import main
main()  # Processes sample texts, outputs JSON
```

### Custom Text Processing
```python
from processor import Processor
from repo import StockRepository

repo = StockRepository()
processor = Processor(repo)
signals = processor.process_texts(["Buy 100 AAPL at 150"])
print(signals)
```

### Direct Command Detection
```python
from shell_integration import detect_commands

commands = detect_commands("TSLA sell 50 market order")
# [{'action': 'SELL', 'symbol': 'TSLA', 'qty': 50, 'price_type': 'market', ...}]
```

### Execution Simulation
```python
from execution_engine import ExecutionEngine

engine = ExecutionEngine()
order = engine.place_order("AAPL", "BUY", 100, 150.0)
ledger = engine.list_ledger()
```

---

## Configuration

### Environment Variables
- **LLM_MODE** (default: `mock`): Set to `openai` to use real OpenAI API
- **OPENAI_API_KEY**: Required if `LLM_MODE=openai`

### Data Files
None required. All data is in-memory (repo, execution ledger, etc.)

---

## Output Format

All recommendations follow this schema:
```json
{
  "recommendations": [
    {
      "symbol": "AAPL",
      "company": "Apple Inc.",
      "action": "BUY",
      "score": 0.75,
      "size": 25,
      "confidence": 0.90,
      "evidence": ["Buy 100 AAPL"],
      "timestamps": ["2026-03-03T12:34:56Z"]
    }
  ],
  "executions": [
    {
      "id": 1,
      "symbol": "AAPL",
      "action": "BUY",
      "qty": 25,
      "requested_price": 150.0,
      "filled_qty": 25,
      "avg_fill_price": 150.42,
      "status": "FILLED",
      "timestamp": "2026-03-03T12:34:56Z"
    }
  ],
  "meta": {
    "generated_by": "LLM-adapter",
    "version": "0.2"
  }
}
```

---

## Design Patterns Used

1. **Adapter Pattern** (`LLMAdapter`): Switches between mock and real implementations
2. **Strategy Pattern** (`Processor`): Combines multiple signal sources (commands + NLP)
3. **Repository Pattern** (`StockRepository`): Centralized data access
4. **Facade Pattern** (`AlertEngine`): Simplifies complex orchestration
5. **Deterministic Simulation** (`ExecutionEngine`): Reproducible order execution

---

## Future Extensions

- [ ] Real database (SQLite/PostgreSQL) for stock data
- [ ] Async execution for large-scale processing
- [ ] ML-based sentiment analysis replacing keyword matching
- [ ] WebSocket support for real-time price feeds
- [ ] Risk management constraints (max position size, daily loss limits)

---

## Contributing

When adding new features:
1. Write test specs first
2. Implement deterministic behavior
3. Document module purpose and specs
4. Update this README

---

**Last Updated**: March 3, 2026  
**Version**: 0.2
