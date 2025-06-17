"""Tests for the Streamlit application."""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
import streamlit as st

# Add app directory to PYTHONPATH
app_dir = str(Path(__file__).parent.parent)
if app_dir not in sys.path:
    sys.path.append(app_dir)

from app.streamlit_app import (
    StreamlitUI,
    clean_numeric_series,
    generate_predictions,
    safe_st_error,
    safe_st_info,
    safe_st_warning,
    load_uploaded_file,
    create_dashboard_analysis,
)

@pytest.fixture
def sample_hotel_data():
    """Create sample hotel data for testing."""
    return pd.DataFrame({
        'Date': pd.date_range(start=datetime.now(), periods=30),
        'Chambres Occupées': [80 + (i % 10) for i in range(30)],
        'Libre (%)': [20 - (i % 5) for i in range(30)],
        'Prévision C.A': [10000 + (i * 100) for i in range(30)]
    })

@pytest.fixture
def streamlit_ui():
    """Create a StreamlitUI instance with mocked dependencies."""
    with patch('app.streamlit_app.safe_import') as mock_import:
        # Mock Streamlit
        mock_st = MagicMock()
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.sidebar = MagicMock()
        mock_import.return_value = mock_st
        
        ui = StreamlitUI()
        ui.st = mock_st
        return ui

@pytest.fixture
def mock_file_uploader():
    """Create a mock file uploader."""
    class MockUploadedFile:
        def __init__(self, content, file_type="text/csv"):
            self.content = content
            self.type = file_type
            
        def getvalue(self):
            return self.content
            
    return MockUploadedFile

@pytest.fixture
def sample_csv_content():
    """Create sample CSV content."""
    return (
        "Date,Chambres Occupées,Libre (%),Prévision C.A\n"
        "2025-06-01,80,20,10000\n"
        "2025-06-02,85,15,10500\n"
        "2025-06-03,90,10,11000\n"
    ).encode('utf-8')

def test_clean_numeric_series():
    """Test the numeric series cleaning function."""
    # Test avec une série déjà numérique
    numeric_series = pd.Series([1.0, 2.0, 3.0, 4.0])
    assert clean_numeric_series(numeric_series).equals(numeric_series)
    
    # Test avec une série contenant des virgules
    string_series = pd.Series(['1,5', '2,0', '3,5', '4,0'])
    expected = pd.Series([1.5, 2.0, 3.5, 4.0])
    pd.testing.assert_series_equal(
        clean_numeric_series(string_series),
        expected,
        check_dtype=False
    )

def test_generate_predictions(sample_hotel_data):
    """Test the prediction generation function."""
    predictions = generate_predictions(sample_hotel_data)
    
    # Vérifier la structure des prédictions
    assert isinstance(predictions, pd.DataFrame)
    assert 'Date' in predictions.columns
    assert 'Taux Occupation' in predictions.columns
    assert 'CA Prévu' in predictions.columns
    
    # Vérifier les valeurs
    assert len(predictions) == 30  # 30 jours de prédictions
    assert predictions['Taux Occupation'].min() >= 0
    assert predictions['Taux Occupation'].max() <= 100
    assert predictions['CA Prévu'].min() >= 0

def test_streamlit_ui_init(streamlit_ui):
    """Test StreamlitUI initialization."""
    assert streamlit_ui.st is not None
    streamlit_ui.st.set_page_config.assert_called_once()

def test_streamlit_ui_show_metrics(streamlit_ui, sample_hotel_data):
    """Test metrics display in StreamlitUI."""
    streamlit_ui.show_metrics(sample_hotel_data)
    streamlit_ui.st.subheader.assert_called_with("Indicateurs clés")

@pytest.mark.parametrize("safe_func,input_msg", [
    (safe_st_error, "Test error"),
    (safe_st_info, "Test info"),
    (safe_st_warning, "Test warning")
])
def test_safe_streamlit_functions(safe_func, input_msg):
    """Test safe Streamlit wrapper functions."""
    with patch('app.streamlit_app.st') as mock_st:
        # Test with Streamlit available
        safe_func(input_msg)
        
        # Test without Streamlit
        mock_st.side_effect = AttributeError
        safe_func(input_msg)  # Should not raise an error

def test_date_handling(streamlit_ui, sample_hotel_data):
    """Test date handling in the application."""
    # Test avec différents formats de date
    dates = pd.date_range(start=datetime.now(), periods=5)
    test_data = pd.DataFrame({
        'Date': dates,
        'Chambres Occupées': range(5)
    })
    
    # Devrait fonctionner avec des dates datetime
    streamlit_ui.show_data_preview(test_data)
    
    # Convertir en string et tester
    test_data['Date'] = test_data['Date'].dt.strftime('%Y-%m-%d')
    streamlit_ui.show_data_preview(test_data)

def test_predictions_with_missing_data(streamlit_ui):
    """Test prediction handling with missing or invalid data."""
    # Données vides
    empty_data = pd.DataFrame()
    predictions = generate_predictions(empty_data)
    assert predictions is None
    
    # Données sans colonne date
    invalid_data = pd.DataFrame({'Value': [1, 2, 3]})
    predictions = generate_predictions(invalid_data)
    assert predictions is None

