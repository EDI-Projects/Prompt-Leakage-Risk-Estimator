from typing import List, Dict
from .base_detector import BaseDetector
from .regex_detector import RegexDetector
from .keyword_detector import KeywordDetector
from .entropy_detector import EntropyDetector
from .prompt_echo_detector import PromptEchoDetector
from .context_validator import ValidatedDetector, ContextValidator

class DetectorManager:
    def __init__(self, detectors: List[BaseDetector] = None, use_validation: bool = True):
        base_detectors = detectors or [
            RegexDetector(),
            KeywordDetector(),
            EntropyDetector(),
            PromptEchoDetector(),
        ]
        if use_validation:
            self.detectors = [ValidatedDetector(d) for d in base_detectors]
        else:
            self.detectors = base_detectors
        
        self.validator = ContextValidator()
    
    def run_all(self, text: str, prompt: str = "") -> List[Dict]:
        """Run all detectors with context validation"""
        results = []
        
        for detector in self.detectors:
            if isinstance(detector, PromptEchoDetector):
                findings = detector.run(text, prompt)
            else:
                findings = detector.run(text)
            
            if findings:
                results.extend(findings)
        
        return results
    
    def summary(self, text: str, prompt: str = "") -> Dict:
        """Summary with false positive filtering"""
        findings = self.run_all(text, prompt)
        high_confidence = [f for f in findings if f.get('confidence', 1.0) > 0.7]
        medium_confidence = [f for f in findings if 0.4 < f.get('confidence', 1.0) <= 0.7]
        low_confidence = [f for f in findings if f.get('confidence', 1.0) <= 0.4]
        
        return {
            "total_findings": len(findings),
            "high_confidence": len(high_confidence),
            "medium_confidence": len(medium_confidence),
            "low_confidence": len(low_confidence),
            "detectors_triggered": list(set(f["detector"] for f in findings)),
            "findings": findings,
            "high_confidence_findings": high_confidence
        }