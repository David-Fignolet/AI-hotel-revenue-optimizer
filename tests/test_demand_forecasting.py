"""
Tests unitaires pour le module demand_forecasting.py
"""
import os
import sys
import unittest
import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.demand_forecasting import DemandForecaster
from src.data_processor import HotelDataProcessor
from src.config import PATHS, DEMAND_MODEL_PARAMS

@pytest.fixture(scope="class")
def tmp_path_fixture(request, tmp_path_factory):
    request.cls.tmp_path = tmp_path_factory.mktemp("data")

@pytest.mark.usefixtures("tmp_path_fixture")
class TestDemandForecaster(unittest.TestCase):
    """Classe de tests pour DemandForecaster"""
    
    @classmethod
    def setUpClass(cls):
        """Configuration avant tous les tests"""
        # Créer un jeu de données de test
        cls.create_test_data()
        
        # Initialiser le processeur de données
        cls.processor = HotelDataProcessor(country='FR')
        
        # Préparer les données
        cls.prepare_data()
        
    @classmethod
    def create_test_data(cls):
        """Créer un jeu de données de test"""
        # Créer des dates pour une année complète
        end_date = datetime.now().replace(day=1) - timedelta(days=1)  # Fin du mois dernier
        start_date = end_date - timedelta(days=365)  # 1 an de données
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Créer un DataFrame avec des données simulées
        np.random.seed(42)  # Pour la reproductibilité
        
        # Données de base
        data = {
            'date': dates,
            'room_type': np.random.choice(['Standard', 'Deluxe', 'Suite'], size=len(dates)),
            'occupancy_rate': np.clip(0.4 + 0.4 * np.sin(2 * np.pi * np.arange(len(dates)) / 30) + 
                               np.random.normal(0, 0.1, len(dates)), 0, 1),
            'price': np.clip(100 + 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 180) + 
                          np.random.normal(0, 10, len(dates)), 80, 300)
        }
        
        df = pd.DataFrame(data)
        
        # Ajouter des caractéristiques temporelles
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['dayofweek'] = df['date'].dt.dayofweek
        
        # Sauvegarder les données de test
        if not os.path.exists(os.path.dirname(PATHS['raw_data'])):
            os.makedirs(os.path.dirname(PATHS['raw_data']))
        df.to_csv(PATHS['raw_data'], index=False)
        
        return df
    
    @classmethod
    def prepare_data(cls):
        """Préparer les données pour les tests"""
        # Charger les données brutes
        df = pd.read_csv(PATHS['raw_data'], parse_dates=['date'])
        
        # Filtrer pour une seule catégorie de chambre pour simplifier
        cls.test_room_type = 'Standard'
        df = df[df['room_type'] == cls.test_room_type].copy()
        
        # Trier par date
        df = df.sort_values('date').reset_index(drop=True)
        
        # Diviser en ensembles d'entraînement et de test (80/20)
        split_idx = int(0.8 * len(df))
        cls.train_data = df.iloc[:split_idx].copy()
        cls.test_data = df.iloc[split_idx:].copy()
        
        # Colonnes cible
        cls.target_column = 'occupancy_rate'
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Réinitialiser le modèle avant chaque test
        self.model = DemandForecaster(**DEMAND_MODEL_PARAMS)
    
    def test_model_initialization(self):
        """Teste l'initialisation du modèle"""
        self.assertIsNotNone(self.model.model)
        self.assertEqual(self.model.model.n_estimators, DEMAND_MODEL_PARAMS['n_estimators'])
        self.assertEqual(self.model.model.max_depth, DEMAND_MODEL_PARAMS['max_depth'])
    
    def test_feature_engineering(self):
        """Teste la création des caractéristiques"""
        X, y = self.model.prepare_features(self.train_data)
        
        # Vérifier les dimensions
        self.assertIsNotNone(X)
        self.assertIsNotNone(y)
        self.assertEqual(len(X.columns), 9)  # Nombre de features de base
        
        # Vérifier que les colonnes attendues sont présentes
        expected_columns = [
            'month_sin', 'month_cos', 'day_sin', 'day_cos',
            'dayofweek_sin', 'dayofweek_cos', 'is_weekend',
            'is_holiday', 'is_school_holiday'
        ]
        self.assertTrue(all(col in X.columns for col in expected_columns))
        
        # Vérifier qu'il n'y a pas de NaN dans les features
        self.assertFalse(X.isna().any().any())
    
    def test_train_model(self):
        """Teste l'entraînement du modèle"""
        # Entraîner le modèle
        mae = self.model.train(
            self.train_data,
            target_column=self.target_column,
            room_type=self.test_room_type,
            save_model=False
        )
        
        # Vérifier que le MAE est un nombre raisonnable
        self.assertIsInstance(mae, float)
        self.assertGreater(mae, 0.0)
        self.assertLess(mae, 0.3)  # MAE devrait être inférieur à 30%
    
    def test_predict(self):
        """Teste les prédictions du modèle"""
        # Entraîner d'abord le modèle
        self.model.train(
            self.train_data,
            target_column=self.target_column,
            room_type=self.test_room_type,
            save_model=False
        )
        
        # Faire des prédictions sur l'ensemble de test
        predictions = self.model.predict(self.test_data)
        
        # Vérifier les dimensions des prédictions
        self.assertEqual(len(predictions), len(self.test_data))
        
        # Vérifier que les prédictions sont dans la plage attendue (0-1 pour un taux d'occupation)
        self.assertTrue(all(0 <= p <= 1.5 for p in predictions))  # Tolérance pour les valeurs légèrement > 1
    
    def test_predict_future(self):
        """Teste la prédiction future"""
        # Entraîner le modèle
        self.model.train(
            self.train_data,
            target_column=self.target_column,
            room_type=self.test_room_type,
            save_model=False
        )
        
        # Créer un DataFrame pour la prédiction future
        future_dates = pd.date_range(
            start=self.test_data['date'].max() + pd.Timedelta(days=1),
            periods=7,
            freq='D'
        )
        future_data = pd.DataFrame({'date': future_dates})
        future_data['room_type'] = self.test_room_type
        
        # Faire des prédictions
        predictions = self.model.predict(future_data)
        
        # Vérifier que nous avons le bon nombre de prédictions
        self.assertEqual(len(predictions), len(future_dates))
        
        # Vérifier que les prédictions sont raisonnables
        self.assertTrue(all(0 <= p <= 1.5 for p in predictions))
    
    def test_save_load_model(self):
        """Teste la sauvegarde et le chargement du modèle"""
        # Créer un modèle et l'entraîner
        self.model.train(
            self.train_data,
            target_column=self.target_column,
            room_type=self.test_room_type,
            save_model=False
        )
        
        # Chemin temporaire pour le test
        model_path = self.tmp_path / 'test_model.joblib'
        
        # Sauvegarder le modèle
        self.model.save_model(str(model_path))
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(model_path))
        
        # Créer un nouveau modèle et charger le modèle sauvegardé
        new_model = DemandForecaster()
        new_model.load_model(str(model_path))
        
        # Vérifier que le modèle chargé fait les mêmes prédictions
        old_preds = self.model.predict(self.test_data.head(10))
        new_preds = new_model.predict(self.test_data.head(10))
        
        np.testing.assert_array_almost_equal(old_preds, new_preds)
