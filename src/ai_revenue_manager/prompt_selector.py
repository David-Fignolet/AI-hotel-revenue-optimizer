"""
Sélecteur automatique de prompts selon le contexte
"""

from typing import Dict, Any, Optional

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
        current_occupancy = self._parse_percentage(context.get('current_occupancy', '0%'))
        
        if current_occupancy is not None and current_occupancy <= 30:
            print("🚨 Détection: CRISE (occupation <= 30%)")
            return 'crisis_management'
        
        # 2. DÉTECTION D'ÉVÉNEMENT SPÉCIAL
        special_events = context.get('special_events', [])
        local_events = context.get('local_events', '')
        
        # Vérifier si il y a vraiment des événements
        has_events = (
            (isinstance(special_events, list) and len(special_events) > 0 and special_events != []) or
            (isinstance(local_events, str) and local_events.strip() and local_events.lower() not in ['aucun', 'none', ''])
        )
        
        if has_events:
            print(f"🎪 Détection: ÉVÉNEMENT (events: {special_events}, local: {local_events})")
            return 'special_event'
        
        # 3. DÉTECTION DE GAP DE PRIX SIGNIFICATIF
        price_gap = self._parse_price_gap(context.get('price_gap', '0'))
        
        print(f"🔍 Debug - Gap prix numérique: {price_gap}€")
        
        if price_gap is not None and abs(price_gap) >= 20:
            print(f"💰 Détection: DIVERGENCE PRIX (gap: {price_gap}€)")
            return 'price_gap'
            
        # 4. ANALYSE QUOTIDIENNE PAR DÉFAUT
        print("📊 Mode: ANALYSE QUOTIDIENNE")
        return 'daily_pricing'
    
    def _parse_percentage(self, value: str) -> Optional[float]:
        """Parse une chaîne de pourcentage en float"""
        if isinstance(value, (int, float)):
            return float(value)
            
        if isinstance(value, str):
            try:
                return float(value.rstrip('%'))
            except (ValueError, AttributeError):
                print(f"⚠️ Debug - Erreur parsing pourcentage: {value}")
                return None
                
        return None
    
    def _parse_price_gap(self, value: Any) -> Optional[float]:
        """Parse une valeur de gap de prix en float"""
        if isinstance(value, (int, float)):
            return float(value)
            
        if isinstance(value, str):
            try:
                # Enlever le symbole € et autres caractères non numériques
                cleaned = ''.join(c for c in value if c.isdigit() or c in '.-')
                return float(cleaned)
            except (ValueError, AttributeError):
                print(f"⚠️ Debug - Erreur parsing gap prix: {value}")
                return None
                
        return None
    
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