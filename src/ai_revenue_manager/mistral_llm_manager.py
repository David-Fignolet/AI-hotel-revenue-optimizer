"""
Gestionnaire LLM utilisant Mistral AI via Ollama
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import re
import requests
from dotenv import load_dotenv

# Import des composants internes
from .prompts import PromptTemplates
from .prompt_selector import PromptSelector
from ..utils.context_builder import ContextBuilder

# Charger les variables d'environnement
load_dotenv()

class MistralRevenueManager:
    """Revenue Manager utilisant Mistral via Ollama"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le Revenue Manager avec Mistral
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        self.model_name = os.getenv('MISTRAL_MODEL', 'mistral')
        self.api_base = "http://localhost:11434/api"
        
        # Configuration de génération
        self.generation_config = {
            'temperature': 0.3,
            'top_p': 0.8,
            'max_tokens': 2000,
            'stop': None
        }
        
        # Composants internes
        self.prompt_templates = PromptTemplates()
        self.prompt_selector = PromptSelector()
        self.context_builder = ContextBuilder()
        
        # Configuration par défaut
        self.config = self._load_config(config_path)
        
        # Vérifier la disponibilité d'Ollama
        self._check_ollama_available()
        
        print(f"✅ Mistral Revenue Manager initialisé avec le modèle: {self.model_name}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier ou les variables d'environnement"""
        return {
            'llm': {
                'model': self.model_name,
                'temperature': 0.3,
                'max_tokens': 2000
            },
            'hotel': {
                'name': os.getenv('HOTEL_NAME', 'Hotel Revenue Optimizer'),
                'category': os.getenv('HOTEL_CATEGORY', '4 étoiles'),
                'location': 'Centre-ville'
            }
        }
    
    def _check_ollama_available(self):
        """Vérifie si Ollama est disponible et si le modèle est installé"""
        try:
            # Vérifier si Ollama est en cours d'exécution
            response = requests.get(f"{self.api_base}/tags")
            if response.status_code != 200:
                raise ConnectionError("Ollama n'est pas en cours d'exécution")
            
            # Vérifier si le modèle est disponible
            models = response.json()
            model_exists = any(model['name'] == self.model_name for model in models['models'])
            
            if not model_exists:
                print(f"⚙️ Installation du modèle {self.model_name}...")
                self._install_model()
            
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Impossible de se connecter à Ollama. "
                "Assurez-vous qu'Ollama est installé et en cours d'exécution."
            )
    
    def _install_model(self):
        """Installe le modèle Mistral via Ollama"""
        try:
            response = requests.post(
                f"{self.api_base}/pull",
                json={"name": self.model_name}
            )
            
            if response.status_code != 200:
                raise Exception(f"Erreur lors de l'installation du modèle: {response.text}")
            
            print(f"✅ Modèle {self.model_name} installé avec succès")
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'installation du modèle: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_mistral_api(self, prompt: str) -> str:
        """
        Appelle l'API Ollama avec gestion d'erreurs et retry
        
        Args:
            prompt: Le prompt formaté
            
        Returns:
            Réponse du modèle Mistral
        """
        try:
            response = requests.post(
                f"{self.api_base}/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    **self.generation_config
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Erreur API: {response.text}")
            
            return response.json()['response']
            
        except Exception as e:
            print(f"❌ Erreur lors de l'appel à Mistral: {str(e)}")
            raise
    
    def analyze_situation(self, 
                         hotel_data: Dict[str, Any],
                         market_data: Dict[str, Any],
                         historical_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Analyse la situation et génère des recommandations via Mistral
        
        Args:
            hotel_data: Données de l'hôtel
            market_data: Données du marché
            historical_data: Données historiques (optionnel)
            
        Returns:
            Dictionnaire avec l'analyse et les recommandations
        """
        try:
            # 1. Construire le contexte
            context = self.context_builder.build_context(
                hotel_data, market_data, historical_data, self.config
            )
            
            # 2. Sélectionner le prompt optimal
            prompt_type = self.prompt_selector.select_prompt_type(context)
            
            # 3. Formater le prompt
            formatted_prompt = self.prompt_templates.format_template(
                prompt_type, context
            )
            
            print(f"🔍 Analyse en cours avec {prompt_type}...")
            
            # 4. Appeler Mistral
            llm_response = self._call_mistral_api(formatted_prompt)
            
            # 5. Parser la réponse
            parsed_response = self._parse_mistral_response(llm_response, context)
            
            return {
                'prompt_type': prompt_type,
                'context': context,
                'raw_response': llm_response,
                'analysis': parsed_response,
                'model_used': self.model_name,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Erreur dans l'analyse: {str(e)}")
            return {
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def _parse_mistral_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse la réponse de Mistral en format structuré
        
        Args:
            response: Réponse brute de Mistral
            context: Contexte utilisé pour la génération
            
        Returns:
            Dictionnaire structuré avec l'analyse
        """
        try:
            # Extraire le prix recommandé
            price_match = re.search(r'PRIX OPTIMAL RECOMMANDÉ.*?(\d+)€', response, re.IGNORECASE)
            recommended_price = float(price_match.group(1)) if price_match else None
            
            # Extraire le niveau de confiance
            confidence_match = re.search(r'NIVEAU DE CONFIANCE.*?(\d+)%', response, re.IGNORECASE)
            confidence_score = float(confidence_match.group(1)) / 100 if confidence_match else 0.8
            
            # Extraire l'impact estimé
            impact_match = re.search(r'IMPACT ESTIMÉ.*?([+-]?\d+\.?\d*)%', response, re.IGNORECASE)
            expected_impact = float(impact_match.group(1)) if impact_match else 0.0
            
            # Extraire les actions recommandées
            actions = self._extract_actions_from_response(response)
            
            # Extraire le diagnostic
            diagnostic_match = re.search(r'DIAGNOSTIC[:\s]+(.*?)(?=PRIX OPTIMAL|$)', response, re.IGNORECASE | re.DOTALL)
            diagnostic = diagnostic_match.group(1).strip() if diagnostic_match else ""
            
            return {
                'summary': response,
                'diagnostic': diagnostic,
                'recommended_price': recommended_price or float(context.get('current_price', 150)),
                'confidence_score': confidence_score,
                'expected_impact': expected_impact,
                'recommended_actions': actions,
                'pricing_strategy': self._extract_strategy(response),
                'risk_assessment': self._extract_risks(response)
            }
            
        except Exception as e:
            print(f"⚠️ Erreur lors du parsing: {str(e)}")
            # Retour par défaut en cas d'erreur de parsing
            return {
                'summary': response,
                'diagnostic': "Analyse générée avec succès",
                'recommended_price': float(context.get('current_price', 150)),
                'confidence_score': 0.7,
                'expected_impact': 0.0,
                'recommended_actions': ["Surveiller les métriques", "Ajuster si nécessaire"],
                'pricing_strategy': "Maintenir la stratégie actuelle",
                'risk_assessment': "Risque modéré"
            }
    
    def _extract_actions_from_response(self, response: str) -> List[str]:
        """Extrait les actions recommandées de la réponse"""
        actions = []
        
        # Rechercher les listes avec puces ou numéros
        action_patterns = [
            r'[-•]\s*([^-•\n]+)',
            r'\d+\.\s*([^\d\n]+)',
            r'ACTIONS?\s*[:\-]\s*\n?(.*?)(?=\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE | re.MULTILINE)
            actions.extend([action.strip() for action in matches if action.strip()])
        
        # Nettoyer et limiter à 5 actions
        unique_actions = []
        for action in actions:
            if len(action) > 10 and action not in unique_actions:
                unique_actions.append(action)
        
        return unique_actions[:5]
    
    def _extract_strategy(self, response: str) -> str:
        """Extrait la stratégie de pricing de la réponse"""
        strategy_match = re.search(r'STRATÉGIE[:\s]+(.*?)(?=\n[A-Z]|$)', response, re.IGNORECASE | re.DOTALL)
        return strategy_match.group(1).strip() if strategy_match else "Stratégie d'optimisation continue"
    
    def _extract_risks(self, response: str) -> str:
        """Extrait l'évaluation des risques de la réponse"""
        risk_match = re.search(r'RISQUE[S]?[:\s]+(.*?)(?=\n[A-Z]|$)', response, re.IGNORECASE | re.DOTALL)
        return risk_match.group(1).strip() if risk_match else "Risque standard"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le modèle utilisé"""
        return {
            'model_name': self.model_name,
            'provider': 'Mistral (Ollama)',
            'api_base': self.api_base,
            'generation_config': self.generation_config
        }


# Fonction utilitaire pour tester la connexion
def test_mistral_connection():
    """Test rapide de la connexion à Mistral via Ollama"""
    try:
        manager = MistralRevenueManager()
        
        # Test simple
        test_data = {
            'occupancy_rate': 0.7,
            'current_price': 150
        }
        
        market_data = {
            'competitor_prices': [145, 155, 160],
            'events': [],
            'weather': 'Normal'
        }
        
        result = manager.analyze_situation(test_data, market_data)
        
        if result.get('success'):
            print("✅ Connexion Mistral réussie !")
            return True
        else:
            print(f"❌ Erreur de test: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False

if __name__ == "__main__":
    # Test de connexion
    test_mistral_connection()
