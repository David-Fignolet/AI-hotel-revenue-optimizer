"""
Module de visualisation pour le tableau de bord de revenue management
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

class DashboardVisuals:
    """
    Classe pour générer les visualisations du tableau de bord
    """
    
    @staticmethod
    def create_occupancy_forecast_chart(df, title, color_main='rgba(30, 136, 229, 0.8)', color_fill='rgba(30, 136, 229, 0.2)'):
        """
        Crée un graphique de prévision d'occupation avec intervalle de confiance
        """
        fig = go.Figure()
        
        # Zone de confiance
        if 'upper_bound' in df.columns and 'lower_bound' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['upper_bound']*100,
                fill=None,
                mode='lines',
                line_color=color_main,
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['lower_bound']*100,
                fill='tonexty',
                mode='lines',
                line_color=color_main,
                fillcolor=color_fill,
                name='Intervalle de confiance'
            ))
            
        # Ligne principale
        occupancy_col = next((col for col in ['predicted_occupancy_rate', 'predicted_occupancy', 'occupancy_rate', 'occupancy'] if col in df.columns), None)
        if occupancy_col:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df[occupancy_col]*100,
                mode='lines',
                name='Taux d\'occupation',
                line=dict(color=color_main)
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Taux d\'occupation',
            template='plotly_white'
        )
        
        return fig
        
    @staticmethod
    def create_historical_trends_chart(df, title, y_title, color):
        """Crée un graphique des tendances historiques"""
        fig = go.Figure()
        
        occupancy_col = next((col for col in ['occupancy_rate', 'occupancy'] if col in df.columns), None)
        if occupancy_col:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df[occupancy_col]*100,
                mode='lines',
                name='Historique',
                line=dict(color=color)
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title=y_title,
            template='plotly_white'
        )
        
        return fig
        
    @staticmethod
    def create_price_sensitivity_chart(df, title, x_title, y_title):
        """Crée un graphique de sensibilité aux prix"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['price'],
            y=df['demand'],
            mode='lines+markers',
            name='Demande',
            line=dict(color='rgba(30, 136, 229, 0.8)')
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            template='plotly_white'
        )
        
        return fig
        
    @staticmethod
    def create_weekly_heatmap(df, title, z_title):
        """Crée une heatmap hebdomadaire"""
        # Préparer les données
        df['weekday'] = pd.to_datetime(df['date']).dt.day_name()
        df['hour'] = pd.to_datetime(df['date']).dt.hour
        
        occupancy_col = next((col for col in ['occupancy_rate', 'occupancy'] if col in df.columns), None)
        if occupancy_col:
            pivot = pd.pivot_table(
                df,
                values=occupancy_col,
                index='weekday',
                columns='hour',
                aggfunc='mean'
            )
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot.values * 100,
                x=pivot.columns,
                y=pivot.index,
                colorscale='Viridis'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title='Jour de la semaine',
                yaxis_title='Heure de la journée',
                template='plotly_white'
            )
            
            return fig
        return None
        
    @staticmethod
    def create_price_occupancy_scatter(df, title, x_title, y_title):
        """Crée un nuage de points prix/occupation"""
        fig = go.Figure()
        
        occupancy_col = next((col for col in ['occupancy_rate', 'occupancy'] if col in df.columns), None)
        if occupancy_col:
            fig.add_trace(go.Scatter(
                x=df['price'],
                y=df[occupancy_col]*100,
                mode='markers',
                name='Observations',
                marker=dict(
                    color='rgba(30, 136, 229, 0.8)',
                    size=8
                )
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            template='plotly_white'
        )
        
        return fig
        
    @staticmethod
    def create_revenue_forecast_chart(predictions_df, historical_df, title, y_title):
        """Crée un graphique de prévision des revenus"""
        fig = go.Figure()
        
        # Ajouter les données historiques si disponibles et contiennent la colonne 'revenue'
        revenue_cols = ['revenue', 'actual_revenue', 'historical_revenue']
        revenue_col = next((col for col in revenue_cols if col in (historical_df.columns if historical_df is not None else [])), None)
        
        if historical_df is not None and revenue_col:
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df[revenue_col],
                mode='lines',
                name='Historique',
                line=dict(color='rgba(180, 180, 180, 0.8)')
            ))
        
        # Ajouter les prévisions
        pred_revenue_cols = ['predicted_revenue', 'revenue_forecast', 'forecast_revenue']
        pred_col = next((col for col in pred_revenue_cols if col in predictions_df.columns), None)
        
        if pred_col:
            fig.add_trace(go.Scatter(
                x=predictions_df['date'],
                y=predictions_df[pred_col],
                mode='lines',
                name='Prévisions',
                line=dict(color='rgba(30, 136, 229, 0.8)')
            ))
        
        # Si aucune donnée n'est présente, ajouter une trace vide pour éviter une erreur
        if not (revenue_col or pred_col):
            fig.add_trace(go.Scatter(
                x=[],
                y=[],
                mode='lines',
                name='Pas de données disponibles',
                line=dict(color='rgba(180, 180, 180, 0.8)')
            ))
            
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title=y_title,
            template='plotly_white'
        )
        
        return fig

# Exemple d'utilisation
if __name__ == "__main__":
    # Génération de données d'exemple
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    
    # Simulation de données réalistes
    data = []
    for date in dates:
        # Tendance saisonnière
        seasonal = 0.65 + 0.20 * np.sin(2 * np.pi * date.month / 12)
        # Effet week-end
        weekend_boost = 0.15 if date.weekday() >= 5 else 0
        # Bruit aléatoire
        noise = np.random.normal(0, 0.05)
        
        occupancy = np.clip(seasonal + weekend_boost + noise, 0.1, 0.98)
        base_price = 100 + 30 * seasonal + 20 * weekend_boost
        price = base_price + np.random.normal(0, 10)
        
        data.append({
            'date': date,
            'occupancy_rate': occupancy,
            'price': max(80, min(200, price))
        })
    
    df = pd.DataFrame(data)
    
    # Création des graphiques
    dashboard = DashboardVisuals()
    
    # Exemple de prévision (simulée)
    future_dates = pd.date_range('2024-01-01', periods=30, freq='D')
    predictions = pd.DataFrame({
        'date': future_dates,
        'predicted_occupancy': 0.7 + 0.1 * np.sin(np.linspace(0, 6, 30)),
        'lower_bound': 0.6 + 0.1 * np.sin(np.linspace(0, 6, 30)) - 0.1,
        'upper_bound': 0.6 + 0.1 * np.sin(np.linspace(0, 6, 30)) + 0.1
    })
    
    # Affichage des graphiques
    fig1 = dashboard.create_occupancy_forecast_chart(predictions)
    fig1.show()
    
    # Exemple d'analyse de scénarios (simulée)
    prices = np.linspace(80, 200, 50)
    scenarios = pd.DataFrame({
        'price': prices,
        'occupancy_rate': 0.9 * (1 - 0.5 * ((prices - 140) / 60) ** 2) + np.random.normal(0, 0.02, 50),
        'revpar': prices * (0.9 * (1 - 0.5 * ((prices - 140) / 60) ** 2) + np.random.normal(0, 0.02, 50))
    })
    
    fig2 = dashboard.create_price_sensitivity_chart(scenarios)
    fig2.show()
    
    fig3 = dashboard.create_historical_trends_chart(df)
    fig3.show()
    
    fig4 = dashboard.create_weekly_heatmap(df)
    fig4.show()
