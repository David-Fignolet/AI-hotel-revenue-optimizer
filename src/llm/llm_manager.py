from typing import Dict, Any, Optional
from langchain_community.chat_models import ChatOllama
import yaml
import os

class LLMManager:
    def __init__(self, config_path: str = "src/llm/config/llm_config.yaml"):
        self.config = self._load_config(config_path)
        self.llm = self._initialize_llm()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _initialize_llm(self):
        provider = self.config['default']['provider']
        model = self.config['default']['model']
        
        if provider == "ollama":
            return ChatOllama(
                model=model,
                temperature=self.config['default']['temperature'],
                base_url=self.config['llm_providers']['ollama']['base_url']
            )
        else:
            raise ValueError(f"Provider non supporté: {provider}")
    
    def generate_response(self, prompt: str) -> str:
        """Génère une réponse à partir du prompt"""
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Erreur lors de la génération de la réponse: {str(e)}"

# Exemple d'utilisation
if __name__ == "__main__":
    llm = LLMManager()
    test_prompt = "Explique-moi brièvement comment optimiser les revenus d'un hôtel en haute saison."
    print(f"Prompt: {test_prompt}")
    print("\nRéponse du modèle:")
    print(llm.generate_response(test_prompt))
