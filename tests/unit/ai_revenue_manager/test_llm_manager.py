import pytest
from src.ai_revenue_manager.llm_manager import AIRevenueManager

class TestAIRevenueManager:
    def test_initialization(self):
        """Teste l'initialisation du gestionnaire LLM"""
        manager = AIRevenueManager("config/config.yaml")
        assert manager is not None
        assert hasattr(manager, 'analyze_situation')

    def test_analyze_situation(self, sample_hotel_data, sample_market_data, sample_historical_data):
        """Teste l'analyse de situation de base"""
        manager = AIRevenueManager("config/config.yaml")
        result = manager.analyze_situation(
            sample_hotel_data,
            sample_market_data,
            sample_historical_data
        )
        assert isinstance(result, dict)
        assert 'recommendation' in result
        assert 'context' in result
