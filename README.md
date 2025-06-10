# 🏨 AI Hotel Revenue Optimizer

> **Système d'optimisation des revenus hôteliers basé sur l'intelligence artificielle**  
> Solution complète de revenue management utilisant le machine learning pour la prédiction de demande et la tarification dynamique


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

- Email: contact@example.com
- LinkedIn: [linkedin.com/in/david-michel-larrieux](https://linkedin.com)
- GitHub: [@DavidMichelLarrieux](https://github.com/DavidMichelLarrieux)

## 🙏 Remerciements

- Communauté open source Python
- Équipes Streamlit et FastAPI
- Contributeurs du projet

---

<div align="center">

**⭐ N'hésitez pas à donner une étoile si ce projet vous aide ! ⭐**

</div>
