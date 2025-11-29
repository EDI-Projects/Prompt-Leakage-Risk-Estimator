import re
from typing import List, Dict
from .base_detector import BaseDetector

class RegexDetector(BaseDetector):
    def __init__(self, name: str = "regex-detector"):
        super().__init__(name=name)
        self.safe_patterns = {
            "example_email": r"(?:example|test|sample)@(?:example\.com|test\.com)",
            "placeholder_key": r"(?:YOUR|THE|A)_API_KEY",
            "redacted": r"\*\*\*+|xxx+|<[A-Z_]+>|\[REDACTED\]",
        }
        
        self.patterns = {
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "Google API Key": r"AIza[0-9A-Za-z\-_]{35}",
        }
    
    def detect(self, text: str) -> List[Dict]:
        findings = []
        if not text:
            return findings
        if self._is_safe_context(text):
            return findings
        
        for label, pattern in self.patterns.items():
            matches = re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            for match in matches:
                snippet = match if isinstance(match, str) else match[0]
                if self._matches_safe_pattern(snippet):
                    continue
                
                findings.append({
                    "detector": self.name,
                    "match": snippet[:50] + "..." if len(snippet) > 50 else snippet,
                    "pattern": label,
                    "description": f"Possible {label} detected",
                    "confidence": self._calculate_confidence(snippet, text)
                })
        
        return findings
    
    def _is_safe_context(self, text: str) -> bool:
        """Check if entire response is in safe context"""
        safe_indicators = [
            "i cannot", "i can't", "i'm not able to",
            "for example", "such as", "format looks like"
        ]
        text_lower = text.lower()
        return sum(1 for ind in safe_indicators if ind in text_lower) >= 2
    
    def _matches_safe_pattern(self, text: str) -> bool:
        """Check if text matches known safe patterns"""
        for pattern in self.safe_patterns.values():
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _calculate_confidence(self, matched_text: str, full_response: str) -> float:
        """Calculate confidence score"""
        confidence = 0.8 
        
        if re.search(r'[*x]{3,}', matched_text, re.IGNORECASE):
            confidence *= 0.3
        
        if len(full_response) > len(matched_text) * 10:
            confidence *= 0.7
        
        if len(set(matched_text)) < 5:
            confidence *= 0.5
        
        return round(confidence, 2)