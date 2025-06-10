# test_ai_manager.py
from src.ai_revenue_manager.llm_manager import AIRevenueManager
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_sample_data():
    """Génère des données factices pour les tests"""
    # Générer des dates pour les 90 derniers jours
    dates = pd.date_range(end=datetime.now(), periods=90)
    
    # Générer des données d'occupation aléatoires
    np.random.seed(42)
    base_occupancy = np.sin(np.linspace(0, 10, 90)) * 0.2 + 0.6  # Tendance sinusoïdale
    noise = np.random.normal(0, 0.05, 90)
    occupancy_rates = np.clip(base_occupancy + noise, 0.3, 0.95)  # Garder entre 30% et 95%
    
    # Créer le DataFrame
    df = pd.DataFrame({
        'date': dates,
        'occupancy_rate': occupancy_rates,
        'avg_daily_rate': np.random.normal(150, 20, 90).round(2),
        'revenue': (np.random.normal(150, 20, 90) * 100 * occupancy_rates).round(2)
    })
    
    return df

def main():
    # Données factices pour le test
    hotel_data = {
        'occupancy_rate': 0.75,
        'current_price': 180,
        'room_type': 'Deluxe'
    }
    
    market_data = {
        'competitor_prices': [175, 185, 190, 170, 195],
        'events': ['Salon du tourisme - 15/06', 'Festival local - 20/06'],
        'weather': 'Ensoleillé'
    }
    
    # Générer des données historiques
    historical_data = generate_sample_data()
    
    # Initialiser le gestionnaire de revenus
    revenue_manager = AIRevenueManager()
    
    # Effectuer l'analyse
    print("Analyse en cours...")
    analysis = revenue_manager.analyze_situation(
        hotel_data=hotel_data,
        market_data=market_data,
        historical_data=historical_data
    )
    
    # Afficher les résultats
    print("\n=== RÉSULTATS DE L'ANALYSE ===")
    print(f"Hôtel: {revenue_manager.config['hotel']['name']}")
    print(f"Modèle LLM: {revenue_manager.config['llm']['model']}")
    print("\nRecommandations tarifaires:")
    for room_type, price in analysis['price_recommendations'].items():
        print(f"- {room_type.capitalize()}: {price}€")
    
    print("\nActions recommandées:")
    for i, action in enumerate(analysis['recommended_actions'], 1):
        print(f"{i}. {action}")
    
    print("\nAnalyse complète:")
    print(analysis['summary'])

if __name__ == "__main__":
    main()
