# PLRE (Prompt Leakage Risk Estimator)

## Goal
Automated tester for LLM apps that detects and scores prompt leakage risks.

## Features
- Attack library (prompt injection, multi-turn, multilingual).
- Leakage detectors (regex, PII, semantic judge).
- Scoring system (0-100).
- Reporting dashboards + CI/CD integration.

## Getting Started
```bash
git clone <repo>
cd plre
pip install -r requirements.txt
pytest
