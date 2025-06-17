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
                   historical_data: Optional[pd.DataFrame] = None,
                   config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Construit un contexte complet pour les prompts"""
        context = {}
        
        # Informations de base
        if config:
            context.update(self._build_basic_info(config))
        
        # Métriques actuelles
        context.update(self._build_current_metrics(hotel_data))
        
        # Analyse concurrentielle
        if market_data:
            context.update(self._build_competitive_analysis(market_data))
        
        # Tendances historiques
        if historical_data is not None:
            context.update(self._build_historical_trends(historical_data))
            
        return context
        
    def _build_current_metrics(self, hotel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construit les métriques actuelles"""
        return {
            'current_occupancy': f"{hotel_data.get('occupancy_rate', 0) * 100:.1f}%",
            'current_price': str(hotel_data.get('current_price', 0))
        }
    
    def _build_historical_trends(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyse les tendances historiques"""
        if historical_data.empty:
            return {'trend_data': 'Pas de données historiques disponibles'}
            
        occupancy_col = next((col for col in ['occupancy_rate', 'occupancy']
                          if col in historical_data.columns), None)
        
        if not occupancy_col:
            return {'trend_data': 'Colonne occupation non trouvée'}
            
        recent = historical_data[occupancy_col].iloc[-7:].mean()
        trend = historical_data[occupancy_col].diff().iloc[-30:].mean()
        
        return {
            'recent_occupancy': f"{recent * 100:.1f}%",
            'trend': 'à la hausse' if trend > 0.01 else 'à la baisse' if trend < -0.01 else 'stable'
        }
    
    def _build_competitive_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse la situation concurrentielle"""
        return {
            'competitor_prices': ', '.join(map(str, market_data.get('competitor_prices', []))),
            'market_events': ', '.join(market_data.get('events', [])) or 'Aucun événement'
        }
        
    def _build_basic_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Informations de base de l'hôtel"""
        hotel_config = config.get('hotel', {})
        return {
            'hotel_name': hotel_config.get('name', 'Hotel'),
            'hotel_category': hotel_config.get('category', 'Non spécifié')
        }