@pytest.mark.parametrize("input_data,expected_columns", [
    # Test avec colonnes standard
    ({
        'Date': ['2025-06-01'],
        'Chambres Occupées': [80],
        'Libre (%)': [20],
        'Prévision C.A': [10000]
    }, ['Date', 'Taux Occupation', 'CA Prévu']),
    # Test avec colonnes alternatives
    ({
        'date': ['2025-06-01'],
        'occupation': [0.8],
        'revenu': [10000]
    }, ['Date', 'Taux Occupation', 'CA Prévu']),
])
def test_predictions_with_different_columns(input_data, expected_columns):
    """Test predictions with different column names."""
    df = pd.DataFrame(input_data)
    predictions = generate_predictions(df)
    
    assert predictions is not None
    for col in expected_columns:
        assert col in predictions.columns

def test_streamlit_ui_full_workflow(streamlit_ui, sample_hotel_data):
    """Test the complete UI workflow."""
    # Test data preview
    streamlit_ui.show_data_preview(sample_hotel_data)
    streamlit_ui.st.dataframe.assert_called_once()
    
    # Test metrics display
    streamlit_ui.show_metrics(sample_hotel_data)
    streamlit_ui.st.subheader.assert_called_with("Indicateurs clés")
    
    # Test predictions
    streamlit_ui.show_predictions(sample_hotel_data)
    # Le spinner devrait être appelé
    streamlit_ui.st.spinner.assert_called_once()

def test_dashboard_analysis_creation(streamlit_ui, sample_hotel_data):
    """Test dashboard analysis creation."""
    with patch('app.streamlit_app.DASHBOARD_AVAILABLE', True):
        with patch('app.streamlit_app.DashboardVisuals') as MockDashboard:
            mock_dashboard = MockDashboard.return_value
            mock_dashboard.create_occupancy_forecast_chart.return_value = {}
            
            create_dashboard_analysis(sample_hotel_data)
            
            # Vérifier que le dashboard a été créé
            MockDashboard.assert_called_once()
            mock_dashboard.create_occupancy_forecast_chart.assert_called_once()

def test_ai_manager_section(streamlit_ui):
    """Test AI manager setup and initialization."""
    with patch('app.streamlit_app.AI_MANAGERS_AVAILABLE', True):
        # Mock the sidebar checkbox
        streamlit_ui.st.sidebar.checkbox.return_value = True
        streamlit_ui.st.session_state = {}
        
        # Mock the AIRevenueManager
        with patch('app.streamlit_app.AIRevenueManager') as MockManager:
            mock_manager = MockManager.return_value
            
            # Test the AI section
            streamlit_ui.show_ai_section()
            
            # Verify the sidebar is used
            streamlit_ui.st.sidebar.checkbox.assert_called_once_with("🤖 Activer AI Revenue Manager")
            streamlit_ui.st.sidebar.markdown.assert_called()

def test_streamlit_ui_session_state(streamlit_ui):
    """Test session state management in StreamlitUI."""
    # Simuler un état de session
    streamlit_ui.st.session_state = {}
    streamlit_ui.st.sidebar.checkbox.return_value = True
    
    with patch('app.streamlit_app.AI_MANAGERS_AVAILABLE', True):
        with patch('app.streamlit_app.AIRevenueManager') as MockManager:
            mock_manager = MockManager.return_value
            
            # Tester l'initialisation de l'IA
            streamlit_ui.show_ai_section()
            
            # Vérifier que le gestionnaire IA est initialisé et en session
            assert 'ai_manager' in streamlit_ui.st.session_state

@pytest.mark.skipif(pd is None, reason="pandas is not available")
def test_load_uploaded_file_csv(mock_file_uploader, sample_csv_content, monkeypatch):
    """Test loading a CSV file."""
    from io import StringIO
    
    def mock_read_csv(*args, **kwargs):
        content = sample_csv_content.decode('utf-8')
        return pd.read_csv(StringIO(content))
    
    monkeypatch.setattr(pd, 'read_csv', mock_read_csv)
    
    uploaded_file = mock_file_uploader(sample_csv_content)
    data = load_uploaded_file(uploaded_file)
    
    assert isinstance(data, pd.DataFrame)
    assert 'Date' in data.columns
    assert 'Chambres Occupées' in data.columns
    assert 'Libre (%)' in data.columns
    assert 'Prévision C.A' in data.columns
    assert len(data) == 3

def test_load_uploaded_file_invalid_csv(mock_file_uploader):
    """Test loading an invalid CSV file."""
    # Test with invalid CSV content
    invalid_content = b"Invalid,CSV\nContent"
    uploaded_file = mock_file_uploader(invalid_content)
    data = load_uploaded_file(uploaded_file)
    assert data is None

def test_load_uploaded_file_unsupported_type(mock_file_uploader):
    """Test loading an unsupported file type."""
    uploaded_file = mock_file_uploader(b"content", file_type="application/json")
    data = load_uploaded_file(uploaded_file)
    assert data is None
