# PLRE (Prompt Leakage Risk Estimator)

**ML-powered security testing framework for LLM applications**

## Overview

PLRE uses machine learning to automatically generate adaptive attacks and detect prompt leaks in Large Language Model responses. Unlike static testing tools, PLRE learns from successful attacks and evolves its strategies over time.

## Features

- 🤖 **ML Attack Generation**: Generates infinite attack variants using templates and genetic algorithms
- 🧠 **ML Leak Detection**: Trained classifier detects leaks in LLM responses  
- 🔄 **Adaptive Learning**: Evolves successful attacks across iterations
- 📊 **Interactive Dashboard**: Visualize results with Streamlit
- 🎯 **8 Attack Types**: Injection, jailbreak, role confusion, encoding bypass, and more
- �� **Multi-Provider**: Supports Ollama, Gemini, Claude

## Quick Start

### 1. Installation

```bash
git clone https://github.com/EDI-Projects/Prompt-Leakage-Risk-Estimator.git
cd Prompt-Leakage-Risk-Estimator
poetry install
```

### 2. Train ML Detector (One-time)

```bash
poetry run python train_ml_model.py
```

This trains the leak detection model (~95% accuracy on synthetic data).

### 3. Run Attacks

```bash
# Test with Ollama (default)
poetry run python run_attack_test.py

# Test with Gemini
poetry run python run_attack_test.py --provider gemini

# More iterations for better learning
poetry run python run_attack_test.py --iterations 5
```

### 4. View Results

```bash
poetry run streamlit run plre/reporting/dashboard.py
```

## How It Works

### ML Attack Generation

The attack generator uses:
- **Templates**: 8 attack type templates with variable placeholders
- **Genetic Evolution**: Mutates successful attacks to create variants  
- **Adaptive Campaigns**: Learns which patterns work and generates more

Attack types:
- Prompt Injection
- Jailbreak
- Role Confusion
- Context Manipulation
- Encoding Bypass
- Multi-Turn Attacks
- Chain-of-Thought Exploitation
- Context Poisoning

### ML Leak Detection

The detector uses:
- **TF-IDF Vectorization**: Converts text to numerical features
- **Random Forest Classifier**: Trained on 1000+ synthetic examples
- **Confidence Scoring**: Returns probability of leak detection

## Architecture

```
run_attack_test.py
    ↓
AttackOrchestrator
    ↓
MLAttackOrchestrator
    ↓
AttackPromptGenerator → LLM → MLDetector → Results
MLAttackEvolver
```

## Advanced Usage

### Custom Attack Campaign

```bash
# Run specific attack types
poetry run python run_ml_attacks.py --types prompt_injection jailbreak

# Enable evolution
poetry run python run_ml_attacks.py --evolve --iterations 10

# Run adaptive campaign
poetry run python run_ml_attacks.py --adaptive
```

### Retrain Detector

```bash
# Train with more samples
poetry run python train_ml_model.py --samples 5000

# Use different model
poetry run python train_ml_model.py --model logistic_regression
```

## Documentation

- [ML Attack Generation Guide](RUN_WITH_ML_ATTACKS.md)
- [ML Detection Implementation](ML_IMPLEMENTATION.md)

## License

See [LICENSE](LICENCE) file.
