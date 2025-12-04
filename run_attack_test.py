#!/usr/bin/env python
"""
Run ML-generated attacks against LLMs (simplified interface)
"""
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from plre.models.llm_providers import LLMFactory, LLMCallback
from plre.attacks.orchestrator import AttackOrchestrator

MODEL_CONFIG = {
    'ollama-tinyllama': {'provider': 'ollama', 'model': 'tinyllama'},
    'ollama-phi': {'provider': 'ollama', 'model': 'phi'},
    'ollama-phi3': {'provider': 'ollama', 'model': 'phi3'},
    'ollama-gemma': {'provider': 'ollama', 'model': 'gemma:2b'},
    'ollama-qwen': {'provider': 'ollama', 'model': 'qwen2.5:0.5b'},
    'ollama': {'provider': 'ollama', 'model': 'llama2:7b'},
    'gemini': {'provider': 'gemini', 'model': 'gemini-2.5-flash'},
}

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Run ML-generated attacks against LLM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  poetry run python run_attack_test.py                    # Use default (ollama)
  poetry run python run_attack_test.py --provider gemini  # Use Gemini
  poetry run python run_attack_test.py --iterations 5     # More iterations
        """
    )
    parser.add_argument(
        '--provider',
        type=str,
        default='ollama',
        choices=list(MODEL_CONFIG.keys()),
        help='LLM provider to use (default: ollama)'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=3,
        help='Number of adaptive iterations (default: 3)'
    )
    return parser.parse_args()

def convert_to_dashboard_format(report: dict, provider: str) -> dict:
    """Convert orchestrator output to dashboard format"""
    timestamp = datetime.now().isoformat()
    run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    attacks = []
    attack_id = 1
    total_leakage = 0
    total_attacks = 0
    successful_attacks = 0
    
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
                "points": attack_result.get('points', 0),
                "detected_by": ["ml-detector"]
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
        print(f"Initializing {config['provider']} with model: {config['model']}")
        
        llm_factory = LLMFactory()
        llm_instance = llm_factory.create_llm(
            provider=config['provider'],
            model_name=config['model']
        )
        
        llm_callback = LLMCallback(llm_instance)
        
        print("\n" + "="*70)
        print("ML-GENERATED ATTACK TEST")
        print("="*70)
        print(f"Provider: {provider}")
        print(f"Model: {config['model']}")
        print(f"Adaptive Iterations: {args.iterations}")
        print("="*70 + "\n")
        
        orchestrator = AttackOrchestrator(llm_callback)
        
        print("Running ML-generated attacks...")
        report = orchestrator.run_all_attacks(max_iterations=args.iterations)
        
        dashboard_data = convert_to_dashboard_format(report, provider)
        
        output_file = f"reporting/artifacts/run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_file}")
        print(f"\n{'='*70}")
        print("SUMMARY")
        print("="*70)
        print(f"Total Attacks: {dashboard_data['total_attacks']}")
        print(f"Successful: {dashboard_data['successful_attacks']}")
        print(f"Success Rate: {dashboard_data['aggregate_score']:.1f}%")
        print(f"Total Leakage: {dashboard_data['total_leakage']}")
        print("="*70)
        
        print("\nView results in dashboard:")
        print("  poetry run streamlit run plre/reporting/dashboard.py")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

