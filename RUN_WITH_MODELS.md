# Running PLRE with Real Models & Dashboard

## Supported Providers

PLRE supports 2 LLM providers:
- ✅ **Ollama** (local, free, open-source)
- ✅ **Gemini** (Google, requires API key)

## Prerequisites

### 1. Start Ollama (Local Models)
```bash
ollama serve

ollama pull llama2
# or try: mistral, neural-chat, llama-pro, etc.
```

### 2. Install Streamlit (for Dashboard)
```bash
poetry add streamlit
```

## Running Options

### Option A: Run Main Application

```bash
# Run comprehensive attack test with your configured provider
poetry run python run_attack_test.py
```

### Option B: CLI Commands

```bash
# Detect leakage in text
poetry run plre detect --text "My API key is sk-abc123xyz"

# Detect in file
poetry run plre detect --file response.txt --output findings.json

# Score detected findings
poetry run plre score --output risk_report.json

# View dashboard
poetry run streamlit run plre/reporting/dashboard.py
```

### Option C: Use Poetry with Python

```bash
poetry run python -c "
from plre.models.llm_providers import LLMFactory, LLMCallback
from plre.attacks.orchestrator import AttackOrchestrator

# Create Ollama provider
provider = LLMFactory.create('ollama', model='llama2')
llm = LLMCallback(provider, temperature=0.7, max_tokens=500)

# Run orchestrated test
orchestrator = AttackOrchestrator()
result = orchestrator.run_scenario('basic_injection', llm)
print(f'Risk Level: {result.overall_risk_level}')
"
```

### Option D: Interactive Dashboard

```bash
# Start dashboard server
poetry run streamlit run plre/reporting/dashboard.py

# Opens at http://localhost:8501
# Shows real attack results from JSON files saved to reporting/artifacts/
```

## Environment Configuration

Current `.env` setup:
```env
OLLAMA_BASE_URL="http://localhost:11434"
DEFAULT_MODEL=ollama
FALLBACK_MODEL=llama

GOOGLE_API_KEY="AIzaSy..."         # Optional: Gemini
```

## Full Workflow Example

### Using Ollama (Default)
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run comprehensive attack test (uses PROVIDER='ollama' by default)
poetry run python run_attack_test.py

# Terminal 3: View dashboard
poetry run streamlit run plre/reporting/dashboard.py
```

### Using Gemini (Google)
```bash
# 1. Set API key in .env:
# GOOGLE_API_KEY="AIzaSy..."

# 2. Edit run_attack_test.py, line 9:
# PROVIDER = 'gemini'

# 3. Run:
poetry run python run_attack_test.py
```

The script will:
1. ✅ Connect to your chosen provider (Ollama or Gemini)
2. ✅ Run 5 scenarios (basic_injection, leakage, integrity, resource_threats, comprehensive)
3. ✅ Execute 10 total attacks on the model
4. ✅ Save formatted results to `reporting/artifacts/`
5. ✅ Display results in the Streamlit dashboard


## Supported Models (via Ollama)

```bash
ollama pull llama2           # Meta's Llama 2 (7B-70B)
ollama pull mistral          # Mistral (7B)
ollama pull neural-chat      # Neural Chat (7B)
ollama pull llama-pro        # Llama Pro (8B)
ollama pull dolphin-mixtral  # Dolphin Mixtral (8x7B)
ollama pull orca-mini        # Orca Mini (3B)
```

## Troubleshooting

### Ollama Issues
**Ollama not running?**
```
Error: Cannot connect to http://localhost:11434
→ Start Ollama with: ollama serve
```

**Model not found?**
```
Error: Model 'llama2' not found
→ Pull it with: ollama pull llama2
```


### Gemini (Google) Issues
**API key not configured?**
```
Error: Google API key not configured
→ Set GOOGLE_API_KEY in .env file
→ Restart the script
```

### Model Issues
```
Error: Model not found or unavailable
→ For Ollama: Make sure model is downloaded with: ollama pull <model_name>
→ For Gemini: Check API quota and rate limits
```

**Memory issues?**
```
Use smaller models: neural-chat, orca-mini, or try mistral
Ollama will cache downloaded models in ~/.ollama/
```

**Want to use GPU?**
```
Ollama auto-detects CUDA/Metal. Check logs: ollama logs
```
