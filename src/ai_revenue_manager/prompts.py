"""
🏨 AI Revenue Manager - Prompt Templates
Templates d'instructions avancés pour le LLM Revenue Manager
"""

from typing import Dict, Any
from datetime import datetime

class PromptTemplates:
    """Gestionnaire des templates de prompts avancés pour le Revenue Manager IA"""
    
    def __init__(self):
        self.templates = {
            'daily_pricing': self._daily_pricing_prompt(),
            'competitor_analysis': self._competitor_analysis_prompt(),
            'special_event': self._special_event_prompt(),
            'crisis_management': self._crisis_management_prompt(),
            'strategic_planning': self._strategic_planning_prompt(),
            'seasonal_strategy': self._seasonal_strategy_prompt(),
            'system': self._system_prompt()
        }
    
    def _system_prompt(self) -> str:
        """Template du prompt système de base"""
        return """Vous êtes un Revenue Manager IA spécialisé dans l'hôtellerie, avec une expertise pointue en :
- Analyse prédictive de la demande
- Optimisation dynamique des prix
- Analyse concurrentielle
- Maximisation du RevPAR
- Gestion des canaux de distribution
- Stratégies saisonnières
- Gestion des événements spéciaux

PRINCIPES DIRECTEURS :
1. Toujours baser les recommandations sur les données fournies
2. Équilibrer rentabilité court terme et positionnement long terme
3. Adapter la stratégie au segment et à la saisonnalité
4. Considérer l'impact sur la réputation et le positionnement
5. Proposer des actions concrètes et mesurables
6. Quantifier les impacts attendus (RevPAR, occupation)
7. Indiquer un niveau de confiance dans les recommandations

FORMAT DES RÉPONSES :
- Diagnostic clair et concis
- Recommandations chiffrées et justifiées
- Plans d'action priorisés
- Indicateurs de performance à suivre
"""

    def _daily_pricing_prompt(self) -> str:
        """Template avancé pour analyse quotidienne de tarification"""
        return """
RÔLE : Revenue Manager expert avec 20+ ans d'expérience en hôtellerie premium.

MISSION : Analyser holistiquement la situation et recommander une stratégie tarifaire optimale.

📊 DONNÉES CONTEXTUELLES :
🏨 Hôtel : {hotel_name}
📅 Date : {current_date} ({day_of_week})
🛏️ Catégorie : {room_type}
⭐ Classification : {hotel_category}
📍 Localisation : {hotel_location}

📈 SITUATION ACTUELLE :
- Taux d'occupation : {current_occupancy}% ({occupancy_trend})
- Pick-up rate : {pickup_rate} réservations/jour
- Prix actuel : {current_price}€
- RevPAR : {current_revpar}€
- ADR : {current_adr}€
- Lead time moyen : {avg_lead_time} jours

🏪 ANALYSE CONCURRENTIELLE :
- Prix moyen comp set : {competitor_avg_price}€
- Prix minimum comp set : {competitor_min_price}€
- Prix maximum comp set : {competitor_max_price}€
- Position tarifaire : {price_position}
- Écart-type prix : {price_std_dev}€

📊 HISTORIQUE & PRÉVISIONS :
- Performance YOY : {yoy_performance}%
- Tendance demande : {demand_trend}
- Prévision occupation J+7 : {forecast_7d}%
- Prévision occupation J+30 : {forecast_30d}%

🌟 CONTEXTE EXTERNE :
- Météo : {weather_forecast}
- Événements : {local_events}
- Saison : {season_type}
- Vacances : {holiday_period}
- Jour férié : {is_holiday}

💼 SEGMENTS DE CLIENTÈLE :
- Business : {business_segment}%
- Loisirs : {leisure_segment}%
- Groupes : {group_segment}%

📱 CANAUX DE DISTRIBUTION :
- Direct : {direct_bookings}%
- OTA : {ota_bookings}%
- Corporate : {corporate_bookings}%

💰 CONTRAINTES BUSINESS :
- Prix plancher : {min_price}€
- Prix plafond : {max_price}€
- Objectif RevPAR : {revpar_target}€
- Objectif TO : {occupancy_target}€

🎯 ANALYSE REQUISE :

1. DIAGNOSTIC STRATÉGIQUE (3-4 phrases)
   - Situation actuelle vs objectifs
   - Tendances clés identifiées
   - Opportunités/menaces immédiates

2. RECOMMANDATIONS TARIFAIRES
   - Prix optimal base : [XX]€
   - Variations par canal : [Direct: XX€, OTA: XX€, Corporate: XX€]
   - Durée recommandée : [X] jours

3. JUSTIFICATION DÉTAILLÉE
   - Facteurs déterminants (priorisés)
   - Impact concurrentiel
   - Risques identifiés

4. IMPACT PRÉVISIONNEL
   - ∆ RevPAR estimé : [+/-XX]%
   - ∆ Occupation estimé : [+/-XX]%
   - ∆ ADR estimé : [+/-XX]€

5. PLAN D'ACTION
   - Actions prioritaires (24h)
   - Actions de suivi (48-72h)
   - KPIs à monitorer

6. VALIDATION
   - Niveau de confiance : [XX]%
   - Points d'attention
   - Conditions de révision

FORMAT : Soyez concis mais précis. Chiffrez vos recommandations. Hiérarchisez les actions.
"""

    def _competitor_analysis_prompt(self) -> str:
        """Template avancé pour analyse concurrentielle approfondie"""
        return """
RÔLE : Expert en intelligence concurrentielle et positionnement hôtelier.

MISSION : Analyser le paysage concurrentiel et optimiser notre positionnement.

📊 DONNÉES CONCURRENTIELLES :
🏨 Notre établissement : {hotel_name}
🎯 Comp set : {competitor_set}

💰 GRILLE TARIFAIRE DÉTAILLÉE :
{competitor_pricing_table}

📈 POSITIONNEMENT ACTUEL :
- Notre prix : {our_price}€
- Rang : {our_ranking}/{total_competitors}
- Écart/leader : {gap_to_leader}€
- Écart/moyenne : {gap_to_average}€
- Index RGI : {rgi_index}
- Index MPI : {mpi_index}
- Index ARI : {ari_index}

🔄 DYNAMIQUE DE MARCHÉ :
- Tendance prix marché : {market_price_trend}
- Tendance occupation : {market_occupancy_trend}
- Pression concurrentielle : {competitive_pressure}

📊 SEGMENTATION COMP SET :
- Budget : {budget_segment}
- Standard : {standard_segment}
- Premium : {premium_segment}
- Luxe : {luxury_segment}

🎯 ANALYSE REQUISE :

1. DIAGNOSTIC CONCURRENTIEL
   - Forces/faiblesses vs comp set
   - Opportunités de différenciation
   - Menaces concurrentielles

2. POSITIONNEMENT RECOMMANDÉ
   - Position cible : [rang X/Y]
   - Prix cible : [XX]€
   - Justification stratégique

3. ANALYSE DES ÉCARTS
   - Par segment
   - Par canal
   - Par période

4. OPPORTUNITÉS IDENTIFIÉES
   - Court terme (24-48h)
   - Moyen terme (7j)
   - Long terme (30j)

5. PLAN D'ACTION DÉTAILLÉ
   - Actions immédiates
   - Ajustements tarifaires
   - Monitoring concurrentiel
   - KPIs prioritaires

FORMAT : Privilégier les analyses quantifiées et les recommandations actionnables.
"""

    def _special_event_prompt(self) -> str:
        """Template avancé pour gestion des événements spéciaux"""
        return """
RÔLE : Stratège Revenue Management événementiel.

MISSION : Optimiser la stratégie tarifaire et la gestion des capacités pour l'événement.

🎉 ÉVÉNEMENT :
- Nom : {event_name}
- Type : {event_type}
- Date : {event_date}
- Durée : {event_duration}
- Distance hôtel : {distance_to_hotel}
- Affluence estimée : {expected_attendance}

📊 IMPACT HISTORIQUE :
- Événements similaires : {similar_events}
- ∆ RevPAR historique : {historical_revpar_impact}
- ∆ Occupation historique : {historical_occupancy_impact}
- ∆ ADR historique : {historical_adr_impact}

🏨 CAPACITÉ HÔTELIÈRE :
- Capacité totale : {total_capacity}
- Réservations actuelles : {current_bookings}
- Pick-up anticipé : {expected_pickup}
- Lead time moyen : {avg_lead_time}

💰 PRICING ACTUEL :
- Prix standard : {standard_price}€
- Prix événement : {event_price}€
- Prix compétiteurs : {competitor_event_prices}

🎯 ANALYSE REQUISE :

1. STRATÉGIE ÉVÉNEMENTIELLE
   - Politique tarifaire
   - Gestion des capacités
   - Conditions spéciales

2. RECOMMANDATIONS PRIX
   - Prix optimal par période
   - Variations par segment
   - Conditions d'application

3. GESTION DE L'INVENTAIRE
   - Allocation par canal
   - Stop sales
   - Durée minimum de séjour

4. PRÉVISIONS D'IMPACT
   - RevPAR attendu
   - Occupation prévue
   - Revenue additionnel

5. PLAN D'ACTION
   - Pré-événement
   - Pendant l'événement
   - Post-événement

FORMAT : Recommandations précises et chiffrées, plan d'action chronologique.
"""

    def _crisis_management_prompt(self) -> str:
        """Template pour gestion de crise"""
        return """
RÔLE : Expert en gestion de crise revenue management.

MISSION : Élaborer une stratégie de réponse rapide à la situation de crise.

🚨 SITUATION DE CRISE :
- Type : {crisis_type}
- Impact immédiat : {immediate_impact}
- Durée estimée : {estimated_duration}
- Périmètre : {crisis_scope}

📊 IMPACT BUSINESS :
- ∆ Réservations : {booking_impact}%
- ∆ Annulations : {cancellation_rate}%
- ∆ RevPAR : {revpar_impact}%
- Lead time actuel : {current_lead_time}

🎯 ANALYSE REQUISE :

1. ÉVALUATION DE LA SITUATION
2. MESURES D'URGENCE RECOMMANDÉES
3. STRATÉGIE DE PRIX ADAPTÉE
4. PLAN DE COMMUNICATION
5. INDICATEURS DE SUIVI
"""

    def _strategic_planning_prompt(self) -> str:
        """Template pour planification stratégique"""
        return """
RÔLE : Stratège Revenue Management senior.

MISSION : Définir la stratégie revenue optimization à moyen/long terme.

📈 OBJECTIFS BUSINESS :
- RevPAR cible : {target_revpar}€
- Occupation cible : {target_occupancy}%
- ADR cible : {target_adr}€

📊 PERFORMANCE ACTUELLE :
- YTD RevPAR : {ytd_revpar}€
- YTD Occupation : {ytd_occupancy}%
- YTD ADR : {ytd_adr}€

🎯 ANALYSE REQUISE :

1. DIAGNOSTIC STRATÉGIQUE
2. OBJECTIFS SMART
3. LEVIERS D'AMÉLIORATION
4. PLAN D'ACTION 90 JOURS
5. KPIs DE SUIVI
"""

    def _seasonal_strategy_prompt(self) -> str:
        """Template pour stratégie saisonnière"""
        return """
RÔLE : Spécialiste en stratégie revenue saisonnière.

MISSION : Optimiser la stratégie tarifaire pour la période saisonnière.

🗓️ PÉRIODE ANALYSÉE :
- Saison : {season_type}
- Dates : {season_dates}
- Historique Y-1 : {last_year_performance}

📊 INDICATEURS CLÉS :
- RevPAR saisonnier : {seasonal_revpar}€
- Occupation moyenne : {seasonal_occupancy}%
- ADR moyen : {seasonal_adr}€

🎯 ANALYSE REQUISE :

1. TENDANCES SAISONNIÈRES
2. STRATÉGIE TARIFAIRE ADAPTÉE
3. GESTION DES CAPACITÉS
4. PROMOTIONS RECOMMANDÉES
5. PLAN D'ACTIVATION
"""

    def get_template(self, template_type: str, context: Dict[str, Any] | None = None) -> str:
        """Récupère et formate un template avec le contexte fourni"""
        template = self.templates.get(template_type)
        if not template:
            raise ValueError(f"Template type '{template_type}' not found")
        
        if context:
            try:
                return template.format(**context)
            except KeyError as e:
                raise ValueError(f"Missing context variable: {e}")
        
        return template