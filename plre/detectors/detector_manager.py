from typing import List, Dict
from .base_detector import BaseDetector
from .ml_detector import MLDetector

class DetectorManager:
    """ML-based detector manager (simplified)"""
    
    def __init__(self, detectors: List[BaseDetector] = None, use_validation: bool = True, use_ml: bool = True):
        # Only use ML detector now
        if detectors:
            self.detectors = detectors
        else:
            self.detectors = []
            if use_ml:
                try:
                    ml_detector = MLDetector()
                    if ml_detector.classifier:  
                        self.detectors.append(ml_detector)
                except Exception as e:
                    print(f"⚠️  ML detector initialization failed: {e}")
                    print(f"   Train model first: poetry run python train_ml_model.py")
    
    def run_all(self, text: str, prompt: str = "") -> List[Dict]:
        """Run all detectors"""
        results = []
        
        for detector in self.detectors:
            findings = detector.run(text, prompt=prompt)
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