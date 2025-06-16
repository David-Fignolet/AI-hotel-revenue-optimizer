"""
Test AI Manager corrigé
"""

from src.ai_revenue_manager.llm_manager import AIRevenueManager

def test_ai_scenarios():
    """Test de différents scénarios"""
    
    print("🧪 TEST AI REVENUE MANAGER")
    print("=" * 40)
    
    # Initialiser l'AI Manager
    ai = AIRevenueManager()
    print("✅ AI Manager initialisé")
    
    # Scénario 1 : Situation normale
    print("\n📊 SCÉNARIO 1: Situation normale")
    hotel_data = {
        'occupancy_rate': 0.72,
        'current_price': 175,
        'min_price': 80,
        'max_price': 300
    }
    market_data = {
        'competitor_prices': [180, 190, 165, 185],
        'events': [],  # Pas d'événements
        'weather': 'Ensoleillé'
    }
    
    try:
        result = ai.analyze_situation(hotel_data, market_data)
        print("   ✅ Analyse réussie")
        print(f"   - Type: {result['prompt_type']}")
        print(f"   - Prix recommandé: {result['analysis']['recommended_price']}€")
        print(f"   - Confiance: {result['analysis']['confidence_score']:.0%}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Scénario 2 : Avec événement
    print("\n🎪 SCÉNARIO 2: Avec événement")
    market_data_event = {
        'competitor_prices': [200, 220, 190, 210],
        'events': ['Salon du tourisme'],
        'weather': 'Parfait'
    }
    
    try:
        result = ai.analyze_situation(hotel_data, market_data_event)
        print("   ✅ Analyse réussie")
        print(f"   - Type: {result['prompt_type']}")
        print(f"   - Prix recommandé: {result['analysis']['recommended_price']}€")
        print(f"   - Confiance: {result['analysis']['confidence_score']:.0%}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Scénario 3 : Crise
    print("\n🚨 SCÉNARIO 3: Situation de crise")
    hotel_data_crisis = {
        'occupancy_rate': 0.25,  # Très faible
        'current_price': 120,
        'min_price': 60,
        'max_price': 300
    }
    market_data_crisis = {
        'competitor_prices': [100, 90, 110, 95],
        'events': [],
        'weather': 'Pluvieux'
    }
    
    try:
        result = ai.analyze_situation(hotel_data_crisis, market_data_crisis)
        print("   ✅ Analyse réussie")
        print(f"   - Type: {result['prompt_type']}")
        print(f"   - Prix recommandé: {result['analysis']['recommended_price']}€")
        print(f"   - Confiance: {result['analysis']['confidence_score']:.0%}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n🎉 TOUS LES TESTS TERMINÉS!")

if __name__ == "__main__":
    test_ai_scenarios()