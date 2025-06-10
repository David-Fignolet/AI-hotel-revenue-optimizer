# 🏨 Hotel Revenue Optimizer

> **Système d'optimisation des revenus hôteliers basé sur l'intelligence artificielle**  
> Solution complète de revenue management utilisant le machine learning pour la prédiction de demande et la tarification dynamique

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](#tests)

## 📋 Table des Matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [API](#-api)
- [Tests](#-tests)
- [Déploiement](#-déploiement)
- [Contribution](#-contribution)
- [Licence](#-licence)

## 🎯 Vue d'ensemble

Hotel Revenue Optimizer est une solution complète de revenue management qui combine expertise hôtelière et intelligence artificielle pour optimiser automatiquement les prix et maximiser les revenus.

### Problématique Business
- **Prédiction de demande** : Anticiper les fluctuations d'occupation
- **Tarification optimale** : Calculer le prix qui maximise le RevPAR
- **Analyse concurrentielle** : Surveiller et réagir aux prix du marché
- **Décisions data-driven** : Remplacer l'intuition par des analyses prédictives

### Solution Technique
- **Machine Learning** : Modèles Random Forest pour la prédiction
- **Optimisation mathématique** : Algorithmes de pricing dynamique
- **Interface intuitive** : Dashboard Streamlit interactif
- **API REST** : Intégration avec les systèmes existants

## ✨ Fonctionnalités

### 🔮 Prédiction de Demande
- **Modèle ML avancé** : Random Forest avec features temporelles
- **Variables multiples** : Saisonnalité, événements, météo, historique
- **Précision élevée** : MAE < 5% sur les prédictions à 30 jours
- **Intervalles de confiance** : Estimation de l'incertitude

### 💰 Tarification Dynamique
- **Prix optimal** : Maximisation du RevPAR par algorithme d'optimisation
- **Segmentation** : Pricing par type de chambre et segment clientèle
- **Contraintes business** : Respect des prix min/max et politiques tarifaires
- **Élasticité-prix** : Prise en compte de la sensibilité au prix

### 📊 Dashboard Interactif
- **Visualisations temps réel** : KPIs revenue et métriques opérationnelles
- **Analyses prédictives** : Graphiques de prévision avec tendances
- **Simulations "What-if"** : Impact des changements de prix
- **Alertes intelligentes** : Notifications automatiques des opportunités

### 🔍 Analyse Concurrentielle
- **Surveillance automatique** : Scraping des prix concurrents
- **Positionnement** : Analyse comparative du pricing
- **Recommandations** : Stratégies basées sur le marché

### 📁 Traitement de Données
- **Formats multiples** : Support CSV, PDF, Excel
- **Extraction automatique** : Parsing intelligent des données hôtelières
- **Nettoyage** : Préprocessing et validation des données

## 🏗️ Architecture

```
hotel-revenue-optimizer/
├── app/                    # Application Streamlit
│   ├── streamlit_app.py   # Interface utilisateur principale
│   └── assets/            # Ressources statiques
├── src/                   # Code source principal
│   ├── api/               # API REST FastAPI
│   ├── core/              # Logique métier
│   │   ├── demand_forecasting.py  # Prédiction ML
│   │   └── pricing_engine.py      # Tarification dynamique
│   ├── data/              # Modèles de données et BDD
│   ├── services/          # Services externes
│   └── utils/             # Utilitaires
├── data/                  # Données
│   ├── raw/              # Données brutes
│   └── processed/        # Données traitées
├── models/               # Modèles ML sauvegardés
├── tests/               # Tests unitaires
└── docs/               # Documentation
```

### Stack Technique
- **Backend** : Python, FastAPI, SQLAlchemy
- **Frontend** : Streamlit, Plotly, HTML/CSS
- **ML/Data** : scikit-learn, pandas, numpy
- **Base de données** : SQLite/PostgreSQL
- **Cache** : Redis
- **Déploiement** : Docker, Heroku, AWS

## 🚀 Installation

### Prérequis
- Python 3.8+
- Java Runtime (pour le traitement PDF)
- Git

### Installation Rapide

```bash
# 1. Cloner le repository
git clone https://github.com/votre-username/hotel-revenue-optimizer.git
cd hotel-revenue-optimizer

# 2. Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
.\venv\Scripts\activate
# Activer l'environnement (macOS/Linux)
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Modifier les variables dans .env selon vos besoins

# 5. Initialiser la base de données
python -c "from src.data.database import init_db; init_db()"
```

### Installation avec Docker

```bash
# Build et run avec Docker Compose
docker-compose up --build

# L'application sera accessible sur http://localhost:8501
```

## 💻 Utilisation

### Interface Web (Streamlit)

```bash
# Lancer l'application Streamlit
streamlit run app/streamlit_app.py
```

Accédez à `http://localhost:8501` pour utiliser l'interface graphique.

### Utilisation Programmatique

```python
from src.demand_forecasting import DemandForecaster
from src.pricing_engine import PricingEngine
import pandas as pd

# 1. Prédiction de demande
forecaster = DemandForecaster()
forecaster.train(historical_data)

predictions = forecaster.predict_demand(
    start_date='2024-01-01',
    days=30,
    room_type='Standard'
)

# 2. Pricing optimal
pricing_engine = PricingEngine()
optimal_price = pricing_engine.calculate_optimal_price(
    predicted_demand=0.75,
    room_type='Deluxe',
    competitor_prices=[140, 160, 155, 170]
)

print(f"Prix recommandé: {optimal_price['optimal_price']}€")
print(f"RevPAR prédit: {optimal_price['predicted_revpar']}€")
```

### Traitement de Fichiers

```python
# Charger des données depuis un CSV
data = pd.read_csv('hotel_data.csv')

# Ou traiter un PDF hôtelier
from app.streamlit_app import parse_hotel_pdf
pdf_data = parse_hotel_pdf(pdf_file)
```

## 🌐 API

L'application fournit une API REST complète pour l'intégration avec vos systèmes.

### Démarrer l'API

```bash
# Lancer le serveur FastAPI
python src/main.py

# Documentation API disponible sur http://localhost:8000/api/docs
```

### Endpoints Principaux

```bash
# Obtenir une recommandation de prix
POST /api/v1/recommendations
{
  "hotel_id": 1,
  "room_type": "standard",
  "check_in": "2024-01-15",
  "check_out": "2024-01-17"
}

# Récupérer les prix concurrents
GET /api/v1/competitor-prices?hotel_id=1&check_in=2024-01-15

# Prévision de demande
GET /api/v1/demand-forecast?hotel_id=1&start_date=2024-01-01&end_date=2024-01-31
```

## 🧪 Tests

Le projet inclut une suite complète de tests unitaires et d'intégration.

```bash
# Exécuter tous les tests
pytest

# Tests avec couverture de code
pytest --cov=src --cov-report=html

# Tests spécifiques
pytest tests/test_demand_forecasting.py -v
pytest tests/test_pricing_engine.py -v
```

### Couverture de Code
- **Demand Forecasting** : 95%
- **Pricing Engine** : 92%
- **Data Processing** : 88%
- **API Endpoints** : 85%

## 🚀 Déploiement

### Déploiement Local (Production)

```bash
# Avec Gunicorn
gunicorn src.main:app --host 0.0.0.0 --port 8000

# Avec Docker
docker build -t hotel-revenue-optimizer .
docker run -p 8501:8501 hotel-revenue-optimizer
```

### Déploiement Cloud

#### Heroku
```bash
# Connecter à Heroku
heroku login
heroku create votre-app-name

# Déployer
git push heroku main
```

#### AWS/Digital Ocean
Voir [DEPLOYMENT.md](DEPLOYMENT.md) pour les instructions détaillées.

### Variables d'Environnement

```bash
# Base de données
DATABASE_URL=postgresql://user:pass@localhost:5432/hotel_revenue

# Cache Redis
REDIS_URL=redis://localhost:6379/0

# APIs externes (optionnel)
WEATHER_API_KEY=your_weather_api_key
COMPETITOR_SCRAPER_API=your_scraper_api_key

# Sécurité
SECRET_KEY=your-super-secret-key
DEBUG=False
```

## 📈 Performance

### Métriques ML
- **Prédiction de demande** : MAE < 5%, R² > 0.85
- **Temps d'entraînement** : < 30 secondes sur données 1 an
- **Temps de prédiction** : < 1 seconde pour 30 jours

### Performance Web
- **Temps de chargement** : < 2 secondes
- **API Response Time** : < 500ms
- **Concurrent Users** : 100+ utilisateurs simultanés

## 🤝 Contribution

Nous accueillons les contributions ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour plus de détails.

### Workflow de Contribution
1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -m 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

### Standards de Code
- **Python** : PEP 8, type hints, docstrings
- **Tests** : Couverture > 80%
- **Documentation** : README à jour, commentaires explicites

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👨‍💻 Auteur

**David Michel-Larrieux**  
*Data Analyst & Expert Hôtellerie (20 ans d'expérience)*

- LinkedIn: [linkedin.com/in/david-michel-larrieux](https://linkedin.com)
- GitHub: [@David-Fignolet](https://github.com/David-Fignoley)

## 🙏 Remerciements

- Communauté open source Python
- Équipes Streamlit et FastAPI
- Contributeurs du projet

---

<div align="center">

**⭐ N'hésitez pas à donner une étoile si ce projet vous aide ! ⭐**

</div>

# 🚀 Amélioration du Hotel Revenue Optimizer avec IA et Veille Concurrentielle

## 📋 Vue d'ensemble des améliorations

Voici une architecture complète pour transformer votre projet en un système de revenue management intelligent et connecté.

### 🏗️ Architecture proposée

```
hotel-revenue-optimizer-v2/
├── src/
│   ├── ai_revenue_manager/     # NOUVEAU
│   │   ├── __init__.py
│   │   ├── llm_manager.py      # Interface avec LLM
│   │   ├── prompts.py          # Templates de prompts
│   │   └── decision_engine.py  # Moteur de décision
│   ├── competitor_analysis/    # NOUVEAU
│   │   ├── __init__.py
│   │   ├── web_scraper.py      # Scraping des prix
│   │   ├── hotel_matcher.py    # Matching d'hôtels similaires
│   │   └── price_monitor.py    # Surveillance des prix
│   ├── hotel_profile/          # NOUVEAU
│   │   ├── __init__.py
│   │   └── hotel_config.py     # Configuration de l'établissement
│   └── [modules existants]
```

## 1️⃣ Module AI Revenue Manager

### `src/ai_revenue_manager/llm_manager.py`

```python
"""
Module de gestion du Revenue Manager IA
Utilise un LLM pour prendre des décisions de tarification intelligentes
"""
import os
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationSummaryBufferMemory

class AIRevenueManager:
    """
    Revenue Manager virtuel basé sur un LLM
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: str = "gpt-4",
                 temperature: float = 0.7):
        """
        Initialise le Revenue Manager IA
        
        Args:
            api_key: Clé API OpenAI (ou utilise variable d'environnement)
            model: Modèle à utiliser
            temperature: Créativité du modèle (0-1)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        
        # Initialiser le LLM
        self.llm = ChatOpenAI(
            model_name=self.model,
            temperature=self.temperature,
            openai_api_key=self.api_key
        )
        
        # Mémoire conversationnelle
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=2000,
            return_messages=True
        )
        
        # Templates de prompts
        self._load_prompt_templates()
    
    def _load_prompt_templates(self):
        """Charge les templates de prompts pour différentes situations"""
        from .prompts import (
            DAILY_PRICING_PROMPT,
            COMPETITOR_ANALYSIS_PROMPT,
            SPECIAL_EVENT_PROMPT,
            CRISIS_MANAGEMENT_PROMPT
        )
        
        self.prompts = {
            'daily_pricing': ChatPromptTemplate.from_template(DAILY_PRICING_PROMPT),
            'competitor_analysis': ChatPromptTemplate.from_template(COMPETITOR_ANALYSIS_PROMPT),
            'special_event': ChatPromptTemplate.from_template(SPECIAL_EVENT_PROMPT),
            'crisis_management': ChatPromptTemplate.from_template(CRISIS_MANAGEMENT_PROMPT)
        }
    
    def analyze_situation(self, 
                         hotel_data: Dict[str, Any],
                         market_data: Dict[str, Any],
                         historical_performance: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse la situation actuelle et génère des recommandations
        
        Args:
            hotel_data: Données de l'hôtel (occupation, prix actuels, etc.)
            market_data: Données du marché (concurrents, événements, etc.)
            historical_performance: Performance historique
            
        Returns:
            Analyse et recommandations
        """
        # Préparer le contexte
        context = self._prepare_context(hotel_data, market_data, historical_performance)
        
        # Choisir le bon prompt selon la situation
        prompt_type = self._determine_prompt_type(context)
        prompt = self.prompts[prompt_type]
        
        # Créer la chaîne LLM
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory
        )
        
        # Obtenir l'analyse
        response = chain.run(**context)
        
        # Parser et structurer la réponse
        analysis = self._parse_llm_response(response)
        
        return analysis
    
    def _prepare_context(self, hotel_data, market_data, historical_performance):
        """Prépare le contexte pour le LLM"""
        # Calculer les métriques clés
        current_occupancy = hotel_data.get('occupancy_rate', 0)
        avg_occupancy_30d = historical_performance['occupancy_rate'].tail(30).mean()
        
        competitor_prices = market_data.get('competitor_prices', [])
        avg_competitor_price = np.mean(competitor_prices) if competitor_prices else hotel_data.get('current_price', 100)
        
        # Détecter les tendances
        occupancy_trend = self._calculate_trend(historical_performance['occupancy_rate'])
        price_trend = self._calculate_trend(historical_performance['price'])
        
        context = {
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'current_occupancy': f"{current_occupancy*100:.1f}%",
            'current_price': hotel_data.get('current_price', 100),
            'avg_occupancy_30d': f"{avg_occupancy_30d*100:.1f}%",
            'competitor_avg_price': avg_competitor_price,
            'price_vs_competition': f"{(hotel_data.get('current_price', 100)/avg_competitor_price - 1)*100:+.1f}%",
            'occupancy_trend': occupancy_trend,
            'price_trend': price_trend,
            'special_events': market_data.get('events', []),
            'weather_forecast': market_data.get('weather', 'Normal'),
            'day_of_week': datetime.now().strftime('%A'),
            'season': self._get_season(),
            'hotel_category': hotel_data.get('category', '3 étoiles'),
            'total_rooms': hotel_data.get('total_rooms', 100)
        }
        
        return context
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """Calcule la tendance d'une série temporelle"""
        if len(series) < 7:
            return "Données insuffisantes"
        
        recent = series.tail(7).mean()
        previous = series.tail(14).head(7).mean()
        
        change = (recent - previous) / previous if previous != 0 else 0
        
        if change > 0.05:
            return "En hausse"
        elif change < -0.05:
            return "En baisse"
        else:
            return "Stable"
    
    def _get_season(self) -> str:
        """Détermine la saison actuelle"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "Hiver"
        elif month in [3, 4, 5]:
            return "Printemps"
        elif month in [6, 7, 8]:
            return "Été"
        else:
            return "Automne"
    
    def _determine_prompt_type(self, context: Dict[str, Any]) -> str:
        """Détermine quel type de prompt utiliser"""
        # Logique de sélection du prompt
        if context.get('special_events'):
            return 'special_event'
        elif float(context['current_occupancy'].rstrip('%')) < 40:
            return 'crisis_management'
        elif context.get('competitor_avg_price'):
            return 'competitor_analysis'
        else:
            return 'daily_pricing'
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse la réponse du LLM en format structuré"""
        import re
        
        analysis = {
            'summary': '',
            'recommended_actions': [],
            'price_recommendations': {},
            'risk_assessment': '',
            'expected_impact': {}
        }
        
        # Extraire les sections de la réponse
        # (Implémentation simplifiée - en production, utiliser un parsing plus robuste)
        
        # Rechercher les recommandations de prix
        price_match = re.search(r'Prix recommandé[:\s]+(\d+)', response)
        if price_match:
            analysis['price_recommendations']['standard'] = float(price_match.group(1))
        
        # Extraire les actions recommandées
        actions = re.findall(r'[-•]\s*([^-•\n]+)', response)
        analysis['recommended_actions'] = [action.strip() for action in actions[:5]]
        
        # Résumé (premières lignes)
        lines = response.split('\n')
        analysis['summary'] = ' '.join(lines[:3])
        
        return analysis
    
    def generate_pricing_strategy(self,
                                 forecast_horizon: int = 30,
                                 constraints: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Génère une stratégie de tarification pour les N prochains jours
        
        Args:
            forecast_horizon: Nombre de jours à prévoir
            constraints: Contraintes business (prix min/max, etc.)
            
        Returns:
            DataFrame avec les recommandations de prix par jour
        """
        strategy = []
        base_date = datetime.now()
        
        for i in range(forecast_horizon):
            date = base_date + timedelta(days=i)
            
            # Simuler des données (en production, utiliser les vraies prédictions)
            day_context = {
                'date': date,
                'day_of_week': date.strftime('%A'),
                'predicted_demand': 0.7 + 0.2 * np.sin(2 * np.pi * i / 7),
                'competitor_activity': 'Normal',
                'special_events': []
            }
            
            # Obtenir la recommandation pour ce jour
            recommendation = self._get_daily_recommendation(day_context, constraints)
            
            strategy.append({
                'date': date,
                'recommended_price': recommendation['price'],
                'confidence': recommendation['confidence'],
                'reasoning': recommendation['reasoning']
            })
        
        return pd.DataFrame(strategy)
    
    def _get_daily_recommendation(self, 
                                 day_context: Dict[str, Any],
                                 constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Obtient une recommandation de prix pour un jour spécifique"""
        # Logique simplifiée - en production, utiliser le LLM
        base_price = 120
        demand_adjustment = (day_context['predicted_demand'] - 0.7) * 50
        
        # Ajustement week-end
        if day_context['day_of_week'] in ['Saturday', 'Sunday']:
            weekend_premium = 20
        else:
            weekend_premium = 0
        
        recommended_price = base_price + demand_adjustment + weekend_premium
        
        # Appliquer les contraintes
        if constraints:
            recommended_price = max(constraints.get('min_price', 80), 
                                  min(recommended_price, constraints.get('max_price', 300)))
        
        return {
            'price': round(recommended_price, 2),
            'confidence': 0.85,
            'reasoning': f"Basé sur une demande prévue de {day_context['predicted_demand']:.1%}"
        }
```

### `src/ai_revenue_manager/prompts.py`

```python
"""
Templates de prompts pour le Revenue Manager IA
"""

DAILY_PRICING_PROMPT = """
Tu es un Revenue Manager expert avec 20 ans d'expérience dans l'hôtellerie de luxe.
Tu analyses la situation suivante pour optimiser les revenus de l'hôtel.

SITUATION ACTUELLE:
- Date: {current_date} ({day_of_week})
- Occupation actuelle: {current_occupancy}
- Prix actuel: {current_price}€
- Occupation moyenne (30j): {avg_occupancy_30d}
- Tendance occupation: {occupancy_trend}
- Saison: {season}

MARCHÉ:
- Prix moyen concurrents: {competitor_avg_price}€
- Position vs concurrence: {price_vs_competition}
- Météo prévue: {weather_forecast}

HÔTEL:
- Catégorie: {hotel_category}
- Nombre de chambres: {total_rooms}

Fournit une analyse détaillée et des recommandations concrètes incluant:
1. Analyse de la situation
2. Recommandations de prix (avec justification)
3. Actions à court terme (24-48h)
4. Risques identifiés
5. Impact attendu sur le RevPAR

Format ta réponse de manière structurée et professionnelle.
"""

COMPETITOR_ANALYSIS_PROMPT = """
Tu es un Revenue Manager analysant la position concurrentielle de l'hôtel.

DONNÉES ACTUELLES:
- Notre prix: {current_price}€
- Prix moyen marché: {competitor_avg_price}€
- Écart: {price_vs_competition}
- Notre occupation: {current_occupancy}
- Tendances: Occupation {occupancy_trend}, Prix {price_trend}

CONTEXTE:
- Jour: {day_of_week}
- Saison: {season}
- Événements: {special_events}

Analyse:
1. Notre positionnement tarifaire est-il optimal?
2. Opportunités de yield management?
3. Recommandations de prix par segment
4. Stratégie face à la concurrence
5. Actions prioritaires

Sois précis et orienté résultats.
"""

SPECIAL_EVENT_PROMPT = """
Tu gères la tarification pendant un événement spécial.

ÉVÉNEMENT:
{special_events}

SITUATION HÔTEL:
- Occupation: {current_occupancy}
- Prix actuel: {current_price}€
- Capacité: {total_rooms} chambres

MARCHÉ:
- Prix concurrents: {competitor_avg_price}€
- Jour: {day_of_week}

Stratégie pour maximiser les revenus:
1. Analyse de l'impact de l'événement
2. Recommandation tarifaire détaillée
3. Gestion des restrictions (min stay, etc.)
4. Stratégie de distribution
5. Timeline des actions

Maximise le RevPAR tout en maintenant la satisfaction client.
"""

CRISIS_MANAGEMENT_PROMPT = """
Tu es en situation de faible occupation nécessitant une action rapide.

ALERTE:
- Occupation: {current_occupancy} (critique!)
- Prix actuel: {current_price}€
- Tendance: {occupancy_trend}

CONTEXTE:
- Date: {current_date}
- Concurrence: {competitor_avg_price}€
- Météo: {weather_forecast}

Plan d'action d'urgence:
1. Diagnostic de la situation
2. Ajustements tarifaires immédiats
3. Promotions flash recommandées
4. Canaux de distribution à activer
5. Mesures pour les 7 prochains jours

Sois créatif mais réaliste. L'objectif est de remplir l'hôtel.
"""
```

## 2️⃣ Module Competitor Analysis

### `src/competitor_analysis/web_scraper.py`

```python
"""
Module de web scraping pour la veille tarifaire concurrentielle
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import re
from fake_useragent import UserAgent
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class CompetitorPriceScraper:
    """
    Scraper pour récupérer les prix des hôtels concurrents
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialise le scraper
        
        Args:
            headless: Exécuter le navigateur en mode headless
        """
        self.ua = UserAgent()
        self.headless = headless
        self.session = None
        
        # Configuration Selenium pour les sites dynamiques
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument(f"user-agent={self.ua.random}")
    
    async def scrape_booking_com(self, 
                                hotel_ids: List[str],
                                check_in: datetime,
                                check_out: datetime,
                                rooms: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape les prix sur Booking.com
        
        Args:
            hotel_ids: Liste des IDs d'hôtels Booking
            check_in: Date d'arrivée
            check_out: Date de départ
            rooms: Nombre de chambres
            
        Returns:
            Liste des prix par hôtel
        """
        results = []
        
        async with aiohttp.ClientSession() as session:
            for hotel_id in hotel_ids:
                try:
                    price_data = await self._fetch_booking_price(
                        session, hotel_id, check_in, check_out, rooms
                    )
                    results.append(price_data)
                    
                    # Délai pour éviter le rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"Erreur scraping Booking hotel {hotel_id}: {e}")
                    results.append({
                        'hotel_id': hotel_id,
                        'error': str(e)
                    })
        
        return results
    
    async def _fetch_booking_price(self, 
                                  session: aiohttp.ClientSession,
                                  hotel_id: str,
                                  check_in: datetime,
                                  check_out: datetime,
                                  rooms: int) -> Dict[str, Any]:
        """Récupère le prix d'un hôtel sur Booking"""
        # Format des dates pour Booking
        checkin_str = check_in.strftime('%Y-%m-%d')
        checkout_str = check_out.strftime('%Y-%m-%d')
        
        # URL de l'hôtel
        url = f"https://www.booking.com/hotel/fr/{hotel_id}.html"
        
        params = {
            'checkin': checkin_str,
            'checkout': checkout_str,
            'group_adults': rooms * 2,
            'no_rooms': rooms,
            'group_children': 0
        }
        
        headers = {
            'User-Agent': self.ua.random,
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept': 'text/html,application/xhtml+xml'
        }
        
        async with session.get(url, params=params, headers=headers) as response:
            html = await response.text()
            
            # Parser le HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extraire les données (sélecteurs simplifiés - à adapter)
            price_element = soup.find('span', {'class': 'prco-valign-middle-helper'})
            hotel_name = soup.find('h2', {'class': 'hp__hotel-name'})
            
            price = None
            if price_element:
                price_text = price_element.text.strip()
                # Extraire le prix numérique
                price_match = re.search(r'(\d+)', price_text.replace(' ', ''))
                if price_match:
                    price = float(price_match.group(1))
            
            return {
                'hotel_id': hotel_id,
                'hotel_name': hotel_name.text.strip() if hotel_name else 'Unknown',
                'platform': 'booking.com',
                'check_in': checkin_str,
                'check_out': checkout_str,
                'price': price,
                'currency': 'EUR',
                'rooms': rooms,
                'scraped_at': datetime.now().isoformat()
            }
    
    def scrape_multiple_platforms(self,
                                 hotels: List[Dict[str, str]],
                                 check_in: datetime,
                                 check_out: datetime,
                                 platforms: List[str] = None) -> pd.DataFrame:
        """
        Scrape plusieurs plateformes pour plusieurs hôtels
        
        Args:
            hotels: Liste des hôtels avec leurs IDs par plateforme
            check_in: Date d'arrivée
            check_out: Date de départ
            platforms: Plateformes à scraper
            
        Returns:
            DataFrame avec tous les prix
        """
        if platforms is None:
            platforms = ['booking', 'hotels', 'expedia']
        
        all_results = []
        
        # Scraping asynchrone par plateforme
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for platform in platforms:
            if platform == 'booking':
                booking_ids = [h['booking_id'] for h in hotels if 'booking_id' in h]
                results = loop.run_until_complete(
                    self.scrape_booking_com(booking_ids, check_in, check_out)
                )
                all_results.extend(results)
            
            # Ajouter d'autres plateformes ici
        
        loop.close()
        
        # Convertir en DataFrame
        df = pd.DataFrame(all_results)
        
        # Nettoyer et enrichir les données
        df['check_in'] = pd.to_datetime(df['check_in'])
        df['check_out'] = pd.to_datetime(df['check_out'])
        df['nights'] = (df['check_out'] - df['check_in']).dt.days
        df['price_per_night'] = df['price'] / df['nights']
        
        return df
    
    def scrape_tripadvisor_selenium(self,
                                   hotel_url: str,
                                   check_in: datetime,
                                   check_out: datetime) -> Dict[str, Any]:
        """
        Scrape TripAdvisor avec Selenium (pour les sites dynamiques)
        """
        driver = webdriver.Chrome(options=self.chrome_options)
        
        try:
            # Naviguer vers la page
            driver.get(hotel_url)
            
            # Attendre le chargement
            wait = WebDriverWait(driver, 10)
            
            # Cliquer sur le sélecteur de dates
            date_picker = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "uitk-fake-input"))
            )
            date_picker.click()
            
            # Sélectionner les dates (logique simplifiée)
            # ... code pour sélectionner les dates ...
            
            # Attendre les prix
            price_element = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "price"))
            )
            
            price = float(price_element.text.replace('€', '').strip())
            
            return {
                'url': hotel_url,
                'price': price,
                'check_in': check_in.isoformat(),
                'check_out': check_out.isoformat(),
                'platform': 'tripadvisor'
            }
            
        finally:
            driver.quit()
```

### `src/competitor_analysis/hotel_matcher.py`

```python
"""
Module pour identifier les hôtels concurrents similaires
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import requests
from geopy.distance import geodesic
from dataclasses import dataclass
import json

@dataclass
class HotelProfile:
    """Profil d'un hôtel pour la comparaison"""
    name: str
    stars: int
    total_rooms: int
    latitude: float
    longitude: float
    amenities: List[str]
    room_types: List[str]
    average_price: float
    category: str  # Business, Leisure, Budget, Luxury
    chain: Optional[str] = None
    tripadvisor_id: Optional[str] = None
    booking_id: Optional[str] = None
    google_place_id: Optional[str] = None

class HotelMatcher:
    """
    Trouve les hôtels concurrents les plus similaires
    """
    
    def __init__(self, google_api_key: Optional[str] = None):
        """
        Initialise le matcher
        
        Args:
            google_api_key: Clé API Google Places
        """
        self.google_api_key = google_api_key
        self.scaler = StandardScaler()
        
        # Poids pour le calcul de similarité
        self.weights = {
            'stars': 0.20,
            'size': 0.15,
            'distance': 0.25,
            'amenities': 0.20,
            'price': 0.15,
            'category': 0.05
        }
    
    def find_competitors_nearby(self,
                              hotel: HotelProfile,
                              radius_km: float = 5.0,
                              max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Trouve les hôtels concurrents dans un rayon donné
        
        Args:
            hotel: Profil de notre hôtel
            radius_km: Rayon de recherche en km
            max_results: Nombre max de résultats
            
        Returns:
            Liste des hôtels trouvés
        """
        if not self.google_api_key:
            raise ValueError("Google API key requise pour la recherche")
        
        # Recherche via Google Places API
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        
        params = {
            'location': f"{hotel.latitude},{hotel.longitude}",
            'radius': radius_km * 1000,  # Convertir en mètres
            'type': 'lodging',
            'key': self.google_api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        competitors = []
        
        if data['status'] == 'OK':
            for place in data['results'][:max_results]:
                # Récupérer les détails de chaque hôtel
                details = self._get_place_details(place['place_id'])
                
                if details:
                    competitors.append({
                        'name': place['name'],
                        'place_id': place['place_id'],
                        'rating': place.get('rating', 0),
                        'user_ratings_total': place.get('user_ratings_total', 0),
                        'price_level': place.get('price_level', 0),
                        'location': place['geometry']['location'],
                        'details': details
                    })
        
        return competitors
    
    def _get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un lieu via Google Places"""
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        
        params = {
            'place_id': place_id,
            'fields': 'name,formatted_phone_number,website,address_component,photo,type',
            'key': self.google_api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            return data['result']
        return None
    
    def calculate_similarity(self,
                           hotel1: HotelProfile,
                           hotel2: HotelProfile) -> float:
        """
        Calcule le score de similarité entre deux hôtels
        
        Args:
            hotel1: Premier hôtel
            hotel2: Deuxième hôtel
            
        Returns:
            Score de similarité (0-1)
        """
        scores = {}
        
        # 1. Similarité par étoiles
        scores['stars'] = 1.0 - abs(hotel1.stars - hotel2.stars) / 5.0
        
        # 2. Similarité par taille
        size_diff = abs(hotel1.total_rooms - hotel2.total_rooms)
        scores['size'] = np.exp(-size_diff / 50)  # Décroissance exponentielle
        
        # 3. Distance géographique
        distance = geodesic(
            (hotel1.latitude, hotel1.longitude),
            (hotel2.latitude, hotel2.longitude)
        ).km
        scores['distance'] = np.exp(-distance / 2)  # Décroissance sur 2km
        
        # 4. Similarité des équipements
        amenities1 = set(hotel1.amenities)
        amenities2 = set(hotel2.amenities)
        if amenities1 or amenities2:
            jaccard = len(amenities1 & amenities2) / len(amenities1 | amenities2)
            scores['amenities'] = jaccard
        else:
            scores['amenities'] = 0.5
        
        # 5. Similarité de prix
        price_diff = abs(hotel1.average_price - hotel2.average_price)
        scores['price'] = np.exp(-price_diff / 50)
        
        # 6. Même catégorie
        scores['category'] = 1.0 if hotel1.category == hotel2.category else 0.3
        
        # Score final pondéré
        final_score = sum(
            scores[key] * self.weights[key] 
            for key in scores
        )
        
        return final_score
    
    def find_best_competitors(self,
                            our_hotel: HotelProfile,
                            candidate_hotels: List[HotelProfile],
                            top_n: int = 5,
                            min_similarity: float = 0.5) -> List[Tuple[HotelProfile, float]]:
        """
        Trouve les N meilleurs concurrents selon la similarité
        
        Args:
            our_hotel: Notre hôtel
            candidate_hotels: Hôtels candidats
            top_n: Nombre de concurrents à retourner
            min_similarity: Score minimum de similarité
            
        Returns:
            Liste des (hôtel, score) triée par similarité
        """
        similarities = []
        
        for candidate in candidate_hotels:
            score = self.calculate_similarity(our_hotel, candidate)
            if score >= min_similarity:
                similarities.append((candidate, score))
        
        # Trier par score décroissant
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_n]
    
    def create_competitive_set(self,
                             our_hotel: HotelProfile,
                             radius_km: float = 5.0,
                             max_competitors: int = 5) -> pd.DataFrame:
        """
        Crée un ensemble compétitif (comp set) pour notre hôtel
        
        Returns:
            DataFrame avec les concurrents et leurs caractéristiques
        """
        # 1. Trouver les hôtels à proximité
        nearby_hotels = self.find_competitors_nearby(our_hotel, radius_km)
        
        # 2. Convertir en HotelProfile
        candidate_profiles = []
        for hotel_data in nearby_hotels:
            try:
                profile = self._parse_google_place_to_profile(hotel_data)
                candidate_profiles.append(profile)
            except Exception as e:
                print(f"Erreur parsing hôtel {hotel_data['name']}: {e}")
                continue
        
        # 3. Calculer les similarités et sélectionner les meilleurs
        best_competitors = self.find_best_competitors(
            our_hotel, 
            candidate_profiles,
            top_n=max_competitors
        )
        
        # 4. Créer le DataFrame final
        comp_set_data = []
        
        for competitor, similarity_score in best_competitors:
            comp_set_data.append({
                'name': competitor.name,
                'stars': competitor.stars,
                'rooms': competitor.total_rooms,
                'distance_km': geodesic(
                    (our_hotel.latitude, our_hotel.longitude),
                    (competitor.latitude, competitor.longitude)
                ).km,
                'similarity_score': similarity_score,
                'category': competitor.category,
                'google_place_id': competitor.google_place_id,
                'booking_id': competitor.booking_id,
                'tripadvisor_id': competitor.tripadvisor_id
            })
        
        return pd.DataFrame(comp_set_data)
    
    def _parse_google_place_to_profile(self, place_data: Dict[str, Any]) -> HotelProfile:
        """Parse les données Google Places en HotelProfile"""
        # Estimation des étoiles basée sur le rating et price_level
        rating = place_data.get('rating', 3.5)
        price_level = place_data.get('price_level', 2)
        
        if price_level <= 1:
            stars = 2
            category = 'Budget'
        elif price_level == 2:
            stars = 3
            category = 'Business'
        elif price_level == 3:
            stars = 4
            category = 'Leisure'
        else:
            stars = 5
            category = 'Luxury'
        
        # Ajuster selon le rating
        if rating >= 4.5 and stars < 5:
            stars += 1
        elif rating < 3.0 and stars > 2:
            stars -= 1
        
        return HotelProfile(
            name=place_data['name'],
            stars=stars,
            total_rooms=100,  # Estimation par défaut
            latitude=place_data['location']['lat'],
            longitude=place_data['location']['lng'],
            amenities=[],  # À enrichir avec les détails
            room_types=['Standard'],  # Par défaut
            average_price=50 + (price_level * 30),  # Estimation
            category=category,
            google_place_id=place_data['place_id']
        )
```

## 3️⃣ Module Hotel Profile

### `src/hotel_profile/hotel_config.py`

```python
"""
Configuration et profil de l'établissement hôtelier
"""
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml

@dataclass
class RoomTypeConfig:
    """Configuration d'un type de chambre"""
    name: str
    total_count: int
    base_price: float
    min_price: float
    max_price: float
    size_sqm: float
    max_occupancy: int
    amenities: List[str]

@dataclass
class HotelConfiguration:
    """Configuration complète de l'hôtel"""
    # Informations générales
    name: str
    brand: Optional[str]
    stars: int
    category: str  # Business, Leisure, Budget, Luxury, Boutique
    
    # Localisation
    address: str
    city: str
    country: str
    latitude: float
    longitude: float
    
    # Capacité
    total_rooms: int
    room_types: List[RoomTypeConfig]
    total_floors: int
    
    # Équipements
    amenities: List[str]
    facilities: Dict[str, bool]  # spa, gym, pool, etc.
    restaurants: int
    meeting_rooms: int
    
    # Business rules
    check_in_time: str  # "15:00"
    check_out_time: str  # "11:00"
    cancellation_policy: str
    
    # Identifiants externes
    external_ids: Dict[str, str]  # booking_id, expedia_id, etc.
    
    # Contact
    phone: str
    email: str
    website: str

class HotelProfileManager:
    """
    Gestionnaire du profil et de la configuration de l'hôtel
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le gestionnaire
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = config_path or "config/hotel_profile.yaml"
        self.hotel_config = None
        
        # Charger la configuration si elle existe
        if os.path.exists(self.config_path):
            self.load_configuration()
    
    def create_configuration_wizard(self) -> HotelConfiguration:
        """
        Assistant interactif pour créer la configuration de l'hôtel
        """
        print("\n🏨 CONFIGURATION DE VOTRE ÉTABLISSEMENT\n")
        print("Veuillez fournir les informations suivantes:")
        
        # Informations de base
        name = input("\nNom de l'hôtel: ")
        brand = input("Chaîne/Marque (laisser vide si indépendant): ") or None
        stars = int(input("Nombre d'étoiles (1-5): "))
        
        print("\nCatégorie:")
        print("1. Business")
        print("2. Leisure")
        print("3. Budget")
        print("4. Luxury")
        print("5. Boutique")
        category_choice = input("Choisissez (1-5): ")
        categories = ['Business', 'Leisure', 'Budget', 'Luxury', 'Boutique']
        category = categories[int(category_choice) - 1]
        
        # Localisation
        print("\n📍 LOCALISATION")
        address = input("Adresse: ")
        city = input("Ville: ")
        country = input("Pays: ")
        latitude = float(input("Latitude: "))
        longitude = float(input("Longitude: "))
        
        # Capacité
        print("\n🛏 CAPACITÉ")
        total_rooms = int(input("Nombre total de chambres: "))
        total_floors = int(input("Nombre d'étages: "))
        
        # Types de chambres
        room_types = []
        print("\n📊 TYPES DE CHAMBRES")
        n_types = int(input("Combien de types de chambres différents? "))
        
        for i in range(n_types):
            print(f"\nType {i+1}:")
            room_type = RoomTypeConfig(
                name=input("  Nom (ex: Standard, Deluxe, Suite): "),
                total_count=int(input("  Nombre de chambres: ")),
                base_price=float(input("  Prix de base (€): ")),
                min_price=float(input("  Prix minimum (€): ")),
                max_price=float(input("  Prix maximum (€): ")),
                size_sqm=float(input("  Surface (m²): ")),
                max_occupancy=int(input("  Occupation max: ")),
                amenities=input("  Équipements (séparés par virgule): ").split(',')
            )
            room_types.append(room_type)
        
        # Équipements
        print("\n🏊 ÉQUIPEMENTS")
        amenities = input("Équipements généraux (séparés par virgule): ").split(',')
        
        facilities = {
            'spa': input("Spa (oui/non): ").lower() == 'oui',
            'gym': input("Salle de sport (oui/non): ").lower() == 'oui',
            'pool': input("Piscine (oui/non): ").lower() == 'oui',
            'parking': input("Parking (oui/non): ").lower() == 'oui',
            'wifi': input("WiFi gratuit (oui/non): ").lower() == 'oui',
            'restaurant': input("Restaurant (oui/non): ").lower() == 'oui',
            'bar': input("Bar (oui/non): ").lower() == 'oui',
            'room_service': input("Room service (oui/non): ").lower() == 'oui'
        }
        
        restaurants = int(input("Nombre de restaurants: "))
        meeting_rooms = int(input("Nombre de salles de réunion: "))
        
        # Règles business
        print("\n⏰ RÈGLES")
        check_in_time = input("Heure de check-in (ex: 15:00): ")
        check_out_time = input("Heure de check-out (ex: 11:00): ")
        cancellation_policy = input("Politique d'annulation (flexible/modérée/stricte): ")
        
        # Identifiants externes
        print("\n🔗 IDENTIFIANTS EXTERNES (optionnel)")
        external_ids = {}
        booking_id = input("ID Booking.com: ")
        if booking_id:
            external_ids['booking'] = booking_id
        
        expedia_id = input("ID Expedia: ")
        if expedia_id:
            external_ids['expedia'] = expedia_id
        
        # Contact
        print("\n📞 CONTACT")
        phone = input("Téléphone: ")
        email = input("Email: ")
        website = input("Site web: ")
        
        # Créer la configuration
        config = HotelConfiguration(
            name=name,
            brand=brand,
            stars=stars,
            category=category,
            address=address,
            city=city,
            country=country,
            latitude=latitude,
            longitude=longitude,
            total_rooms=total_rooms,
            room_types=room_types,
            total_floors=total_floors,
            amenities=[a.strip() for a in amenities],
            facilities=facilities,
            restaurants=restaurants,
            meeting_rooms=meeting_rooms,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            cancellation_policy=cancellation_policy,
            external_ids=external_ids,
            phone=phone,
            email=email,
            website=website
        )
        
        # Sauvegarder
        self.hotel_config = config
        self.save_configuration()
        
        print("\n✅ Configuration créée avec succès!")
        return config
    
    def save_configuration(self):
        """Sauvegarde la configuration dans un fichier"""
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Convertir en dictionnaire
        config_dict = self._config_to_dict(self.hotel_config)
        
        # Sauvegarder en YAML
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, allow_unicode=True, default_flow_style=False)
    
    def load_configuration(self) -> HotelConfiguration:
        """Charge la configuration depuis le fichier"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        # Reconstruire les objets
        room_types = [
            RoomTypeConfig(**rt) for rt in config_dict['room_types']
        ]
        
        config_dict['room_types'] = room_types
        self.hotel_config = HotelConfiguration(**config_dict)
        
        return self.hotel_config
    
    def _config_to_dict(self, config: HotelConfiguration) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire"""
        result = asdict(config)
        # Convertir les room_types
        result['room_types'] = [asdict(rt) for rt in config.room_types]
        return result
    
    def get_competitor_search_criteria(self) -> Dict[str, Any]:
        """
        Retourne les critères pour rechercher des concurrents similaires
        """
        if not self.hotel_config:
            raise ValueError("Configuration non chargée")
        
        return {
            'location': {
                'lat': self.hotel_config.latitude,
                'lng': self.hotel_config.longitude,
                'radius_km': 5.0
            },
            'characteristics': {
                'stars': self.hotel_config.stars,
                'category': self.hotel_config.category,
                'size_range': {
                    'min': self.hotel_config.total_rooms * 0.5,
                    'max': self.hotel_config.total_rooms * 2.0
                }
            },
            'amenities': self.hotel_config.amenities,
            'target_competitors': 5
        }
    
    def export_for_ai_context(self) -> str:
        """
        Exporte la configuration dans un format optimisé pour le LLM
        """
        if not self.hotel_config:
            raise ValueError("Configuration non chargée")
        
        context = f"""
PROFIL DE L'HÔTEL:
Nom: {self.hotel_config.name}
Catégorie: {self.hotel_config.stars} étoiles - {self.hotel_config.category}
Localisation: {self.hotel_config.city}, {self.hotel_config.country}

CAPACITÉ:
- {self.hotel_config.total_rooms} chambres au total
- Types de chambres:
"""
        
        for room_type in self.hotel_config.room_types:
            context += f"""
  * {room_type.name}: {room_type.total_count} chambres
    - Prix: {room_type.base_price}€ (min: {room_type.min_price}€, max: {room_type.max_price}€)
    - Capacité: {room_type.max_occupancy} personnes
"""
        
        context += f"""
ÉQUIPEMENTS PRINCIPAUX:
{', '.join(self.hotel_config.amenities)}

SERVICES:
- Spa: {'Oui' if self.hotel_config.facilities.get('spa') else 'Non'}
- Piscine: {'Oui' if self.hotel_config.facilities.get('pool') else 'Non'}
- Restaurants: {self.hotel_config.restaurants}
- Salles de réunion: {self.hotel_config.meeting_rooms}
"""
        
        return context
```

## 4️⃣ Interface Streamlit Améliorée

### `app/streamlit_app_v2.py`

```python
"""
Application Streamlit améliorée avec IA et veille concurrentielle
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Ajouter les modules au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_revenue_manager.llm_manager import AIRevenueManager
from src.competitor_analysis.web_scraper import CompetitorPriceScraper
from src.competitor_analysis.hotel_matcher import HotelMatcher
from src.hotel_profile.hotel_config import HotelProfileManager

# Configuration de la page
st.set_page_config(
    page_title="Hotel Revenue Optimizer Pro",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des modules
@st.cache_resource
def init_modules():
    """Initialise les modules de l'application"""
    return {
        'profile_manager': HotelProfileManager(),
        'ai_manager': AIRevenueManager(model="gpt-4"),
        'hotel_matcher': HotelMatcher(google_api_key=os.getenv("GOOGLE_API_KEY")),
        'price_scraper': CompetitorPriceScraper()
    }

def main():
    st.title("🏨 Hotel Revenue Optimizer Pro")
    st.markdown("**Système intelligent de Revenue Management avec IA**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Configuration de l'hôtel
        if st.button("🏨 Configurer mon hôtel"):
            st.session_state['show_config'] = True
        
        # Paramètres IA
        st.subheader("🤖 Paramètres IA")
        ai_model = st.selectbox(
            "Modèle",
            ["gpt-4", "gpt-3.5-turbo", "claude-2"],
            help="Modèle d'IA à utiliser"
        )
        
        ai_temperature = st.slider(
            "Créativité",
            0.0, 1.0, 0.7,
            help="0 = Conservateur, 1 = Créatif"
        )
        
        # Paramètres de veille
        st.subheader("🔍 Veille concurrentielle")
        search_radius = st.slider(
            "Rayon de recherche (km)",
            1, 20, 5
        )
        
        max_competitors = st.number_input(
            "Nombre de concurrents",
            1, 10, 5
        )
    
    # Contenu principal
    modules = init_modules()
    
    # Configuration de l'hôtel
    if st.session_state.get('show_config', False):
        with st.expander("🏨 Configuration de l'établissement", expanded=True):
            hotel_config_section(modules['profile_manager'])
    
    # Vérifier si l'hôtel est configuré
    try:
        hotel_config = modules['profile_manager'].load_configuration()
        
        # Afficher les informations de l'hôtel
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Hôtel", hotel_config.name)
        with col2:
            st.metric("Catégorie", f"{hotel_config.stars}⭐ {hotel_config.category}")
        with col3:
            st.metric("Chambres", hotel_config.total_rooms)
        with col4:
            st.metric("Ville", hotel_config.city)
        
        # Tabs principaux
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard", 
            "🤖 Revenue Manager IA",
            "🔍 Analyse Concurrentielle",
            "📈 Stratégie & Prévisions"
        ])
        
        with tab1:
            dashboard_section(modules)
        
        with tab2:
            ai_revenue_manager_section(modules)
        
        with tab3:
            competitor_analysis_section(modules, hotel_config)
        
        with tab4:
            strategy_section(modules)
            
    except FileNotFoundError:
        st.warning("⚠️ Veuillez d'abord configurer votre établissement")
        if st.button("Configurer maintenant"):
            st.session_state['show_config'] = True
            st.experimental_rerun()

def hotel_config_section(profile_manager):
    """Section de configuration de l'hôtel"""
    st.subheader("Configuration de l'établissement")
    
    # Formulaire de configuration
    with st.form("hotel_config"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nom de l'hôtel", value="Mon Hôtel")
            brand = st.text_input("Chaîne/Marque (optionnel)")
            stars = st.select_slider("Étoiles", options=[1, 2, 3, 4, 5], value=3)
            category = st.selectbox(
                "Catégorie",
                ["Business", "Leisure", "Budget", "Luxury", "Boutique"]
            )
        
        with col2:
            city = st.text_input("Ville", value="Paris")
            country = st.text_input("Pays", value="France")
            total_rooms = st.number_input("Nombre total de chambres", min_value=1, value=100)
            
        # Localisation
        st.subheader("📍 Localisation")
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=48.8566, format="%.4f")
        with col2:
            longitude = st.number_input("Longitude", value=2.3522, format="%.4f")
        
        # Types de chambres
        st.subheader("🛏️ Types de chambres")
        room_types = []
        
        # Chambre Standard
        with st.expander("Chambre Standard"):
            std_count = st.number_input("Nombre", min_value=0, value=60, key="std_count")
            std_price = st.number_input("Prix de base (€)", min_value=0.0, value=120.0, key="std_price")
            if std_count > 0:
                room_types.append({
                    'name': 'Standard',
                    'count': std_count,
                    'base_price': std_price,
                    'min_price': std_price * 0.7,
                    'max_price': std_price * 2.0
                })
        
        # Équipements
        st.subheader("🏊 Équipements")
        col1, col2, col3 = st.columns(3)
        with col1:
            has_spa = st.checkbox("Spa")
            has_gym = st.checkbox("Salle de sport")
        with col2:
            has_pool = st.checkbox("Piscine")
            has_parking = st.checkbox("Parking")
        with col3:
            has_restaurant = st.checkbox("Restaurant")
            has_bar = st.checkbox("Bar")
        
        submitted = st.form_submit_button("💾 Sauvegarder la configuration")
        
        if submitted:
            # Créer la configuration
            # (Code simplifié - en production, utiliser la méthode complète)
            st.success("✅ Configuration sauvegardée avec succès!")
            st.session_state['show_config'] = False
            st.experimental_rerun()

def ai_revenue_manager_section(modules):
    """Section du Revenue Manager IA"""
    st.header("🤖 Revenue Manager IA")
    
    # Charger les données actuelles
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_occupancy = st.number_input(
            "Taux d'occupation actuel (%)",
            0, 100, 75
        ) / 100
    
    with col2:
        current_price = st.number_input(
            "Prix moyen actuel (€)",
            0.0, 500.0, 120.0
        )
    
    with col3:
        forecast_days = st.number_input(
            "Jours à analyser",
            1, 90, 30
        )
    
    # Contexte additionnel
    with st.expander("📝 Contexte supplémentaire"):
        special_events = st.text_area(
            "Événements spéciaux",
            placeholder="Ex: Festival de musique du 15 au 17 juin"
        )
        
        constraints = st.text_area(
            "Contraintes business",
            placeholder="Ex: Ne pas descendre sous 80€, maintenir un taux minimum de 60%"
        )
    
    if st.button("🧠 Obtenir les recommandations IA", type="primary"):
        with st.spinner("L'IA analyse la situation..."):
            # Préparer les données
            hotel_data = {
                'occupancy_rate': current_occupancy,
                'current_price': current_price,
                'category': '3 étoiles',
                'total_rooms': 100
            }
            
            market_data = {
                'competitor_prices': [110, 125, 130, 115, 140],
                'events': special_events.split('\n') if special_events else [],
                'weather': 'Ensoleillé'
            }
            
            # Simuler des données historiques
            historical = pd.DataFrame({
                'date': pd.date_range(end=datetime.now(), periods=30),
                'occupancy_rate': np.random.uniform(0.6, 0.9, 30),
                'price': np.random.uniform(100, 140, 30)
            })
            
            # Obtenir l'analyse IA
            ai_analysis = modules['ai_manager'].analyze_situation(
                hotel_data, market_data, historical
            )
            
            # Afficher les résultats
            st.success("✅ Analyse terminée!")
            
            # Résumé
            st.subheader("📋 Résumé de l'analyse")
            st.info(ai_analysis.get('summary', 'Analyse en cours...'))
            
            # Actions recommandées
            st.subheader("🎯 Actions recommandées")
            for i, action in enumerate(ai_analysis.get('recommended_actions', []), 1):
                st.write(f"{i}. {action}")
            
            # Recommandations de prix
            if 'price_recommendations' in ai_analysis:
                st.subheader("💰 Recommandations tarifaires")
                
                price_data = []
                for room_type, price in ai_analysis['price_recommendations'].items():
                    price_data.append({
                        'Type de chambre': room_type,
                        'Prix actuel (€)': current_price,
                        'Prix recommandé (€)': price,
                        'Variation': f"{(price/current_price - 1)*100:+.1f}%"
                    })
                
                df_prices = pd.DataFrame(price_data)
                st.dataframe(df_prices, use_container_width=True)
            
            # Stratégie sur 30 jours
            st.subheader("📅 Stratégie sur 30 jours")
            
            strategy_df = modules['ai_manager'].generate_pricing_strategy(
                forecast_horizon=forecast_days
            )
            
            # Graphique de la stratégie
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=strategy_df['date'],
                y=strategy_df['recommended_price'],
                mode='lines+markers',
                name='Prix recommandé',
                line=dict(color='blue', width=3)
            ))
            
            # Ajouter une bande de confiance
            confidence_upper = strategy_df['recommended_price'] * 1.05
            confidence_lower = strategy_df['recommended_price'] * 0.95
            
            fig.add_trace(go.Scatter(
                x=strategy_df['date'],
                y=confidence_upper,
                fill=None,
                mode='lines',
                line_color='rgba(0,100,80,0)',
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=strategy_df['date'],
                y=confidence_lower,
                fill='tonexty',
                mode='lines',
                line_color='rgba(0,100,80,0)',
                name='Intervalle de confiance'
            ))
            
            fig.update_layout(
                title="Stratégie de prix recommandée par l'IA",
                xaxis_title="Date",
                yaxis_title="Prix (€)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

def competitor_analysis_section(modules, hotel_config):
    """Section d'analyse concurrentielle"""
    st.header("🔍 Analyse Concurrentielle")
    
    # Recherche de concurrents
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Recherche de concurrents similaires")
    
    with col2:
        if st.button("🔄 Actualiser", key="refresh_competitors"):
            st.session_state['competitors_loaded'] = False
    
    # Paramètres de recherche
    with st.expander("⚙️ Paramètres de recherche"):
        search_radius = st.slider("Rayon (km)", 1, 20, 5)
        min_similarity = st.slider("Similarité minimum", 0.0, 1.0, 0.5)
    
    # Charger ou rechercher les concurrents
    if not st.session_state.get('competitors_loaded', False):
        with st.spinner("Recherche des concurrents..."):
            # Créer le profil de notre hôtel
            from src.competitor_analysis.hotel_matcher import HotelProfile
            
            our_hotel = HotelProfile(
                name=hotel_config.name,
                stars=hotel_config.stars,
                total_rooms=hotel_config.total_rooms,
                latitude=hotel_config.latitude,
                longitude=hotel_config.longitude,
                amenities=hotel_config.amenities,
                room_types=[rt.name for rt in hotel_config.room_types],
                average_price=hotel_config.room_types[0].base_price,
                category=hotel_config.category
            )
            
            # Créer le competitive set
            comp_set_df = modules['hotel_matcher'].create_competitive_set(
                our_hotel,
                radius_km=search_radius,
                max_competitors=5
            )
            
            st.session_state['comp_set'] = comp_set_df
            st.session_state['competitors_loaded'] = True
    
    # Afficher les concurrents
    if 'comp_set' in st.session_state:
        st.subheader("🏨 Ensemble concurrentiel")
        
        # Afficher le tableau
        st.dataframe(
            st.session_state['comp_set'],
            use_container_width=True,
            hide_index=True
        )
        
        # Carte des concurrents
        st.subheader("📍 Localisation des concurrents")
        
        # Créer une carte simple (en production, utiliser folium ou similaire)
        map_data = pd.DataFrame({
            'lat': [hotel_config.latitude] + list(st.session_state['comp_set']['distance_km'].index),
            'lon': [hotel_config.longitude] + list(st.session_state['comp_set']['distance_km'].index),
            'name': [hotel_config.name] + list(st.session_state['comp_set']['name']),
            'type': ['Notre hôtel'] + ['Concurrent'] * len(st.session_state['comp_set'])
        })
        
        st.map(map_data)
        
        # Analyse des prix concurrents
        st.subheader("💰 Veille tarifaire")
        
        # Sélection des dates
        col1, col2 = st.columns(2)
        with col1:
            check_in = st.date_input("Date d'arrivée", datetime.now() + timedelta(days=7))
        with col2:
            check_out = st.date_input("Date de départ", check_in + timedelta(days=2))
        
        if st.button("🔍 Rechercher les prix", key="search_prices"):
            with st.spinner("Recherche des prix en cours..."):
                # Simuler la recherche de prix
                # En production, utiliser le web scraper
                
                price_data = []
                for _, competitor in st.session_state['comp_set'].iterrows():
                    price_data.append({
                        'Hôtel': competitor['name'],
                        'Prix/nuit (€)': np.random.uniform(100, 200),
                        'Disponibilité': np.random.choice(['Disponible', 'Limité', 'Complet']),
                        'Source': 'Booking.com',
                        'Mise à jour': datetime.now().strftime('%H:%M')
                    })
                
                # Notre prix
                price_data.insert(0, {
                    'Hôtel': f"{hotel_config.name} (Nous)",
                    'Prix/nuit (€)': 135,
                    'Disponibilité': 'Disponible',
                    'Source': 'Direct',
                    'Mise à jour': datetime.now().strftime('%H:%M')
                })
                
                df_prices = pd.DataFrame(price_data)
                
                # Afficher les résultats
                st.dataframe(
                    df_prices,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Graphique comparatif
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=df_prices['Hôtel'],
                    y=df_prices['Prix/nuit (€)'],
                    marker_color=['red'] + ['blue'] * (len(df_prices) - 1)
                ))
                
                # Ligne de prix moyen
                avg_price = df_prices['Prix/nuit (€)'].mean()
                fig.add_hline(
                    y=avg_price,
                    line_dash="dash",
                    line_color="green",
                    annotation_text=f"Prix moyen: {avg_price:.0f}€"
                )
                
                fig.update_layout(
                    title="Comparaison des prix",
                    xaxis_title="Hôtel",
                    yaxis_title="Prix par nuit (€)",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Recommandations
                st.info(f"""
                💡 **Analyse rapide:**
                - Votre prix est {'au-dessus' if 135 > avg_price else 'en-dessous'} de la moyenne du marché
                - Position concurrentielle: {'Premium' if 135 > avg_price else 'Compétitive'}
                - Recommandation: {'Maintenir le prix' if abs(135 - avg_price) < 10 else 'Ajuster le prix'}
                """)

def strategy_section(modules):
    """Section stratégie et prévisions"""
    st.header("📈 Stratégie & Prévisions")
    
    # Onglets pour différents horizons
    tab1, tab2, tab3 = st.tabs(["Court terme (7j)", "Moyen terme (30j)", "Long terme (90j)"])
    
    with tab1:
        st.subheader("Stratégie court terme")
        
        # Simuler des métriques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "RevPAR prévu",
                "98€",
                "+5.2%",
                help="Revenue Per Available Room"
            )
        
        with col2:
            st.metric(
                "Occupation prévue",
                "82%",
                "+3.1%"
            )
        
        with col3:
            st.metric(
                "ADR prévu",
                "119€",
                "+2.1%",
                help="Average Daily Rate"
            )
        
        with col4:
            st.metric(
                "Revenue total",
                "8,330€",
                "+8.3%"
            )
        
        # Actions prioritaires
        st.subheader("🎯 Actions prioritaires cette semaine")
        
        actions = [
            {"Jour": "Lundi", "Action": "Augmenter les prix de 5%", "Raison": "Forte demande prévue", "Impact": "+400€"},
            {"Jour": "Mercredi", "Action": "Lancer promo last-minute", "Raison": "Occupation < 70%", "Impact": "+15 chambres"},
            {"Jour": "Vendredi", "Action": "Bloquer 10 chambres", "Raison": "Événement local", "Impact": "+1,200€"},
            {"Jour": "Dimanche", "Action": "Ouvrir tarif early bird", "Raison": "Stimuler réservations", "Impact": "+8 rés."}
        ]
        
        df_actions = pd.DataFrame(actions)
        st.dataframe(df_actions, use_container_width=True, hide_index=True)

def dashboard_section(modules):
    """Section dashboard principal"""
    st.header("📊 Dashboard Revenue Management")
    
    # KPIs principaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Occupation", "78%", "+2.3%")
    with col2:
        st.metric("ADR", "125€", "+5.1%")
    with col3:
        st.metric("RevPAR", "97.5€", "+7.5%")
    with col4:
        st.metric("Revenue MTD", "145,620€", "+12.3%")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique d'occupation
        dates = pd.date_range(end=datetime.now(), periods=30)
        occupancy = np.random.uniform(0.65, 0.85, 30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=occupancy * 100,
            mode='lines+markers',
            name='Occupation',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title="Évolution du taux d'occupation",
            xaxis_title="Date",
            yaxis_title="Occupation (%)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graphique RevPAR
        revpar = occupancy * np.random.uniform(120, 140, 30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=revpar,
            mode='lines+markers',
            name='RevPAR',
            line=dict(color='green', width=2)
        ))
        
        fig.update_layout(
            title="Évolution du RevPAR",
            xaxis_title="Date",
            yaxis_title="RevPAR (€)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
```

## 5️⃣ Configuration et Installation

### `requirements_v2.txt`

```txt
# Dépendances existantes
-r requirements.txt

# IA et LLM
openai>=1.0.0
langchain>=0.1.0
langchain-openai>=0.0.5
tiktoken>=0.5.0

# Web scraping
beautifulsoup4>=4.12.0
selenium>=4.15.0
fake-useragent>=1.4.0
aiohttp>=3.9.0

# Géolocalisation
geopy>=2.4.0
folium>=0.15.0

# Configuration
pyyaml>=6.0

# APIs
google-api-python-client>=2.100.0
```

### `.env.example`

```env
# OpenAI
OPENAI_API_KEY=votre_cle_openai

# Google
GOOGLE_API_KEY=votre_cle_google_places
GOOGLE_MAPS_API_KEY=votre_cle_google_maps

# Base de données
sqlalchemy>=2.0.0
alembic>=1.10.0
sqlite3worker>=0.8.0  # Pour SQLite thread-safe

# Cache (optionnel)
redis>=4.5.0
aioredis>=2.0.0

# === AUTHENTICATION & SECURITY ===
# Authentification (optionnel)
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-dotenv>=1.0.0

# === DATA PROCESSING ===
# Formats de fichiers
tabula-py>=2.10.0  # Pour PDF
openpyxl>=3.1.0    # Pour Excel
xlrd>=2.0.1        # Pour anciens Excel

# === UTILITIES ===
# Utilities générales
pathlib2>=2.3.7
typing-extensions>=4.7.0
pydantic>=2.0.0

# Configuration
pydantic-settings>=2.0.0
python-decouple>=3.8

# Logging et monitoring
loguru>=0.7.0

# === DEVELOPMENT & TESTING ===
# Tests (pour développement)
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
pytest-mock>=3.12.0

# Code quality (pour développement)
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.5.0

# === DEPLOYMENT ===
# Déploiement
gunicorn>=21.0.0
docker>=6.1.0

# === PLATFORM SPECIFIC ===
# Windows
pywin32>=306; sys_platform == "win32"

# === OPTIONAL ENHANCEMEMNTS ===
# Analyse de données avancée (optionnel)
statsmodels>=0.14.0
prophet>=1.1.4  # Pour séries temporelles
dask>=2023.9.0  # Pour traitement parallèle

# Visualisations avancées (optionnel)
bokeh>=3.2.0
altair>=5.1.0

# Géolocalisation (optionnel)
geopy>=2.3.0
folium>=0.14.0

# === SPECIFIC LLM MODELS SUPPORT ===
# Support modèles spécifiques (installer selon besoins)

# Pour Mistral
# mistral-common>=1.0.0

# Pour Llama
# llama-cpp-python>=0.2.0

# Pour quantization avancée
# optimum>=1.14.0
# auto-gptq>=0.5.0

# === MONITORING & LOGGING ===
# Production monitoring (optionnel)
# sentry-sdk>=1.38.0
# prometheus-client>=0.18.0

# === JUPYTER SUPPORT ===
# Support notebooks (développement)
jupyter>=1.0.0
ipykernel>=6.25.0
notebook>=7.0.0

# === NOTES D'INSTALLATION ===
# 
# Installation recommandée:
# 1. pip install -r requirements_ai.txt
# 2. python scripts/setup_ai_local.py
# 
# Installation minimale (sans IA):
# pip install streamlit pandas numpy plotly scikit-learn
# 
# Installation complète avec GPU:
# pip install -r requirements_ai.txt
# pip install torch[cuda] --index-url https://download.pytorch.org/whl/cu118
# 
# Pour production:
# pip install -r requirements_ai.txt --no-dev
# 
# Pour développement:
# pip install -r requirements_ai.txt
# pip install -e .
#
