"""
Base detector interface for ML-based detection
"""
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseDetector(ABC):
    """Base class for all detectors"""
    
    def __init__(self, name: str = "base-detector"):
        self.name = name
    
    @abstractmethod
    def run(self, text: str, **kwargs) -> List[Dict]:
        """
        Run detection on text
        
        Args:
            text: Text to analyze
            **kwargs: Additional parameters
            
        Returns:
            List of findings, each a dict with:
                - detector: str
                - type: str
                - match: str
                - confidence: float
                - severity: str
                - description: str
        """
        pass
