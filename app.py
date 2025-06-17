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

# Initialisation explicite de st.session_state.hotel_profile
if 'hotel_profile' not in st.session_state:
    st.session_state.hotel_profile = None

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
        st.session_state.hotel_profile = manager.get_hotel_info()
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
        hotel = st.session_state.hotel_profile or {}
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Hôtel", hotel.get('name', 'Nom indisponible'))
            st.metric("Catégorie", f"{hotel.get('stars', 'N/A')} ⭐ - {hotel.get('category', 'N/A')}")
        
        with col2:
            st.metric("Chambres", hotel.get('total_rooms', 'N/A'))
            st.metric("Étages", hotel.get('total_floors', 'N/A'))
        
        with col3:
            st.metric("Adresse", f"{hotel.get('address', 'Adresse indisponible')}, {hotel.get('city', 'Ville indisponible')}")
            st.metric("Contact", hotel.get('phone', 'Contact indisponible'))
            if hotel.get('website'):
                st.markdown(f"**Site web**: [{hotel.get('website')}]({hotel.get('website')})")
        
        # Display forecast reports
        st.subheader("📈 Rapports Prévisionnels")
        if 'forecast_reports' in st.session_state:
            st.dataframe(st.session_state.forecast_reports)
        else:
            st.warning("Aucun rapport prévisionnel disponible.")
            
        # Ajout de la fonctionnalité de téléversement de fichiers CSV
        uploaded_file = st.file_uploader("Téléverser un rapport prévisionnel (CSV)", type="csv")
        if uploaded_file is not None:
            import pandas as pd
            try:
                # Lecture du fichier CSV
                forecast_data = pd.read_csv(uploaded_file)
                st.success("Rapport prévisionnel chargé avec succès !")
                st.dataframe(forecast_data)
            except Exception as e:
                st.error(f"Erreur lors du chargement du fichier : {e}")
        else:
            st.info("Veuillez téléverser un fichier CSV pour afficher les données.")
    else:
        st.error("Veuillez initialiser le système dans la barre latérale.")

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
                    'category': f"{hotel.get('stars', 'N/A')} étoiles",
                    'total_rooms': hotel.get('total_rooms', 'N/A')
                }
                
                market_data = {
                    'competitor_prices': [r.get('price') for r in st.session_state.competitor_data or [] 
                                         if r and 'price' in r],
                    'events': events,
                    'weather': weather
                }
                
                historical_data = generate_sample_historical_data()
                
                # Ajout de vérifications robustes pour éviter les erreurs liées à NoneType
                if hotel and isinstance(hotel, dict):
                    category = f"{hotel.get('stars', 'N/A')} étoiles"
                    total_rooms = hotel.get('total_rooms', 'N/A')
                else:
                    category = "N/A"
                    total_rooms = "N/A"

                # Vérification pour manager avant d'appeler analyze_situation
                if manager:
                    analysis = manager.analyze_situation(
                        hotel_data=hotel_data,
                        market_data=market_data,
                        historical_data=historical_data
                    )
                else:
                    analysis = None
                
                # Afficher les résultats
                st.subheader("🎯 Recommandations IA")
                
                if analysis and 'price_recommendations' in analysis:
                    st.metric(
                        "Prix recommandé",
                        f"{analysis['price_recommendations'].get('standard', 'N/A')} €"
                    )
                
                if analysis and 'recommended_actions' in analysis:
                    st.subheader("✅ Actions recommandées")
                    for action in analysis.get('recommended_actions', []):
                        st.write(f"- {action}")
                
                if analysis and 'summary' in analysis:
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
        # Ajout de vérifications robustes pour éviter les erreurs liées à NoneType
        if hotel and isinstance(hotel, dict):
            st.metric("Nom", hotel.get('name', 'Inconnu'))
            if hotel.get('brand'):
                st.metric("Marque", hotel.get('brand', 'Inconnu'))
            st.metric("Catégorie", f"{hotel.get('stars', 'N/A')} ⭐ - {hotel.get('category', 'N/A')}")
        
    with col2:
        if hotel and isinstance(hotel, dict):
            st.metric("Adresse", f"{hotel.get('address', 'Inconnu')}, {hotel.get('city', 'Inconnu')}")
            st.metric("Contact", f"{hotel.get('phone', 'Inconnu')} | {hotel.get('email', 'Inconnu')}")
            if hotel.get('website'):
                st.markdown(f"**Site web**: [{hotel.get('website')}]({hotel.get('website')})")
    
    # Types de chambres
    st.subheader("Types de chambres")
    if hotel and isinstance(hotel, dict):
        if 'room_types' in hotel and hotel.get('room_types'):
            room_types = []
            for rt in hotel.get('room_types', []):
                room_types.append({
                    'Type': rt.get('name', 'Inconnu'),
                    'Quantité': rt.get('total_count', 0),
                    'Prix de base': f"{rt.get('base_price', 0)} €",
                    'Surface': f"{rt.get('size_sqm', 0)} m²",
                    'Occupation max': rt.get('max_occupancy', 1)
                })
            
            st.dataframe(
                pd.DataFrame(room_types),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Aucun type de chambre défini")
    else:
        st.warning("Les informations de l'hôtel sont manquantes ou invalides.")

    # Équipements
    st.subheader("Équipements")
    if hotel and isinstance(hotel, dict):
        amenities = hotel.get('amenities', []).copy() if 'amenities' in hotel else []
        if 'facilities' in hotel:
            for amenity, available in hotel.get('facilities', {}).items():
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
        st.warning("Les informations sur les équipements sont manquantes ou invalides.")

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