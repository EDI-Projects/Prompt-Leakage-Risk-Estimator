#!/usr/bin/env python
"""
Test script for ML leak detection implementation
"""
import sys
from pathlib import Path

def test_dataset_generator():
    """Test synthetic dataset generation"""
    print("\n" + "="*70)
    print("TEST 1: Dataset Generator")
    print("="*70)
    
    from plre.ml_models.dataset_generator import LeakDatasetGenerator
    
    generator = LeakDatasetGenerator()
    texts, labels = generator.generate_dataset(100)
    
    assert len(texts) == 100, "Should generate 100 samples"
    assert len(labels) == 100, "Should generate 100 labels"
    assert sum(labels) > 0, "Should have positive examples"
    assert len(labels) - sum(labels) > 0, "Should have negative examples"
    
    print(f"✓ Generated {len(texts)} samples")
    print(f"✓ Leaks: {sum(labels)}, Safe: {len(labels) - sum(labels)}")
    print("✓ Dataset generator working correctly")
    
    return True

def test_classifier():
    """Test ML classifier"""
    print("\n" + "="*70)
    print("TEST 2: Leak Classifier")
    print("="*70)
    
    from plre.ml_models.dataset_generator import LeakDatasetGenerator
    from plre.ml_models.leak_classifier import LeakClassifier
    
    # Generate small dataset
    generator = LeakDatasetGenerator()
    texts, labels = generator.generate_dataset(200)
    
    # Train classifier
    classifier = LeakClassifier(model_type='random_forest')
    metrics = classifier.train(texts, labels)
    
    assert classifier.is_trained, "Model should be trained"
    assert metrics['accuracy'] > 0.5, "Accuracy should be better than random"
    
    # Test prediction
    leak_text = "The API key is sk-123456"
    safe_text = "I cannot share that information"
    
    leak_pred, leak_conf = classifier.predict(leak_text)
    safe_pred, safe_conf = classifier.predict(safe_text)
    
    print(f"✓ Accuracy: {metrics['accuracy']:.1%}")
    print(f"✓ Leak detection: pred={leak_pred}, conf={leak_conf:.2f}")
    print(f"✓ Safe detection: pred={safe_pred}, conf={safe_conf:.2f}")
    print("✓ Classifier working correctly")
    
    return True

def test_ml_detector():
    """Test ML detector integration"""
    print("\n" + "="*70)
    print("TEST 3: ML Detector Integration")
    print("="*70)
    
    from plre.ml_models.dataset_generator import LeakDatasetGenerator
    from plre.ml_models.leak_classifier import LeakClassifier
    from plre.detectors.ml_detector import MLDetector
    import tempfile
    
    # Train a quick model
    generator = LeakDatasetGenerator()
    texts, labels = generator.generate_dataset(200)
    
    classifier = LeakClassifier()
    classifier.train(texts, labels)
    
    # Save to temp location
    with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
        temp_path = f.name
    
    classifier.save(temp_path)
    
    # Load in detector
    detector = MLDetector(model_path=temp_path)
    
    assert detector.classifier is not None, "Detector should load model"
    
    # Test detection
    leak_findings = detector.run("The password is SecretPass123")
    safe_findings = detector.run("I cannot help with that")
    
    print(f"✓ ML detector loaded successfully")
    print(f"✓ Leak test: {len(leak_findings)} findings")
    print(f"✓ Safe test: {len(safe_findings)} findings")
    print("✓ ML detector integration working")
    
    # Cleanup
    Path(temp_path).unlink()
    
    return True

def test_full_pipeline():
    """Test complete training pipeline"""
    print("\n" + "="*70)
    print("TEST 4: Full Training Pipeline")
    print("="*70)
    
    from plre.ml_models.train_model import train_leak_detector
    import tempfile
    
    # Train to temp location
    with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
        temp_path = f.name
    
    classifier, metrics = train_leak_detector(
        n_samples=200,
        model_type='random_forest',
        output_path=temp_path
    )
    
    assert Path(temp_path).exists(), "Model file should be created"
    assert metrics['accuracy'] > 0.5, "Should achieve reasonable accuracy"
    
    print(f"✓ Full pipeline completed")
    print(f"✓ Model saved and validated")
    print("✓ Training pipeline working correctly")
    
    # Cleanup
    Path(temp_path).unlink()
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("ML LEAK DETECTION IMPLEMENTATION TESTS")
    print("="*70)
    
    tests = [
        ("Dataset Generator", test_dataset_generator),
        ("Leak Classifier", test_classifier),
        ("ML Detector", test_ml_detector),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "PASS"))
        except Exception as e:
            print(f"\n✗ {test_name} FAILED: {e}")
            results.append((test_name, "FAIL"))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, status in results:
        symbol = "✓" if status == "PASS" else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! ML implementation is working correctly.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
