#!/usr/bin/env python
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from plre.models.llm_providers import LLMFactory, LLMCallback
from plre.attacks.orchestrator import AttackOrchestrator

MODEL_CONFIG = {
    'ollama': {'provider': 'ollama', 'model': 'llama2'},
    'gemini': {'provider': 'gemini', 'model': 'gemini-2.5-flash'}
}

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Run PLRE comprehensive attack test against LLM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  poetry run python run_attack_test.py                    # Use default provider (ollama)
  poetry run python run_attack_test.py --provider gemini  # Use Gemini
  poetry run python run_attack_test.py --provider ollama  # Use Ollama explicitly
        """
    )
    parser.add_argument(
        '--provider',
        type=str,
        default='ollama',
        choices=['ollama', 'gemini'],
        help='LLM provider to use (default: ollama)'
    )
    return parser.parse_args()

def convert_to_dashboard_format(report: dict, provider: str) -> dict:
    """Convert orchestrator output to dashboard-compatible format."""
    timestamp = datetime.now().isoformat()
    run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    attacks = []
    attack_id = 1
    total_leakage = 0
    total_attacks = 0
    successful_attacks = 0
    
    # Flatten scenario results into attacks array
    for scenario_name, scenario_data in report.get('scenario_results', {}).items():
        for attack_result in scenario_data.get('attack_results', []):
            total_attacks += 1
            if attack_result.get('success'):
                successful_attacks += 1
            
            leakage = attack_result.get('leakage_detected', [])
            total_leakage += len(leakage)
            
            attack_entry = {
                "attack_id": str(attack_id),
                "scenario": scenario_name,
                "name": attack_result.get('attack_name', 'Unknown'),
                "attack_type": attack_result.get('attack_type', 'unknown'),
                "prompt": attack_result.get('prompt', '')[:200],
                "response": attack_result.get('response', '')[:200],
                "leaked_canaries": leakage,
                "leak_type": "secret" if leakage else "none",
                "success": attack_result.get('success', False),
                "points": 10 if attack_result.get('success') else 0,
                "detected_by": [attack_result.get('attack_type', 'orchestrator')]
            }
            attacks.append(attack_entry)
            attack_id += 1
    aggregate_score = (successful_attacks / total_attacks * 100) if total_attacks > 0 else 0
    
    return {
        "run_id": run_id,
        "timestamp": timestamp,
        "model": report.get('model', MODEL_CONFIG[provider]['model']),
        "provider": provider,
        "aggregate_score": round(aggregate_score, 2),
        "total_attacks": total_attacks,
        "successful_attacks": successful_attacks,
        "total_leakage": total_leakage,
        "attacks": attacks,
        "summary": report.get('summary', {})
    }

# Create output directory
Path("reporting/artifacts").mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    args = parse_arguments()
    provider = args.provider
    
    try:
        if provider not in MODEL_CONFIG:
            print(f"✗ Invalid provider: {provider}")
            print(f"Available: {list(MODEL_CONFIG.keys())}")
            sys.exit(1)
        
        config = MODEL_CONFIG[provider]
        print(f"📡 Initializing {provider.upper()} provider...")
        print(f"   Model: {config['model']}")
        
        llm_provider = LLMFactory.create(config['provider'], model=config['model'])
        llm = LLMCallback(llm_provider, temperature=0.7, max_tokens=300)
        orchestrator = AttackOrchestrator()
        
        print(f"🎯 Running comprehensive attack test...")
        report = orchestrator.run_comprehensive_test(llm)
        report['model'] = config['model']
        report['provider'] = provider
        
        # Convert to dashboard format
        dashboard_format = convert_to_dashboard_format(report, provider)
        
        # Save in dashboard format
        output_file = f"reporting/artifacts/run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(dashboard_format, f, indent=2)
        
        print(f"✓ Report saved to {output_file}")
        print(f"✓ Attacks executed: {dashboard_format['total_attacks']}")
        print(f"✓ Successful attacks: {dashboard_format['successful_attacks']}")
        print(f"✓ Risk score: {dashboard_format['aggregate_score']:.1f}%")
        print(f"📊 Refresh dashboard at http://localhost:8501")
    except Exception as e:
        print(f"✗ Error: {e}")
        if provider == 'ollama':
            print("   Make sure Ollama is running: ollama serve")
        elif provider == 'gemini':
            print("   Make sure GOOGLE_API_KEY is set in .env")
        import traceback
        traceback.print_exc()
        sys.exit(1)

