import streamlit as st
from pathlib import Path
import yaml
import sys
from datetime import datetime
import pandas as pd
import plotly.express as px

# Configuration du chemin
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

# Configuration de la page
st.set_page_config(
    page_title="AI Hotel Revenue Optimizer",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Charger la configuration
@st.cache_data
def load_config():
    config_path = BASE_DIR / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Style personnalisé
def load_css():
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .stProgress>div>div>div>div {
            background-color: #FF4B4B;
        }
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

def generate_sample_data(days=30):
    """Génère des données factices pour les démonstrations"""
    dates = pd.date_range(end=datetime.now(), periods=days)
    return pd.DataFrame({
        'date': dates,
        'occupation': [min(95, 70 + (i % 30) * 0.5) for i in range(days)],
        'price': [180 + (i % 7) * 2 for i in range(days)],
        'revenue': [12000 + (i * 200) for i in range(days)],
        'competitor_avg': [175 + (i % 5) for i in range(days)]
    })

def show_dashboard():
    st.title("📊 Tableau de bord")
    
    # Données factices
    data = generate_sample_data()
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">'
                   '<h3>👥 Occupation</h3>'
                   f'<h2>{data["occupation"].iloc[-1]:.1f}%</h2>'
                   f'<p>{1.2 if data["occupation"].iloc[-1] > data["occupation"].iloc[-2] else "-"}{abs(data["occupation"].iloc[-1] - data["occupation"].iloc[-2]):.1f}% vs hier</p>'
                   '</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">'
                   '<h3>💰 Prix Moyen</h3>'
                   f'<h2>{data["price"].iloc[-1]:.2f}€</h2>'
                   f'<p>{"+" if data["price"].iloc[-1] > data["price"].iloc[-2] else ""}{(data["price"].iloc[-1] - data["price"].iloc[-2]):.2f}€ vs hier</p>'
                   '</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">'
                   '<h3>📈 RevPAR</h3>'
                   f'<h2>{(data["price"].iloc[-1] * data["occupation"].iloc[-1]/100):.2f}€</h2>'
                   f'<p>{"+" if data["revenue"].iloc[-1] > data["revenue"].iloc[-2] else ""}{((data["revenue"].iloc[-1] - data["revenue"].iloc[-2])/data["revenue"].iloc[-2]*100):.1f}% vs hier</p>'
                   '</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">'
                   '<h3>💵 Revenu</h3>'
                   f'<h2>{data["revenue"].iloc[-1]:.0f}€</h2>'
                   f'<p>{"+" if data["revenue"].iloc[-1] > data["revenue"].iloc[-2] else ""}{((data["revenue"].iloc[-1] - data["revenue"].iloc[-2])/data["revenue"].iloc[-2]*100):.1f}% vs hier</p>'
                   '</div>', unsafe_allow_html=True)
    
    # Graphiques
    tab1, tab2, tab3 = st.tabs(["📈 Occupation", "💶 Prix", "💰 Revenu"])
    
    with tab1:
        fig = px.line(data, x='date', y='occupation', 
                     title="Taux d'occupation (30 derniers jours)",
                     labels={'occupation': "Taux d'occupation (%)", 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.line(data, x='date', y=['price', 'competitor_avg'],
                     title="Évolution des prix vs concurrence",
                     labels={'value': 'Prix (€)', 'date': 'Date', 'variable': 'Légende'},
                     color_discrete_map={'price': '#FF4B4B', 'competitor_avg': '#808080'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = px.bar(data, x='date', y='revenue',
                    title="Revenu journalier",
                    labels={'revenue': 'Revenu (€)', 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)

def show_competitor_analysis():
    st.title("🔍 Analyse Concurrentielle")
    st.write("Analyse des prix des hôtels concurrents dans votre zone.")
    
    # Données factices de compétiteurs
    competitors = [
        {"name": "Hôtel Rival", "price": 185, "rating": 4.2, "distance": 0.8},
        {"name": "Grand Hôtel", "price": 210, "rating": 4.5, "distance": 1.2},
        {"name": "Hôtel Central", "price": 195, "rating": 4.0, "distance": 0.5},
        {"name": "Plaza Hôtel", "price": 230, "rating": 4.7, "distance": 1.5},
        {"name": "Hôtel du Parc", "price": 175, "rating": 3.9, "distance": 0.9}
    ]
    
    # Afficher les cartes des compétiteurs
    cols = st.columns(3)
    for i, comp in enumerate(competitors):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <h3>{comp['name']}</h3>
                <p>Prix: <strong>{comp['price']}€</strong></p>
                <p>Note: {comp['rating']} ⭐</p>
                <p>Distance: {comp['distance']} km</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Graphique comparatif
    df_comp = pd.DataFrame(competitors)
    fig = px.bar(df_comp, x='name', y='price', 
                title="Comparaison des prix des hôtels concurrents",
                labels={'name': 'Hôtel', 'price': 'Prix (€)'})
    st.plotly_chart(fig, use_container_width=True)

def show_ai_recommendations():
    st.title("🤖 Recommandations IA")
    st.write("Recommandations personnalisées basées sur l'analyse des données.")
    
    # Exemple de recommandation
    st.markdown("""
    <div style="
        border-left: 5px solid #FF4B4B;
        background-color: #f8f9fa;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 0 10px 10px 0;
    ">
        <h3>Recommandation du jour</h3>
        <p>Augmentez votre prix de 5% pour les réservations du week-end prochain. 
        L'analyse prédictive montre une forte demande et des prix plus élevés chez les concurrents.</p>
        <p>Impact estimé : <strong>+8% de revenu</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Actions recommandées
    st.subheader("Actions recommandées")
    actions = [
        {"action": "Ajuster les prix pour les séjours longs", "impact": "Moyen", "difficulty": "Facile"},
        {"action": "Proposer des offres spéciales en semaine", "impact": "Élevé", "difficulty": "Moyen"},
        {"action": "Mettre à jour les photos de l'hôtel", "impact": "Faible", "difficulty": "Facile"}
    ]
    
    for act in actions:
        st.markdown(f"""
        <div style="
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background-color: white;
        ">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <strong>{act['action']}</strong>
                <span>Impact: {act['impact']} | Difficulté: {act['difficulty']}</span>
            </div>
            <button style="
                background-color: #FF4B4B;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                cursor: pointer;
            ">Mettre en œuvre</button>
        </div>
        """, unsafe_allow_html=True)

def show_hotel_profile():
    st.title("🏨 Profil Hôtelier")
    st.write("Gérez les informations de votre établissement.")
    
    # Charger la configuration
    config = load_config()
    
    # Formulaire d'édition
    with st.form("hotel_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nom de l'hôtel", value=config['hotel']['name'])
            category = st.selectbox(
                "Catégorie",
                ["3 étoiles", "4 étoiles", "5 étoiles", "Palace"],
                index=1
            )
            city = st.text_input("Ville", value=config['hotel']['location']['city'])
        
        with col2:
            total_rooms = st.number_input("Nombre total de chambres", 
                                         min_value=1, 
                                         value=config['hotel']['total_rooms'])
            country = st.text_input("Pays", value=config['hotel']['location']['country'])
        
        # Bouton de soumission
        submitted = st.form_submit_button("Enregistrer les modifications")
        if submitted:
            # Mettre à jour la configuration
            config['hotel'].update({
                'name': name,
                'category': category,
                'total_rooms': total_rooms,
                'location': {
                    'city': city,
                    'country': country
                }
            })
            
            # Sauvegarder dans le fichier
            with open(BASE_DIR / "config" / "config.yaml", 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
            
            st.success("Profil mis à jour avec succès !")

def main():
    load_css()
    config = load_config()
    
    # Barre latérale
    st.sidebar.title("🏨 AI Hotel Revenue Optimizer")
    st.sidebar.markdown(f"**Version:** {config.get('version', '1.0.0')}")
    
    # Menu de navigation
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.radio("", 
                          ["Tableau de bord", "Analyse Concurrentielle", 
                           "Recommandations IA", "Profil Hôtelier"])
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Développé avec ❤️ par votre équipe\n"
        "© 2025 Tous droits réservés"
    )
    
    # Affichage conditionnel des pages
    if page == "Tableau de bord":
        show_dashboard()
    elif page == "Analyse Concurrentielle":
        show_competitor_analysis()
    elif page == "Recommandations IA":
        show_ai_recommendations()
    elif page == "Profil Hôtelier":
        show_hotel_profile()

if __name__ == "__main__":
    main()