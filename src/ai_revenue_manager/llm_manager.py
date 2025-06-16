"""
Gestionnaire principal du LLM Revenue Manager - Version corrigée avec simulation dynamique
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd

# Import des composants internes
from .prompts import PromptTemplates
from .prompt_selector import PromptSelector

# Import avec gestion d'erreur
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils.context_builder import ContextBuilder
except ImportError:
    # Fallback basique si context_builder n'est pas trouvé
    class ContextBuilder:
        def build_context(self, hotel_data, market_data, historical_data, config):
            return {
                'hotel_name': 'Hotel Example',
                'current_occupancy': f"{hotel_data.get('occupancy_rate', 0.7) * 100:.1f}%",
                'current_price': str(hotel_data.get('current_price', 150)),
                'special_events': market_data.get('events', []),
                'local_events': ', '.join(market_data.get('events', [])) or 'Aucun'
            }

class AIRevenueManager:
    """Revenue Manager virtuel basé sur un LLM - Version avec simulation dynamique"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialise le Revenue Manager IA"""
        self.prompt_templates = PromptTemplates()
        self.prompt_selector = PromptSelector()
        self.context_builder = ContextBuilder()
        
        self.config = {
            'llm': {
                'model': 'gpt-4',
                'temperature': 0.3,
                'max_tokens': 2000
            },
            'hotel': {
                'name': 'Hotel Example',
                'category': '4 étoiles',
                'location': 'Centre-ville'
            }
        }
    
    def analyze_situation(self, 
                         hotel_data: Dict[str, Any],
                         market_data: Dict[str, Any],
                         historical_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Analyse la situation et génère des recommandations"""
        
        print("🔄 Démarrage analyse AI...")
        
        # 1. Construire le contexte
        context = self.context_builder.build_context(
            hotel_data, market_data, historical_data, self.config
        )
        print(f"✅ Contexte construit: {len(context)} variables")
        
        # 2. Sélectionner le prompt optimal
        prompt_type = self.prompt_selector.select_prompt_type(context)
        print(f"✅ Type de prompt sélectionné: {prompt_type}")
        
        # 3. Formater le prompt
        try:
            formatted_prompt = self.prompt_templates.format_template(
                prompt_type, context
            )
            print(f"✅ Prompt formaté: {len(formatted_prompt)} caractères")
        except Exception as e:
            print(f"❌ Erreur formatage prompt: {e}")
            # Fallback vers daily_pricing si erreur
            formatted_prompt = self.prompt_templates.format_template(
                'daily_pricing', context
            )
            prompt_type = 'daily_pricing'
        
        # 4. Simulation LLM dynamique selon le type
        llm_response = self._simulate_llm_response_dynamic(context, prompt_type)
        
        # 5. Parser la réponse
        parsed_response = self._parse_response(llm_response, context, prompt_type)
        
        return {
            'prompt_type': prompt_type,
            'context': context,
            'raw_response': llm_response,
            'analysis': parsed_response,
            'timestamp': datetime.now().isoformat()
        }
    
    def _simulate_llm_response_dynamic(self, context: Dict[str, Any], prompt_type: str) -> str:
        """Simule une réponse LLM dynamique selon le type de prompt et contexte"""
        
        current_price = float(context.get('current_price', 150))
        occupancy_str = context.get('current_occupancy', '70%')
        occupancy = float(occupancy_str.rstrip('%'))
        
        if prompt_type == 'crisis_management':
            # Stratégie de crise : prix bas, actions urgentes
            recommended_price = max(current_price * 0.7, float(context.get('min_price', 80)))
            confidence = 0.85
            impact = 15.0
            
            return f"""
DIAGNOSTIC : Situation critique avec occupation de {occupancy:.1f}%. Action immédiate requise pour stimuler la demande.

PRIX OPTIMAL RECOMMANDÉ : {recommended_price:.0f}€

JUSTIFICATION : Réduction substantielle du prix actuel de {current_price:.0f}€ nécessaire pour relancer les réservations. Stratégie de récupération rapide d'occupation.

IMPACT ESTIMÉ : +{impact}% d'occupation attendue avec cette stratégie agressive.

ACTIONS DE SUIVI :
- Mise en place immédiate du nouveau prix
- Campagne promotionnelle flash 48h
- Contact direct des anciens clients
- Surveillance intensive des réservations

NIVEAU DE CONFIANCE : {confidence:.0%}
"""
        
        elif prompt_type == 'special_event':
            # Stratégie événementielle : prix premium
            event_premium = 1.2 if context.get('special_events') else 1.1
            recommended_price = min(current_price * event_premium, float(context.get('max_price', 300)))
            confidence = 0.92
            impact = 8.5
            
            events = context.get('special_events', [])
            event_text = f"présence de {', '.join(events)}" if events else "contexte favorable"
            
            return f"""
DIAGNOSTIC : Situation favorable avec {event_text}. Opportunité d'optimisation tarifaire détectée.

PRIX OPTIMAL RECOMMANDÉ : {recommended_price:.0f}€

JUSTIFICATION : La {event_text} justifie un premium événementiel. Augmentation de {current_price:.0f}€ à {recommended_price:.0f}€ (+{((recommended_price/current_price-1)*100):+.1f}%) recommandée.

IMPACT ESTIMÉ : +{impact}% sur le RevPAR grâce au premium événementiel.

ACTIONS DE SUIVI :
- Application du premium dès maintenant
- Communication sur la valeur ajoutée
- Surveillance de la conversion
- Ajustement si résistance détectée

NIVEAU DE CONFIANCE : {confidence:.0%}
"""
        
        elif prompt_type == 'competitor_analysis':
            # Stratégie concurrentielle : alignement optimal
            competitor_avg = float(context.get('competitor_avg_price', current_price))
            price_gap = float(context.get('price_gap', '0').replace('+', ''))
            
            if price_gap > 0:
                # Nous sommes plus chers
                recommended_price = current_price - (abs(price_gap) * 0.5)
                strategy = "réduction pour améliorer la compétitivité"
            else:
                # Nous sommes moins chers
                recommended_price = current_price + (abs(price_gap) * 0.3)
                strategy = "augmentation modérée pour optimiser sans perdre l'avantage"
            
            confidence = 0.89
            impact = 6.2
            
            return f"""
DIAGNOSTIC : Analyse concurrentielle révèle un écart de {price_gap:+.0f}€ avec la moyenne marché ({competitor_avg:.0f}€).

PRIX OPTIMAL RECOMMANDÉ : {recommended_price:.0f}€

JUSTIFICATION : {strategy.capitalize()}. Positionnement optimal entre compétitivité et rentabilité.

IMPACT ESTIMÉ : +{impact}% sur le RevPAR avec ce repositionnement.

ACTIONS DE SUIVI :
- Ajustement tarifaire progressif
- Monitoring réaction concurrentielle
- Analyse des taux de conversion
- Veille prix continue

NIVEAU DE CONFIANCE : {confidence:.0%}
"""
        
        else:  # daily_pricing par défaut
            # Stratégie quotidienne : optimisation standard
            if occupancy < 50:
                recommended_price = current_price * 0.95  # Légère baisse
                strategy = "légère réduction pour stimuler la demande"
                impact = 4.2
            elif occupancy > 80:
                recommended_price = current_price * 1.05  # Légère hausse
                strategy = "optimisation à la hausse vu la forte demande"
                impact = 6.8
            else:
                recommended_price = current_price + 5  # Augmentation modérée
                strategy = "augmentation modérée pour optimiser le RevPAR"
                impact = 5.7
            
            confidence = 0.87
            
            return f"""
DIAGNOSTIC : Situation équilibrée avec occupation de {occupancy:.1f}%. Optimisation tarifaire possible.

PRIX OPTIMAL RECOMMANDÉ : {recommended_price:.0f}€

JUSTIFICATION : {strategy.capitalize()}. Le marché permet cette optimisation sans risque majeur sur l'occupation.

IMPACT ESTIMÉ : +{impact}% sur le RevPAR quotidien.

ACTIONS DE SUIVI :
- Surveillance du booking pace sur 48h
- Ajustement si résistance client détectée
- Monitoring de la réaction concurrentielle

NIVEAU DE CONFIANCE : {confidence:.0%}
"""
    
    def _parse_response(self, response: str, context: Dict[str, Any], prompt_type: str) -> Dict[str, Any]:
        """Parse la réponse simulée selon le type"""
        
        # Extraire le prix recommandé de la réponse
        import re
        price_match = re.search(r'PRIX OPTIMAL RECOMMANDÉ : (\d+)€', response)
        recommended_price = float(price_match.group(1)) if price_match else 150.0
        
        # Extraire le niveau de confiance
        confidence_match = re.search(r'NIVEAU DE CONFIANCE : (\d+)%', response)
        confidence = float(confidence_match.group(1)) / 100 if confidence_match else 0.85
        
        # Extraire l'impact estimé
        impact_match = re.search(r'\+(\d+\.?\d*)%', response)
        expected_impact = float(impact_match.group(1)) if impact_match else 5.0
        
        # Actions recommandées selon le type
        if prompt_type == 'crisis_management':
            actions = [
                'Mise en place immédiate du nouveau prix',
                'Campagne promotionnelle flash 48h',
                'Contact direct des anciens clients',
                'Surveillance intensive des réservations'
            ]
        elif prompt_type == 'special_event':
            actions = [
                'Application du premium dès maintenant',
                'Communication sur la valeur ajoutée',
                'Surveillance de la conversion',
                'Ajustement si résistance détectée'
            ]
        elif prompt_type == 'competitor_analysis':
            actions = [
                'Ajustement tarifaire progressif',
                'Monitoring réaction concurrentielle',
                'Analyse des taux de conversion',
                'Veille prix continue'
            ]
        else:  # daily_pricing
            actions = [
                'Surveillance du booking pace sur 48h',
                'Ajustement si résistance client détectée',
                'Monitoring de la réaction concurrentielle'
            ]
        
        return {
            'summary': response.strip(),
            'confidence_score': confidence,
            'recommended_price': recommended_price,
            'expected_impact': expected_impact,
            'recommended_actions': actions,
            'prompt_type_used': prompt_type
        }