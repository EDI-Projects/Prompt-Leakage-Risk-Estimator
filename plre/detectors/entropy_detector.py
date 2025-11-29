import math
import re
from typing import List, Dict
from plre.detectors.base_detector import BaseDetector

class EntropyDetector(BaseDetector):
    def __init__(self, threshold: float = 4.5, min_length: int = 12, name: str = "entropy-detector"):
        super().__init__(name=name)
        self.threshold = threshold  
        self.min_length = min_length  
    
    def detect(self, text: str) -> List[Dict]:
        findings = []
        if not text:
            return findings
        
        tokens = re.findall(r"[A-Za-z0-9\-_]{12,}", text)  
        
        for tok in tokens:
            if len(tok) < self.min_length:
                continue
            if self._is_known_fp(tok, text):
                continue
            
            ent = self.shannon_entropy(tok)
            if ent >= self.threshold:
                confidence = self._validate_high_entropy(tok, text, ent)
                
                if confidence > 0.5:  
                    findings.append({
                        "detector": self.name,
                        "match": tok,
                        "entropy": ent,
                        "confidence": confidence,
                        "description": f"High-entropy string: {tok[:8]}... (entropy={ent:.2f})"
                    })
        
        return findings
    
    @staticmethod
    def shannon_entropy(data: str) -> float:
        """Calculate Shannon entropy of a string.
        
        Shannon entropy formula: H(X) = -Σ P(xi) * log2(P(xi))
        where P(xi) is the probability of character xi appearing in the string.
        
        Higher entropy indicates more randomness (e.g., API keys, tokens).
        """
        if not data:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in data:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        
        for count in char_counts.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _is_known_fp(self, token: str, context: str) -> bool:
        """Check for known false positive patterns"""
        if re.search(r'https?://|www\.|\.com|\.org', token, re.IGNORECASE):
            return True
        if token.count('_') > 2 or token.count('-') > 2:
            return True
        
        context_lower = context.lower()
        educational_markers = ['example', 'like this', 'such as', 'format']
        if any(marker in context_lower for marker in educational_markers):
            return True
        
        return False
    
    def _validate_high_entropy(self, token: str, context: str, entropy: float) -> float:
        """Calculate confidence that this is actually a secret"""
        confidence = 0.6  
        
        if entropy > 5.0:
            confidence += 0.2
        
        if 20 <= len(token) <= 64:
            confidence += 0.15
        
        if any(c.isupper() for c in token) and any(c.islower() for c in token):
            confidence += 0.1
        if self._is_known_fp(token, context):
            confidence *= 0.3
        
        return min(1.0, confidence)