"""
Service de gestion des événements pour le revenue management
Combine plusieurs sources de données : Ticketmaster API, base locale, etc.
"""

from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import pandas as pd

class EventsService:
    """Service de gestion des événements pour l'analyse revenue management"""
    
    def __init__(self):
        """Initialisation du service événements"""
        load_dotenv()
        self.ticketmaster_key = os.getenv('TICKETMASTER_API_KEY')
        self.base_url = "https://app.ticketmaster.com/discovery/v2"
        self.cache = {}
        self.cache_duration = timedelta(hours=12)
        self.local_events_file = "data/local_events.json"
        
    async def get_events(self, 
                      latitude: float, 
                      longitude: float, 
                      radius_km: int = 20,
                      days_ahead: int = 30) -> Dict[str, Any]:
        """
        Récupère les événements à venir dans un rayon donné
        
        Args:
            latitude: Latitude de l'hôtel
            longitude: Longitude de l'hôtel
            radius_km: Rayon de recherche en kilomètres
            days_ahead: Nombre de jours à l'avance
            
        Returns:
            Dict contenant les événements formatés pour le revenue management
        """
        cache_key = f"{latitude},{longitude},{radius_km},{days_ahead}"
        
        # Vérification du cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data
        
        try:
            # Combinaison des sources de données
            events = []
            
            # 1. Événements Ticketmaster
            if self.ticketmaster_key:
                tm_events = await self._fetch_ticketmaster_events(
                    latitude, longitude, radius_km, days_ahead
                )
                events.extend(tm_events)
            
            # 2. Événements locaux depuis le fichier JSON
            local_events = await self._fetch_local_events(
                latitude, longitude, radius_km, days_ahead
            )
            events.extend(local_events)
            
            # Analyse et formatage des événements
            analyzed_events = self._analyze_events_impact(events)
            
            # Mise en cache
            self.cache[cache_key] = (analyzed_events, datetime.now())
            
            return analyzed_events
            
        except Exception as e:
            print(f"Erreur lors de la récupération des événements: {str(e)}")
            return self._get_fallback_events()
    
    async def _fetch_ticketmaster_events(self, 
                                     latitude: float, 
                                     longitude: float,
                                     radius_km: int,
                                     days_ahead: int) -> List[Dict[str, Any]]:
        """Récupère les événements via l'API Ticketmaster"""
        if not self.ticketmaster_key:
            return []
            
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'apikey': self.ticketmaster_key,
                    'latlong': f"{latitude},{longitude}",
                    'radius': f"{radius_km}",
                    'unit': 'km',
                    'size': 100,
                    'startDateTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'endDateTime': (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%dT%H:%M:%SZ')
                }
                
                async with session.get(f"{self.base_url}/events", params=params) as response:
                    if response.status != 200:
                        return []
                        
                    data = await response.json()
                    
                    # Extraction et formatage des événements
                    events = []
                    for event in data.get('_embedded', {}).get('events', []):
                        events.append({
                            'source': 'ticketmaster',
                            'name': event.get('name'),
                            'type': event.get('type'),
                            'category': event.get('classifications', [{}])[0].get('segment', {}).get('name'),
                            'start_date': event.get('dates', {}).get('start', {}).get('dateTime'),
                            'end_date': event.get('dates', {}).get('end', {}).get('dateTime'),
                            'venue': event.get('_embedded', {}).get('venues', [{}])[0].get('name'),
                            'capacity': event.get('_embedded', {}).get('venues', [{}])[0].get('capacity'),
                            'url': event.get('url')
                        })
                    
                    return events
                    
        except Exception as e:
            print(f"Erreur Ticketmaster API: {str(e)}")
            return []
    
    async def _fetch_local_events(self,
                               latitude: float,
                               longitude: float,
                               radius_km: int,
                               days_ahead: int) -> List[Dict[str, Any]]:
        """Récupère les événements depuis la base locale"""
        try:
            if not os.path.exists(self.local_events_file):
                return []
                
            with open(self.local_events_file, 'r', encoding='utf-8') as f:
                local_data = json.load(f)
            
            # Filtrage des événements
            now = datetime.now()
            max_date = now + timedelta(days=days_ahead)
            
            events = []
            for event in local_data.get('events', []):
                start_date = datetime.strptime(event['start_date'], '%Y-%m-%dT%H:%M:%S')
                if now <= start_date <= max_date:
                    # TODO: Ajouter filtrage par distance
                    events.append({
                        'source': 'local',
                        **event
                    })
            
            return events
            
        except Exception as e:
            print(f"Erreur lecture événements locaux: {str(e)}")
            return []
    
    def _analyze_events_impact(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse l'impact des événements sur le revenue management"""
        if not events:
            return self._get_fallback_events()
        
        # Groupement par date
        events_by_date = {}
        for event in events:
            date = event['start_date'][:10]  # YYYY-MM-DD
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].append(event)
        
        # Analyse de l'impact
        daily_impacts = []
        for date, day_events in events_by_date.items():
            # Score basé sur plusieurs facteurs
            score = 0
            total_capacity = 0
            
            for event in day_events:
                # Impact basé sur la catégorie
                category_impact = {
                    'Sports': 0.8,
                    'Music': 0.7,
                    'Arts & Theatre': 0.5,
                    'Family': 0.4,
                    'Other': 0.3
                }.get(event.get('category', 'Other'), 0.3)
                
                # Impact basé sur la capacité
                capacity = event.get('capacity', 0)
                if capacity:
                    total_capacity += capacity
                    capacity_impact = min(capacity / 10000, 1)  # Normalisé à 10000
                else:
                    capacity_impact = 0.3  # Impact moyen si capacité inconnue
                
                score += (category_impact + capacity_impact) / 2
            
            daily_impacts.append({
                'date': date,
                'events': len(day_events),
                'total_capacity': total_capacity,
                'impact_score': score / len(day_events)
            })
        
        # Impact global
        avg_score = sum(d['impact_score'] for d in daily_impacts) / len(daily_impacts)
        max_score = max(d['impact_score'] for d in daily_impacts)
        
        return {
            'events': events,
            'daily_impacts': daily_impacts,
            'summary': self._generate_events_summary(events, daily_impacts),
            'revenue_impact': {
                'impact': self._determine_impact_level(avg_score),
                'peak_impact': self._determine_impact_level(max_score),
                'score': avg_score,
                'confidence': min(len(events) * 10, 100)  # Confiance basée sur le nombre d'événements
            }
        }
    
    def _determine_impact_level(self, score: float) -> str:
        """Détermine le niveau d'impact basé sur le score"""
        if score > 0.7:
            return "très fort"
        elif score > 0.5:
            return "fort"
        elif score > 0.3:
            return "modéré"
        else:
            return "faible"
    
    def _generate_events_summary(self, 
                             events: List[Dict[str, Any]], 
                             daily_impacts: List[Dict[str, Any]]) -> str:
        """Génère un résumé des événements pour le revenue management"""
        if not events:
            return "Aucun événement significatif"
        
        total_events = len(events)
        high_impact_days = sum(1 for d in daily_impacts if d['impact_score'] > 0.5)
        
        summary = f"{total_events} événements sur la période, "
        summary += f"dont {high_impact_days} jours à fort impact. "
        
        # Top événements
        top_events = sorted(events, 
                          key=lambda x: x.get('capacity', 0), 
                          reverse=True)[:3]
        
        if top_events:
            summary += "Événements majeurs : "
            summary += ", ".join(e['name'] for e in top_events)
        
        return summary
    
    def _get_fallback_events(self) -> Dict[str, Any]:
        """Retourne des données par défaut en cas d'erreur"""
        return {
            'events': [],
            'daily_impacts': [],
            'summary': "Données événements temporairement indisponibles",
            'revenue_impact': {
                'impact': 'indéterminé',
                'peak_impact': 'indéterminé',
                'score': 0,
                'confidence': 0
            }
        }
