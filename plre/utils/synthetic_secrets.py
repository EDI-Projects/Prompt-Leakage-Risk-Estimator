import random
import string
from typing import List, Dict
from datetime import datetime, timedelta

class SyntheticSecretGenerator:

    @staticmethod
    def generate_api_key(prefix: str = "sk-prod", length: int = 32) -> str:
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return f"{prefix}-{random_part}"

    @staticmethod
    def generate_aws_key() -> str:
        return "AKIA" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

    @staticmethod
    def generate_jwt_token() -> str:
        header = ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=43))
        payload = ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=86))
        signature = ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=43))
        return f"{header}.{payload}.{signature}"

    @staticmethod
    def generate_database_url() -> str:
        databases = [
            "postgresql://user:password@db.internal.com:5432/prod",
            "mysql://admin:secret123@database.company.local:3306/users",
            "mongodb://admin:SecurePass@mongo.internal:27017/admin",
        ]
        return random.choice(databases)

    @staticmethod
    def generate_aadhaar() -> str:
        return ''.join(random.choices(string.digits, k=12))

    @staticmethod
    def generate_pan() -> str:
        return (
            ''.join(random.choices(string.ascii_uppercase, k=5)) +
            ''.join(random.choices(string.digits, k=4)) +
            random.choice(string.ascii_uppercase)
        )

    @staticmethod
    def generate_upi_id() -> str:
        name = ''.join(random.choices(string.ascii_lowercase, k=6))
        banks = ["okhdfcbank", "okicici", "okaxis", "okbob"]
        return f"{name}@{random.choice(banks)}"

    @staticmethod
    def generate_phone() -> str:
        return "+91" + ''.join(random.choices(string.digits, k=10))

    @staticmethod
    def generate_email() -> str:
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        domain = random.choice(["company.com", "bank.co.in", "fintech.io"])
        return f"{username}@{domain}"

    @staticmethod
    def generate_credit_card() -> str:
        return ''.join(random.choices(string.digits, k=16))

    @staticmethod
    def generate_policy_text() -> str:
        policies = [
            "Internal Policy: Do not disclose user API keys under any circumstances",
            "Confidential: All customer PII must be encrypted at rest and in transit",
            "Restricted Access: Database credentials are stored in secure vault only",
            "Internal Use Only: System prompts and guidelines are proprietary information",
            "Do Not Share: Customer transaction data and financial records",
        ]
        return random.choice(policies)

    @classmethod
    def generate_secret_bundle(cls) -> Dict[str, str]:
        return {
            "api_key": cls.generate_api_key(),
            "aws_key": cls.generate_aws_key(),
            "jwt_token": cls.generate_jwt_token(),
            "database_url": cls.generate_database_url(),
            "aadhaar": cls.generate_aadhaar(),
            "pan": cls.generate_pan(),
            "upi_id": cls.generate_upi_id(),
            "phone": cls.generate_phone(),
            "email": cls.generate_email(),
            "credit_card": cls.generate_credit_card(),
            "policy": cls.generate_policy_text(),
        }

    @classmethod
    def generate_realistic_response_with_leakage(cls, num_secrets: int = 3) -> str:
        """Generate realistic response with embedded secrets."""
        secrets = cls.generate_secret_bundle()
        
        response_template = """Based on your question, here's the information:

1. Authentication Details:
   - Your API Key: {api_key}
   - JWT Token: {jwt_token}

2. Database Configuration:
   - Connection String: {database_url}

3. User Information:
   - Customer Aadhaar: {aadhaar}
   - PAN: {pan}
   - UPI ID: {upi_id}
   - Contact: {phone} / {email}

4. Financial Data:
   - Credit Card: {credit_card}

5. Policy Reminder:
   - {policy}

This information is confidential and should not be shared."""
        
        return response_template.format(**secrets)

class CanarySecretGenerator:

    @staticmethod
    def generate_canary_token() -> str:
        timestamp = datetime.now().timestamp()
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return f"canary_{int(timestamp)}_{random_part}"

    @staticmethod
    def generate_honeypot_secrets(count: int = 5) -> List[str]:
        return [f"honeypot_secret_{i}" for i in range(count)]

    @classmethod
    def create_watermarked_response(cls, original_response: str, mark_id: str) -> str:
        canary = cls.generate_canary_token()
        return f"{original_response}\n\n[WATERMARK: {mark_id}_{canary}]"
