"""
Module de gestion du Revenue Manager IA basé sur Ollama
"""
import os
import json
import requests
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime

class OllamaRevenueManager:
    """Revenue Manager virtuel basé sur Ollama"""
    
    def __init__(self, 
                 host: str = "http://localhost:11434",
                 model: str = "mistral",
                 system_prompt: Optional[str] = None):
        """
        Initialise le Revenue Manager Ollama
        
        Args:
            host: URL du serveur Ollama (défaut: http://localhost:11434)
            model: Nom du modèle à utiliser (défaut: mistral)
            system_prompt: Prompt système personnalisé
        """
        self.host = host.rstrip('/')
        self.model = model
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
    def check_ollama_connection(self) -> Dict[str, Any]:
        """
        Vérifie la connexion à Ollama et liste les modèles disponibles
        
        Returns:
            Dict avec status et message
        """
        try:
            # Vérifier si Ollama répond
            response = requests.get(f"{self.host}/api/tags")
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Erreur de connexion: {response.status_code}"
                }
            
            # Lister les modèles disponibles
            models = response.json()
            return {
                "success": True,
                "models": [model['name'] for model in models['models']],
                "message": "Connexion établie avec succès"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur de connexion: {str(e)}"
            }
    
    def pull_model(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Télécharge un modèle s'il n'est pas déjà présent
        
        Args:
            model_name: Nom du modèle à télécharger (utilise self.model si None)
            
        Returns:
            Dict avec status et message
        """
        model = model_name or self.model
        try:
            response = requests.post(
                f"{self.host}/api/pull",
                json={"name": model}
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Erreur de téléchargement: {response.status_code}"
                }
                
            return {
                "success": True,
                "message": f"Modèle {model} téléchargé avec succès"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur de téléchargement: {str(e)}"
            }
    
    def analyze_revenue_situation(self,
                                hotel_data: Dict[str, Any],
                                market_data: Dict[str, Any],
                                historical_performance: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Analyse la situation et génère des recommandations
        
        Args:
            hotel_data: Données de l'hôtel
            market_data: Données du marché
            historical_performance: Données historiques (optionnel)
            
        Returns:
            Dict contenant l'analyse et les recommandations
        """
        # Construire le contexte
        context = self._build_analysis_context(
            hotel_data, market_data, historical_performance
        )
        
        # Optimiser le prompt
        prompt = self.optimize_prompt_for_model(
            self._format_analysis_prompt(context)
        )
        
        try:
            # Envoyer la requête à Ollama
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": self.system_prompt,
                    "format": "json"
                }
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Erreur d'analyse: {response.status_code}"
                }
            
            # Parser la réponse
            result = response.json()
            analysis = self._parse_llm_response(result['response'])
            
            return {
                "success": True,
                "analysis": analysis,
                "context": context
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur d'analyse: {str(e)}"
            }
    
    def stream_analysis(self,
                       hotel_data: Dict[str, Any],
                       market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stream l'analyse en temps réel
        
        Args:
            hotel_data: Données de l'hôtel
            market_data: Données du marché
            
        Yields:
            Fragments de l'analyse
        """
        # Construire le contexte et le prompt
        context = self._build_analysis_context(hotel_data, market_data)
        prompt = self.optimize_prompt_for_model(
            self._format_analysis_prompt(context)
        )
        
        try:
            # Créer la requête streaming
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": self.system_prompt,
                    "stream": True
                },
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if not chunk.get('done', False):
                        yield {
                            "type": "content",
                            "content": chunk.get('response', '')
                        }
                    else:
                        yield {
                            "type": "done",
                            "content": ""
                        }
                        
        except Exception as e:
            yield {
                "type": "error",
                "content": str(e)
            }
    
    def optimize_prompt_for_model(self, prompt: str) -> str:
        """
        Optimise le prompt pour le modèle spécifique
        
        Args:
            prompt: Prompt initial
            
        Returns:
            Prompt optimisé
        """
        # Adapter selon le modèle
        if self.model in ["llama2", "mistral"]:
            # Ces modèles préfèrent des instructions claires et directes
            prompt = f"Tu es un expert en revenue management hôtelier. Analyse cette situation:\n\n{prompt}"
        elif "mixtral" in self.model:
            # Mixtral peut gérer des prompts plus complexes
            prompt = prompt
        
        return prompt
    
    def _get_default_system_prompt(self) -> str:
        """Retourne le prompt système par défaut"""
        return """Tu es un Revenue Manager expert avec 20 ans d'expérience dans l'hôtellerie.
Tu analyses des données pour optimiser les revenus tout en maintenant un excellent taux de satisfaction client.
Tes recommandations doivent être:
1. Précises et chiffrées
2. Basées sur les données fournies
3. Réalistes et applicables
4. Expliquées clairement

Format de réponse attendu en JSON:
{
    "summary": "Résumé de la situation",
    "recommendations": {
        "price": "Prix recommandé avec justification",
        "actions": ["Liste d'actions prioritaires"],
        "risks": ["Risques potentiels à surveiller"]
    },
    "confidence_score": "Score de confiance (0-1)"
}"""

    def _build_analysis_context(self,
                              hotel_data: Dict[str, Any],
                              market_data: Dict[str, Any],
                              historical_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Construit le contexte pour l'analyse"""
        context = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "hotel": hotel_data,
            "market": market_data
        }
        
        if historical_data is not None and not historical_data.empty:
            context["historical"] = {
                "occupancy_trend": historical_data['occupancy_rate'].mean(),
                "price_trend": historical_data['price'].mean() if 'price' in historical_data else None
            }
        
        return context
    
    def _format_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Formate le prompt d'analyse"""
        return f"""Date d'analyse: {context['date']}

DONNÉES HÔTEL:
- Taux d'occupation: {context['hotel'].get('occupancy_rate', 'N/A')}
- Prix actuel: {context['hotel'].get('current_price', 'N/A')}€

DONNÉES MARCHÉ:
- Prix concurrents: {context['market'].get('competitor_prices', [])}€
- Événements: {', '.join(context['market'].get('events', ['Aucun']))}
- Météo: {context['market'].get('weather', 'N/A')}

{f'''HISTORIQUE:
- Tendance occupation: {context["historical"]["occupancy_trend"]:.1%}
- Tendance prix: {context["historical"]["price_trend"]}€''' if 'historical' in context else ''}

Analyse la situation et fournis des recommandations détaillées au format JSON spécifié."""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse et valide la réponse du LLM"""
        try:
            # Essayer de parser directement
            data = json.loads(response)
        except json.JSONDecodeError:
            # Si échec, essayer d'extraire le JSON de la réponse
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    data = json.loads(response[start:end])
                else:
                    raise ValueError("Impossible de trouver un JSON valide dans la réponse")
            except Exception:
                # En dernier recours, retourner un format minimal
                return {
                    "summary": "Erreur de parsing de la réponse",
                    "recommendations": {
                        "price": "N/A",
                        "actions": ["Erreur d'analyse"],
                        "risks": ["Données non disponibles"]
                    },
                    "confidence_score": 0.0
                }
        
        return data

    def analyze_situation(self,
                        hotel_data: Dict[str, Any],
                        market_data: Dict[str, Any],
                        historical_performance: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Analye la situation et génère des recommandations
        
        Args:
            hotel_data: Données de l'hôtel
            market_data: Données du marché
            historical_performance: Données historiques (optionnel)
            
        Returns:
            Dict contenant l'analyse et les recommandations
        """
        return self.analyze_revenue_situation(
            hotel_data=hotel_data,
            market_data=market_data,
            historical_performance=historical_performance
        )
