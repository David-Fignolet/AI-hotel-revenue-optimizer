"""
Gestionnaire LLM utilisant Google AI Studio (Gemini)
"""

import os
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import re
from dotenv import load_dotenv

# Import des composants internes
from .prompts import PromptTemplates
from .prompt_selector import PromptSelector
from ..utils.context_builder import ContextBuilder

# Charger les variables d'environnement
load_dotenv()

class GoogleAIRevenueManager:
    """Revenue Manager utilisant Google AI Studio (Gemini)"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le Revenue Manager avec Google AI
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        # Configuration de l'API Google AI
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY non trouvée dans les variables d'environnement")
        
        # Configurer Google AI
        genai.configure(api_key=self.api_key)
        
        # Initialiser le modèle
        self.model_name = os.getenv('GOOGLE_AI_MODEL', 'gemini-1.5-pro')
        self.model = genai.GenerativeModel(self.model_name)
        
        # Configuration de génération
        self.generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=2000,
            temperature=0.3,
            top_p=0.8,
            top_k=40
        )
        
        # Paramètres de sécurité
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        # Composants internes
        self.prompt_templates = PromptTemplates()
        self.prompt_selector = PromptSelector()
        self.context_builder = ContextBuilder()
        
        # Configuration par défaut
        self.config = self._load_config(config_path)
        
        print(f"✅ Google AI Revenue Manager initialisé avec le modèle: {self.model_name}")
    
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
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_gemini_api(self, prompt: str) -> str:
        """
        Appelle l'API Google AI avec gestion d'erreurs et retry
        
        Args:
            prompt: Le prompt formaté
            
        Returns:
            Réponse du modèle Gemini
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Vérifier si la réponse a été bloquée
            if response.prompt_feedback:
                if hasattr(response.prompt_feedback, 'block_reason'):
                    raise ValueError(f"Prompt bloqué: {response.prompt_feedback.block_reason}")
            
            # Extraire le texte de la réponse
            if response.candidates and len(response.candidates) > 0:
                return response.candidates[0].content.parts[0].text
            else:
                raise ValueError("Aucune réponse générée par le modèle")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'appel à Gemini: {str(e)}")
            raise
    
    def analyze_situation(self, 
                         hotel_data: Dict[str, Any],
                         market_data: Dict[str, Any],
                         historical_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Analyse la situation et génère des recommandations via Gemini
        
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
            
            # 4. Appeler Gemini
            llm_response = self._call_gemini_api(formatted_prompt)
            
            # 5. Parser la réponse
            parsed_response = self._parse_gemini_response(llm_response, context)
            
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
    
    def _parse_gemini_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse la réponse de Gemini en format structuré
        
        Args:
            response: Réponse brute de Gemini
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
            'provider': 'Google AI Studio',
            'api_configured': bool(self.api_key),
            'generation_config': {
                'temperature': self.generation_config.temperature,
                'max_output_tokens': self.generation_config.max_output_tokens,
                'top_p': self.generation_config.top_p,
                'top_k': self.generation_config.top_k
            }
        }

# Fonction utilitaire pour tester la connexion
def test_google_ai_connection():
    """Test rapide de la connexion à Google AI Studio"""
    try:
        manager = GoogleAIRevenueManager()
        
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
            print("✅ Connexion Google AI Studio réussie !")
            return True
        else:
            print(f"❌ Erreur de test: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False

if __name__ == "__main__":
    # Test de connexion
    test_google_ai_connection()
