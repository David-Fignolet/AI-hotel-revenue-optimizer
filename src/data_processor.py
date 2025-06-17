"""
Module de traitement des données pour l'application Hotel Revenue Optimizer
"""
import pandas as pd
import numpy as np
from datetime import datetime

class HotelDataProcessor:
    def __init__(self, country='FR', **kwargs):
        """Initialize the data processor with configuration.
        
        Args:
            country (str): The country code for localization (default: 'FR')
            **kwargs: Additional configuration parameters
        """
        self.country = country
        self.config = kwargs
        
    @staticmethod
    def clean_data(df):
        """Nettoie les données brutes du DataFrame"""
        # Faire une copie pour éviter les modifications inattendues
        df_clean = df.copy()
        
        # Nettoyage des colonnes numériques
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
        # Nettoyage des dates
        if 'date' in df_clean.columns:
            df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
            
        return df_clean

    @staticmethod
    def calculate_metrics(df):
        """Calcule les métriques clés à partir des données nettoyées"""
        metrics = {}
        
        if 'price' in df.columns:
            metrics['avg_price'] = df['price'].mean()
            metrics['max_price'] = df['price'].max()
            metrics['min_price'] = df['price'].min()
            
        if 'occupancy_rate' in df.columns:
            metrics['avg_occupancy'] = df['occupancy_rate'].mean()
            
        return metrics
        
    def create_calendar_features(self, df, date_column):
        """Crée des caractéristiques calendaires à partir d'une colonne de date.
        
        Args:
            df (pd.DataFrame): Le DataFrame source
            date_column (str): Le nom de la colonne de date
            
        Returns:
            pd.DataFrame: DataFrame avec les nouvelles caractéristiques
        """
        df = df.copy()
        
        # Convertir en datetime si nécessaire
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            
        # Caractéristiques de base
        df['year'] = df[date_column].dt.year
        df['month'] = df[date_column].dt.month
        df['day'] = df[date_column].dt.day
        df['dayofweek'] = df[date_column].dt.dayofweek
        df['weekday'] = df[date_column].dt.day_name()
        df['quarter'] = df[date_column].dt.quarter
        df['is_weekend'] = df[date_column].dt.dayofweek.isin([5, 6]).astype(int)
        
        # Caractéristiques cycliques
        df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
        df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
        df['day_sin'] = np.sin(2 * np.pi * df['day']/31)
        df['day_cos'] = np.cos(2 * np.pi * df['day']/31)
        df['dayofweek_sin'] = np.sin(2 * np.pi * df['dayofweek']/7)
        df['dayofweek_cos'] = np.cos(2 * np.pi * df['dayofweek']/7)
        
        # Caractéristiques françaises si nécessaire
        if self.country == 'FR':
            from datetime import date
            df['is_holiday'] = df[date_column].apply(self._is_french_holiday).astype(int)
        
        return df
        
    def create_lag_features(self, df, target_col, lags=None, group_col=None):
        """Crée des caractéristiques de décalage temporel (lagged features).
        
        Args:
            df (pd.DataFrame): Le DataFrame source
            target_col (str): La colonne cible pour laquelle créer les décalages
            lags (list): Liste des décalages à créer (par défaut: [1, 7, 30])
            group_col (str): Colonne pour le groupement (ex: type de chambre)
        
        Returns:
            pd.DataFrame: DataFrame avec les nouvelles caractéristiques
        """
        df = df.copy()
        if lags is None:
            lags = [1, 7, 30]  # Décalages par défaut: jour précédent, semaine précédente, mois précédent
            
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
            
        # Trier par date (et groupe si spécifié)
        sort_cols = ['date']
        if group_col:
            sort_cols = [group_col] + sort_cols
        df = df.sort_values(sort_cols)
        
        # Créer les décalages
        for lag in lags:
            if group_col:
                # Créer les décalages par groupe
                df[f'{target_col}_lag_{lag}'] = df.groupby(group_col)[target_col].shift(lag)
            else:
                df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
                
        # Créer des statistiques mobiles
        windows = [7, 30]  # semaine et mois
        for window in windows:
            if group_col:
                df[f'{target_col}_rolling_mean_{window}d'] = (
                    df.groupby(group_col)[target_col]
                    .transform(lambda x: x.rolling(window, min_periods=1).mean())
                )
                df[f'{target_col}_rolling_std_{window}d'] = (
                    df.groupby(group_col)[target_col]
                    .transform(lambda x: x.rolling(window, min_periods=1).std())
                )
            else:
                df[f'{target_col}_rolling_mean_{window}d'] = (
                    df[target_col].rolling(window, min_periods=1).mean()
                )
                df[f'{target_col}_rolling_std_{window}d'] = (
                    df[target_col].rolling(window, min_periods=1).std()
                )
                
        return df
        
    def _is_french_holiday(self, dt):
        """Vérifie si une date est un jour férié en France."""
        if not isinstance(dt, (datetime, pd.Timestamp)):
            return False
            
        # Liste des jours fériés fixes
        fixed_holidays = [
            (1, 1),   # Jour de l'an
            (5, 1),   # Fête du travail
            (5, 8),   # Victoire 1945
            (7, 14),  # Fête nationale
            (8, 15),  # Assomption
            (11, 1),  # Toussaint
            (11, 11), # Armistice
            (12, 25), # Noël
        ]
        
        # Vérifier les jours fériés fixes
        if (dt.month, dt.day) in fixed_holidays:
            return True
            
        return False