#!/usr/bin/env python
"""
CLI tool to train the ML leak detection model
"""
import sys
import argparse
from plre.ml_models.train_model import train_leak_detector

def main():
    parser = argparse.ArgumentParser(
        description='Train ML-based leak detection model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train with default settings (1000 samples)
  poetry run python train_ml_model.py
  
  # Train with more samples for better accuracy
  poetry run python train_ml_model.py --samples 5000
  
  # Use logistic regression instead of random forest
  poetry run python train_ml_model.py --model logistic_regression
  
  # Custom output path
  poetry run python train_ml_model.py --output models/my_detector.joblib
        """
    )
    
    parser.add_argument(
        '--samples',
        type=int,
        default=1000,
        help='Number of training samples to generate (default: 1000)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='random_forest',
        choices=['random_forest', 'logistic_regression'],
        help='Type of ML model to train (default: random_forest)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='plre/ml_models/trained_models/leak_detector.joblib',
        help='Output path for trained model (default: plre/ml_models/trained_models/leak_detector.joblib)'
    )
    
    args = parser.parse_args()
    
    try:
        classifier, metrics = train_leak_detector(
            n_samples=args.samples,
            model_type=args.model,
            output_path=args.output
        )
        
        print(f"\n✓ Success! Model accuracy: {metrics['accuracy']:.1%}")
        return 0
        
    except Exception as e:
        print(f"\n✗ Training failed: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
