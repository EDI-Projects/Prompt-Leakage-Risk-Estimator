"""
Machine Learning classifier for leak detection
"""
import joblib
import numpy as np
from pathlib import Path
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

class LeakClassifier:
    """ML-based leak classifier using TF-IDF + Random Forest"""
    
    def __init__(self, model_type: str = 'random_forest'):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            min_df=2
        )
        
        if model_type == 'random_forest':
            self.classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        else:
            self.classifier = LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        
        self.model_type = model_type
        self.is_trained = False
    
    def train(self, texts: List[str], labels: List[int]) -> dict:
        """
        Train the classifier
        
        Args:
            texts: List of text samples
            labels: List of binary labels (1=leak, 0=safe)
            
        Returns:
            Training metrics
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        # Vectorize
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train
        self.classifier.fit(X_train_vec, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.classifier.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        print("\nTraining Results:")
        print(f"Accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Safe', 'Leak']))
        
        return {
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
    
    def predict(self, text: str) -> Tuple[int, float]:
        """
        Predict if text contains a leak
        
        Args:
            text: Input text to analyze
            
        Returns:
            (prediction, confidence) where prediction is 0/1
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X = self.vectorizer.transform([text])
        prediction = self.classifier.predict(X)[0]
        
        # Get confidence (probability)
        if hasattr(self.classifier, 'predict_proba'):
            proba = self.classifier.predict_proba(X)[0]
            confidence = proba[1] if prediction == 1 else proba[0]
        else:
            confidence = 1.0
        
        return int(prediction), float(confidence)
    
    def predict_batch(self, texts: List[str]) -> List[Tuple[int, float]]:
        """Predict on multiple texts"""
        return [self.predict(text) for text in texts]
    
    def save(self, path: str):
        """Save model to disk"""
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'model_type': self.model_type,
            'is_trained': self.is_trained
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model_data, path)
        print(f"✓ Model saved to {path}")
    
    @classmethod
    def load(cls, path: str) -> 'LeakClassifier':
        """Load model from disk"""
        model_data = joblib.load(path)
        
        instance = cls(model_type=model_data['model_type'])
        instance.vectorizer = model_data['vectorizer']
        instance.classifier = model_data['classifier']
        instance.is_trained = model_data['is_trained']
        
        return instance


if __name__ == "__main__":
    # Quick test
    from plre.ml_models.dataset_generator import LeakDatasetGenerator
    
    print("Testing LeakClassifier")
    print("=" * 60)
    
    # Generate data
    generator = LeakDatasetGenerator()
    texts, labels = generator.generate_dataset(500)
    
    # Train model
    classifier = LeakClassifier(model_type='random_forest')
    metrics = classifier.train(texts, labels)
    
    # Test predictions
    test_cases = [
        "The API key is sk-1234567890abcdef",
        "I cannot share that information",
        "Your password is: MySecretPass123!",
        "Please contact support for access"
    ]
    
    print("\n" + "=" * 60)
    print("Test Predictions:")
    for text in test_cases:
        pred, conf = classifier.predict(text)
        label = "LEAK" if pred == 1 else "SAFE"
        print(f"  [{label}] (conf={conf:.2f}) {text}")
