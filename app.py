import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import yaml
import os
import asyncio
from typing import Dict, Any, List
from pathlib import Path

# Configuration des chemins
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"
HOTEL_PROFILE_PATH = BASE_DIR / "config" / "hotel_profile.yaml"

# Configuration de la page
st.set_page_config(
    page_title="AI Hotel Revenue Optimizer",
    page_icon="🏨",
    layout="wide"
)

# Initialisation de session
if 'hotel_profile' not in st.session_state:
    st.session_state.hotel_profile = None
if 'revenue_manager' not in st.session_state:
    st.session_state.revenue_manager = None
if 'competitor_data' not in st.session_state:
    st.session_state.competitor_data = None

def load_config() -> Dict[str, Any]:
    """Charge la configuration depuis le fichier YAML"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"Erreur lors du chargement de la configuration: {e}")
        return {}

def load_hotel_profile():
    """Charge le profil de l'hôtel"""
    try:
        from src.hotel_profile.hotel_config import HotelProfileManager
        manager = HotelProfileManager(str(HOTEL_PROFILE_PATH))
        st.session_state.hotel_profile = manager.load_configuration()
        st.success("Profil hôtelier chargé avec succès!")
        return True
    except Exception as e:
        st.error(f"Erreur lors du chargement du profil: {e}")
        return False

def initialize_revenue_manager():
    """Initialise le gestionnaire de revenus IA"""
    try:
        from src.ai_revenue_manager.llm_manager import AIRevenueManager
        st.session_state.revenue_manager = AIRevenueManager(str(CONFIG_PATH))
        st.success("Gestionnaire de revenus IA initialisé!")
        return True
    except Exception as e:
        st.error(f"Erreur d'initialisation de l'IA: {e}")
        return False

async def scrape_competitor_prices(hotel_profile, check_in: datetime, nights: int = 2):
    """Scrape les prix des concurrents"""
    try:
        from src.competitor_analysis.web_scraper import CompetitorPriceScraper
        scraper = CompetitorPriceScraper()
        
        check_out = check_in + timedelta(days=nights)
        competitor_ids = [
            id_ for id_ in hotel_profile.external_ids.values() 
            if id_.startswith('booking')
        ]
        
        if not competitor_ids:
            st.warning("Aucun ID de concurrent trouvé dans le profil")
            return None
            
        results = await scraper.scrape_booking_com(
            hotel_ids=competitor_ids,
            check_in=check_in,
            check_out=check_out
        )
        return results
    except Exception as e:
        st.error(f"Erreur lors du scraping: {e}")
        return None

def generate_sample_historical_data(days: int = 90) -> pd.DataFrame:
    """Génère des données historiques factices"""
    dates = pd.date_range(end=datetime.now(), periods=days)
    return pd.DataFrame({
        'date': dates,
        'occupancy_rate': [0.6 + 0.2 * (i % 7) / 6 for i in range(days)],
        'avg_daily_rate': [120 + 30 * (i % 14) / 13 for i in range(days)],
        'revenue': [10000 + 5000 * (i % 30) / 29 for i in range(days)]
    })

# Barre latérale
st.sidebar.title("Configuration")

# Initialisation du système
if st.sidebar.button("🔄 Initialiser le système"):
    with st.spinner("Initialisation en cours..."):
        if load_hotel_profile() and initialize_revenue_manager():
            st.sidebar.success("Système initialisé avec succès!")

# Menu principal
menu = st.sidebar.radio(
    "Menu",
    ["Tableau de bord", "Analyse concurrentielle", "Recommandations IA", "Profil Hôtelier"]
)

