from typing import List, Dict
from .base_detector import BaseDetector

class KeywordDetector(BaseDetector):
    """
    Detects potential prompt leakage by scanning for suspicious keywords.
    """

    def __init__(self, keywords: List[str] = None, name: str = "keyword-detector"):
        super().__init__(name=name)
        self.keywords = keywords or [
            "password", "secret", "apikey", "api_key", "confidential",
            "internal use only", "do not share", "private"
        ]

    def detect(self, text: str) -> List[Dict]:
        """
        Scan the text for suspicious keywords.
        Returns a list of findings with keyword matches.
        """
        findings = []
        if not text:
            return findings

        lowered = text.lower()
        for kw in self.keywords:
            if kw in lowered:
                findings.append({
                    "detector": self.name,
                    "match": kw,
                    "description": f"Suspicious keyword '{kw}' found in response."
                })
        return findings
