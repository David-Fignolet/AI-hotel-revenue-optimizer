"""
Démonstration finale complète de l'AI Revenue Manager
"""

from src.ai_revenue_manager.llm_manager import AIRevenueManager
from datetime import datetime
import time

def demo_complete():
    """Démonstration complète avec tous les types d'analyses"""
    
    print("🏨 DÉMONSTRATION FINALE - AI REVENUE MANAGER")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    ai = AIRevenueManager()
    
    scenarios = [
        {
            "name": "📊 ANALYSE QUOTIDIENNE STANDARD",
            "hotel": {"occupancy_rate": 0.65, "current_price": 150},
            "market": {"competitor_prices": [155, 145, 160], "events": [], "weather": "Normal"}
        },
        {
            "name": "🎪 ÉVÉNEMENT MAJEUR - PREMIUM PRICING",
            "hotel": {"occupancy_rate": 0.90, "current_price": 200},
            "market": {"competitor_prices": [220, 250, 230], "events": ["Salon international", "Festival de musique"], "weather": "Parfait"}
        },
        {
            "name": "🚨 GESTION DE CRISE - RÉCUPÉRATION D'URGENCE",
            "hotel": {"occupancy_rate": 0.15, "current_price": 140},
            "market": {"competitor_prices": [100, 80, 90], "events": [], "weather": "Très mauvais"}
        },
        {
            "name": "🏪 GUERRE DES PRIX - REPOSITIONNEMENT",
            "hotel": {"occupancy_rate": 0.55, "current_price": 180},
            "market": {"competitor_prices": [140, 135, 145], "events": [], "weather": "Correct"}
        },
        {
            "name": "📈 FORTE DEMANDE - OPTIMISATION MAXIMUM",
            "hotel": {"occupancy_rate": 0.95, "current_price": 180},
            "market": {"competitor_prices": [190, 200, 185], "events": ["Congrès médical"], "weather": "Excellent"}
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{scenario['name']}")
        print("-" * 50)
        
        try:
            result = ai.analyze_situation(scenario['hotel'], scenario['market'])
            analysis = result['analysis']
            
            print(f"🔍 Type d'analyse: {result['prompt_type']}")
            print(f"💰 Prix actuel: {scenario['hotel']['current_price']}€")
            print(f"💎 Prix recommandé: {analysis['recommended_price']:.0f}€")
            print(f"📈 Variation: {((analysis['recommended_price']/scenario['hotel']['current_price'] - 1) * 100):+.1f}%")
            print(f"📊 Confiance: {analysis['confidence_score']:.0%}")
            print(f"🎯 Impact RevPAR: +{analysis['expected_impact']:.1f}%")
            
            print("\n📋 Actions prioritaires:")
            for j, action in enumerate(analysis['recommended_actions'][:3], 1):
                print(f"   {j}. {action}")
            
            results.append({
                'scenario': scenario['name'][:20],
                'type': result['prompt_type'],
                'prix_actuel': scenario['hotel']['current_price'],
                'prix_recommande': analysis['recommended_price'],
                'variation': ((analysis['recommended_price']/scenario['hotel']['current_price'] - 1) * 100),
                'confiance': analysis['confidence_score']
            })
            
            print(f"\n✅ Scénario {i}/5 analysé avec succès")
            
        except Exception as e:
            print(f"❌ Erreur scénario {i}: {e}")
        
        if i < len(scenarios):
            time.sleep(0.5)  # Pause pour la lisibilité
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 TABLEAU DE BORD RÉCAPITULATIF")
    print("=" * 60)
    
    for result in results:
        print(f"{result['scenario']:.<25} {result['type']:.<18} {result['prix_recommande']:>6.0f}€ ({result['variation']:+5.1f}%) - {result['confiance']:.0%}")
    
    print("\n🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
    print(f"⚡ {len(results)}/5 analyses réussies")
    print("\n🚀 Votre AI Revenue Manager est prêt pour la production!")
    print("   → Lancez: streamlit run app/streamlit_app.py")
    print("   → Interface web: http://localhost:8501")

if __name__ == "__main__":
    demo_complete()