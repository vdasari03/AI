# Car Damage Assessment & Insurance Claiming Application

An intelligent image-driven cost estimation and insurance claiming system that leverages LLM technology to assess vehicle damage, estimate repair costs, and process insurance claims automatically.

## 🎯 Features

- **Image Processing**: Validates and processes car damage images with support for multiple formats
- **LLM-Based Analysis**: Integrates with OpenAI GPT-4 Vision and Anthropic Claude for intelligent damage detection
- **Cost Estimation**: Calculates repair costs based on damage severity, labor rates, and materials
- **Insurance Claim Processing**: Automatically generates insurance claims with payout estimates
- **Modular Architecture**: Fully decoupled, scalable, and testable components
- **JSON Output**: Structured JSON results for easy integration
- **Mock LLM Provider**: Built-in mock provider for testing without API keys
- **Comprehensive Testing**: Unit tests, integration tests, and test automation

## 📋 Project Structure

```
car_denting_repair_charges/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── app.py                   # Main application orchestrator
│   ├── models.py                # Data models (Pydantic)
│   ├── image_processor.py       # Image loading and validation
│   ├── llm_integration.py       # LLM providers and analyzers
│   ├── cost_estimator.py        # Cost calculation logic
│   ├── insurance_claimer.py     # Insurance claim processing
│   ├── formatters.py            # JSON output formatting
│   └── logger.py                # Logging configuration
├── tests/
│   ├── conftest.py              # Pytest configuration
│   ├── mocks/
│   │   ├── responses.py         # Mock LLM responses
│   │   └── utils.py             # Mock utilities
│   ├── fixtures/
│   │   └── images/              # Test images (5 samples)
│   ├── test_image_processor.py  # Image processor tests
│   ├── test_llm_integration.py  # LLM integration tests
│   ├── test_cost_estimator.py   # Cost estimator tests
│   ├── test_insurance_claimer.py # Insurance claimer tests
│   └── test_integration.py      # Integration tests
├── config/
│   └── settings.py              # Configuration settings
├── main.py                      # Entry point
├── generate_test_images.py      # Test image generator
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── pytest.ini                   # Pytest configuration
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. **Clone the repository** (or navigate to the project directory)

```bash
cd car_denting_repair_charges
```

2. **Create a virtual environment**

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n car-damage-assessment python=3.10
conda activate car-damage-assessment
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Generate test images**

```bash
python generate_test_images.py
```

5. **Setup environment variables**

```bash
cp .env.example .env
# Edit .env with your API keys (optional for mock mode)
```

## 💻 Usage

### Command Line Interface

```bash
# Assess single image
python main.py tests/fixtures/images/car_damage_1.jpg

# Assess multiple images
python main.py tests/fixtures/images/car_damage_*.jpg

# Save to output file
python main.py tests/fixtures/images/car_damage_*.jpg -o results.json

# Pretty print results
python main.py tests/fixtures/images/car_damage_1.jpg --pretty

# Enable verbose logging
python main.py tests/fixtures/images/car_damage_1.jpg -v
```

### Python API

```python
from src.app import CarDamageAssessmentApp
from src.formatters import JSONFormatter

# Initialize application (using mock LLM)
app = CarDamageAssessmentApp(use_mock_llm=True)

# Assess single image
result = app.assess_damage("path/to/car_image.jpg")

# Assess multiple images
results = app.assess_multiple([
    "path/to/image1.jpg",
    "path/to/image2.jpg",
])

# Format and save results
JSONFormatter.save_to_file(results, "assessment_results.json")

# Print results
print(JSONFormatter.print_result(result, pretty=True))
```

## 📊 Output Format

The application outputs JSON results in the following structure:

```json
{
  "image_id": "car_damage_1",
  "image_path": "tests/fixtures/images/car_damage_1.jpg",
  "timestamp": "2024-01-15T10:30:00.000000",
  "damages": [
    {
      "location": "front_bumper",
      "severity": "moderate",
      "estimated_size_inches": 2.5,
      "description": "Moderate dent on front bumper with paint damage",
      "repair_type": "repairable",
      "repair_complexity": "medium"
    }
  ],
  "cost_estimate": {
    "labor_cost": 225.0,
    "materials_cost": 150.0,
    "paint_cost": 200.0,
    "total_estimated_cost": 575.0,
    "confidence_level": 0.85
  },
  "insurance_claim": {
    "claim_id": "A1B2C3D4",
    "claim_type": "damage",
    "is_covered": true,
    "deductible": 500.0,
    "coverage_percentage": 0.8,
    "estimated_payout": 60.0,
    "notes": "Claim not covered under policy | Damage locations: front_bumper | ..."
  },
  "summary": "Assessment identified 1 damage(s). Estimated repair cost: $575.00. Estimated insurance payout: $60.00. Claim status: Approved.",
  "metadata": {
    "size": [800, 600],
    "width": 800,
    "height": 600,
    "format": "JPEG",
    "mode": "RGB"
  }
}
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_*.py -v

# Integration tests
pytest tests/test_integration.py -v