# Page principale
if menu == "Tableau de bord":
    st.title("📊 Tableau de bord - Revenue Manager IA")
    
    if st.session_state.hotel_profile:
        hotel = st.session_state.hotel_profile
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Hôtel", hotel.name)
            st.metric("Catégorie", f"{hotel.stars} ⭐ - {hotel.category}")
            
        with col2:
            st.metric("Chambres", hotel.total_rooms)
            st.metric("Étages", hotel.total_floors)
            
        with col3:
            st.metric("Check-in/out", f"{hotel.check_in_time} / {hotel.check_out_time}")
            st.metric("Restaurants", hotel.restaurants)
        
        # Graphique des performances
        st.subheader("📈 Performances récentes")
        historical_data = generate_sample_historical_data()
        
        tab1, tab2, tab3 = st.tabs(["Taux d'occupation", "Prix moyen", "Revenu"])
        
        with tab1:
            fig = px.line(
                historical_data.tail(30), 
                x='date', 
                y='occupancy_rate',
                title="Taux d'occupation (30 derniers jours)",
                labels={'occupancy_rate': "Taux d'occupation", 'date': 'Date'}
            )
            fig.update_layout(yaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            fig = px.line(
                historical_data.tail(30), 
                x='date', 
                y='avg_daily_rate',
                title="Prix moyen journalier (30 derniers jours)",
                labels={'avg_daily_rate': "Prix moyen (€)", 'date': 'Date'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with tab3:
            fig = px.line(
                historical_data.tail(30), 
                x='date', 
                y='revenue',
                title="Revenu journalier (30 derniers jours)",
                labels={'revenue': "Revenu (€)", 'date': 'Date'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
    else:
        st.warning("Veuillez initialiser le système dans la barre latérale")

elif menu == "Analyse concurrentielle":
    st.title("🔍 Analyse Concurrentielle")
    
    if not st.session_state.hotel_profile:
        st.warning("Veuillez initialiser le système dans la barre latérale")
        st.stop()
        
    hotel = st.session_state.hotel_profile
    
    st.subheader("Configuration de l'analyse")
    col1, col2 = st.columns(2)
    
    with col1:
        check_in = st.date_input(
            "Date d'arrivée",
            datetime.now() + timedelta(days=7)
        )
        
    with col2:
        nights = st.number_input(
            "Nombre de nuits",
            min_value=1,
            max_value=30,
            value=2
        )
    
    if st.button("🔍 Lancer l'analyse concurrentielle"):
        with st.spinner("Analyse en cours..."):
            results = asyncio.run(scrape_competitor_prices(hotel, check_in, nights))
            
            if results:
                st.session_state.competitor_data = results
                
                # Afficher les résultats
                df_results = pd.DataFrame([
                    {
                        'Hôtel': r.get('hotel_name', 'Inconnu'),
                        'Prix (€)': r.get('price', 'N/A'),
                        'Plateforme': r.get('platform', 'N/A'),
                        'Date': r.get('scraped_at', 'N/A')
                    }
                    for r in results
                ])
                
                st.subheader("📊 Résultats de l'analyse")
                st.dataframe(
                    df_results,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Graphique des prix
                if not df_results.empty and 'Prix (€)' in df_results.columns:
                    fig = px.bar(
                        df_results,
                        x='Hôtel',
                        y='Prix (€)',
                        title="Comparaison des prix concurrents",
                        color='Hôtel'
                    )
                    st.plotly_chart(fig, use_container_width=True)

elif menu == "Recommandations IA":
    st.title("🤖 Recommandations de tarification IA")
    
    if not st.session_state.revenue_manager or not st.session_state.hotel_profile:
        st.warning("Veuillez initialiser le système dans la barre latérale")
        st.stop()
        
    hotel = st.session_state.hotel_profile
    manager = st.session_state.revenue_manager
    
    st.subheader("Paramètres d'analyse")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_occupancy = st.slider(
            "Taux d'occupation actuel (%)",
            min_value=0,
            max_value=100,
            value=75
        ) / 100
        
        current_price = st.number_input(
            "Prix actuel (€)",
            min_value=50.0,
            max_value=1000.0,
            value=180.0,
            step=5.0
        )
    
    with col2:
        weather = st.selectbox(
            "Météo prévue",
            ["Ensoleillé", "Nuageux", "Pluvieux", "Orageux", "Neige"]
        )
        
        events = st.multiselect(
            "Événements à venir",
            ["Salon professionnel", "Festival", "Conférence", "Mariage", "Autre"]
        )
    
    if st.button("🚀 Générer des recommandations IA"):
        with st.spinner("Analyse en cours avec l'IA..."):
            try:
                # Préparer les données pour l'analyse
                hotel_data = {
                    'occupancy_rate': current_occupancy,
                    'current_price': current_price,
                    'category': f"{hotel.stars} étoiles",
                    'total_rooms': hotel.total_rooms
                }
                
                market_data = {
                    'competitor_prices': [r.get('price') for r in st.session_state.competitor_data or [] 
                                         if r and 'price' in r],
                    'events': events,
                    'weather': weather
                }
                
                historical_data = generate_sample_historical_data()
                
                # Obtenir les recommandations
                analysis = manager.analyze_situation(
                    hotel_data=hotel_data,
                    market_data=market_data,
                    historical_data=historical_data
                )
                
                # Afficher les résultats
                st.subheader("🎯 Recommandations IA")
                
                if 'price_recommendations' in analysis:
                    st.metric(
                        "Prix recommandé",
                        f"{analysis['price_recommendations'].get('standard', 'N/A')} €"
                    )
                
                if 'recommended_actions' in analysis:
                    st.subheader("✅ Actions recommandées")
                    for action in analysis.get('recommended_actions', []):
                        st.write(f"- {action}")
                
                if 'summary' in analysis:
                    st.subheader("📝 Analyse détaillée")
                    st.write(analysis.get('summary', 'Aucune analyse disponible'))
                
            except Exception as e:
                st.error(f"Erreur lors de l'analyse: {str(e)}")

elif menu == "Profil Hôtelier":
    st.title("🏨 Profil de l'hôtel")
    
    if not st.session_state.hotel_profile:
        st.warning("Veuillez initialiser le système dans la barre latérale")
        st.stop
        
    hotel = st.session_state.hotel_profile
    
    # Affichage des informations de base
    st.subheader("Informations générales")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Nom", hotel.name)
        if hotel.brand:
            st.metric("Marque", hotel.brand)
        st.metric("Catégorie", f"{hotel.stars} ⭐ - {hotel.category}")
        
    with col2:
        st.metric("Adresse", f"{hotel.address}, {hotel.city}")
        st.metric("Contact", f"{hotel.phone} | {hotel.email}")
        if hotel.website:
            st.markdown(f"**Site web**: [{hotel.website}]({hotel.website})")
    
    # Types de chambres
    st.subheader("Types de chambres")
    if hasattr(hotel, 'room_types') and hotel.room_types:
        room_types = []
        for rt in hotel.room_types:
            room_types.append({
                'Type': rt.name,
                'Quantité': rt.total_count,
                'Prix de base': f"{rt.base_price} €",
                'Surface': f"{rt.size_sqm} m²",
                'Occupation max': rt.max_occupancy
            })
        
        st.dataframe(
            pd.DataFrame(room_types),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Aucun type de chambre défini")
    
    # Équipements
    st.subheader("Équipements")
    if hasattr(hotel, 'amenities') and hasattr(hotel, 'facilities'):
        amenities = hotel.amenages.copy() if hasattr(hotel, 'amenities') else []
        if hasattr(hotel, 'facilities'):
            for amenity, available in hotel.facilities.items():
                if available:
                    amenities.append(amenity.replace('_', ' ').title())
        
        if amenities:
            cols = st.columns(3)
            for i, amenity in enumerate(sorted(amenities)):
                with cols[i % 3]:
                    st.markdown(f"✓ {amenity}")
        else:
            st.info("Aucun équipement défini")
    else:
        st.warning("Informations sur les équipements non disponibles")

# Pied de page
st.sidebar.markdown("---")
st.sidebar.info(
    "AI Hotel Revenue Optimizer v2.0\n\n"
    "Développé avec ❤️\n"
    "© 2025 Tous droits réservés"
)

# Exécution asynchrone
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()