"""
AI Hotel Revenue Optimizer - Application principale
Interface utilisateur Streamlit pour l'optimisation des revenus hôteliers
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import yaml
import os
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import nest_asyncio

# Active le support asynchrone pour Streamlit
nest_asyncio.apply()

# Import des services
from src.utils.context_builder import ContextBuilder
from src.utils.services import ExternalServices
from src.ai_revenue_manager.ollama_manager import OllamaRevenueManager
from src.competitor_analysis.web_scraper import CompetitorPriceScraper

# Configuration des chemins
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"
HOTEL_PROFILE_PATH = BASE_DIR / "config" / "hotel_profile.yaml"

def get_nested_value(data: dict, *keys: str, default: Any = None) -> Any:
    """Récupère en toute sécurité une valeur imbriquée dans un dictionnaire"""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is None:
            return default
    return current

def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Récupère en toute sécurité une valeur d'un dictionnaire ou objet"""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

async def analyze_hotel_situation(manager: Any, analysis_data: dict, stream: bool = True):
    """Fonction asynchrone pour l'analyse de situation"""
    try:
        if not manager or not hasattr(manager, 'analyze_situation'):
            raise ValueError("Revenue Manager non initialisé")
            
        return await manager.analyze_situation(
            analysis_data,
            stream=stream
        )
    except Exception as e:
        raise Exception(f"Erreur lors de l'analyse: {str(e)}")

async def refresh_external_context():
    """Rafraîchit le contexte externe (météo et événements)"""
    if not st.session_state.hotel_profile:
        return
        
    try:
        hotel = st.session_state.hotel_profile
        context = await st.session_state.context_builder.build_context(            hotel_data={
                'current_date': st.session_state.current_date.strftime('%Y-%m-%d'),
                'occupancy_rate': safe_get(hotel, 'current_occupancy', 0.7),
                'current_price': safe_get(hotel, 'current_price', 100)
            },
            market_data=st.session_state.competitor_data or {},
            historical_data=generate_sample_historical_data() if 'historical_data' not in st.session_state else st.session_state.historical_data,
            config={'hotel': hotel}
        )
        st.session_state.external_context = context.get('external_factors', {})
        return context
    except Exception as e:
        st.error(f"Erreur lors du rafraîchissement du contexte : {str(e)}")
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

