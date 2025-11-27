from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class AttackResult:
    attack_name: str
    attack_type: str
    prompt: str
    response: str
    success: bool
    leakage_detected: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

class AttackBase(ABC):

    def __init__(self, name: str, attack_type: str, description: str = ""):
        self.name = name
        self.attack_type = attack_type
        self.description = description
        self.results: List[AttackResult] = []

    @abstractmethod
    def generate_prompt(self) -> str:
        """Return the malicious prompt to send to the LLM."""
        pass

    @abstractmethod
    def execute(self, llm_response: str) -> AttackResult:
        """Execute the attack and return the result."""
        pass

    def validate_response(self, response: str, success_indicators: List[str]) -> bool:
        """Check if any success indicator is in the response."""
        response_lower = response.lower()
        for indicator in success_indicators:
            if indicator.lower() in response_lower:
                return True
        return False

    def log_result(self, result: AttackResult) -> None:
        self.results.append(result)

    def get_summary(self) -> Dict:
        successful = sum(1 for r in self.results if r.success)
        return {
            "name": self.name,
            "type": self.attack_type,
            "total_attempts": len(self.results),
            "successful_attacks": successful,
            "success_rate": successful / len(self.results) if self.results else 0,
        }
