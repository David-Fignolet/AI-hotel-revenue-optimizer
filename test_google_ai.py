#!/usr/bin/env python3
"""
Script de test rapide pour Google AI Studio
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_configuration():
    """Test de configuration de base"""
    print("🔍 Test de configuration Google AI Studio...")
    
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ GOOGLE_AI_API_KEY non trouvée dans .env")
        return False
    
    print(f"✅ Clé API trouvée: {api_key[:10]}...")
    return True

def test_import():
    """Test d'import des modules"""
    print("📦 Test d'import des modules...")
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai importé")
        
        from src.ai_revenue_manager.google_llm_manager import GoogleAIRevenueManager
        print("✅ GoogleAIRevenueManager importé")
        
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_analysis():
    """Test d'analyse complète"""
    print("🤖 Test d'analyse avec Gemini...")
    
    try:
        from src.ai_revenue_manager.google_llm_manager import GoogleAIRevenueManager
        
        # Initialiser le manager
        manager = GoogleAIRevenueManager()
        
        # Données de test
        hotel_data = {
            'occupancy_rate': 0.72,
            'current_price': 175,
            'min_price': 80,
            'max_price': 300
        }
        
        market_data = {
            'competitor_prices': [180, 190, 165, 185],
            'events': ['Test Event'],
            'weather': 'Ensoleillé'
        }
        
        # Analyser
        result = manager.analyze_situation(hotel_data, market_data)
        
        if result.get('success'):
            print("✅ Analyse réussie !")
            print(f"📊 Prix recommandé: {result['analysis']['recommended_price']}€")
            print(f"🎯 Confiance: {result['analysis']['confidence_score']:.0%}")
            return True
        else:
            print(f"❌ Échec de l'analyse: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur d'analyse: {e}")
        return False

def main():
    """Test complet"""
    print("🚀 Test complet Google AI Studio Revenue Manager\n")
    
    tests = [
        ("Configuration", test_configuration),
        ("Import des modules", test_import),
        ("Analyse Gemini", test_analysis)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"TEST: {name}")
        print('='*50)
        
        success = test_func()
        results.append((name, success))
        
        if success:
            print(f"✅ {name}: SUCCÈS")
        else:
            print(f"❌ {name}: ÉCHEC")
    
    # Résumé
    print(f"\n{'='*50}")
    print("RÉSUMÉ DES TESTS")
    print('='*50)
    
    for name, success in results:
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"{name}: {status}")
    
    total_success = sum(1 for _, success in results if success)
    print(f"\nTotal: {total_success}/{len(results)} tests réussis")
    
    if total_success == len(results):
        print("\n🎉 Tous les tests sont passés ! Google AI est prêt.")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main()
