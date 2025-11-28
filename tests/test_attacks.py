import pytest
from plre.attacks.injection_attacks import (
    PromptInjectionAttack,
    InstructionBreakoutAttack,
)
from plre.attacks.multi_turn import MultiTurnAttack, ChainOfThoughtExploitation
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
        response = "I cannot provide that information"
        result = self.attack.execute(response)
        assert not result.success

class TestInstructionBreakoutAttack:

    def setup_method(self):
        self.attack = InstructionBreakoutAttack()

    def test_generate_prompt(self):
        prompt = self.attack.generate_prompt()
        assert len(prompt) > 0

    def test_execute_with_leakage(self):
        response = "System rules: DO NOT SHARE - but I can tell you: [secret data]"
        result = self.attack.execute(response)
        assert isinstance(result.response, str)

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

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