def display_weather_card():
    """Affiche la carte météo"""
    if not st.session_state.external_context:
        return
        
    weather = st.session_state.external_context.get('weather', {})
    if not weather:
        return
        
    with st.expander("🌤️ Météo et Impact", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            current = weather.get('current', {})
            st.metric(
                "Température actuelle",
                current.get('temp', 'N/A'),
                delta=None,
                delta_color="off"
            )
            st.markdown(f"**Conditions**: {current.get('description', 'N/A')}")
            
        with col2:
            impact = weather.get('revenue_impact', {})
            st.metric(
                "Impact Revenue",
                impact.get('impact', 'neutre').title(),
                delta=f"{impact.get('score', 0)*100:.1f}%",
                delta_color="normal" if impact.get('score', 0) >= 0 else "inverse"
            )
            st.progress(min(abs(impact.get('score', 0))*100, 100))
            
        # Prévisions
        if weather.get('forecast'):
            st.subheader("Prévisions 5 jours")
            forecast_df = pd.DataFrame(weather['forecast'])
            fig = px.line(forecast_df, 
                         x='date', 
                         y=['temp_max', 'temp_min'],
                         title="Températures prévues")
            st.plotly_chart(fig, use_container_width=True)

def display_events_card():
    """Affiche la carte des événements"""
    st.subheader("📅 Événements à venir")
    
    events = safe_get(st.session_state.get('external_context', {}), 'events', {}).get('events', [])
    
    if not events:
        st.info("Aucun événement à venir")
        return
        
    for event in events[:5]:  # Afficher les 5 premiers événements
        with st.container():
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(f"**{event.get('name', 'Événement')}**")
                st.caption(f"📍 {event.get('venue', 'Lieu non spécifié')}")
            with cols[1]:
                st.write(f"📅 {event.get('date', 'Date non spécifiée')}")
                if impact := event.get('impact'):
                    st.caption(f"Impact: {impact}")

# Configuration de la page
st.set_page_config(
    page_title="AI Hotel Revenue Optimizer",
    page_icon="🏨",
    layout="wide"
)

# Initialisation de session
def init_session_state():
    """Initialise tous les états de session nécessaires"""
    if 'hotel_profile' not in st.session_state:
        st.session_state.hotel_profile = None
    if 'revenue_manager' not in st.session_state:
        st.session_state.revenue_manager = None
    if 'competitor_data' not in st.session_state:
        st.session_state.competitor_data = None
    if 'current_date' not in st.session_state:
        st.session_state.current_date = datetime.now().strftime('%Y-%m-%d')
    if 'context_builder' not in st.session_state:
        st.session_state.context_builder = ContextBuilder()
    if 'external_context' not in st.session_state:
        st.session_state.external_context = None
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = None
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []

# Initialisation au démarrage
init_session_state()
if 'context_builder' not in st.session_state:
    st.session_state.context_builder = ContextBuilder()
if 'external_context' not in st.session_state:
    st.session_state.external_context = None

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
        from src.ai_revenue_manager.ollama_manager import OllamaRevenueManager
        manager = OllamaRevenueManager()
        
        # Vérifier la connexion à Ollama
        status = manager.check_ollama_connection()
        if not status['success']:
            st.error(f"Erreur de connexion à Olloma: {status['error']}")
            return False
            
        # Télécharger le modèle si nécessaire
        pull_status = manager.pull_model()
        if not pull_status['success']:
            st.error(f"Erreur de téléchargement du modèle: {pull_status['error']}")
            return False
            
        st.session_state.revenue_manager = manager
        st.success("✅ Gestionnaire de revenus IA initialisé avec succès!")
        return True
        
    except Exception as e:
        st.error(f"❌ Erreur d'initialisation de l'IA: {str(e)}")
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
              # Construction des URLs des concurrents
        competitor_urls = [f"https://booking.com/hotel/{hotel_id}" for hotel_id in competitor_ids]
        nights = (check_out - check_in).days
        
        results = await scraper.scrape_prices(
            urls=competitor_urls,
            check_in=check_in,
            nights=nights
        )
        return results
    except Exception as e:
        st.error(f"Erreur lors du scraping: {e}")
        return None

async def get_competitor_prices(competitor_ids: List[str], check_in: datetime, check_out: datetime) -> List[Dict[str, Any]]:
    """Récupère les prix des concurrents de manière asynchrone"""
    try:
        async with CompetitorPriceScraper() as scraper:
            # Construction des URLs des concurrents
            competitor_urls = [f"https://booking.com/hotel/{hotel_id}" for hotel_id in competitor_ids]
            nights = (check_out - check_in).days
            
            results = await scraper.scrape_prices(
                urls=competitor_urls,
                check_in=check_in,
                nights=nights
            )
            return results
    except Exception as e:
        st.error(f"Erreur lors de la récupération des prix concurrents : {str(e)}")
        return []

async def update_competitor_data():
    """Met à jour les données des concurrents"""
    try:
        competitor_ids = st.session_state.get('competitor_ids', [])
        if not competitor_ids:
            return
            
        check_in = datetime.now()
        check_out = check_in + timedelta(days=1)
        
        prices = await get_competitor_prices(competitor_ids, check_in, check_out)
        if prices:
            st.session_state.competitor_data = {
                'prices': prices,
                'updated_at': datetime.now().isoformat()
            }
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour des données concurrents : {str(e)}")

async def get_metrics_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Prépare le contexte des métriques"""
    try:
        return {
            'metrics': {
                'occupancy_rate': safe_get(st.session_state.hotel_profile, 'current_occupancy', 0.7),
                'avg_daily_rate': safe_get(st.session_state.hotel_profile, 'current_price', 100),
                'revpar': safe_get(st.session_state.hotel_profile, 'current_price', 100) * 
                         safe_get(st.session_state.hotel_profile, 'current_occupancy', 0.7),
                'upcoming_events': len(safe_get(context, 'external_factors', {}).get('events', {}).get('events', [])),
                'weather_risk': safe_get(context, 'external_factors', {}).get('weather', {}).get('risk', 'faible'),
                'market_pressure': safe_get(context, 'market_analysis', {}).get('competitive_pressure', 'moyenne')
            }
        }
    except Exception as e:
        st.error(f"Erreur lors de la préparation du contexte des métriques : {str(e)}")
        return {'metrics': {}}

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
        # Rafraîchissement du contexte
        if st.button("🔄 Rafraîchir les données"):
            with st.spinner("Mise à jour des données..."):
                asyncio.run(refresh_external_context())
        
        hotel = st.session_state.hotel_profile or {}
        
        # Informations de base
        with st.container():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Hôtel", hotel.get('name', 'Nom indisponible'))
                st.metric("Catégorie", f"{hotel.get('stars', 'N/A')} ⭐ - {hotel.get('category', 'N/A')}")
            
            with col2:
                st.metric("Chambres", hotel.get('total_rooms', 'N/A'))
                st.metric("Chambres disponibles", 
                         hotel.get('available_rooms', hotel.get('total_rooms', 0)))
            
            with col3:
                st.metric(
                    "Taux d'occupation", 
                    f"{hotel.get('current_occupancy', 0)*100:.1f}%",
                    delta=f"{hotel.get('occupancy_trend', 0)*100:+.1f}%"
                )
                st.metric(
                    "RevPAR", 
                    f"{hotel.get('current_revpar', 0):.2f}€",
                    delta=f"{hotel.get('revpar_trend', 0):+.2f}€"
                )
        
        # Carte météo et événements
        st.subheader("📊 Contexte externe")
        col1, col2 = st.columns(2)
        
        with col1:
            display_weather_card()
            
        with col2:
            display_events_card()
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
    st.title("🤖 Recommandations IA")
    
    if not st.session_state.hotel_profile or not st.session_state.revenue_manager:
        st.warning("Veuillez initialiser le système dans la barre latérale")
        st.stop()
        
    hotel = st.session_state.hotel_profile
    manager = st.session_state.revenue_manager
    
    # Interface d'analyse
    st.subheader("🔍 Analyse de situation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_type = st.selectbox(
            "Type d'analyse",
            ["Quotidienne", "Concurrentielle", "Événementielle", "Stratégique"]
        )
    
    with col2:
        horizon = st.slider(
            "Horizon d'analyse (jours)",
            min_value=1,
            max_value=90,
            value=7
        )
        
    async def run_analysis(analysis_type: str, horizon: int, manager: Any):
        """Exécute l'analyse de situation de manière asynchrone"""
        try:
            # Rafraîchissement du contexte externe
            context = await refresh_external_context()
            
            if not context:
                st.error("Impossible de récupérer le contexte externe")
                return
                
            # Préparation des données enrichies
            analysis_data = {
                'hotel': safe_get(hotel, 'name', 'Hotel'),
                'current_date': st.session_state.current_date,
                'analysis_type': analysis_type.lower(),
                'horizon_days': horizon,
                
                # Métriques actuelles
                'occupancy_rate': safe_get(hotel, 'current_occupancy', 0.7),
                'average_daily_rate': safe_get(hotel, 'current_price', 100),
                'revpar': safe_get(hotel, 'current_revpar', 70),
                'rooms_available': safe_get(hotel, 'available_rooms', 
                                        safe_get(hotel, 'total_rooms', 0)),
                
                # Contexte externe
                'weather_impact': safe_get(context.get('external_factors', {})
                                       .get('weather', {})
                                       .get('revenue_impact', {}), 'impact', 'neutre'),
                'weather_confidence': safe_get(context.get('external_factors', {})
                                           .get('weather', {})
                                           .get('revenue_impact', {}), 'confidence', 0),
                'events_impact': safe_get(context.get('external_factors', {})
                                      .get('events', {})
                                      .get('revenue_impact', {}), 'impact', 'neutre'),
                'events_confidence': safe_get(context.get('external_factors', {})
                                          .get('events', {})
                                          .get('revenue_impact', {})
                                          .get('confidence'), 'score', 0),
                'upcoming_events': len(safe_get(context.get('external_factors', {})
                                           .get('events', {})
                                           .get('events', []), 'events', [])),
                'market_pressure': safe_get(context, 'competitive_pressure', 'moyenne'),
                
                # Tendances
                'occupancy_trend': safe_get(hotel, 'occupancy_trend', 0),
                'revpar_trend': safe_get(hotel, 'revpar_trend', 0),
                'booking_pace': safe_get(context, 'booking_pace', 'normal')
            }
            
            # Affichage du contexte d'analyse
            with st.expander("📊 Contexte d'analyse", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Taux d'occupation",
                        f"{analysis_data['occupancy_rate']*100:.1f}%",
                        f"{analysis_data['occupancy_trend']*100:+.1f}%"
                    )
                    
                with col2:
                    st.metric(
                        "Impact météo",
                        analysis_data['weather_impact'].title(),
                        f"{analysis_data['weather_confidence']:.0f}% confiance"
                    )
                    
                with col3:
                    st.metric(
                        "Événements à venir",
                        str(analysis_data['upcoming_events']),
                        analysis_data['events_impact'].title()
                    )
            
            # Lancement de l'analyse IA
            analysis_placeholder = st.empty()
            analysis = await analyze_hotel_situation(
                manager,
                analysis_data,
                stream=True
            )
            
            if analysis:
                analysis_placeholder.markdown(analysis)
                
                # Affichage des recommandations spécifiques
                if 'recommendations' in st.session_state:
                    with st.expander("📈 Recommandations détaillées", expanded=True):
                        for rec in st.session_state.recommendations:
                            st.markdown(f"- {rec}")
                            
        except Exception as e:
            st.error(f"Erreur lors de l'analyse: {str(e)}")
            return None

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

def load_forecast_report(uploaded_file):
    """Charge et affiche un rapport prévisionnel depuis un fichier CSV"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Affichage des données
        st.subheader("📊 Rapport Prévisionnel")
        
        # Métriques clés
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_occupancy = df['Chambres Occupées'].mean()
            st.metric("Occupation moyenne", f"{avg_occupancy:.1f} chambres")
        with col2:
            avg_revenue = df['Prévision C.A'].mean()
            st.metric("CA moyen", f"{avg_revenue:.2f}€")
        with col3:
            total_revenue = df['Prévision C.A'].sum()
            st.metric("CA total", f"{total_revenue:.2f}€")
        
        # Tableau détaillé
        st.dataframe(df, use_container_width=True)
        
        # Graphiques
        fig = px.line(df, x='Date', y=['Chambres Occupées', 'Libre (%)'])
        st.plotly_chart(fig, use_container_width=True)
        
        return True
    except Exception as e:
        st.error(f"Erreur lors du chargement du rapport: {str(e)}")
        return False

# Interface principale
st.title("🏨 Hotel Revenue Optimizer")

# Tabs
tab1, tab2 = st.tabs(["Dashboard", "Rapports Prévisionnels"])

with tab1:
    # Dashboard existant
    # ...existing code...
    pass

with tab2:
    st.header("📈 Rapports Prévisionnels")
    forecast_file = st.file_uploader(
        "Téléverser un rapport prévisionnel (CSV)",
        type="csv",
        key="forecast_upload"  # Clé unique pour éviter les doublons
    )
    
    if forecast_file is not None:
        load_forecast_report(forecast_file)

async def get_ai_recommendations(data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Obtient les recommandations IA pour l'optimisation des revenus"""
    try:
        if not st.session_state.get('revenue_manager'):
            st.error("Le gestionnaire de revenue n'est pas initialisé")
            return {}

        # Préparation des données d'analyse
        analysis_data = {
            'hotel_data': {
                'current_date': st.session_state.current_date,
                'occupancy_rate': safe_get(st.session_state.hotel_profile, 'current_occupancy', 0.7),
                'current_price': safe_get(st.session_state.hotel_profile, 'current_price', 100),
                'hotel_class': safe_get(st.session_state.hotel_profile, 'class', 3),
                'total_rooms': safe_get(st.session_state.hotel_profile, 'total_rooms', 100)
            },
            'market_data': st.session_state.get('competitor_data', {}),
            'historical_data': st.session_state.get('historical_data', generate_sample_historical_data()),
            'external_context': st.session_state.get('external_context', {})
        }
        
        # Enrichissement avec le contexte externe
        context = await refresh_external_context()
        if context:
            analysis_data['external_context'] = context.get('external_factors', {})
            
        # Analyse de la situation
        recommendations = await analyze_hotel_situation(
            st.session_state.revenue_manager,
            analysis_data,
            stream=True
        )
        
        return recommendations
    except Exception as e:
        st.error(f"Erreur lors de l'obtention des recommandations : {str(e)}")
        return {}

def display_ai_recommendations():
    """Affiche les recommandations IA dans l'interface"""
    st.subheader("🤖 Recommandations IA")
    
    with st.container():
        # Bouton pour rafraîchir les recommandations
        if st.button("Rafraîchir les recommandations", key="refresh_recommendations"):
            with st.spinner("Analyse en cours..."):
                try:
                    recommendations = asyncio.run(get_ai_recommendations())
                    st.session_state.current_recommendations = recommendations
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse : {str(e)}")
                    return

        # Affichage des recommandations
        recommendations = st.session_state.get('current_recommendations', {})
        
        if recommendations:
            # Prix recommandé
            price_rec = safe_get(recommendations, 'price_recommendation.suggested_price')
            if price_rec:
                st.metric(
                    "Prix recommandé",
                    f"{price_rec:.2f} €",
                    delta=f"{price_rec - safe_get(st.session_state.hotel_profile, 'current_price', 0):.2f} €"
                )

            # Analyse de la demande
            demand = safe_get(recommendations, 'demand_analysis')
            if demand:
                st.write("### Analyse de la demande")
                st.write(demand)

            # Facteurs d'influence
            factors = safe_get(recommendations, 'influence_factors', [])
            if factors:
                st.write("### Facteurs d'influence")
                for factor in factors:
                    st.write(f"- {factor}")

            # Stratégies suggérées
            strategies = safe_get(recommendations, 'suggested_strategies', [])
            if strategies:
                st.write("### Stratégies suggérées")
                for strategy in strategies:
                    st.write(f"- {strategy}")
        else:
            st.info("Cliquez sur 'Rafraîchir les recommandations' pour obtenir une analyse IA de votre situation.")

async def perform_analysis(manager, analysis_data):
    """Effectue l'analyse de situation de manière asynchrone"""
    try:
        analysis_placeholder = st.empty()
        analysis = await analyze_hotel_situation(
            manager,
            analysis_data,
            stream=True
        )
        analysis_placeholder.markdown(analysis)
        return analysis
    except Exception as e:
        st.error(f"Erreur lors de l'analyse: {str(e)}")
        return None

async def main():
    """Fonction principale de l'application"""

    # Initialisation de la session si nécessaire
    if 'current_date' not in st.session_state:
        st.session_state.current_date = datetime.now()
    
    if 'context_builder' not in st.session_state:
        st.session_state.context_builder = ContextBuilder()
    
    if 'external_services' not in st.session_state:
        st.session_state.external_services = ExternalServices()
    
    if 'revenue_manager' not in st.session_state:
        st.session_state.revenue_manager = OllamaRevenueManager()
        # Test de la connexion Ollama
        try:
            connection_status = st.session_state.revenue_manager.check_ollama_connection()
            if not connection_status.get('status') == 'ok':
                st.error("Erreur de connexion à Olloma. Assurez-vous que le service est actif.")
        except Exception as e:
            st.error(f"Erreur d'initialisation du Revenue Manager: {str(e)}")

    # Sidebar pour la configuration
    with st.sidebar:
        st.title("🏨 Configuration")
        
        # Sélection de la date
        st.session_state.current_date = st.date_input(
            "Date d'analyse",
            st.session_state.current_date
        )

    # Corps principal
    st.title("🏨 AI Hotel Revenue Optimizer")

    # Mise en page du dashboard
    col1, col2 = st.columns(2)

    with col1:
        display_weather_card()

    with col2:
        display_events_card()

    # Section des recommandations IA
    display_ai_recommendations()


if __name__ == "__main__":
    asyncio.run(main())
