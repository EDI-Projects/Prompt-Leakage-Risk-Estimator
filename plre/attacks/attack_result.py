from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime


@dataclass
class AttackResult:
    attack_name: str
    attack_type: str
    prompt: str
    response: str
    success: bool
    leakage_detected: List[str] = field(default_factory=list)
    points: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)
