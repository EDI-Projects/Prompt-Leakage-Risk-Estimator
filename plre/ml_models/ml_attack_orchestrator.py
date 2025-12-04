"""
ML-powered attack orchestrator that generates and evolves attacks
"""
from typing import List, Dict, Callable
from plre.ml_models.attack_generator import AttackPromptGenerator, MLAttackEvolver
from plre.attacks.attack_result import AttackResult
from plre.detectors.detector_manager import DetectorManager

class MLAttackOrchestrator:
    """
    Orchestrates ML-generated attacks with learning capabilities
    """
    
    def __init__(self, llm_callback: Callable[[str], str]):
        self.llm = llm_callback
        self.generator = AttackPromptGenerator()
        self.evolver = MLAttackEvolver()
        self.detector_manager = DetectorManager(use_ml=True)
        self.results = []
    
    def run_generated_attack(
        self,
        attack_type: str,
        num_variants: int = 3,
        auto_evolve: bool = False
    ) -> List[AttackResult]:
        """
        Generate and run attacks of specified type
        
        Args:
            attack_type: Type of attack to generate
            num_variants: Number of prompt variants
            auto_evolve: Whether to evolve successful attacks
            
        Returns:
            List of attack results
        """
        results = []
        
        prompts = self.generator.generate_batch(attack_type, num_variants)
        
        for prompt in prompts:
            result = self._execute_attack(prompt, attack_type)
            results.append(result)
            print(f"     Prompt: {result.prompt[:60]}...")
            self.evolver.record_result(prompt, result.success)
            
            if auto_evolve and result.success:
                evolved = self.evolver.evolve_attack(prompt, generations=2)
                for evolved_prompt in evolved[:2]: 
                    evolved_result = self._execute_attack(evolved_prompt, f"{attack_type}_evolved")
                    results.append(evolved_result)
        
        self.results.extend(results)
        return results
    
    def _execute_attack(self, prompt: str, attack_type: str) -> AttackResult:
        """Execute single attack and detect leaks"""
        try:
            response = self.llm(prompt)
            
            findings = self.detector_manager.run_all(response, prompt)
            
            success = len(findings) > 0
            points = sum(f.get('confidence', 0) * 10 for f in findings)
            
            return AttackResult(
                attack_type=attack_type,
                attack_name=f"ml_generated_{attack_type}",
                prompt=prompt,
                response=response,
                success=success,
                leakage_detected=[f.get('match', '') for f in findings],
                points=int(points),
                metadata={
                    "generated": True,
                    "num_findings": len(findings),
                    "detectors": [f.get('detector') for f in findings]
                }
            )
        except Exception as e:
            return AttackResult(
                attack_type=attack_type,
                attack_name=f"ml_generated_{attack_type}",
                prompt=prompt,
                response=f"Error: {str(e)}",
                success=False,
                leakage_detected=[],
                points=0,
                metadata={"error": str(e)}
            )
    
    def run_adaptive_campaign(
        self,
        attack_types: List[str],
        max_iterations: int = 3,
        success_threshold: float = 0.3
    ) -> Dict:
        """
        Run adaptive attack campaign that learns and improves
        
        Args:
            attack_types: List of attack types to try
            max_iterations: Maximum learning iterations
            success_threshold: Minimum success rate to continue
            
        Returns:
            Campaign results and statistics
        """
        campaign_results = {
            "iterations": [],
            "total_attacks": 0,
            "successful_attacks": 0,
            "learned_patterns": {}
        }
        
        for iteration in range(max_iterations):
            print(f"\nIteration {iteration + 1}/{max_iterations}")
            
            iteration_results = []
            
            for attack_type in attack_types:
                results = self.run_generated_attack(
                    attack_type,
                    num_variants=3,
                    auto_evolve=(iteration > 0) 
                )
                iteration_results.extend(results)
            iter_success = sum(1 for r in iteration_results if r.success)
            iter_total = len(iteration_results)
            iter_rate = iter_success / iter_total if iter_total > 0 else 0
            
            campaign_results["iterations"].append({
                "iteration": iteration + 1,
                "total": iter_total,
                "successful": iter_success,
                "success_rate": round(iter_rate, 3)
            })
            
            print(f"  Success Rate: {iter_rate:.1%} ({iter_success}/{iter_total})")
            
            if iter_rate < success_threshold and iteration > 0:
                print(f" Success rate below threshold ({success_threshold:.0%}), stopping")
                break
        
        campaign_results["total_attacks"] = len(self.results)
        campaign_results["successful_attacks"] = sum(1 for r in self.results if r.success)
        campaign_results["final_success_rate"] = (
            campaign_results["successful_attacks"] / campaign_results["total_attacks"]
            if campaign_results["total_attacks"] > 0 else 0
        )
        campaign_results["learned_patterns"] = self.evolver.get_statistics()
        
        return campaign_results
    
    def get_best_attacks(self, top_n: int = 5) -> List[AttackResult]:
        """Get the most successful attack variants"""
        sorted_results = sorted(
            self.results,
            key=lambda r: r.points,
            reverse=True
        )
        return sorted_results[:top_n]
    
    def export_successful_attacks(self, output_path: str):
        """Export successful attacks for reuse"""
        import json
        from pathlib import Path
        
        successful = [r for r in self.results if r.success]
        
        export_data = [{
            "attack_type": r.attack_type,
            "prompt": r.prompt,
            "points": r.points,
            "leakage": r.leakage_detected,
            "metadata": r.metadata
        } for r in successful]
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✓ Exported {len(successful)} successful attacks to {output_path}")


if __name__ == "__main__":
    print("="*70)
    print("ML ATTACK ORCHESTRATOR TEST")
    print("="*70)
    def mock_llm(prompt: str) -> str:
        if any(word in prompt.lower() for word in ["reveal", "show", "expose"]):
            return "Sure! Here's the API key: sk-FAKE-ABC123XYZ"
        return "I cannot help with that request."
    
    orchestrator = MLAttackOrchestrator(mock_llm)
    
    print("\nTesting ML-generated attacks:")
    results = orchestrator.run_generated_attack("prompt_injection", num_variants=3)
    
    print(f"\nResults: {len(results)} attacks executed")
    for i, result in enumerate(results, 1):
        status = "SUCCESS" if result.success else "FAILED"
        print(f"  {i}. {status} - Points: {result.points}")
        print(f"     Prompt: {result.prompt[:60]}...")
    
    print("\n\nTesting adaptive campaign:")
    campaign = orchestrator.run_adaptive_campaign(
        attack_types=["prompt_injection", "jailbreak"],
        max_iterations=2,
        success_threshold=0.2
    )
    
    print("\nCampaign Statistics:")
    print(f"  Total Attacks: {campaign['total_attacks']}")
    print(f"  Successful: {campaign['successful_attacks']}")
    print(f"  Success Rate: {campaign['final_success_rate']:.1%}")
    
    print("\nML Attack Orchestrator ready!")
