"""
Service de récupération des données météorologiques via Meteoblue
"""

from typing import Dict, Any, Optional
import aiohttp
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

class WeatherService:
    """Service de prévisions météo pour l'analyse revenue management"""
    
    def __init__(self):
        """Initialisation du service météo"""
        self.api_key = "L4KEneiS9XJb6lYv"  # Clé API Meteoblue fixe
        self.base_url = "http://my.meteoblue.com/packages/basic-1h"
        self.cache = {}
        self.cache_duration = timedelta(hours=3)
    async def get_weather_forecast(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Récupère les prévisions météo pour une localisation donnée via Meteoblue
        
        Args:
            latitude: Latitude de l'hôtel
            longitude: Longitude de l'hôtel
            
        Returns:
            Dict contenant les prévisions météo formatées pour le revenue management
        """
        cache_key = f"{latitude},{longitude}"
        
        # Vérification du cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data
        
        try:
            # Appel API Meteoblue
            async with aiohttp.ClientSession() as session:
                params = {
                    'apikey': self.api_key,
                    'lat': latitude,
                    'lon': longitude,
                    'asl': '0',  # Altitude (auto)
                    'format': 'json',
                    'temperature': 'C',  # Celsius
                    'windspeed': 'kmh',
                    'precipitationamount': 'mm',
                    'timeformat': 'iso8601',
                    'timezone': 'Europe/Paris'
                }
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        print(f"Erreur API Meteoblue: {response.status}")
                        return self._get_fallback_forecast()
                    
                    data = await response.json()
                    
                # Formatage des données pour le revenue management
                forecast = self._format_meteoblue_forecast(data)
                
                # Mise en cache
                self.cache[cache_key] = (forecast, datetime.now())
                
                return forecast
                
        except Exception as e:
            print(f"Erreur lors de la récupération météo Meteoblue: {str(e)}")
            return self._get_fallback_forecast()
    def _format_meteoblue_forecast(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les données météo Meteoblue pour l'analyse revenue"""
        try:
            # Extraction des données Meteoblue
            data_1h = api_data.get('data_1h', {})
            if not data_1h:
                return self._get_fallback_forecast()
            
            # Construction des prévisions journalières
            daily_forecasts = []
            current_date = None
            temps_max = []
            temps_min = []
            weather_codes = []
            
            time_indices = data_1h.get('time', [])
            temperatures = data_1h.get('temperature', [])
            precip_prob = data_1h.get('precipitation_probability', [])
            weather_symbols = data_1h.get('weather_symbol', [])
            
            for i, timestamp in enumerate(time_indices):
                date = datetime.fromisoformat(timestamp.split('T')[0])
                day = date.date()
                
                if day != current_date:
                    # Sauvegarde du jour précédent
                    if current_date and temps_max and temps_min:
                        daily_forecasts.append({
                            'date': current_date.strftime('%Y-%m-%d'),
                            'temp_max': max(temps_max),
                            'temp_min': min(temps_min),
                            'precip_prob': max(precip_prob[i-24:i] if i >= 24 else precip_prob[:i]),
                            'weather_code': max(set(weather_codes), key=weather_codes.count)
                        })
                    # Nouveau jour
                    current_date = day
                    temps_max = []
                    temps_min = []
                    weather_codes = []
                
                if i < len(temperatures):
                    temps_max.append(temperatures[i])
                    temps_min.append(temperatures[i])
                if i < len(weather_symbols):
                    weather_codes.append(weather_symbols[i])
            
            # Ajout du dernier jour
            if current_date and temps_max and temps_min:
                daily_forecasts.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'temp_max': max(temps_max),
                    'temp_min': min(temps_min),
                    'precip_prob': max(precip_prob[-24:]),
                    'weather_code': max(set(weather_codes), key=weather_codes.count)
                })
            
            # Analyse des conditions pour le revenue management
            weather_impact = self._analyze_weather_impact(daily_forecasts)
            
            # Construction de la réponse
            current_temp = temperatures[0] if temperatures else 20
            current_symbol = weather_symbols[0] if weather_symbols else 1
            
            return {
                'current': {
                    'temp': f"{current_temp:.1f}°C",
                    'weather': self._meteoblue_code_to_weather(current_symbol),
                    'description': self._meteoblue_code_to_description(current_symbol)
                },
                'forecast': daily_forecasts[:5],  # 5 jours
                'revenue_impact': weather_impact,
                'summary': self._generate_weather_summary(daily_forecasts)
            }
            
        except Exception as e:
            print(f"Erreur lors du formatage météo Meteoblue: {str(e)}")
            return self._get_fallback_forecast()
    
    def _meteoblue_code_to_weather(self, code: int) -> str:
        """Convertit un code météo Meteoblue en description générale"""
        weather_codes = {
            1: "Dégagé",
            2: "Peu nuageux",
            3: "Partiellement nuageux",
            4: "Nuageux",
            5: "Très nuageux",
            6: "Couvert",
            7: "Brouillard",
            10: "Pluie légère",
            11: "Pluie",
            12: "Pluie forte",
            20: "Neige légère",
            21: "Neige",
            22: "Neige forte",
            30: "Pluie et neige mêlées",
            40: "Orage possible",
            41: "Orage"
        }
        return weather_codes.get(code, "Indéterminé")
    
    def _meteoblue_code_to_description(self, code: int) -> str:
        """Convertit un code météo Meteoblue en description détaillée"""
        descriptions = {
            1: "Ciel dégagé",
            2: "Quelques nuages",
            3: "Ciel partiellement nuageux",
            4: "Ciel nuageux",
            5: "Ciel très nuageux",
            6: "Ciel couvert",
            7: "Conditions brumeuses",
            10: "Légères précipitations",
            11: "Précipitations modérées",
            12: "Fortes précipitations",
            20: "Légères chutes de neige",
            21: "Chutes de neige modérées",
            22: "Fortes chutes de neige",
            30: "Précipitations mixtes (pluie et neige)",
            40: "Risque d'orage",
            41: "Conditions orageuses"
        }
        return descriptions.get(code, "Conditions météorologiques indéterminées")
    def _analyze_weather_impact(self, forecasts: list) -> Dict[str, Any]:
        """Analyse l'impact de la météo sur le revenue management avec codes Meteoblue"""
        if not forecasts:
            return {'impact': 'neutre', 'score': 0}
        
        # Définition des scores d'impact par code météo
        weather_impact_scores = {
            # Conditions très favorables
            1: 1.0,    # Dégagé
            2: 0.8,    # Peu nuageux
            
            # Conditions favorables
            3: 0.6,    # Partiellement nuageux
            4: 0.4,    # Nuageux
            
            # Conditions neutres
            5: 0.0,    # Très nuageux
            6: -0.2,   # Couvert
            7: -0.3,   # Brouillard
            
            # Conditions défavorables
            10: -0.4,  # Pluie légère
            11: -0.6,  # Pluie modérée
            12: -0.8,  # Pluie forte
            
            # Conditions très défavorables
            20: -0.7,  # Neige légère
            21: -0.8,  # Neige modérée
            22: -1.0,  # Neige forte
            30: -0.8,  # Pluie et neige
            40: -0.5,  # Orage possible
            41: -0.9   # Orage
        }
        
        # Analyse des prochains jours
        daily_scores = []
        for forecast in forecasts:
            weather_code = forecast.get('weather_code', 0)
            temp_max = forecast.get('temp_max', 20)
            temp_min = forecast.get('temp_min', 10)
            precip_prob = forecast.get('precip_prob', 0)
            
            # Score base sur le code météo
            weather_score = weather_impact_scores.get(weather_code, 0)
            
            # Ajustement basé sur la température
            temp_score = 0
            if 20 <= temp_max <= 28:  # Température idéale
                temp_score = 1
            elif 15 <= temp_max < 20 or 28 < temp_max <= 32:  # Température acceptable
                temp_score = 0.5
            elif temp_max > 35 or temp_max < 5:  # Température extrême
                temp_score = -1
            
            # Ajustement basé sur la probabilité de précipitation
            precip_impact = -0.5 if precip_prob > 70 else -0.2 if precip_prob > 40 else 0
            
            # Score final pour la journée
            daily_score = (weather_score + temp_score) / 2 + precip_impact
            daily_score = max(min(daily_score, 1), -1)  # Normalisation entre -1 et 1
            
            daily_scores.append(daily_score)
        
        # Score moyen sur la période
        avg_score = sum(daily_scores) / len(daily_scores)
        
        # Détermination de l'impact
        if avg_score > 0.5:
            impact = 'très favorable'
        elif avg_score > 0.2:
            impact = 'favorable'
        elif avg_score < -0.5:
            impact = 'très défavorable'
        elif avg_score < -0.2:
            impact = 'défavorable'
        else:
            impact = 'neutre'
        
        # Calcul de la confiance basé sur la cohérence des prévisions
        std_dev = (sum((score - avg_score) ** 2 for score in daily_scores) / len(daily_scores)) ** 0.5
        confidence = max(0, min(100, 100 * (1 - std_dev)))
        
        return {
            'impact': impact,
            'score': avg_score,
            'confidence': confidence,
            'daily_scores': daily_scores
        }
    
    def _generate_weather_summary(self, forecasts: list) -> str:
        """Génère un résumé météo pour le revenue management"""
        if not forecasts:
            return "Données météo non disponibles"
        
        # Analyse des tendances
        conditions = [f['weather'] for f in forecasts]
        temps = [f['temp_max'] for f in forecasts]
        
        # Tendance dominante
        main_condition = max(set(conditions), key=conditions.count)
        avg_temp = sum(temps) / len(temps)
        
        # Formatage du résumé
        summary = f"Principalement {main_condition.lower()}, "
        summary += f"température moyenne de {avg_temp:.1f}°C"
        
        return summary
    
    def _get_fallback_forecast(self) -> Dict[str, Any]:
        """Retourne des données par défaut en cas d'erreur"""
        return {
            'current': {
                'temp': '20.0°C',
                'weather': 'Clear',
                'description': 'Ciel dégagé'
            },
            'forecast': [],
            'revenue_impact': {
                'impact': 'neutre',
                'score': 0,
                'confidence': 0
            },
            'summary': "Données météo temporairement indisponibles"
        }
