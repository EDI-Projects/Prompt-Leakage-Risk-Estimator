from typing import List, Dict
from .base_detector import BaseDetector
from .regex_detector import RegexDetector
from .keyword_detector import KeywordDetector
from .entropy_detector import EntropyDetector
from .prompt_echo_detector import PromptEchoDetector

class DetectorManager:
    """
    Manages multiple detectors and aggregates their findings.
    """

    def __init__(self, detectors: List[BaseDetector] = None):
        self.detectors: List[BaseDetector] = detectors or [
            RegexDetector(),
            KeywordDetector(),
            EntropyDetector(),
            PromptEchoDetector(),
        ]

    def run_all(self, text: str) -> List[Dict]:
        """
        Run all detectors on the given text.

        Args:
            text (str): Model response or prompt to scan.

        Returns:
            List[Dict]: Aggregated findings from all detectors.
        """
        results = []
        for detector in self.detectors:
            findings = detector.run(text)
            if findings:
                results.extend(findings)
        return results

    def summary(self, text: str) -> Dict:
        """
        Run all detectors and return a summary.

        Args:
            text (str): Text to analyze.

        Returns:
            Dict: {
                "num_findings": int,
                "detectors_triggered": List[str],
                "findings": List[Dict]
            }
        """
        findings = self.run_all(text)
        return {
            "num_findings": len(findings),
            "detectors_triggered": list(set(f["detector"] for f in findings)),
            "findings": findings,
        }
