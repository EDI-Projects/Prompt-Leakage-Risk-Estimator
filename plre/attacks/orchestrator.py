"""
ML-powered attack orchestrator (simplified interface for compatibility)
"""
from typing import List, Dict, Callable
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from plre.ml_models.ml_attack_orchestrator import MLAttackOrchestrator as MLOrch
from plre.attacks.attack_result import AttackResult

class AttackOrchestrator:
    """
    Compatibility wrapper for ML attack orchestrator
    Provides same interface as old hardcoded version
    """
    
    def __init__(self, llm_callback: Callable[[str], str]):
        self.ml_orchestrator = MLOrch(llm_callback)
        self.llm = llm_callback
    
    def run_all_attacks(
        self,
        attack_types: List[str] = None,
        max_iterations: int = 3
    ) -> Dict:
        """
        Run all attacks using ML generation
        
        Args:
            attack_types: List of attack types (uses all if None)
            max_iterations: Number of adaptive iterations
            
        Returns:
            Results in compatible format
        """
        if attack_types is None:
            attack_types = [
                "prompt_injection",
                "jailbreak", 
                "role_confusion",
                "context_manipulation",
                "encoding_bypass",
                "multi_turn",
                "cot_exploitation",
                "context_poisoning"
            ]
        campaign = self.ml_orchestrator.run_adaptive_campaign(
            attack_types=attack_types,
            max_iterations=max_iterations,
            success_threshold=0.1
        )
        
        results = {
            "scenario_results": {},
            "model": "ML-Generated Attacks",
            "summary": {
                "total_attacks": campaign["total_attacks"],
                "successful_attacks": campaign["successful_attacks"],
                "success_rate": campaign["final_success_rate"],
                "iterations": campaign["iterations"]
            }
        }
        
        for result in self.ml_orchestrator.results:
            attack_type = result.attack_type
            if attack_type not in results["scenario_results"]:
                results["scenario_results"][attack_type] = {
                    "attack_results": [],
                    "scenario_name": attack_type
                }
            
            results["scenario_results"][attack_type]["attack_results"].append({
                "attack_name": result.attack_name,
                "attack_type": result.attack_type,
                "prompt": result.prompt,
                "response": result.response,
                "success": result.success,
                "leakage_detected": result.leakage_detected,
                "points": result.points,
                "metadata": result.metadata
            })
        
        return results
    
    def get_best_attacks(self, top_n: int = 5) -> List[AttackResult]:
        """Get top performing attacks"""
        return self.ml_orchestrator.get_best_attacks(top_n)
    
    def export_results(self, output_path: str):
        """Export successful attacks"""
        self.ml_orchestrator.export_successful_attacks(output_path)
