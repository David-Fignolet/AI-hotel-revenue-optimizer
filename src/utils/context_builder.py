"""
Constructeur de contexte avancé pour les prompts LLM Revenue Manager
Supporte l'ensemble des métriques et KPIs nécessaires aux analyses
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import defaultdict
import os
from dotenv import load_dotenv

from .services import ExternalServices

class ContextBuilder:
    """Construit le contexte enrichi pour les prompts LLM Revenue Manager"""
    
    def __init__(self):
        """Initialisation du builder avec les services externes"""
        load_dotenv()
        
        self.external_services = ExternalServices()
        self.hotel_location = {
            'latitude': float(os.getenv('HOTEL_LATITUDE', '48.8566')),
            'longitude': float(os.getenv('HOTEL_LONGITUDE', '2.3522')),
            'radius_km': int(os.getenv('HOTEL_RADIUS_KM', '20'))
        }
    
    def __init__(self):
        self.weather_service = None  # TODO: Intégrer service météo
        self.event_service = None    # TODO: Intégrer service événements
    
    async def build_context(self, 
                   hotel_data: Dict[str, Any],
                   market_data: Dict[str, Any],
                   historical_data: Optional[pd.DataFrame] = None,
                   config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Construit un contexte complet pour les prompts
        
        Args:
            hotel_data: Données actuelles de l'hôtel
            market_data: Données du marché et de la concurrence
            historical_data: Historique des performances
            config: Configuration de l'hôtel
            
        Returns:
            Dict[str, Any]: Contexte enrichi pour les prompts
        """
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
        
        # Contexte externe (météo + événements)
        external_context = await self.external_services.get_external_context(
            latitude=self.hotel_location['latitude'],
            longitude=self.hotel_location['longitude'],
            radius_km=self.hotel_location['radius_km']
        )
        
        # Mise à jour du contexte avec les données externes
        context.update({
            'weather_forecast': external_context['weather']['summary'],
            'weather_impact': external_context['weather']['revenue_impact']['impact'],
            'local_events': external_context['events']['summary'],
            'events_impact': external_context['events']['revenue_impact']['impact'],
            'external_factors': {
                'weather': external_context['weather'],
                'events': external_context['events'],
                'combined_impact': external_context['combined_impact']
            }
        })
            
        return context
    
    def _build_basic_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Informations détaillées de l'hôtel"""
        hotel_config = config.get('hotel', {})
        return {
            'hotel_name': hotel_config.get('name', 'Hotel'),
            'hotel_category': hotel_config.get('category', '4 étoiles'),
            'hotel_location': hotel_config.get('location', 'Non spécifié'),
            'room_types': hotel_config.get('room_types', []),
            'total_rooms': hotel_config.get('total_rooms', 0),
            'min_price': hotel_config.get('min_price', 0),
            'max_price': hotel_config.get('max_price', 0),
            'revpar_target': hotel_config.get('revpar_target', 0),
            'occupancy_target': hotel_config.get('occupancy_target', 0.75),
            'adr_target': hotel_config.get('adr_target', 0)
        }
    
    def _build_current_metrics(self, hotel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Métriques actuelles détaillées"""
        current_date = datetime.strptime(
            hotel_data.get('current_date', datetime.now().strftime('%Y-%m-%d')),
            '%Y-%m-%d'
        )
        
        occupancy_rate = hotel_data.get('occupancy_rate', 0)
        current_price = hotel_data.get('current_price', 0)
        rooms_sold = hotel_data.get('rooms_sold', 0)
        total_rooms = hotel_data.get('total_rooms', 100)
        
        # Calculs dérivés
        revpar = current_price * occupancy_rate
        adr = current_price if rooms_sold == 0 else (current_price * rooms_sold) / rooms_sold
        
        return {
            'current_date': current_date.strftime('%Y-%m-%d'),
            'day_of_week': current_date.strftime('%A'),
            'current_occupancy': f"{occupancy_rate * 100:.1f}",
            'current_price': current_price,
            'current_revpar': f"{revpar:.2f}",
            'current_adr': f"{adr:.2f}",
            'rooms_sold': rooms_sold,
            'rooms_available': total_rooms - rooms_sold,
            'pickup_rate': hotel_data.get('pickup_rate', 0),
            'avg_lead_time': hotel_data.get('avg_lead_time', 0)
        }
    
    def _build_competitive_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse concurrentielle détaillée"""
        competitor_prices = market_data.get('competitor_prices', [])
        our_price = market_data.get('our_price', 0)
        
        if not competitor_prices:
            return self._empty_competitive_context()
        
        # Calculs statistiques
        comp_array = np.array(competitor_prices)
        avg_price = np.mean(comp_array)
        min_price = np.min(comp_array)
        max_price = np.max(comp_array)
        std_dev = np.std(comp_array)
        
        # Positionnement
        rank = sum(1 for p in competitor_prices if p <= our_price) + 1
        total_competitors = len(competitor_prices) + 1
        
        # Indices de performance
        mpi = market_data.get('market_penetration_index', 1.0)
        ari = market_data.get('average_rate_index', 1.0)
        rgi = mpi * ari
        
        return {
            'competitor_avg_price': f"{avg_price:.2f}",
            'competitor_min_price': f"{min_price:.2f}",
            'competitor_max_price': f"{max_price:.2f}",
            'price_std_dev': f"{std_dev:.2f}",
            'our_ranking': rank,
            'total_competitors': total_competitors,
            'gap_to_leader': f"{(max_price - our_price):.2f}",
            'gap_to_average': f"{(avg_price - our_price):.2f}",
            'price_position': self._determine_price_position(float(our_price), float(min_price), float(avg_price), float(max_price)),
            'competitive_pressure': self._calculate_competitive_pressure(our_price, comp_array),
            'rgi_index': f"{rgi:.2f}",
            'mpi_index': f"{mpi:.2f}",
            'ari_index': f"{ari:.2f}",
            'market_price_trend': market_data.get('price_trend', 'stable'),
            'market_occupancy_trend': market_data.get('occupancy_trend', 'stable')
        }
    
    def _build_historical_trends(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyse approfondie des tendances historiques"""
        if historical_data.empty:
            return {'trend_data': 'Pas de données historiques disponibles'}
        
        # Colonnes attendues
        occupancy_col = next((col for col in ['occupancy_rate', 'occupancy']
                          if col in historical_data.columns), None)
        adr_col = next((col for col in ['adr', 'average_daily_rate']
                     if col in historical_data.columns), None)
        
        if not all([occupancy_col, adr_col]):
            return {'trend_data': 'Colonnes requises non trouvées'}
        
        # Calculs sur différentes périodes
        periods = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            'YTD': 365
        }
        
        trends = {}
        for period_name, days in periods.items():
            period_data = historical_data.iloc[-days:]
            trends[f'avg_occupancy_{period_name}'] = f"{period_data[occupancy_col].mean() * 100:.1f}"
            trends[f'avg_adr_{period_name}'] = f"{period_data[adr_col].mean():.2f}"
            trends[f'trend_{period_name}'] = self._calculate_trend(period_data[occupancy_col])
        
        return {
            **trends,
            'yoy_performance': self._calculate_yoy_performance(historical_data),
            'seasonality_factor': self._calculate_seasonality(historical_data)
        }
    
    def _build_booking_analysis(self, bookings_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyse détaillée des réservations"""
        if bookings_data.empty:
            return {'booking_data': 'Pas de données de réservation disponibles'}
        
        # Segmentation
        segments = defaultdict(int)
        total_bookings = len(bookings_data)
        
        for segment in bookings_data.get('segment', []):
            segments[segment] += 1
        
        # Distribution
        channels = defaultdict(int)
        for channel in bookings_data.get('channel', []):
            channels[channel] += 1
        
        return {
            'business_segment': f"{(segments['business'] / total_bookings) * 100:.1f}",
            'leisure_segment': f"{(segments['leisure'] / total_bookings) * 100:.1f}",
            'group_segment': f"{(segments['group'] / total_bookings) * 100:.1f}",
            'direct_bookings': f"{(channels['direct'] / total_bookings) * 100:.1f}",
            'ota_bookings': f"{(channels['ota'] / total_bookings) * 100:.1f}",
            'corporate_bookings': f"{(channels['corporate'] / total_bookings) * 100:.1f}",
            'avg_length_of_stay': f"{np.mean(bookings_data.get('length_of_stay', [0])):.1f}",
            'booking_pace': self._calculate_booking_pace(bookings_data)
        }
    
    def _build_external_context(self) -> Dict[str, Any]:
        """Construction du contexte externe"""
        current_date = datetime.now()
        
        # TODO: Intégrer API météo réelle
        weather = "Ensoleillé, 22°C"
        
        # TODO: Intégrer API événements réelle
        events = ["Conférence Tech", "Festival Jazz"]
        
        return {
            'weather_forecast': weather,
            'local_events': ", ".join(events),
            'season_type': self._determine_season(current_date),
            'is_holiday': self._is_holiday(current_date),
            'holiday_period': self._get_holiday_period(current_date)
        }
    
    def _calculate_derived_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calcul des métriques dérivées"""
        try:
            occupancy = float(context.get('current_occupancy', 0))
            price = float(context.get('current_price', 0))
            target_revpar = float(context.get('revpar_target', 0))
            
            current_revpar = occupancy * price / 100
            revpar_gap = target_revpar - current_revpar
            
            return {
                'revpar_gap': f"{revpar_gap:.2f}",
                'revpar_achievement': f"{(current_revpar/target_revpar)*100:.1f}%" if target_revpar > 0 else "N/A",
                'revenue_risk_level': self._calculate_risk_level(context)
            }
        except (ValueError, TypeError):
            return {}
    
    # Méthodes utilitaires
    def _determine_price_position(self, our_price: float, min_price: float, 
                                avg_price: float, max_price: float) -> str:
        """Détermine le positionnement tarifaire"""
        if our_price >= max_price:
            return "premium"
        elif our_price <= min_price:
            return "économique"
        elif our_price > avg_price:
            return "supérieur"
        else:
            return "standard"
    
    def _calculate_competitive_pressure(self, our_price: float, comp_prices: np.ndarray) -> str:
        """Calcule la pression concurrentielle"""
        lower_prices = sum(1 for p in comp_prices if p < our_price)
        total = len(comp_prices)
        
        pressure_ratio = lower_prices / total if total > 0 else 0
        
        if pressure_ratio > 0.7:
            return "forte"
        elif pressure_ratio > 0.3:
            return "moyenne"
        else:
            return "faible"
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """Calcule la tendance d'une série"""
        if series.empty:
            return "stable"
            
        slope = np.polyfit(range(len(series)), series, 1)[0]
        
        if slope > 0.01:
            return "hausse"
        elif slope < -0.01:
            return "baisse"
        else:
            return "stable"
    
    def _calculate_yoy_performance(self, data: pd.DataFrame) -> str:
        """Calcule la performance année sur année"""
        try:
            current = data.iloc[-30:]['revpar'].mean()
            last_year = data.iloc[-395:-365]['revpar'].mean()
            
            if last_year == 0:
                return "N/A"
                
            yoy_change = ((current - last_year) / last_year) * 100
            return f"{yoy_change:+.1f}%"
        except:
            return "N/A"
    
    def _calculate_seasonality(self, data: pd.DataFrame) -> float:
        """Calcule le facteur de saisonnalité"""
        try:
            current_month = datetime.now().month
            data['month'] = pd.to_datetime(data.index).month
            monthly_avg = data[data['month'] == current_month]['revpar'].mean()
            yearly_avg = data['revpar'].mean()
            
            return monthly_avg / yearly_avg if yearly_avg != 0 else 1.0
        except:
            return 1.0
    
    def _calculate_booking_pace(self, bookings: pd.DataFrame) -> str:
        """Calcule le rythme des réservations"""
        try:
            recent_bookings = len(bookings[bookings['booking_date'] >= 
                                        datetime.now() - timedelta(days=7)])
            previous_bookings = len(bookings[(bookings['booking_date'] >= 
                                          datetime.now() - timedelta(days=14)) &
                                          (bookings['booking_date'] < 
                                           datetime.now() - timedelta(days=7))])
            
            if previous_bookings == 0:
                return "normal"
                
            pace_ratio = recent_bookings / previous_bookings
            
            if pace_ratio > 1.2:
                return "accéléré"
            elif pace_ratio < 0.8:
                return "ralenti"
            else:
                return "normal"
        except:
            return "normal"
    
    def _determine_season(self, date: datetime) -> str:
        """Détermine la saison"""
        month = date.month
        
        if month in [12, 1, 2]:
            return "hiver"
        elif month in [3, 4, 5]:
            return "printemps"
        elif month in [6, 7, 8]:
            return "été"
        else:
            return "automne"
    
    def _is_holiday(self, date: datetime) -> bool:
        """Vérifie si la date est un jour férié"""
        # TODO: Implémenter calendrier jours fériés
        return False
    
    def _get_holiday_period(self, date: datetime) -> str:
        """Détermine la période de vacances"""
        # TODO: Implémenter calendrier vacances scolaires
        return "Hors vacances"
    
    def _calculate_risk_level(self, context: Dict[str, Any]) -> str:
        """Calcule le niveau de risque revenue"""
        try:
            occupancy = float(context.get('current_occupancy', 0))
            pace = context.get('booking_pace', 'normal')
            pressure = context.get('competitive_pressure', 'moyenne')
            
            if occupancy < 40 and pace == "ralenti" and pressure == "forte":
                return "élevé"
            elif occupancy < 60 and (pace == "ralenti" or pressure == "forte"):
                return "modéré"
            else:
                return "faible"
        except:
            return "indéterminé"
    
    def _empty_competitive_context(self) -> Dict[str, Any]:
        """Retourne un contexte concurrentiel vide"""
        return {
            'competitor_avg_price': "0",
            'competitor_min_price': "0",
            'competitor_max_price': "0",
            'price_std_dev': "0",
            'our_ranking': "N/A",
            'total_competitors': 0,
            'gap_to_leader': "0",
            'gap_to_average': "0",
            'price_position': "N/A",
            'competitive_pressure': "N/A",
            'rgi_index': "N/A",
            'mpi_index': "N/A",
            'ari_index': "N/A"
        }