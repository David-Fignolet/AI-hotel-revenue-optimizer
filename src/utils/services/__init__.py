"""
Initialisation et configuration des services externes
"""

from typing import Dict, Any
from .weather_service import WeatherService
from .events_service import EventsService

class ExternalServices:
    """Gestionnaire des services externes pour le revenue management"""
    
    def __init__(self):
        """Initialisation des services"""
        self.weather_service = WeatherService()
        self.events_service = EventsService()
        
    async def get_external_context(self,
                                latitude: float,
                                longitude: float,
                                radius_km: int = 20,
                                days_ahead: int = 30) -> Dict[str, Any]:
        """
        Récupère le contexte externe complet (météo + événements)
        
        Args:
            latitude: Latitude de l'hôtel
            longitude: Longitude de l'hôtel
            radius_km: Rayon de recherche pour les événements
            days_ahead: Nombre de jours à l'avance
            
        Returns:
            Dict contenant le contexte externe complet
        """
        # Récupération en parallèle des données météo et événements
        weather_data = await self.weather_service.get_weather_forecast(latitude, longitude)
        events_data = await self.events_service.get_events(
            latitude, longitude, radius_km, days_ahead
        )
        
        return {
            'weather': weather_data,
            'events': events_data,
            'combined_impact': self._analyze_combined_impact(weather_data, events_data)
        }
    
    def _analyze_combined_impact(self,
                             weather_data: Dict[str, Any],
                             events_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse l'impact combiné de la météo et des événements"""
        try:
            weather_score = weather_data.get('revenue_impact', {}).get('score', 0)
            events_score = events_data.get('revenue_impact', {}).get('score', 0)
            
            # Moyenne pondérée (événements ont plus de poids)
            combined_score = (weather_score + events_score * 2) / 3
            
            # Détermination de l'impact global
            if combined_score > 0.6:
                impact = "très favorable"
            elif combined_score > 0.3:
                impact = "favorable"
            elif combined_score < -0.3:
                impact = "défavorable"
            else:
                impact = "neutre"
            
            return {
                'score': combined_score,
                'impact': impact,
                'confidence': min(
                    (weather_data.get('revenue_impact', {}).get('confidence', 0) +
                     events_data.get('revenue_impact', {}).get('confidence', 0)) / 2,
                    100
                ),
                'summary': self._generate_combined_summary(weather_data, events_data)
            }
            
        except Exception as e:
            print(f"Erreur analyse impact combiné: {str(e)}")
            return {
                'score': 0,
                'impact': 'indéterminé',
                'confidence': 0,
                'summary': "Analyse d'impact indisponible"
            }
    
    def _generate_combined_summary(self,
                               weather_data: Dict[str, Any],
                               events_data: Dict[str, Any]) -> str:
        """Génère un résumé de l'impact combiné"""
        try:
            weather_summary = weather_data.get('summary', "Météo indisponible")
            events_summary = events_data.get('summary', "Événements indisponibles")
            
            return f"Météo: {weather_summary}. Événements: {events_summary}"
            
        except Exception:
            return "Résumé indisponible"
