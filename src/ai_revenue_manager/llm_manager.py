# src/ai_revenue_manager/llm_manager.py
from typing import Dict, Any, List, Optional
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import yaml
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os

class AIRevenueManager:
    """
    Gestionnaire de revenus basé sur l'IA pour l'optimisation tarifaire hôtelière
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialise le gestionnaire de revenus
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.llm = self._initialize_llm()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier YAML"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def _initialize_llm(self):
        """Initialise le modèle de langage"""
        llm_config = self.config['llm']
        return ChatOllama(
            model=llm_config['model'],
            temperature=llm_config['temperature']
        )
        
    def analyze_situation(self,
                         hotel_data: Dict[str, Any],
                         market_data: Dict[str, Any],
                         historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse la situation actuelle et génère des recommandations
        
        Args:
            hotel_data: Données de l'hôtel (occupation, prix actuels, etc.)
            market_data: Données du marché (concurrents, événements, etc.)
            historical_data: Données historiques (pandas DataFrame)
            
        Returns:
            Dictionnaire contenant l'analyse et les recommandations
        """
        # Préparer le contexte
        context = self._prepare_context(hotel_data, market_data, historical_data)
        
        # Créer le prompt
        prompt = self._create_analysis_prompt(context)
        
        # Obtenir la réponse du LLM
        response = self.llm.invoke(prompt)
        
        # Parser la réponse
        return self._parse_response(response.content, context)
        
    def _prepare_context(self, 
                        hotel_data: Dict[str, Any],
                        market_data: Dict[str, Any],
                        historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Prépare le contexte pour l'analyse"""
        # Calculer les métriques clés
        current_occupancy = hotel_data.get('occupancy_rate', 0)
        competitor_prices = market_data.get('competitor_prices', [])
        avg_competitor_price = np.mean(competitor_prices) if competitor_prices else 0
        
        # Détecter les tendances (simplifié)
        if len(historical_data) >= 7:
            last_week = historical_data['occupancy_rate'].iloc[-7:].mean()
            occupancy_trend = "en hausse" if current_occupancy > last_week else "en baisse"
        else:
            occupancy_trend = "stable"
            
        return {
            'hotel_name': self.config['hotel']['name'],
            'current_occupancy': f"{current_occupancy*100:.1f}%",
            'current_price': hotel_data.get('current_price', 0),
            'competitor_avg_price': round(avg_competitor_price, 2),
            'occupancy_trend': occupancy_trend,
            'special_events': market_data.get('events', []),
            'weather': market_data.get('weather', 'Normal'),
            'day_of_week': datetime.now().strftime('%A')
        }
        
    def _create_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Crée le prompt pour l'analyse"""
        prompt = f"""
        Tu es un expert en revenue management hôtelier avec 20 ans d'expérience.
        Analyse la situation suivante et fournis des recommandations tarifaires.
        
        CONTEXTE:
        - Hôtel: {context['hotel_name']}
        - Occupation actuelle: {context['current_occupancy']} (tendance: {context['occupancy_trend']})
        - Prix actuel: {context['current_price']}€
        - Prix moyen concurrentiel: {context['competitor_avg_price']}€
        - Météo: {context['weather']}
        - Jour: {context['day_of_week']}
        
        ÉVÉNEMENTS À VENIR:
        {chr(10).join(context['special_events']) if context['special_events'] else 'Aucun événement à venir'}
        
        Donne une analyse détaillée et des recommandations concrètes.
        """
        return prompt
        
    def _parse_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse la réponse du LLM en un format structuré"""
        # Ici, vous pourriez ajouter une logique de parsing plus sophistiquée
        return {
            'summary': response,
            'recommended_actions': self._extract_actions(response),
            'price_recommendations': self._extract_prices(response)
        }
        
    def _extract_actions(self, response: str) -> List[str]:
        """Extrait les actions recommandées de la réponse"""
        # Implémentation simplifiée
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        return lines[:3]  # Retourne les 3 premières lignes non vides
        
    def _extract_prices(self, response: str) -> Dict[str, float]:
        """Extrait les recommandations de prix de la réponse"""
        # Implémentation simplifiée
        return {
            'standard': 200,  # À remplacer par une logique d'extraction réelle
            'premium': 250
        }
# src/ai_revenue_manager/llm_manager.py
from typing import Dict, Any, List, Optional
from langchain_ollama import ChatOllama  # Mise à jour de l'import
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import yaml
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os

# Le reste du code reste inchangé...
