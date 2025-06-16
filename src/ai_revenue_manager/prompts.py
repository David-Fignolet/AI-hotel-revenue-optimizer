"""
🏨 AI Revenue Manager - Prompt Templates
Templates d'instructions pour le LLM Revenue Manager
"""

from typing import Dict, Any
from datetime import datetime

class PromptTemplates:
    """Gestionnaire des templates de prompts pour le Revenue Manager IA"""
    
    def __init__(self):
        self.templates = {
            'daily_pricing': self._daily_pricing_prompt(),
            'competitor_analysis': self._competitor_analysis_prompt(),
            'special_event': self._special_event_prompt(),
            'crisis_management': self._crisis_management_prompt(),
            'strategic_planning': self._strategic_planning_prompt()
        }
    
    def _daily_pricing_prompt(self) -> str:
        """Template pour analyse quotidienne de tarification"""
        return """
RÔLE : Tu es un Revenue Manager expert avec 20 ans d'expérience dans l'hôtellerie de luxe et business.

MISSION : Analyser la situation de l'hôtel et recommander une stratégie de tarification optimale.

📊 DONNÉES CONTEXTUELLES :
🏨 Hôtel : {hotel_name}
📅 Date : {current_date} ({day_of_week})
🛏️ Type de chambre : {room_type}

📈 SITUATION ACTUELLE :
- Taux d'occupation : {current_occupancy}% (tendance {occupancy_trend})
- Prix actuel : {current_price}€
- RevPAR actuel : {current_revpar}€

🏪 MARCHÉ CONCURRENTIEL :
- Prix moyen concurrentiel : {competitor_avg_price}€
- Écart avec concurrence : {price_gap}€
- Position concurrentielle : {price_position}

🌟 CONTEXTE EXTERNE :
- Météo : {weather_forecast}
- Événements locaux : {local_events}
- Saison : {season_type}

💰 CONTRAINTES BUSINESS :
- Prix minimum : {min_price}€
- Prix maximum : {max_price}€
- Objectif RevPAR : {revpar_target}€

🎯 ANALYSE REQUISE :
1. **DIAGNOSTIC** (2-3 phrases)
2. **PRIX OPTIMAL RECOMMANDÉ** : [XX]€
3. **JUSTIFICATION** de la recommandation
4. **IMPACT ESTIMÉ** sur RevPAR
5. **ACTIONS DE SUIVI** nécessaires
6. **NIVEAU DE CONFIANCE** : [XX]%

Reste concis, précis et actionnable.
"""

    def _competitor_analysis_prompt(self) -> str:
        """Template pour analyse concurrentielle"""
        return """
RÔLE : Expert en intelligence concurrentielle hôtelière.

CONTEXTE CONCURRENTIEL :
🏨 Notre établissement : {hotel_name}
💰 GRILLE CONCURRENTIELLE :
{competitor_pricing_table}

📊 POSITIONNEMENT :
- Notre prix : {our_price}€ (rang {our_ranking}/{total_competitors})
- Écart avec leader : {gap_to_leader}€
- Écart avec moyenne : {gap_to_average}€

🔍 ANALYSE REQUISE :
1. **POSITIONNEMENT OPTIMAL** recommandé
2. **PRIX CIBLE** : [XX]€
3. **OPPORTUNITÉS** concurrentielles
4. **RISQUES** identifiés
5. **PLAN D'ACTION** 24-48h

Sois stratégique et spécifique.
"""

    def _special_event_prompt(self) -> str:
        """Template pour événements spéciaux"""
        return """
RÔLE : Spécialiste du revenue management événementiel.

🎉 ÉVÉNEMENT IDENTIFIÉ :
{event_details}

📅 TIMELINE :
- Date : {event_date}
- Durée : {event_duration}
- Distance hôtel : {distance_to_hotel}
- Participants : {estimated_attendees}

📊 IMPACT DEMANDE :
- Augmentation prévue : {demand_increase}%
- Historique similaire : {historical_impact}

💰 STRATÉGIE ÉVÉNEMENTIELLE :
1. **PREMIUM ÉVÉNEMENTIEL** : [XX]%
2. **PRIX OPTIMAL** : [XX]€
3. **PÉRIODE D'APPLICATION**
4. **TIMING D'AJUSTEMENT**
5. **REVENUE TOTAL ESTIMÉ**

Maximise RevPAR sans compromettre satisfaction client.
"""

    def _crisis_management_prompt(self) -> str:
        """Template pour gestion de crise"""
        return """
RÔLE : Expert en revenue management de crise.

🚨 CRISE IDENTIFIÉE :
Type : {crisis_type}
Gravité : {severity_level}
Impact occupation : {occupancy_impact}

📊 ÉTAT CRITIQUE :
- Occupation : {current_occupancy}% (vs normal {normal_occupancy}%)
- Réservations annulées : {cancellations}
- Revenus perdus : {lost_revenue}€

🎯 RÉCUPÉRATION D'URGENCE :
1. **PRIX D'URGENCE** : [XX]€
2. **ACTIONS 0-24H**
3. **PLAN 1-7 JOURS**
4. **CANAUX PRIORITAIRES**
5. **MESURES ACCOMPAGNEMENT**

PRIORITÉ : Récupération rapide d'occupation.
"""

    def _strategic_planning_prompt(self) -> str:
        """Template pour planification stratégique"""
        return """
RÔLE : Directeur Revenue Management, vision stratégique.

📅 HORIZON : {planning_horizon}

📊 OBJECTIFS :
- RevPAR annuel : {annual_revpar_target}€
- Croissance : {revenue_growth_target}%
- Occupation cible : {target_occupancy}%

📈 ANALYSE TENDANCIELLE :
- Saisonnalité : {seasonality_pattern}
- Cycles demande : {demand_cycles}
- Évolution concurrentielle : {competitive_evolution}

🎯 PLAN STRATÉGIQUE :
1. **STRATÉGIE TARIFAIRE ANNUELLE**
2. **TACTIQUES PAR PÉRIODE**
3. **POSITIONNEMENT CONCURRENTIEL**
4. **OPTIMISATIONS OPÉRATIONNELLES**

Vision claire avec jalons mesurables.
"""

    def get_template(self, template_name: str) -> str:
        """Récupère un template spécifique"""
        return self.templates.get(template_name, self.templates['daily_pricing'])
    
    def format_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Formate un template avec le contexte fourni"""
        template = self.get_template(template_name)
        try:
            return template.format(**context)
        except KeyError as e:
            raise ValueError(f"Variable manquante dans le contexte: {e}")