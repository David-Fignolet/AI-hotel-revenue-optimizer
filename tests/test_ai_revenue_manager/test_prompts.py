"""
Tests pour les prompt templates
"""

import pytest
from src.ai_revenue_manager.prompts import PromptTemplates
from src.ai_revenue_manager.prompt_selector import PromptSelector

class TestPromptTemplates:
    
    def setup_method(self):
        self.templates = PromptTemplates()
        self.selector = PromptSelector()
    
    def test_daily_pricing_template_exists(self):
        """Test que le template daily_pricing existe"""
        template = self.templates.get_template('daily_pricing')
        assert template is not None
        assert 'RÔLE' in template
        assert 'MISSION' in template
    
    def test_prompt_formatting(self):
        """Test le formatage d'un prompt avec contexte"""
        context = {
            'hotel_name': 'Test Hotel',
            'current_date': '2024-06-16',
            'day_of_week': 'Dimanche',
            'room_type': 'Standard',
            'current_occupancy': '72.0%',
            'occupancy_trend': 'stable',
            'current_price': '175',
            'current_revpar': '126.00',
            'competitor_avg_price': '180',
            'price_gap': '-5',
            'price_position': 'Sous la moyenne',
            'weather_forecast': 'Ensoleillé',
            'local_events': 'Salon du tourisme',
            'season_type': 'Été',
            'min_price': '80',
            'max_price': '300',
            'revpar_target': '130'
        }
        
        formatted = self.templates.format_template('daily_pricing', context)
        assert 'Test Hotel' in formatted
        assert '72.0%' in formatted
        assert 'Salon du tourisme' in formatted
    
    def test_prompt_selection_crisis(self):
        """Test sélection de prompt en cas de crise"""
        crisis_context = {'current_occupancy': 25}
        prompt_type = self.selector.select_prompt_type(crisis_context)
        assert prompt_type == 'crisis_management'
    
    def test_prompt_selection_event(self):
        """Test sélection de prompt pour événement"""
        event_context = {'special_events': ['Concert', 'Festival']}
        prompt_type = self.selector.select_prompt_type(event_context)
        assert prompt_type == 'special_event'
    
    def test_required_variables(self):
        """Test récupération des variables requises"""
        variables = self.selector.get_required_variables('daily_pricing')
        assert 'hotel_name' in variables
        assert 'current_occupancy' in variables
        assert 'competitor_avg_price' in variables