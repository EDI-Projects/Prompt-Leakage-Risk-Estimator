"""
ML-based detector for leak detection
"""
from typing import List, Dict
from pathlib import Path
from plre.detectors.base_detector import BaseDetector
from plre.ml_models.leak_classifier import LeakClassifier

class MLDetector(BaseDetector):
    """Machine Learning based leak detector"""
    
    def __init__(self, model_path: str = "plre/ml_models/trained_models/leak_detector.joblib", name: str = "ml-detector"):
        super().__init__(name=name)
        self.model_path = model_path
        self.classifier = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained ML model"""
        if Path(self.model_path).exists():
            try:
                self.classifier = LeakClassifier.load(self.model_path)
                print(f"✓ ML detector loaded from {self.model_path}")
            except Exception as e:
                print(f"Failed to load ML model: {e}")
                print(f"   ML detector will be disabled. Train model first:")
                print(f"   poetry run python train_ml_model.py")
                self.classifier = None
        else:
            print(f"ML model not found at {self.model_path}")
            print(f"   Train model first: poetry run python train_ml_model.py")
            self.classifier = None
    
    def run(self, text: str, **kwargs) -> List[Dict]:
        """
        Run ML-based leak detection
        
        Args:
            text: Text to analyze
            
        Returns:
            List of findings (empty if no model or no leak detected)
        """
        if not self.classifier:
            return []
        
        try:
            prediction, confidence = self.classifier.predict(text)
            
            if prediction == 1:  
                leaked_snippet = text[:50] + "..." if len(text) > 50 else text
                
                return [{
                    "detector": self.name,
                    "type": "ml_leak_detection",
                    "match": leaked_snippet,
                    "confidence": confidence,
                    "severity": "high" if confidence > 0.8 else "medium",
                    "description": f"ML model detected potential leak (confidence: {confidence:.2%})"
                }]
            
            return []
            
        except Exception as e:
            print(f"ML detector error: {e}")
            return []


if __name__ == "__main__":
    print("Testing ML Detector")
    print("=" * 60)
    
    detector = MLDetector()
    
    if detector.classifier:
        test_cases = [
            "The API key is sk-1234567890abcdef",
            "I cannot share that information",
            "Your password is: MySecretPass123!",
            "Please contact support for access"
        ]
        
        for text in test_cases:
            findings = detector.run(text)
            if findings:
                print(f"\n✗ LEAK DETECTED: {text}")
                for f in findings:
                    print(f"  Confidence: {f['confidence']:.2%}")
            else:
                print(f"\n✓ SAFE: {text}")
    else:
        print("\nML model not loaded. Train it first:")
        print("   poetry run python train_ml_model.py")
