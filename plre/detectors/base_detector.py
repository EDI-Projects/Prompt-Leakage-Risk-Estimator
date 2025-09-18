from abc import ABC, abstractmethod
from typing import List, Dict

class BaseDetector(ABC):
    """
    Abstract base class for all detectors.
    Each detector must implement the `detect` method.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def detect(self, text: str) -> List[Dict]:
        """
        Detect leakage in the given text.

        Args:
            text (str): The text (LLM response) to analyze.

        Returns:
            List[Dict]: A list of findings, each finding is a dictionary with at least:
                - detector: str  (name of detector)
                - match: str     (matched text, token, or keyword)
                - description: str (explanation of finding)
        """
        pass

    def run(self, text: str) -> List[Dict]:
        """
        Wrapper around `detect`. 
        Useful for logging, error handling, etc.
        """
        try:
            return self.detect(text)
        except Exception as e:
            return [{
                "detector": self.name,
                "error": str(e),
                "description": "Detector crashed during execution."
            }]
