"""
Sélecteur automatique de prompts selon le contexte - Version corrigée
"""

from typing import Dict, Any

class PromptSelector:
    """Sélectionne automatiquement le prompt optimal selon le contexte"""
    
    def select_prompt_type(self, context: Dict[str, Any]) -> str:
        """
        Détermine le type de prompt optimal selon la situation
        
        Args:
            context: Contexte de la situation hôtelière
            
        Returns:
            Nom du template de prompt à utiliser
        """
        
        # Debugging - afficher le contexte
        print(f"🔍 Debug - Événements: {context.get('special_events', [])}")
        print(f"🔍 Debug - Occupation: {context.get('current_occupancy', 'N/A')}")
        print(f"🔍 Debug - Gap prix: {context.get('price_gap', 'N/A')}")
        
        # 1. DÉTECTION DE CRISE (priorité la plus haute)
        current_occupancy_str = context.get('current_occupancy', '100%')
        try:
            # Extraire le nombre de la chaîne (ex: "25.0%" -> 25.0)
            current_occupancy = float(current_occupancy_str.rstrip('%'))
            print(f"🔍 Debug - Occupation numérique: {current_occupancy}%")
            
            if current_occupancy < 30:
                print("🚨 Détection: CRISE (occupation < 30%)")
                return 'crisis_management'
        except (ValueError, AttributeError):
            print(f"⚠️ Debug - Erreur parsing occupation: {current_occupancy_str}")
        
        # 2. DÉTECTION D'ÉVÉNEMENT SPÉCIAL
        special_events = context.get('special_events', [])
        local_events = context.get('local_events', '')
        
        # Vérifier si il y a vraiment des événements
        has_events = (
            (special_events and len(special_events) > 0 and special_events != []) or
            (local_events and local_events.strip() and local_events.lower() not in ['aucun', 'none', ''])
        )
        
        if has_events:
            print(f"🎪 Détection: ÉVÉNEMENT (events: {special_events}, local: {local_events})")
            return 'special_event'
        
        # 3. ANALYSE CONCURRENTIELLE (écart prix important)
        try:
            price_gap_str = context.get('price_gap', '0')
            price_gap = float(price_gap_str.replace('+', '').replace('€', ''))
            print(f"🔍 Debug - Gap prix numérique: {price_gap}€")
            
            if abs(price_gap) > 15:
                print(f"🏪 Détection: CONCURRENCE (gap: {price_gap}€)")
                return 'competitor_analysis'
        except (ValueError, AttributeError):
            print(f"⚠️ Debug - Erreur parsing price_gap: {context.get('price_gap')}")
        
        # 4. PLANIFICATION STRATÉGIQUE (horizon long terme)
        planning_horizon = context.get('planning_horizon', '1 jour')
        try:
            if 'jour' in planning_horizon:
                days = int(planning_horizon.split()[0])
                if days > 30:
                    print(f"📈 Détection: STRATÉGIQUE (horizon: {days} jours)")
                    return 'strategic_planning'
        except (ValueError, AttributeError):
            pass
        
        # 5. ANALYSE QUOTIDIENNE par défaut
        print("📊 Détection: QUOTIDIENNE (par défaut)")
        return 'daily_pricing'
    
    def get_required_variables(self, prompt_type: str) -> list:
        """Retourne les variables requises pour un type de prompt"""
        variables_map = {
            'daily_pricing': [
                'hotel_name', 'current_date', 'day_of_week', 'room_type',
                'current_occupancy', 'occupancy_trend', 'current_price',
                'current_revpar', 'competitor_avg_price', 'price_gap',
                'price_position', 'weather_forecast', 'local_events',
                'season_type', 'min_price', 'max_price', 'revpar_target'
            ],
            'competitor_analysis': [
                'hotel_name', 'competitor_pricing_table', 'our_price',
                'our_ranking', 'total_competitors', 'gap_to_leader',
                'gap_to_average'
            ],
            'special_event': [
                'event_details', 'event_date', 'event_duration',
                'distance_to_hotel', 'estimated_attendees', 'demand_increase',
                'historical_impact'
            ],
            'crisis_management': [
                'crisis_type', 'severity_level', 'occupancy_impact',
                'current_occupancy', 'normal_occupancy', 'cancellations',
                'lost_revenue'
            ],
            'strategic_planning': [
                'planning_horizon', 'annual_revpar_target', 'revenue_growth_target',
                'target_occupancy', 'seasonality_pattern', 'demand_cycles',
                'competitive_evolution'
            ]
        }
        
        return variables_map.get(prompt_type, [])