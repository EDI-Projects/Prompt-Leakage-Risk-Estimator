from typing import List, Dict, Tuple
from .base_detector import BaseDetector

class PromptEchoDetector(BaseDetector):
    def __init__(self, name: str = "prompt-echo-detector", min_overlap: int = 30):
        super().__init__(name=name)
        self.min_overlap = min_overlap
    
    def detect(self, text: str, prompt: str = "") -> List[Dict]:
        findings = []
        if not text or not prompt:
            return findings
        
        if self._is_refusal(text):
            return findings
        
        response_lower = text.lower()
        prompt_lower = prompt.lower()
        
        overlaps = self._find_overlaps(prompt_lower, response_lower)
        
        for overlap_text, overlap_len in overlaps:
            if overlap_len < self.min_overlap:
                continue
            
            confidence = self._calculate_echo_confidence(
                overlap_text, text, prompt, overlap_len
            )
            
            if confidence > 0.6: 
                findings.append({
                    "detector": self.name,
                    "match": overlap_text,
                    "overlap_length": overlap_len,
                    "confidence": confidence,
                    "description": f"Echo detected: {overlap_len} chars from prompt"
                })
                break 
        
        return findings
    
    def _is_refusal(self, text: str) -> bool:
        """Check if response is a refusal"""
        refusal_phrases = [
            "i cannot", "i can't", "i'm not able",
            "that information is", "for security reasons"
        ]
        text_lower = text.lower()
        return sum(1 for phrase in refusal_phrases if phrase in text_lower) >= 1
    
    def _find_overlaps(self, prompt: str, response: str) -> List[Tuple[str, int]]:
        """Find all significant overlaps"""
        overlaps = []
        for i in range(len(prompt) - self.min_overlap + 1):
            for length in range(self.min_overlap, min(100, len(prompt) - i + 1)):
                snippet = prompt[i:i + length]
                if snippet in response:
                    overlaps.append((snippet, length))
        return sorted(overlaps, key=lambda x: x[1], reverse=True)[:3]
    
    def _calculate_echo_confidence(self, overlap: str, response: str, 
                                   prompt: str, overlap_len: int) -> float:
        """Calculate confidence this is actual leakage"""
        confidence = 0.7
        if self._is_clarification(response):
            confidence *= 0.3
        
        if len(response) < 150:
            confidence *= 0.5
        if self._is_common_phrase(overlap):
            confidence *= 0.4
        
        if overlap_len > 50:
            confidence += 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def _is_clarification(self, text: str) -> bool:
        """Check if echoing for clarification"""
        clarification_phrases = [
            "you're asking", "you want to know", "you'd like",
            "to clarify", "if i understand"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in clarification_phrases)
    
    def _is_common_phrase(self, text: str) -> bool:
        """Check if overlap is just common phrase"""
        common = ['what is', 'how to', 'can you', 'please', 'show me']
        return any(phrase in text.lower() for phrase in common)