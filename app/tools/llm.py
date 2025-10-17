from abc import ABC, abstractmethod
import os
from google import genai

class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

class GeminiLLM(BaseLLM):
    def __init__(self, model_name: str = None, api_key: str = None):
        self.client = genai.Client(api_key=api_key)
        self.model = self.client.models
        self.model_name = model_name

    def generate(self, prompt) -> str:
        """
        Generate a query using the Gemini model.
        """
        response = self.model.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        return response.text.strip()
    
    
def get_llm(provider: str ="GEMINI", model_name: str ="gemini-2.0-flash", api_key: str =None) -> BaseLLM:
    provider = provider.lower()
    if provider == "gemini":
        return GeminiLLM(model_name, api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")