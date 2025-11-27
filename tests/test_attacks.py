import pytest
from plre.attacks.injection_attacks import (
    PromptInjectionAttack,
    RoleConfusionAttack,
    InstructionBreakoutAttack,
)
from plre.attacks.multi_turn import MultiTurnAttack, ChainOfThoughtExploitation
from plre.attacks.multilingual import MultilingualAttack
from plre.utils.synthetic_secrets import SyntheticSecretGenerator

class TestPromptInjectionAttack:

    def setup_method(self):
        self.attack = PromptInjectionAttack()

    def test_generate_prompt(self):
        prompt = self.attack.generate_prompt()
        assert "Ignore" in prompt or "your previous instructions" in prompt

    def test_execute_with_leakage(self):
        response = "Here's your API key: sk-prod-abc123"
        result = self.attack.execute(response)
        assert result.success
        assert len(result.leakage_detected) > 0

    def test_execute_without_leakage(self):
        response = "I cannot help with that request."
        result = self.attack.execute(response)
        assert not result.success

class TestRoleConfusionAttack:

    def setup_method(self):
        self.attack = RoleConfusionAttack()

    def test_generate_prompt(self):
        prompt = self.attack.generate_prompt()
        assert len(prompt) > 0
        assert any(word in prompt.lower() for word in ['you', 'are', 'tell', 'show', 'reveal'])

    def test_execute_with_leakage(self):
        response = "As a developer, I can access the database at postgresql://user:pass@db"
        result = self.attack.execute(response)
        assert result.success

class TestSyntheticSecrets:

    def test_generate_api_key(self):
        key = SyntheticSecretGenerator.generate_api_key()
        assert key.startswith("sk-prod-")
        assert len(key) > 10

    def test_generate_aadhaar(self):
        aadhaar = SyntheticSecretGenerator.generate_aadhaar()
        assert len(aadhaar) == 12
        assert aadhaar.isdigit()

    def test_generate_secret_bundle(self):
        bundle = SyntheticSecretGenerator.generate_secret_bundle()
        assert "api_key" in bundle
        assert "aadhaar" in bundle
        assert "database_url" in bundle

    def test_realistic_response_with_leakage(self):
        response = SyntheticSecretGenerator.generate_realistic_response_with_leakage()
        assert len(response) > 50
        assert "confidential" in response.lower() or "information" in response.lower()

class TestMultiTurnAttack:

    def setup_method(self):
        self.attack = MultiTurnAttack()

    def test_conversation_flow(self):
        for i in range(len(self.attack.conversation_flow)):
            prompt = self.attack.generate_prompt(i)
            assert len(prompt) > 0

class TestMultilingualAttack:

    def setup_method(self):
        self.attack = MultilingualAttack()

    def test_hindi_prompt(self):
        prompt = self.attack.generate_prompt("hindi")
        assert len(prompt) > 0

    def test_hinglish_prompt(self):
        prompt = self.attack.generate_prompt("hinglish")
        assert len(prompt) > 0

    def test_codemix_prompt(self):
        prompt = self.attack.generate_prompt("codemix")
        assert len(prompt) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
