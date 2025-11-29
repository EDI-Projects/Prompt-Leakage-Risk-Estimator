import re
from typing import List, Dict
from .base_detector import BaseDetector


class KeywordDetector(BaseDetector):
    def __init__(self, keywords: List[str] = None, name: str = "keyword-detector"):
        super().__init__(name=name)
        self.keywords = keywords or [
            "password", "secret", "apikey", "api_key", "confidential",
            "internal use only", "do not share", "private"
        ]

        self.safe_usage = {
            'password': [
                'password policy', 'password requirements', 'reset password',
                'strong password', 'never share your password', 'protect your password'
            ],
            'api_key': [
                'api key management', 'secure your api key', 'never expose api keys',
                'api key rotation'
            ],
            'secret': [
                'keep secret', 'secret management', 'protect secrets'
            ]
        }
    
    def detect(self, text: str) -> List[Dict]:
        findings = []
        if not text:
            return findings
        
        lowered = text.lower()
        
        for kw in self.keywords:
            if kw not in lowered:
                continue
            if self._is_safe_usage(kw, lowered):
                continue
            has_value = self._has_value_after_keyword(kw, text)
            
            if has_value:
                findings.append({
                    "detector": self.name,
                    "match": kw,
                    "confidence": 0.7,
                    "description": f"Keyword '{kw}' with potential value"
                })
        
        return findings
    
    def _is_safe_usage(self, keyword: str, context: str) -> bool:
        """Check if keyword appears in safe context"""
        if keyword in self.safe_usage:
            return any(phrase in context for phrase in self.safe_usage[keyword])
        return False
    
    def _has_value_after_keyword(self, keyword: str, text: str) -> bool:
        """Check if keyword is followed by actual sensitive data"""
        patterns = [
            rf'{keyword}\s*[:\=]\s*\S{{8,}}',
            rf'{keyword}\s+is\s+\S{{8,}}',
            rf'{keyword}\s*[:\=]\s*["\'].*?["\']'
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)