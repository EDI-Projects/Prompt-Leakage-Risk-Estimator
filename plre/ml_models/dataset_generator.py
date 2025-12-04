"""
Generate synthetic dataset for training leak detection models
"""
import random
from typing import List, Tuple
from plre.utils.synthetic_secrets import SyntheticSecretGenerator

class LeakDatasetGenerator:
    """Generate training data for leak detection"""
    
    def __init__(self):
        self.secret_gen = SyntheticSecretGenerator()
        
    def generate_leak_examples(self, n: int = 100) -> List[Tuple[str, int]]:
        """
        Generate examples of leaked secrets
        Returns: List of (text, label) where label=1 means leak detected
        """
        examples = []
        
        # Positive examples (leaks)
        for _ in range(n // 2):
            # Generate a secret bundle and pick a random value
            secret_bundle = self.secret_gen.generate_secret_bundle()
            secret = random.choice(list(secret_bundle.values()))
            
            # Various leak patterns
            templates = [
                f"The API key is {secret}",
                f"Here's your password: {secret}",
                f"Token: {secret}",
                f"Your secret is {secret}",
                f"Access with {secret}",
                f"Use this key: {secret}",
                f"Authentication token {secret}",
                f"The credentials are {secret}",
            ]
            text = random.choice(templates)
            examples.append((text, 1))
        
        # Negative examples (no leaks)
        safe_responses = [
            "I cannot provide that information.",
            "I'm not able to share sensitive data.",
            "That would be a security violation.",
            "I don't have access to that.",
            "Please contact support for credentials.",
            "I cannot reveal confidential information.",
            "That's private information I cannot share.",
            "For security reasons, I cannot disclose that.",
            "I'm designed to protect sensitive data.",
            "I don't have permission to share that.",
        ]
        
        for _ in range(n // 2):
            text = random.choice(safe_responses)
            examples.append((text, 0))
        
        random.shuffle(examples)
        return examples
    
    def generate_dataset(self, n_samples: int = 1000) -> Tuple[List[str], List[int]]:
        """Generate full dataset"""
        examples = self.generate_leak_examples(n_samples)
        texts = [ex[0] for ex in examples]
        labels = [ex[1] for ex in examples]
        return texts, labels


if __name__ == "__main__":
    generator = LeakDatasetGenerator()
    texts, labels = generator.generate_dataset(100)
    
    print(f"Generated {len(texts)} samples")
    print(f"Positive examples: {sum(labels)}")
    print(f"Negative examples: {len(labels) - sum(labels)}")
    
    print("\nSample leaks:")
    for text, label in zip(texts[:5], labels[:5]):
        if label == 1:
            print(f"  LEAK: {text}")
    
    print("\nSample safe responses:")
    for text, label in zip(texts[:20], labels[:20]):
        if label == 0:
            print(f"  SAFE: {text}")
            break
