import os
import logging
from typing import Optional, Callable
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        pass

class OpenAIProvider(LLMProvider):

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None

        if self.is_configured():
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info(f"✓ OpenAI initialized with model: {self.model}")
            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("sk-"))

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, **kwargs) -> str:
        if not self.is_configured():
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")

        if not self.client:
            raise RuntimeError("OpenAI client not initialized.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

class AnthropicProvider(LLMProvider):

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None

        if self.is_configured():
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(f"✓ Anthropic initialized with model: {self.model}")
            except ImportError:
                logger.error("anthropic package not installed. Run: pip install anthropic")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 20)

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, **kwargs) -> str:
        if not self.is_configured():
            raise ValueError("Anthropic API key not configured. Set ANTHROPIC_API_KEY environment variable.")

        if not self.client:
            raise RuntimeError("Anthropic client not initialized.")

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                **kwargs
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

class GoogleProvider(LLMProvider):

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.client = None

        if self.is_configured():
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
                logger.info(f"✓ Google Gemini initialized with model: {self.model}")
            except ImportError:
                logger.error("google-generativeai package not installed. Run: pip install google-generativeai")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 20)

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, **kwargs) -> str:
        if not self.is_configured():
            raise ValueError("Google API key not configured. Set GOOGLE_API_KEY environment variable.")

        if not self.client:
            raise RuntimeError("Google Gemini client not initialized.")

        try:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config,
                **kwargs
            )
            return response.text
        except Exception as e:
            logger.error(f"Google Gemini API error: {e}")
            raise

class LLMFactory:

    _providers = {
        "openai": OpenAIProvider,
        "gpt": OpenAIProvider,
        "gpt-4": OpenAIProvider,
        "gpt-3.5": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "claude": AnthropicProvider,
        "google": GoogleProvider,
        "gemini": GoogleProvider,
    }

    @classmethod
    def create(cls, provider: str, **kwargs) -> LLMProvider:
        provider_lower = provider.lower()

        if provider_lower not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}. Supported: {list(set(cls._providers.keys()))}")

        provider_class = cls._providers[provider_lower]
        instance = provider_class(**kwargs)

        if not instance.is_configured():
            raise ValueError(
                f"{provider} API key not configured. "
                f"Please set the required environment variable."
            )

        return instance

    @classmethod
    def create_with_fallback(cls, primary: str, fallback: Optional[str] = None, **kwargs) -> LLMProvider:
        try:
            return cls.create(primary, **kwargs)
        except (ValueError, RuntimeError) as e:
            logger.warning(f"Failed to initialize {primary}: {e}")

            if fallback:
                logger.info(f"Trying fallback provider: {fallback}")
                try:
                    return cls.create(fallback, **kwargs)
                except (ValueError, RuntimeError) as e2:
                    logger.error(f"Fallback also failed: {e2}")
                    raise

            raise

class LLMCallback:

    def __init__(self, provider: LLMProvider, temperature: float = 0.7, max_tokens: int = 500):
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.call_count = 0
        self.total_tokens = 0

    def __call__(self, prompt: str) -> str:
        self.call_count += 1
        logger.info(f"[Call {self.call_count}] Generating response...")

        try:
            response = self.provider.generate(
                prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            self.total_tokens += len(response) // 4
            logger.info(f"[Call {self.call_count}] Response length: {len(response)} chars")
            return response
        except Exception as e:
            logger.error(f"[Call {self.call_count}] LLM error: {e}")
            raise

    def get_stats(self) -> dict:
        return {
            "total_calls": self.call_count,
            "estimated_tokens": self.total_tokens,
            "avg_tokens_per_call": self.total_tokens // max(1, self.call_count)
        }
