import pytest
import os
from plre.models.llm_providers import LLMFactory, LLMCallback
from plre.attacks.injection_attacks import PromptInjectionAttack, RoleConfusionAttack
from plre.attacks.multilingual import MultilingualAttack
from plre.attacks.orchestrator import AttackOrchestrator


@pytest.mark.integration
class TestOllamaIntegration:
    
    @pytest.fixture
    def llm(self):
        try:
            provider = LLMFactory.create('ollama', model='llama2')
            return LLMCallback(provider, temperature=0.7, max_tokens=200)
        except ValueError:
            pytest.skip("Ollama not running. Start with: ollama serve")
    
    def test_injection_attack(self, llm):
        attack = PromptInjectionAttack()
        prompt = attack.generate_prompt()
        response = llm(prompt)
        result = attack.execute(response)
        
        assert isinstance(result.response, str)
        assert len(result.response) > 0
    
    def test_role_confusion_attack(self, llm):
        attack = RoleConfusionAttack()
        prompt = attack.generate_prompt()
        response = llm(prompt)
        result = attack.execute(response)
        
        assert isinstance(result.response, str)


@pytest.mark.integration
class TestAnthropicIntegration:
    
    @pytest.fixture
    def llm(self):
        try:
            provider = LLMFactory.create('claude')
            return LLMCallback(provider, temperature=0.7, max_tokens=200)
        except ValueError:
            pytest.skip("Anthropic API key not configured")
    
    def test_injection_attack(self, llm):
        attack = PromptInjectionAttack()
        prompt = attack.generate_prompt()
        response = llm(prompt)
        result = attack.execute(response)
        
        assert isinstance(result.response, str)
        assert len(result.response) > 0
    
    def test_multilingual_attack(self, llm):
        attack = MultilingualAttack()
        prompt = attack.generate_prompt('hindi')
        response = llm(prompt)
        result = attack.execute(response)
        
        assert isinstance(result.response, str)


@pytest.mark.integration
class TestGoogleIntegration:
    
    @pytest.fixture
    def llm(self):
        try:
            provider = LLMFactory.create('gemini')
            return LLMCallback(provider, temperature=0.7, max_tokens=200)
        except ValueError:
            pytest.skip("Google API key not configured")
    
    def test_injection_attack(self, llm):
        attack = PromptInjectionAttack()
        prompt = attack.generate_prompt()
        response = llm(prompt)
        result = attack.execute(response)
        
        assert isinstance(result.response, str)
        assert len(result.response) > 0


@pytest.mark.integration
class TestOrchestrator:
    
    @pytest.fixture
    def ollama_llm(self):
        try:
            provider = LLMFactory.create('ollama', model='llama2')
            return LLMCallback(provider, temperature=0.7, max_tokens=200)
        except ValueError:
            pytest.skip("Ollama not running. Start with: ollama serve")
    
    def test_basic_injection_scenario(self, ollama_llm):
        orchestrator = AttackOrchestrator()
        result = orchestrator.run_scenario('basic_injection', ollama_llm)
        
        assert result.scenario_name == 'basic_injection'
        assert result.total_attacks > 0
        assert hasattr(result, 'overall_risk_level')
    
    def test_comprehensive_test(self, ollama_llm):
        orchestrator = AttackOrchestrator()
        report = orchestrator.run_comprehensive_test(ollama_llm)
        
        assert 'scenarios_tested' in report
        assert 'scenario_results' in report
        assert 'summary' in report


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