# With coverage report
pytest --cov=src --cov-report=html
```

### Generate Sample Test Images

```bash
python generate_test_images.py
```

## 📝 Data Models

### DamageAssessment
- `location`: Location of damage
- `severity`: minor | moderate | severe
- `estimated_size_inches`: Size in inches
- `description`: Detailed description
- `repair_type`: repairable | replaceable | total_loss
- `repair_complexity`: simple | medium | complex | very_high

### CostEstimate
- `labor_cost`: Labor cost in USD
- `materials_cost`: Materials cost in USD
- `paint_cost`: Paint cost in USD
- `total_estimated_cost`: Total cost in USD
- `confidence_level`: Confidence score (0-1)

### InsuranceClaimDetails
- `claim_id`: Unique claim ID
- `claim_type`: damage | major_damage | total_loss
- `is_covered`: Coverage status
- `deductible`: Insurance deductible
- `coverage_percentage`: Coverage percentage
- `estimated_payout`: Insurance payout amount
- `notes`: Claim notes

## 🔌 Extensibility

### Add Custom LLM Provider

```python
from src.llm_integration import BaseLLMProvider

class CustomProvider(BaseLLMProvider):
    def analyze_image(self, image_path: str, prompt: str):
        # Implement your custom LLM integration
        pass

# Use it
provider = CustomProvider()
app = CarDamageAssessmentApp(llm_provider=provider)
```

### Customize Cost Estimation

```python
from src.cost_estimator import CostEstimator

estimator = CostEstimator(
    labor_rate=85,  # $85/hour
    paint_cost=250  # $250 per panel
)
```

### Custom Insurance Rules

```python
from src.insurance_claimer import InsuranceClaimer

claimer = InsuranceClaimer(
    deductible=1000,
    coverage_percentage=0.90
)
```

## 🔐 Configuration

Edit `.env` file for configuration:

```env
# LLM Configuration
USE_MOCK_LLM=True
LLM_MODEL=gpt-4-vision-preview
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Cost Estimation
REPAIR_LABOR_RATE=75
PAINT_COST_PER_PANEL=200

# Image Processing
MAX_IMAGE_SIZE=5242880
SUPPORTED_FORMATS=jpg,jpeg,png,gif
```

## 📚 API Documentation

### CarDamageAssessmentApp

#### Methods

- `assess_damage(image_path: str) -> CarDamageAssessmentResult`: Assess single image
- `assess_multiple(image_paths: List[str]) -> List[CarDamageAssessmentResult]`: Assess multiple images

### ImageProcessor

- `validate_image_path(path: str) -> bool`: Validate image
- `load_image(path: str) -> Image`: Load image
- `get_image_metadata(image) -> dict`: Get image metadata
- `resize_image(image, max_width) -> Image`: Resize image

### LLMAnalyzer

- `analyze(image_path: str) -> dict`: Analyze image with LLM

### CostEstimator

- `estimate(damages: List) -> CostEstimate`: Calculate costs

### InsuranceClaimer

- `process_claim(damages, cost_estimate) -> InsuranceClaimDetails`: Process claim

### JSONFormatter

- `format_result(result) -> dict`: Format single result
- `format_results(results) -> dict`: Format multiple results
- `save_to_file(results, path) -> bool`: Save to JSON
- `load_from_file(path) -> dict`: Load from JSON
- `print_result(result, pretty=True) -> str`: Print as JSON string

## 🧩 Architecture

The application follows a modular, decoupled architecture:

```
User Input
    ↓
main.py (Entry Point)
    ↓
CarDamageAssessmentApp
    ├── ImageProcessor (Image loading & validation)
    ├── LLMAnalyzer (Damage analysis)
    ├── CostEstimator (Cost calculation)
    ├── InsuranceClaimer (Claim processing)
    └── JSONFormatter (Output formatting)
    ↓
JSON Output
```

### Key Design Patterns

1. **Dependency Injection**: Components receive their dependencies
2. **Factory Pattern**: Mock vs Real LLM providers
3. **Data Models**: Pydantic for validation and serialization
4. **Strategy Pattern**: Different repair strategies based on damage type
5. **Single Responsibility**: Each module has one clear purpose

## 🧉 Testing Strategy

- **Unit Tests**: Test individual components with mocks
- **Integration Tests**: Test complete workflow
- **Mock Providers**: Mock LLM responses for testing without API calls
- **Test Fixtures**: Reusable test data and images
- **Coverage Reports**: Measure test coverage with pytest-cov

## 📈 Performance Considerations

- Image resizing to optimize processing
- Batch processing for multiple images
- Confidence scores for cost estimates
- Efficient JSON serialization

## 🤝 Contributing

1. Create a feature branch
2. Add tests for new functionality
3. Ensure all tests pass
4. Submit a pull request

## 📄 License

MIT License

## 🆘 Troubleshooting

### Issue: Import errors

```bash
# Ensure PYTHONPATH includes src
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Image not found

```bash
# Generate test images
python generate_test_images.py
```

### Issue: Tests failing

```bash
# Run with verbose output
pytest -vv --tb=long
```

## 📞 Support

For issues or questions, please create an issue in the repository.

## ✨ Future Enhancements

- [ ] Real-time video analysis
- [ ] Machine learning-based severity prediction
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Integration with insurance systems
- [ ] Blockchain for claim verification
- [ ] AR visualization of damage

---

**Version**: 1.0.0  
**Last Updated**: March 2026
