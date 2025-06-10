from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import Dict, Any, List
import yaml
import pandas as pd
import numpy as np
from datetime import datetime

class AIRevenueManager:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.llm = self._initialize_llm()
        self._load_prompts()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _initialize_llm(self):
        """Initialise le modèle Ollama localement"""
        return Ollama(
            model=self.config.get('llm', {}).get('model', 'mistral:7b-instruct'),
            temperature=self.config.get('llm', {}).get('temperature', 0.7)
        )

    def _load_prompts(self):
        """Charge les templates de prompts"""
        self.prompts = {
            'daily_pricing': """Analyse les données suivantes pour recommander une stratégie de tarification:
- Occupation actuelle: {occupancy}%
- Prix actuel: {price}€
- Prix moyen concurrents: {avg_competitor_price}€
- Tendance: {trend}
- Événements: {events}
Fournis une recommandation de prix et une stratégie détaillée."""
        }

    def analyze_situation(self, hotel_data: Dict, market_data: Dict, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyse la situation et génère des recommandations"""
        # Préparation du contexte
        context = {
            'occupancy': hotel_data.get('occupancy_rate', 0) * 100,
            'price': hotel_data.get('current_price', 100),
            'avg_competitor_price': np.mean(market_data.get('competitor_prices', [100])),
            'trend': 'En hausse' if len(historical_data) > 1 and 
                     historical_data['price'].iloc[-1] > historical_data['price'].iloc[-2] else 'Stable ou en baisse',
            'events': ', '.join(market_data.get('events', [])) or 'Aucun'
        }

        # Création de la chaîne LLM
        prompt = ChatPromptTemplate.from_template(self.prompts['daily_pricing'])
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Appel au LLM
        response = chain.run(**context)
        
        return {
            'recommendation': response,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }