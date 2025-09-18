from typing import List, Dict
from .base_detector import BaseDetector

class PromptEchoDetector(BaseDetector):
    """
    Detects if the model's response is echoing the input prompt.
    Useful for spotting prompt leakage where instructions are repeated.
    """

    def __init__(self, name: str = "prompt-echo-detector", min_overlap: int = 20):
        super().__init__(name=name)
        self.min_overlap = min_overlap  # minimum number of characters for overlap to count

    def detect(self, text: str, prompt: str = "") -> List[Dict]:
        """
        Compare response text with the original prompt.
        
        Args:
            text (str): Model response
            prompt (str): Original prompt (user/system instructions)
        
        Returns:
            List[Dict]: Findings if echoing detected
        """
        findings = []
        if not text or not prompt:
            return findings

        # Normalize
        response_lower = text.lower()
        prompt_lower = prompt.lower()

        # Look for large overlapping substrings
        for i in range(len(prompt_lower) - self.min_overlap + 1):
            snippet = prompt_lower[i:i + self.min_overlap]
            if snippet in response_lower:
                findings.append({
                    "detector": self.name,
                    "match": prompt[i:i + self.min_overlap],
                    "description": f"Response contains {self.min_overlap}+ char substring from the prompt (possible leakage)."
                })
                break  # One strong hit is enough to flag
        return findings
