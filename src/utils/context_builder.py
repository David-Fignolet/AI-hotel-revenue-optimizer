"""
Constructeur de contexte pour les prompts LLM - Version corrigée
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

class ContextBuilder:
    """Construit le contexte nécessaire pour les prompts LLM"""
    
    def build_context(self, 
                     hotel_data: Dict[str, Any],
                     market_data: Dict[str, Any],
                     historical_data: Optional[pd.DataFrame],
                     config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construit un contexte complet pour les prompts
        """
        context = {}
        
        # Informations de base
        context.update(self._build_basic_info(config))
        
        # Métriques actuelles
        context.update(self._build_current_metrics(hotel_data))
        
        # Analyse concurrentielle
        context.update(self._build_competitive_analysis(market_data, hotel_data))
        
        # Contexte externe
        context.update(self._build_external_context(market_data))
        
        # Contraintes business
        context.update(self._build_business_constraints(hotel_data, config))
        
        # Variables pour événements spéciaux
        context.update(self._build_event_context(market_data))
        
        # Variables pour crise
        context.update(self._build_crisis_context(hotel_data))
        
        # Variables pour planification strategique
        context.update(self._build_strategic_context(config))
        
        # Tendances historiques
        if historical_data is not None:
            context.update(self._build_historical_trends(historical_data))
        
        return context
    
    def _build_basic_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Construit les informations de base"""
        now = datetime.now()
        return {
            'hotel_name': config.get('hotel', {}).get('name', 'Hotel Example'),
            'current_date': now.strftime('%Y-%m-%d'),
            'day_of_week': now.strftime('%A'),
            'room_type': 'Standard'
        }
    
    def _build_current_metrics(self, hotel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construit les métriques actuelles"""
        occupancy = hotel_data.get('occupancy_rate', 0)
        price = hotel_data.get('current_price', 150)
        
        # Assurer la cohérence des formats
        if occupancy > 1:
            occupancy = occupancy / 100
        
        return {
            'current_occupancy': f"{occupancy * 100:.1f}%",
            'current_price': f"{price:.0f}",
            'current_revpar': f"{occupancy * price:.2f}",
            'occupancy_trend': 'stable',
            'confirmed_bookings': hotel_data.get('bookings', 0)
        }
    
    def _build_competitive_analysis(self, market_data: Dict[str, Any], hotel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construit l'analyse concurrentielle"""
        competitor_prices = market_data.get('competitor_prices', [150])
        our_price = float(hotel_data.get('current_price', 150))
        avg_price = np.mean(competitor_prices)
        
        # Calculer le gap et la position
        price_gap = our_price - avg_price
        if price_gap > 10:
            position = "Au-dessus de la moyenne"
        elif price_gap < -10:
            position = "En-dessous de la moyenne"
        else:
            position = "Aligné avec la moyenne"
        
        # Position concurrentielle
        sorted_prices = sorted(competitor_prices + [our_price])
        our_ranking = sorted_prices.index(our_price) + 1
        
        return {
            'competitor_avg_price': f"{avg_price:.0f}",
            'min_competitor_price': f"{min(competitor_prices):.0f}",
            'max_competitor_price': f"{max(competitor_prices):.0f}",
            'price_gap': f"{price_gap:+.0f}",
            'price_position': position,
            'our_price': f"{our_price:.0f}",
            'our_ranking': our_ranking,
            'total_competitors': len(competitor_prices),
            'gap_to_leader': f"{our_price - min(competitor_prices):+.0f}",
            'gap_to_average': f"{price_gap:+.0f}",
            'competitor_pricing_table': self._format_competitor_table(competitor_prices, our_price)
        }
    
    def _build_external_context(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le contexte externe"""
        events = market_data.get('events', [])
        return {
            'weather_forecast': market_data.get('weather', 'Normal'),
            'local_events': ', '.join(events) if events else 'Aucun',
            'special_events': events,  # Garder la liste pour la détection
            'season_type': self._determine_season(),
            'weekday_type': self._determine_weekday_type()
        }
    
    def _build_business_constraints(self, hotel_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Construit les contraintes business"""
        return {
            'min_price': hotel_data.get('min_price', 80),
            'max_price': hotel_data.get('max_price', 300),
            'revpar_target': hotel_data.get('revpar_target', 120),
            'margin_requirement': hotel_data.get('margin_requirement', 60)
        }
    
    def _build_event_context(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le contexte pour les événements spéciaux"""
        events = market_data.get('events', [])
        
        if events:
            event_details = f"Événements détectés: {', '.join(events)}"
            return {
                'event_details': event_details,
                'event_date': 'Dates à confirmer',
                'event_duration': '1-3 jours',
                'distance_to_hotel': '< 5km',
                'estimated_attendees': 'Non spécifié',
                'demand_increase': '15-25%',
                'historical_impact': 'Impact positif attendu'
            }
        else:
            return {
                'event_details': 'Aucun événement majeur détecté',
                'event_date': 'N/A',
                'event_duration': 'N/A',
                'distance_to_hotel': 'N/A',
                'estimated_attendees': 'N/A',
                'demand_increase': '0%',
                'historical_impact': 'N/A'
            }
    
    def _build_crisis_context(self, hotel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le contexte pour la gestion de crise"""
        occupancy = hotel_data.get('occupancy_rate', 0.7)
        if occupancy > 1:
            occupancy = occupancy / 100
            
        is_crisis = occupancy < 0.3
        
        return {
            'crisis_type': 'Faible occupation' if is_crisis else 'Situation normale',
            'severity_level': 'Élevé' if occupancy < 0.2 else 'Modéré' if occupancy < 0.3 else 'Faible',
            'occupancy_impact': f"{(0.7 - occupancy) * 100:+.1f}%",
            'normal_occupancy': '70%',
            'cancellations': 'Non spécifié',
            'lost_revenue': 'À calculer'
        }
    
    def _build_strategic_context(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le contexte pour la planification stratégique"""
        return {
            'planning_horizon': '30 jours',
            'annual_revpar_target': '150€',
            'revenue_growth_target': '8%',
            'target_occupancy': '75%',
            'seasonality_pattern': 'Été fort, hiver modéré',
            'demand_cycles': 'Hebdomadaire et mensuel',
            'competitive_evolution': 'Marché en croissance'
        }
    
    def _build_historical_trends(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Construit les tendances historiques"""
        if len(historical_data) >= 7:
            recent_occupancy = historical_data['occupancy_rate'].tail(7).mean()
        else:
            recent_occupancy = historical_data['occupancy_rate'].mean()
        
        return {
            'avg_occupancy_7d': f"{recent_occupancy * 100:.1f}%",
            'yoy_performance': '+5.2%',
            'booking_pace': 'Normal'
        }
    
    def _format_competitor_table(self, competitor_prices: list, our_price: float) -> str:
        """Formate un tableau des prix concurrentiels"""
        all_prices = [(f"Concurrent {i+1}", price) for i, price in enumerate(competitor_prices)]
        all_prices.append(("Notre hôtel", our_price))
        all_prices.sort(key=lambda x: x[1])
        
        table = "\n".join([f"   {name}: {price:.0f}€" for name, price in all_prices])
        return table
    
    def _determine_season(self) -> str:
        """Détermine la saison actuelle"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'Hiver'
        elif month in [3, 4, 5]:
            return 'Printemps'
        elif month in [6, 7, 8]:
            return 'Été'
        else:
            return 'Automne'
    
    def _determine_weekday_type(self) -> str:
        """Détermine le type de jour"""
        weekday = datetime.now().weekday()
        if weekday < 5:
            return 'Jour de semaine'
        else:
            return 'Week-end'