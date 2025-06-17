#!/usr/bin/env python3
"""
Script de test rapide pour Mistral AI via Ollama
"""

import os
from dotenv import load_dotenv
import requests

# Charger les variables d'environnement
load_dotenv()

def test_ollama_installation():
    """Test de l'installation d'Ollama"""
    print("🔍 Vérification de l'installation Ollama...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✅ Ollama est en cours d'exécution")
            return True
        else:
            print("❌ Erreur de connexion à Ollama")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama n'est pas en cours d'exécution")
        print("📝 Instructions d'installation Ollama :")
        print("1. Téléchargez Ollama depuis https://ollama.ai/download")
        print("2. Installez et lancez Ollama")
        print("3. Dans un terminal, exécutez : ollama pull mistral")
        return False

def test_mistral_model():
    """Test du modèle Mistral"""
    print("\n📦 Vérification du modèle Mistral...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            return False
        
        models = response.json()
        model_exists = any(model['name'] == 'mistral' for model in models['models'])
        
        if model_exists:
            print("✅ Modèle Mistral disponible")
            return True
        else:
            print("⚙️ Installation du modèle Mistral...")
            install_response = requests.post(
                "http://localhost:11434/api/pull",
                json={"name": "mistral"}
            )
            
            if install_response.status_code == 200:
                print("✅ Modèle Mistral installé")
                return True
            else:
                print("❌ Erreur d'installation du modèle")
                return False
                
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_analysis():
    """Test d'analyse avec Mistral"""
    print("\n🤖 Test d'analyse avec Mistral...")
    
    try:
        from src.ai_revenue_manager.mistral_llm_manager import MistralRevenueManager
        
        # Initialiser le manager
        manager = MistralRevenueManager()
        
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
    print("🚀 Test complet Mistral Revenue Manager via Ollama\n")
    
    tests = [
        ("Installation Ollama", test_ollama_installation),
        ("Modèle Mistral", test_mistral_model),
        ("Analyse", test_analysis)
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
        print("\n🎉 Tous les tests sont passés ! Mistral est prêt.")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez l'installation.")

if __name__ == "__main__":
    main()
