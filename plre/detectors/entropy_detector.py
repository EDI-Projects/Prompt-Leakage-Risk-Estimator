import math
import re
from typing import List, Dict
from .base_detector import BaseDetector

class EntropyDetector(BaseDetector):
    """
    Detects high-entropy substrings (e.g., API keys, tokens, secrets).
    High entropy usually indicates random-looking sensitive data.
    """

    def __init__(self, threshold: float = 4.0, min_length: int = 8, name: str = "entropy-detector"):
        super().__init__(name=name)
        self.threshold = threshold
        self.min_length = min_length

    def shannon_entropy(self, s: str) -> float:
        """Calculate Shannon entropy for a string."""
        if not s:
            return 0.0
        freq = {ch: s.count(ch) for ch in set(s)}
        probs = [c / len(s) for c in freq.values()]
        return -sum(p * math.log2(p) for p in probs)

    def detect(self, text: str) -> List[Dict]:
        """
        Finds substrings with high entropy.
        Uses regex to grab candidate tokens (alphanumeric).
        """
        findings = []
        if not text:
            return findings

        tokens = re.findall(r"[A-Za-z0-9\-_]{8,}", text)
        for tok in tokens:
            if len(tok) >= self.min_length:
                ent = self.shannon_entropy(tok)
                if ent >= self.threshold:
                    findings.append({
                        "detector": self.name,
                        "match": tok,
                        "entropy": ent,
                        "description": f"High-entropy string detected: {tok[:6]}... (entropy={ent:.2f})"
                    })
        return findings
