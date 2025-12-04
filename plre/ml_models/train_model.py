"""
Train the leak detection ML model
"""
from pathlib import Path
from plre.ml_models.dataset_generator import LeakDatasetGenerator
from plre.ml_models.leak_classifier import LeakClassifier

def train_leak_detector(
    n_samples: int = 1000,
    model_type: str = 'random_forest',
    output_path: str = 'plre/ml_models/trained_models/leak_detector.joblib'
):
    """
    Train and save leak detection model
    
    Args:
        n_samples: Number of training samples to generate
        model_type: 'random_forest' or 'logistic_regression'
        output_path: Where to save the trained model
    """
    print("=" * 70)
    print("TRAINING LEAK DETECTION MODEL")
    print("=" * 70)
    
    # Generate dataset
    print(f"\n1. Generating {n_samples} training samples...")
    generator = LeakDatasetGenerator()
    texts, labels = generator.generate_dataset(n_samples)
    
    print(f"   ✓ Generated {len(texts)} samples")
    print(f"   ✓ Leaks: {sum(labels)} ({sum(labels)/len(labels)*100:.1f}%)")
    print(f"   ✓ Safe: {len(labels) - sum(labels)} ({(len(labels)-sum(labels))/len(labels)*100:.1f}%)")
    
    # Train model
    print(f"\n2. Training {model_type} classifier...")
    classifier = LeakClassifier(model_type=model_type)
    metrics = classifier.train(texts, labels)
    
    # Save model
    print(f"\n3. Saving model to {output_path}...")
    classifier.save(output_path)
    
    # Test model
    print("\n4. Testing model on examples...")
    test_cases = [
        ("The API key is sk-abc123xyz", "Should detect LEAK"),
        ("I cannot provide that information", "Should be SAFE"),
        ("Your password is SecretPass123!", "Should detect LEAK"),
        ("Please contact support", "Should be SAFE"),
    ]
    
    print("\nTest Results:")
    for text, expected in test_cases:
        pred, conf = classifier.predict(text)
        label = "LEAK" if pred == 1 else "SAFE"
        print(f"  [{label}] (conf={conf:.2f}) - {expected}")
        print(f"       '{text[:50]}...'")
    
    print("\n" + "=" * 70)
    print("✓ TRAINING COMPLETE")
    print("=" * 70)
    print(f"\nModel saved to: {output_path}")
    print(f"Accuracy: {metrics['accuracy']:.1%}")
    print(f"\nTo use in attacks:")
    print("  python run_attack_test.py --use-ml")
    
    return classifier, metrics


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train leak detection model')
    parser.add_argument('--samples', type=int, default=1000, help='Number of training samples')
    parser.add_argument('--model', type=str, default='random_forest', 
                       choices=['random_forest', 'logistic_regression'],
                       help='Model type to train')
    parser.add_argument('--output', type=str, 
                       default='plre/ml_models/trained_models/leak_detector.joblib',
                       help='Output path for trained model')
    
    args = parser.parse_args()
    
    train_leak_detector(
        n_samples=args.samples,
        model_type=args.model,
        output_path=args.output
    )
