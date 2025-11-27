# Setup Instructions

## Prerequisites
- Python 3.11+
- pip or Poetry
- Git

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/EDI-Projects/Prompt-Leakage-Risk-Estimator.git
cd Prompt-Leakage-Risk-Estimator
```

### 2. Install Dependencies

**Using Poetry (Recommended):**
```bash
pip install poetry
poetry install
poetry shell
```

**Using pip:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
poetry run pytest tests/ -v
```

## Configuration

### API Keys (Optional)
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIzaSy...
```

### Scorer Configuration
Edit `plre/scorer/config.yaml`:
```yaml
weights:
  api_key: 100
  password: 100
  database_url: 95
  aadhaar: 90
  pan: 90

defaults:
  no_leak: 0
  unknown_leak: 10

output_dir: ./output
```

## Running Tests
```bash
poetry run pytest tests/ -v

poetry run pytest tests/ --cov=plre --cov-report=html
```

## Development

Install development tools:
```bash
poetry install --with dev
```

Run code quality checks:
```bash
poetry run black plre tests
poetry run isort plre tests
poetry run flake8 plre tests
poetry run mypy plre
```

## Troubleshooting

### Module not found errors
```bash
source venv/bin/activate
poetry install --no-cache
```

### Python version mismatch
```bash
python --version  # Must be 3.11+
poetry env use python3.11
```

### API key errors
Create a `.env` file with your keys and load it in your script:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Docker (Optional)

```bash
docker build -t plre:latest .
docker run -it -e OPENAI_API_KEY=sk-... plre:latest poetry run plre demo
```
