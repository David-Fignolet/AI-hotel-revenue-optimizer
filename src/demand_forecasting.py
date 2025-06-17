"""
Module de prédiction de demande hôtelière
Auteur: David Michel-Larrieux
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DemandForecaster:
    """
    Prédicteur de demande hôtelière basé sur Random Forest
    
    Utilise les features temporelles, événements locaux et météo
    pour prédire le taux d'occupation futur.
    """
    
    def __init__(self, **kwargs):
        """
        Initialise le modèle de prédiction avec les paramètres spécifiés
        
        Args:
            **kwargs: Paramètres du modèle RandomForestRegressor
        """
        self.model = RandomForestRegressor(
            **{**{
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42,
                'n_jobs': -1
            }, **kwargs}
        )
        self.imputer = SimpleImputer(strategy='mean')
        self.scaler = StandardScaler()
        self.features = None
        self.is_trained = False
        
    def prepare_features(self, df, target_column='occupancy_rate'):
        """
        Prépare les features pour l'entraînement ou la prédiction
        
        Args:
            df (pd.DataFrame): Données brutes
            target_column (str): Nom de la colonne cible
            
        Returns:
            tuple: (X, y) ou (X, None) si pas de target
        """
        df = df.copy()
        
        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract temporal features
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['dayofweek'] = df['date'].dt.dayofweek
        
        # Features temporelles cycliques
        def create_cyclical_features(df, col, period):
            values = df[col] * (2 * np.pi / period)
            return np.sin(values), np.cos(values)
        
        # Month features (1-12)
        df['month_sin'], df['month_cos'] = create_cyclical_features(df, 'month', 12)
        
        # Day features (1-31)
        df['day_sin'], df['day_cos'] = create_cyclical_features(df, 'day', 31)
        
        # Weekday features (0-6)
        df['dayofweek_sin'], df['dayofweek_cos'] = create_cyclical_features(df, 'dayofweek', 7)
        
        # Weekend flag
        df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
        
        # Holiday flag (à implémenter avec un calendrier)
        df['is_holiday'] = 0
        df['is_school_holiday'] = 0
        
        # Lag features for the target if available
        if target_column in df.columns:
            for lag in [1, 7, 30]:
                df[f'{target_column}_lag_{lag}'] = df[target_column].shift(lag)
        
        # Select features
        feature_cols = [
            'month_sin', 'month_cos', 'day_sin', 'day_cos',
            'dayofweek_sin', 'dayofweek_cos', 'is_weekend',
            'is_holiday', 'is_school_holiday'
        ]
        
        if target_column in df.columns:
            lag_cols = [f'{target_column}_lag_{lag}' for lag in [1, 7, 30]]
            feature_cols.extend(lag_cols)
            y = df[target_column].copy()
        else:
            y = None
            
        X = df[feature_cols].copy()
        
        # Handle missing values
        if self.is_trained:
            X = pd.DataFrame(self.imputer.transform(X), columns=X.columns, index=X.index)
            X = pd.DataFrame(self.scaler.transform(X), columns=X.columns, index=X.index)
        else:
            X = pd.DataFrame(self.imputer.fit_transform(X), columns=X.columns, index=X.index)
            X = pd.DataFrame(self.scaler.fit_transform(X), columns=X.columns, index=X.index)
            
        return X, y
    
    def train(self, df, feature_columns=None, target_column='occupancy_rate', room_type=None, save_model=False):
        """
        Entraîne le modèle sur les données historiques
        
        Args:
            df (pd.DataFrame): Données d'entraînement
            feature_columns (list): Liste optionnelle de colonnes features
            target_column (str): Nom de la colonne cible
            room_type (str): Type de chambre à modéliser (optionnel)
            save_model (bool): Sauvegarder le modèle après entraînement
            
        Returns:
            float: Erreur moyenne absolue sur validation
        """
        if room_type:
            df = df[df['room_type'] == room_type].copy()
        
        # Préparer les features
        X, y = self.prepare_features(df, target_column)
        
        if y is None:
            raise ValueError("La colonne cible n'est pas présente dans les données")
        
        # Entraînement avec validation temporelle
        tscv = TimeSeriesSplit(n_splits=5)
        maes = []
        
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_val)
            
            maes.append(mean_absolute_error(y_val, y_pred))
        
        # Entraînement final sur toutes les données
        self.model.fit(X, y)
        self.features = X.columns.tolist()
        self.is_trained = True
        
        return np.mean(maes)
    
    def predict(self, df):
        """
        Fait des prédictions sur de nouvelles données
        
        Args:
            df (pd.DataFrame): Données pour la prédiction
            
        Returns:
            np.array: Prédictions
        """
        if not self.is_trained:
            raise RuntimeError("Le modèle doit d'abord être entraîné")
            
        X, _ = self.prepare_features(df)
        return self.model.predict(X)
        
    def save_model(self, filepath='models/demand_forecaster.joblib'):
        """Sauvegarde le modèle"""
        if not self.is_trained:
            raise RuntimeError("Le modèle doit d'abord être entraîné")
            
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({'model': self.model, 'features': self.features}, filepath)
        
    def load_model(self, filepath='models/demand_forecaster.joblib'):
        """Charge un modèle sauvegardé"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.features = data['features']
        self.is_trained = True

# Exemple d'utilisation
if __name__ == "__main__":
    # Génération de données d'exemple
    from datetime import datetime, timedelta
    
    dates = pd.date_range('2022-01-01', '2023-12-31', freq='D')
    np.random.seed(42)
    
    # Simulation de données réalistes
    occupancy_data = []
    for date in dates:
        # Tendance saisonnière
        seasonal = 0.65 + 0.20 * np.sin(2 * np.pi * date.month / 12)
        # Effet week-end
        weekend_boost = 0.15 if date.weekday() >= 5 else 0
        # Bruit aléatoire
        noise = np.random.normal(0, 0.05)
        
        occupancy = np.clip(seasonal + weekend_boost + noise, 0.1, 0.98)
        
        occupancy_data.append({
            'date': date,
            'occupancy_rate': occupancy,
            'room_type': 'Standard'
        })
    
    df = pd.DataFrame(occupancy_data)
    
    # Test du modèle
    forecaster = DemandForecaster()
    mae = forecaster.train(df)
    
    # Prédiction
    predictions = forecaster.predict_demand('2024-01-01', days=30)
    print("\n📈 Prédictions de demande:")
    print(predictions.head(10))
    
    # Importance des features
    print("\n🔍 Importance des features:")
    print(forecaster.get_feature_importance().head(10))
