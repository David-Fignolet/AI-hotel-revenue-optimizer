import pandas as pd
from src.llm.llm_manager import AIRevenueManager

def main():
    print("Test du gestionnaire LLM...")
    llm = AIRevenueManager()
      # Données de test
    hotel_data = {
        'occupancy_rate': 0.75,
        'current_price': 100
    }
    market_data = {
        'competitor_prices': [95, 105, 110],
        'events': ['Festival de musique']
    }
    historical_data = pd.DataFrame({
        'price': [98, 100]
    })
    
    print("\nAnalyse de la situation...")
    response = llm.analyze_situation(hotel_data, market_data, historical_data)
    print(f"\nRECOMMANDATION:\n{response['recommendation']}")

if __name__ == "__main__":
    main()
