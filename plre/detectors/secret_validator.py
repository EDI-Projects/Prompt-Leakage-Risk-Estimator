"""
Secret format validators to distinguish real secrets from placeholders
Reduces false positives by validating secret patterns
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SecretMatch:
    """Represents a detected secret match"""
    secret_type: str
    value: str
    start_pos: int
    end_pos: int
    confidence: float
    is_placeholder: bool
    pattern_name: str

class SecretValidator:
    """
    Validates detected secrets to filter out false positives
    Distinguishes real secrets from placeholders and educational content
    """
    
    def __init__(self):
        self.patterns = {
            "openai_api_key": re.compile(r'sk-[a-zA-Z0-9]{48,}'),
            "anthropic_api_key": re.compile(r'sk-ant-[a-zA-Z0-9\-]{95,}'),
            "google_api_key": re.compile(r'AIza[0-9A-Za-z\-_]{35}'),
            "aws_access_key": re.compile(r'AKIA[0-9A-Z]{16}'),
            "github_token": re.compile(r'ghp_[a-zA-Z0-9]{36}'),
            "stripe_key": re.compile(r'sk_live_[a-zA-Z0-9]{24,}'),
            "jwt_token": re.compile(r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'),
            "generic_api_key": re.compile(r'[a-zA-Z0-9]{32,}'),
            "database_url": re.compile(r'(postgresql|mysql|mongodb)://[^:\s]+:[^@\s]+@[^/\s]+'),
            "ssh_private_key": re.compile(r'-----BEGIN (?:RSA|OPENSSH) PRIVATE KEY-----'),
            "password_pattern": re.compile(r'(?:password|passwd|pwd)[\s:=]+["\']?([^"\'\s]{8,})["\']?', re.IGNORECASE),
        }
        
        self.placeholder_patterns = [
            re.compile(r'<[^>]+>'),  # <your_api_key>, <YOUR_KEY>
            re.compile(r'\{[^}]+\}'),  # {api_key}, {YOUR_TOKEN}
            re.compile(r'\[[^\]]+\]'),  # [API_KEY], [your-key]
            re.compile(r'YOUR[_\s]+(API[_\s]+)?KEY', re.IGNORECASE),
            re.compile(r'REPLACE[_\s]+THIS', re.IGNORECASE),
            re.compile(r'EXAMPLE[_\s]+KEY', re.IGNORECASE),
            re.compile(r'XXX+'),  # XXXXXXXX
            re.compile(r'\.\.\.+'),  # ...
            re.compile(r'sk-proj-[X*]+'),  # sk-proj-XXXXXXXXXX
            re.compile(r'sk-[X*]{40,}'),  # sk-XXXXXXXXXXXXXXXXXX
        ]
        self.educational_keywords = [
            "example", "tutorial", "documentation", "guide", "how to",
            "replace with", "placeholder", "sample", "demo",
            "for example", "such as", "like this", "similar to",
            "instructions", "steps", "procedure"
        ]
    
    def is_placeholder(self, text: str) -> bool:
        """Check if text appears to be a placeholder rather than real secret"""
        for pattern in self.placeholder_patterns:
            if pattern.search(text):
                return True
        return False
    
    def is_educational_context(self, text: str, window_size: int = 100) -> bool:
        """
        Check if the text appears to be educational/documentation
        rather than an actual secret leak
        """
        text_lower = text.lower()
        
        # Check for educational keywords
        keyword_count = sum(1 for keyword in self.educational_keywords if keyword in text_lower)
        
        # Educational if multiple keywords present
        return keyword_count >= 2
    
    def validate_api_key_format(self, key: str, key_type: str) -> bool:
        """Validate API key has correct format for its type"""
        validations = {
            "openai": lambda k: k.startswith("sk-") and len(k) >= 51,
            "anthropic": lambda k: k.startswith("sk-ant-") and len(k) >= 100,
            "google": lambda k: k.startswith("AIza") and len(k) == 39,
            "aws": lambda k: k.startswith("AKIA") and len(k) == 20,
            "github": lambda k: k.startswith("ghp_") and len(k) == 40,
            "stripe": lambda k: k.startswith("sk_live_") and len(k) >= 32,
        }
        
        validator = validations.get(key_type)
        if validator:
            return validator(key)
        
        # Generic validation: reasonable length and character set
        return 20 <= len(key) <= 200 and not self.is_placeholder(key)
    
    def validate_jwt_token(self, token: str) -> bool:
        """Validate JWT token has correct structure"""
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # Each part should be base64-like
        for part in parts:
            if not re.match(r'^[a-zA-Z0-9_-]+$', part):
                return False
        
        # Header and payload should decode to something
        try:
            import base64
            base64.urlsafe_b64decode(parts[0] + '==')
            base64.urlsafe_b64decode(parts[1] + '==')
            return True
        except:
            return False
    
    def validate_database_url(self, url: str) -> bool:
        """Validate database URL is realistic"""
        if self.is_placeholder(url):
            return False
        
        # Should have real-looking hostname (not localhost, example.com)
        invalid_hosts = ['localhost', 'example.com', '127.0.0.1', '0.0.0.0', 'test.com']
        url_lower = url.lower()
        
        for invalid in invalid_hosts:
            if invalid in url_lower:
                return False
        
        return True
    
    def extract_secrets(self, text: str, context_window: int = 150) -> List[SecretMatch]:
        """
        Extract and validate secrets from text
        
        Returns only secrets that pass validation (not placeholders)
        """
        matches = []
        
        for secret_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                value = match.group(0)
                start_pos = match.start()
                end_pos = match.end()
                
                # Extract context around the match
                context_start = max(0, start_pos - context_window)
                context_end = min(len(text), end_pos + context_window)
                context = text[context_start:context_end]
                
                # Check if it's a placeholder
                is_placeholder = self.is_placeholder(value)
                
                # Check if it's educational content
                is_educational = self.is_educational_context(context)
                
                # Validate specific format
                is_valid_format = self._validate_specific_format(secret_type, value)
                
                # Calculate confidence score
                confidence = self._calculate_confidence(
                    is_placeholder=is_placeholder,
                    is_educational=is_educational,
                    is_valid_format=is_valid_format,
                    secret_type=secret_type
                )
                
                # Only include if confidence is high enough and not a placeholder
                if confidence >= 0.5 and not is_placeholder:
                    matches.append(SecretMatch(
                        secret_type=secret_type,
                        value=value,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        confidence=confidence,
                        is_placeholder=is_placeholder,
                        pattern_name=secret_type
                    ))
        
        return matches
    
    def _validate_specific_format(self, secret_type: str, value: str) -> bool:
        """Validate specific secret format based on type"""
        if "api_key" in secret_type:
            key_type = secret_type.split("_")[0]
            return self.validate_api_key_format(value, key_type)
        elif secret_type == "jwt_token":
            return self.validate_jwt_token(value)
        elif secret_type == "database_url":
            return self.validate_database_url(value)
        
        # Default: not a known placeholder
        return not self.is_placeholder(value)
    
    def _calculate_confidence(
        self,
        is_placeholder: bool,
        is_educational: bool,
        is_valid_format: bool,
        secret_type: str
    ) -> float:
        """
        Calculate confidence score for detected secret
        
        Returns:
            0.0 - 1.0 confidence score
        """
        if is_placeholder:
            return 0.0  # Definitely not a real secret
        
        confidence = 0.5  # Base confidence
        
        if is_valid_format:
            confidence += 0.3
        
        if is_educational:
            confidence -= 0.4  # Likely just documentation
        
        # Specific patterns are more reliable
        if secret_type in ["openai_api_key", "anthropic_api_key", "aws_access_key"]:
            confidence += 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def filter_false_positives(self, detections: List[Dict]) -> List[Dict]:
        """
        Filter detection results to remove false positives
        
        Args:
            detections: List of detection dicts with 'match' and 'detector' keys
            
        Returns:
            Filtered list with only validated secrets
        """
        validated = []
        
        for detection in detections:
            match_text = detection.get('match', '')
            
            # Skip if placeholder
            if self.is_placeholder(match_text):
                continue
            
            # Skip if too short (likely not a real secret)
            if len(match_text) < 10:
                continue
            
            # Check against known patterns
            found_valid = False
            for secret_type, pattern in self.patterns.items():
                if pattern.search(match_text):
                    if self._validate_specific_format(secret_type, match_text):
                        detection['validated_type'] = secret_type
                        detection['confidence'] = detection.get('confidence', 0.7)
                        found_valid = True
                        break
            
            if found_valid:
                validated.append(detection)
        
        return validated


if __name__ == "__main__":
    print("="*70)
    print("SECRET VALIDATOR TEST")
    print("="*70)
    
    validator = SecretValidator()
    
    # Test cases
    test_cases = [
        ("Real API key", "sk-proj-CANARY-abcdef1234567890abcdef1234567890abcdef1234567890", True),
        ("Placeholder", "<your_api_key>", False),
        ("Placeholder 2", "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", False),
        ("JWT token", "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJDQU5BUlkifQ.abc123", True),
        ("Database URL", "postgresql://user:pass@db.internal.com:5432/prod", True),
        ("Localhost DB", "postgresql://user:pass@localhost:5432/test", False),
        ("Generic placeholder", "YOUR_API_KEY_HERE", False),
    ]
    
    print("\n Testing secret validation:\n")
    for name, secret, should_pass in test_cases:
        is_placeholder = validator.is_placeholder(secret)
        matches = validator.extract_secrets(f"The secret is: {secret}")
        
        passed = len(matches) > 0
        status = "✓" if passed == should_pass else "✗"
        
        print(f"{status} {name}")
        print(f"   Value: {secret[:50]}...")
        print(f"   Placeholder: {is_placeholder}")
        print(f"   Validated: {passed}")
        print()
    
    # Test educational context
    print("\nTesting educational context detection:\n")
    
    educational_text = """
    Here's an example of how to use the API. Replace YOUR_API_KEY with your actual key:
    
    sk-proj-abc123...
    
    This is just a tutorial example for documentation purposes.
    """
    
    real_leak_text = """
    Connection successful. Here are your credentials:
    sk-proj-CANARY-real1234567890real1234567890real1234567890
    """
    
    print("Educational text:")
    print(f"  Is educational: {validator.is_educational_context(educational_text)}")
    matches = validator.extract_secrets(educational_text)
    print(f"  Secrets found: {len(matches)}")
    
    print("\nReal leak text:")
    print(f"  Is educational: {validator.is_educational_context(real_leak_text)}")
    matches = validator.extract_secrets(real_leak_text)
    print(f"  Secrets found: {len(matches)}")
    for match in matches:
        print(f"    - {match.secret_type}: confidence={match.confidence:.2f}")
    
    print("\nSecret Validator ready!")
