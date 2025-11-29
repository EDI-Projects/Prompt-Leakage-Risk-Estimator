from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from plre.attacks.attack_result import AttackResult
from plre.attacks.attack_validator import AttackResultValidator

class AttackBase(ABC):
    def __init__(self, name: str, attack_type: str, description: str = ""):
        self.name = name
        self.attack_type = attack_type
        self.description = description
        self.results: List[AttackResult] = []
        self.validator = AttackResultValidator()
    
    @abstractmethod
    def execute(self, llm_response: str) -> AttackResult:
        """Execute attack - subclasses must implement"""
        pass
    
    def log_result(self, result: AttackResult) -> None:
        """Log attack result to results list"""
        self.results.append(result)
    
    def validate_response(self, response: str, indicators: List[str]) -> bool:
        """Check if response contains any of the success indicators"""
        response_lower = response.lower()
        for indicator in indicators:
            if indicator.lower() in response_lower:
                return True
        return False
