# Multi-Agent Weather Query System
## Built with Semantic Kernel (Python)

### Architecture
```
multi_agent_sk/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Abstract base agent
│   ├── geolocation_agent.py   # Resolves city → lat/lon
│   ├── temperature_agent.py   # Fetches weather forecast
│   └── time_agent.py          # Parses/validates datetime
├── plugins/
│   ├── __init__.py
│   ├── geolocation_plugin.py  # SK plugin for geolocation
│   ├── temperature_plugin.py  # SK plugin for temperature
│   └── time_plugin.py         # SK plugin for time
├── services/
│   ├── __init__.py
│   ├── geocoding_service.py   # External geocoding API wrapper
│   ├── weather_service.py     # External weather API wrapper
│   └── datetime_service.py    # Datetime utilities
├── orchestrator/
│   ├── __init__.py
│   └── weather_orchestrator.py # Multi-agent orchestration
├── config/
│   ├── __init__.py
│   └── settings.py            # Environment-based config
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agents.py
│   ├── test_plugins.py
│   ├── test_services.py
│   └── test_orchestrator.py
├── main.py                    # Entry point
├── requirements.txt
└── .env.example
```

### Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
python main.py
```

### Run Tests
```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Design Principles
- **SOLID**: Each agent/service has a single responsibility
- **Dependency Injection**: Services injected via constructors
- **Interface Segregation**: Abstract base agent defines contract
- **Open/Closed**: New agents can be added without modifying orchestrator
- **Testability**: All external I/O mocked; pure unit tests
