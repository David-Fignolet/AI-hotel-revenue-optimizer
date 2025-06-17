"""
Application Streamlit pour le tableau de bord de revenue management
"""
import os
import re
import sys
import tempfile
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

# Gestion sécurisée des imports
MISSING_DEPS = []
DEPENDENCY_ERRORS = {}

# Configuration globale
AI_MANAGERS_AVAILABLE = True
MISTRAL_AVAILABLE = True  # Can be set to False if Mistral is not available
DASHBOARD_AVAILABLE = True  # Feature flag for dashboard components

def safe_import(module_name: str) -> Optional[object]:
    """Import un module de manière sécurisée avec gestion des erreurs."""
    try:
        if module_name in sys.modules:
            return sys.modules[module_name]
        return __import__(module_name)
    except ImportError as e:
        MISSING_DEPS.append(module_name)
        DEPENDENCY_ERRORS[module_name] = str(e)
        return None

# Import des dépendances externes
np = safe_import('numpy')
pd = safe_import('pandas')
plotly = safe_import('plotly')
st = safe_import('streamlit')
load_dotenv = getattr(safe_import('python_dotenv'), 'load_dotenv', None)

# Import des sous-modules plotly si disponible
if plotly is not None:
    go = safe_import('plotly.graph_objects')
    make_subplots = getattr(safe_import('plotly.subplots'), 'make_subplots', None)
else:
    go = None
    make_subplots = None

# Ajout du chemin parent au PYTHONPATH
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.dashboard import DashboardVisuals
from src.ai_revenue_manager.llm_manager import AIRevenueManager
from src.ai_revenue_manager.mistral_llm_manager import MistralRevenueManager
from src.ai_revenue_manager.google_llm_manager import GoogleAIRevenueManager

# Charger les variables d'environnement
if load_dotenv is not None:
    load_dotenv()

# Fonctions d'affichage sécurisé Streamlit
def safe_st_error(msg: str) -> None:
    """Affiche un message d'erreur Streamlit de manière sécurisée."""
    if st is not None and hasattr(st, 'error'):
        st.error(msg)
    else:
        print(f"ERROR: {msg}", file=sys.stderr)

def safe_st_warning(msg: str) -> None:
    """Affiche un avertissement Streamlit de manière sécurisée."""
    if st is not None and hasattr(st, 'warning'):
        st.warning(msg)
    else:
        print(f"WARNING: {msg}", file=sys.stderr)

def safe_st_info(msg: str) -> None:
    """Affiche une information Streamlit de manière sécurisée."""
    if st is not None and hasattr(st, 'info'):
        st.info(msg)
    else:
        print(f"INFO: {msg}")

def safe_st_success(msg: str) -> None:
    """Affiche un message de succès Streamlit de manière sécurisée."""
    if st is not None and hasattr(st, 'success'):
        st.success(msg)
    else:
        print(f"SUCCESS: {msg}")

def safe_st_metric(label: str, value: str, delta: Optional[str] = None) -> None:
    """Affiche une métrique Streamlit de manière sécurisée."""
    if st is not None and hasattr(st, 'metric'):
        if delta:
            st.metric(label=label, value=value, delta=delta)
        else:
            st.metric(label=label, value=value)
    else:
        print(f"{label}: {value}" + (f" ({delta})" if delta else ""))

def safe_st_plotly_chart(fig) -> None:
    """Affiche un graphique Plotly avec Streamlit de manière sécurisée."""
    if st is not None and hasattr(st, 'plotly_chart') and fig is not None:
        st.plotly_chart(fig)
    else:
        print("WARNING: Impossible d'afficher le graphique Plotly")

def safe_st_markdown(text: str) -> None:
    """Affiche du texte formaté en markdown de manière sécurisée."""
    if st is not None and hasattr(st, 'markdown'):
        st.markdown(text)
    else:
        print(text)

def safe_st_text(text: str) -> None:
    """Affiche du texte brut de manière sécurisée."""
    if st is not None and hasattr(st, 'text'):
        st.text(text)
    else:
        print(text)

def safe_st_subheader(text: str) -> None:
    """Affiche un sous-titre de manière sécurisée."""
    if st is not None and hasattr(st, 'subheader'):
        st.subheader(text)
    else:
        print(f"\n=== {text} ===\n")

def clean_numeric_series(series):
    """Nettoie une série numérique en remplaçant les virgules par des points."""
    if pd.api.types.is_numeric_dtype(series):
        return series
    return pd.to_numeric(
        series.astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    )

def parse_hotel_pdf(pdf_file):
    """Traite un fichier PDF d'hôtel et retourne un DataFrame nettoyé."""
    if not TABULA_AVAILABLE:
        st.error("Erreur: tabula-py n'est pas disponible. Impossible de traiter les fichiers PDF.")
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_file.getvalue())
        tmp_path = tmp.name
    
    try:
        dfs = read_pdf(
            tmp_path,
            pages='all',
            multiple_tables=True,
            lattice=False,
            stream=True,
            pandas_options={'header': None},
            guess=False
        )
        
        if not dfs:
            st.error("Aucune donnée trouvée dans le PDF")
            return None
        
        df = pd.concat(dfs, ignore_index=True)
        df = df.dropna(how='all').reset_index(drop=True)
        
        processed_data = {
            'date': [],
            'price': [],
            'occupancy_rate': [],
            'chambres_occupees': [],
            'chambres_totales': [],
            'ca_total': []
        }
        
        for _, row in df.iterrows():
            row_str = ' '.join([str(cell) for cell in row if str(cell) != 'nan'])
            if not row_str.strip():
                continue
                
            date_match = re.search(r'(\d{2}\.\d{2}\.\d{2,4})', row_str)
            if not date_match:
                continue
                
            try:
                date_str = date_match.group(1)
                date = pd.to_datetime(date_str, dayfirst=True).date()
                
                numbers = re.findall(r'(\d+[\.,]?\d*)', row_str)
                numbers = [float(n.replace(',', '.')) for n in numbers if n.replace(',', '').replace('.', '').isdigit()]
                
                if len(numbers) >= 12:
                    processed_data['date'].append(date)
                    processed_data['chambres_occupees'].append(numbers[6])
                    processed_data['chambres_totales'].append(numbers[7])
                    processed_data['occupancy_rate'].append(numbers[8] / 100)  # Convertir en décimal
                    processed_data['price'].append(numbers[10])
                    processed_data['ca_total'].append(numbers[11])
                    
            except Exception as e:
                print(f"Ligne ignorée: {row_str}")
                continue
                
        result_df = pd.DataFrame(processed_data)
        
        if result_df.empty:
            st.error("Aucune donnée valide trouvée dans le PDF")
            return None
            
        return result_df
        
    except Exception as e:
        st.error(f"Erreur lors du traitement du PDF : {str(e)}")
        return None
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def load_uploaded_file(uploaded_file):
    """Charge et traite les données depuis un fichier CSV ou PDF."""
    if uploaded_file is None:
        return None
        
    try:
        if uploaded_file.type == "text/csv":
            # Essai de différents encodages
            encodings = ['utf-8', 'iso-8859-1', 'cp1252']
            data = None
            error = None

            for encoding in encodings:
                try:
                    data = pd.read_csv(uploaded_file, encoding=encoding)
                    if data is not None and len(data) > 0:
                        break
                except (UnicodeDecodeError, pd.errors.EmptyDataError) as e:
                    error = e
                    continue

            if data is None:
                if error:
                    st.error(f"Erreur de lecture du fichier : {str(error)}")
                return None

            # Normaliser les noms de colonnes
            data.columns = data.columns.str.strip()

            # Recherche de la colonne de date avec différents noms possibles
            date_columns = [col for col in data.columns if 'date' in col.lower()]
            if date_columns:
                # Utiliser la première colonne de date trouvée
                date_col = date_columns[0]
                try:
                    data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
                except Exception as e:
                    st.warning(f"Attention: Impossible de convertir la colonne {date_col} en dates. {str(e)}")

            return data
        elif uploaded_file.type == "application/pdf":
            st.error("Le traitement des fichiers PDF n'est pas encore implémenté.")
            return None
        else:
            st.error(f"Type de fichier non supporté: {uploaded_file.type}")
            return None
    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier : {str(e)}")
        return None



def generate_predictions(df, days=30):
    """Génère des prédictions pour les 30 prochains jours."""
    try:
        # Vérifier si on a au moins une date
        date_col = next((col for col in df.columns if col.lower() == 'date'), None)
        if not date_col:
            st.error("Aucune colonne de date trouvée.")
            return None
        
        # Convertir la colonne Date
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        if df[date_col].isnull().any():
            st.warning("Certaines dates n'ont pas pu être converties")
            df = df.dropna(subset=[date_col])
            
        if df.empty:
            raise ValueError("Aucune date valide trouvée")
            
        df = df.sort_values(date_col)
        last_date = df[date_col].max()
        
        # Calculer les dates futures
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=days,
            freq='D',
            name='Date'
        )
        
        # Identifier les colonnes d'occupation et de CA
        occupation_cols = [col for col in df.columns if any(term in col.lower() for term in ['libre', 'occup'])]
        ca_cols = [col for col in df.columns if any(term in col.lower() for term in ['ca', 'revenu', 'chiffre'])]
        
        # Calculer les moyennes et écarts-types
        taux_occupation = None
        std_occupation = None
        if occupation_cols:
            col = occupation_cols[0]
            if 'libre' in col.lower():
                taux_occupation = 100 - df[col].mean()
                std_occupation = df[col].std()
            else:
                taux_occupation = df[col].mean()
                std_occupation = df[col].std()
        else:
            taux_occupation = 50
            std_occupation = 10
        
        ca_moyen = None
        std_ca = None
        if ca_cols:
            col = ca_cols[0]
            ca_moyen = df[col].mean()
            std_ca = df[col].std()
        else:
            ca_moyen = 1000
            std_ca = 100
        
        # Générer les prédictions
        np.random.seed(42)
        
        # Tendances sur les 7 derniers jours
        window = min(7, len(df))
        occupation_trend = 0
        ca_trend = 0
        
        if occupation_cols:
            col = occupation_cols[0]
            occupation_trend = df[col].iloc[-window:].diff().mean()
            if 'libre' in col.lower():
                occupation_trend *= -1
        
        if ca_cols:
            col = ca_cols[0]
            ca_trend = df[col].iloc[-window:].pct_change().mean() or 0
        
        occupation_pred = []
        ca_pred = []
        
        for i in range(days):
            # Prédiction du taux d'occupation
            trend = occupation_trend * (i + 1) / days
            occupation = np.random.normal(taux_occupation + trend, std_occupation/4)
            occupation = max(0, min(100, occupation))
            occupation_pred.append(occupation)
            
            # Prédiction du CA
            trend_factor = 1 + (ca_trend * (i + 1) / days)
            ca = np.random.normal(ca_moyen * trend_factor, std_ca)
            ca = max(0, ca)
            ca_pred.append(ca)
        
        predictions = pd.DataFrame({
            'Date': future_dates,
            'Taux Occupation': occupation_pred,
            'CA Prévu': ca_pred
        })
        
        return predictions
        
    except Exception as e:
        st.error(f"Erreur lors de la génération des prédictions : {str(e)}")
        return None

def display_metrics(df):
    """Affiche les indicateurs clés de performance."""
    if df is None or df.empty:
        return

    if st is not None:
        col1, col2, col3 = st.columns(3)
    else:
        col1 = col2 = col3 = None

    # Identifier les colonnes d'occupation
    occupation_cols = [col for col in df.columns if any(term in col.lower() for term in ['chambres', 'occup'])]
    taux_libre_cols = [col for col in df.columns if 'libre' in col.lower() and '%' in col]
    ca_cols = [col for col in df.columns if any(term in col.lower() for term in ['ca', 'revenu', 'chiffre'])]

    # Colonnes d'occupation
    if col1:
        with col1:
            if occupation_cols:
                col = occupation_cols[0]
                chambres = df[col].mean()
                safe_st_metric("Chambres Occupées (moyenne)", f"{chambres:.1f}")
            else:
                safe_st_metric("Chambres Occupées", "N/A")

    # Taux d'occupation
    if col2:
        with col2:
            if taux_libre_cols:
                taux_libre = df[taux_libre_cols[0]].mean()
                safe_st_metric("Taux d'occupation", f"{100 - taux_libre:.1f}%")
            elif occupation_cols:
                for col in occupation_cols:
                    try:
                        values = pd.to_numeric(df[col], errors='coerce')
                        if values.max() <= 1:  # Si les valeurs sont entre 0 et 1
                            taux = values.mean() * 100
                        elif values.max() <= 100:  # Si les valeurs sont en pourcentage
                            taux = values.mean()
                        else:  # Si ce sont des nombres absolus, on ne peut pas calculer le taux
                            continue
                        safe_st_metric("Taux d'occupation", f"{taux:.1f}%")
                        break
                    except:
                        continue
            else:
                safe_st_metric("Taux d'occupation", "N/A")

    # Chiffre d'affaires
    if col3:
        with col3:
            if ca_cols:
                col = ca_cols[0]
                periode = "jour" if len(df) <= 31 else "mois" if len(df) <= 365 else "année"
                ca_total = df[col].mean()
                safe_st_metric(f"CA moyen par {periode}", f"{ca_total:.0f} €")

def create_dashboard_analysis(data):
    """Crée l'analyse du tableau de bord si possible."""
    if not DASHBOARD_AVAILABLE or data is None or data.empty:
        return
        
    if st is not None:
        st.subheader("Analyse avancée")
    
    try:
        # Identifier les colonnes pour le dashboard
        date_col = next((col for col in data.columns if col.lower() == 'date'), None)
        occupation_cols = [col for col in data.columns if any(term in col.lower() for term in ['occup', 'libre'])]
        
        if not date_col:
            safe_st_warning("Colonne de date non trouvée")
            return
            
        if not occupation_cols:
            safe_st_warning("Colonnes d'occupation non trouvées")
            return
            
        # Préparer les données
        dashboard_data = data[[date_col] + occupation_cols].copy()
        
        # Convertir les taux d'occupation
        occupation_col = occupation_cols[0]
        if 'libre' in occupation_col.lower():
            dashboard_data['predicted_occupancy'] = (100 - dashboard_data[occupation_col]) / 100
        else:
            # Normaliser entre 0 et 1 si nécessaire
            values = dashboard_data[occupation_col]
            if values.max() > 1:
                dashboard_data['predicted_occupancy'] = values / 100
            else:
                dashboard_data['predicted_occupancy'] = values
        
        # Calcul des bornes
        mean_occ = dashboard_data['predicted_occupancy'].mean()
        std_occ = dashboard_data['predicted_occupancy'].std()
        
        dashboard_data['lower_bound'] = (dashboard_data['predicted_occupancy'] - std_occ * 0.5).clip(0, 1)
        dashboard_data['upper_bound'] = (dashboard_data['predicted_occupancy'] + std_occ * 0.5).clip(0, 1)
        
        # Renommer la colonne de date
        dashboard_data = dashboard_data.assign(date=dashboard_data[date_col])
        
        # Créer et afficher le graphique
        try:
            if DashboardVisuals is not None:
                dashboard = DashboardVisuals()
                chart = dashboard.create_occupancy_forecast_chart(dashboard_data)
                if chart is not None:
                    safe_st_plotly_chart(chart)
                else:
                    safe_st_warning("Impossible de créer le graphique d'analyse")
        except Exception as e:
            safe_st_error(f"Erreur lors de la création du graphique : {str(e)}")
            
    except Exception as e:
        safe_st_error(f"Erreur lors de l'analyse avancée : {str(e)}")
        if os.getenv('DEBUG'):
            safe_st_error(traceback.format_exc())

class StreamlitUI:
    """Classe pour gérer l'interface utilisateur Streamlit."""
    
    def __init__(self):
        self.st = safe_import('streamlit')
        self.np = safe_import('numpy')
        self.pd = safe_import('pandas')
        self.go = safe_import('plotly.graph_objects')
        self.make_subplots = getattr(safe_import('plotly.subplots'), 'make_subplots', None)
        
        # Configurer la page si streamlit est disponible
        if self.st is not None:
            self.st.set_page_config(
                page_title="Optimisateur de Revenu Hôtelier",
                page_icon="🏨",
                layout="wide"
            )
    
    def show_title(self):
        """Affiche le titre de l'application."""
        if self.st is not None:
            self.st.title("🏨 Optimisateur de Revenu Hôtelier")
    
    def show_sidebar(self):
        """Affiche la barre latérale pour le chargement des fichiers."""
        if self.st is not None:
            with self.st.sidebar:
                self.st.header("Chargement des données")
                return self.st.file_uploader(
                    "Téléchargez un fichier CSV ou PDF",
                    type=["csv", "pdf"]
                )
        return None
    
    def show_data_preview(self, data):
        """Affiche un aperçu des données."""
        if self.st is not None and data is not None:
            self.st.subheader("Aperçu des données")
            self.st.dataframe(data.head())
    
    def show_metrics(self, data):
        """Affiche les métriques principales."""
        if self.st is not None:
            self.st.subheader("Indicateurs clés")
        display_metrics(data)
    
    def show_predictions(self, data):
        """Affiche les prédictions et graphiques."""
        if data is None or len(data) <= 7:
            return
            
        if self.st is not None:
            with self.st.spinner("Génération des prédictions..."):
                predictions = generate_predictions(data)
                
                if predictions is not None and not predictions.empty:
                    self.st.subheader("Prévisions des 30 prochains jours")
                    
                    try:
                        if self.make_subplots is not None and self.go is not None:
                            fig = self.make_subplots(specs=[[{"secondary_y": True}]])
                            
                            # Ajouter les prédictions de CA
                            fig.add_trace(
                                self.go.Scatter(
                                    x=predictions['Date'],
                                    y=predictions['CA Prévu'],
                                    name='CA Prévu (€)',
                                    line=dict(color='blue')
                                ),
                                secondary_y=False
                            )
                            
                            # Ajouter les prédictions de taux d'occupation
                            fig.add_trace(
                                self.go.Scatter(
                                    x=predictions['Date'],
                                    y=predictions['Taux Occupation'],
                                    name="Taux d'occupation (%)",
                                    line=dict(color='red')
                                ),
                                secondary_y=True
                            )
                            
                            # Mise en forme du graphique
                            fig.update_layout(
                                title="Prévisions du CA et du taux d'occupation",
                                xaxis_title="Date",
                                yaxis_title="CA Prévu (€)",
                                yaxis2_title="Taux d'occupation (%)",
                                hovermode='x unified',
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1
                                )
                            )
                            
                            # Configuration des axes
                            fig.update_yaxes(
                                title_font=dict(color="blue"),
                                tickfont=dict(color="blue"),
                                secondary_y=False
                            )
                            fig.update_yaxes(
                                title_font=dict(color="red"),
                                tickfont=dict(color="red"),
                                secondary_y=True
                            )
                            
                            safe_st_plotly_chart(fig)
                    except Exception as e:
                        safe_st_error(f"Erreur lors de la création du graphique : {str(e)}")
        else:
            safe_st_error("Streamlit n'est pas disponible")
    
    def setup_ai_manager(self):
        """Configure et initialise le gestionnaire d'IA."""
        if self.st is None:
            return None

        with self.st.sidebar:
            self.st.markdown("### 🤖 Configuration IA")
            
            # Sélection du modèle
            ai_model = self.st.radio(
                "Modèle IA",
                options=["Mistral (Local)", "Google AI"],
                index=0 if MISTRAL_AVAILABLE else 1,
                help="Choisissez le modèle d'IA à utiliser"
            )
            
            if ai_model == "Mistral (Local)":
                if not MISTRAL_AVAILABLE:
                    safe_st_error("❌ Mistral n'est pas disponible")
                    safe_st_info("""
                    Pour installer Mistral :
                    1. Téléchargez Ollama sur https://ollama.ai/download
                    2. Installez et lancez Ollama
                    3. Exécutez : `ollama pull mistral`
                    """)
                    return None
                
                try:
                    manager = MistralRevenueManager()
                    safe_st_success("✅ Mistral initialisé")
                    return manager
                except Exception as e:
                    safe_st_error(f"❌ Erreur Mistral: {str(e)}")
                    return None
            else:
                # Google AI
                api_key = os.getenv('GOOGLE_AI_API_KEY')
                if not api_key:
                    safe_st_error("❌ Clé API Google AI manquante")
                    safe_st_info("Ajoutez GOOGLE_AI_API_KEY dans votre fichier .env")
                    return None
                
                try:
                    manager = GoogleAIRevenueManager()
                    safe_st_success("✅ Google AI initialisé")
                    return manager
                except Exception as e:
                    safe_st_error(f"❌ Erreur Google AI: {str(e)}")
                    return None

    def show_ai_section(self):
        """Affiche la section d'analyse IA."""
        if self.st is None:
            return

        if self.st.sidebar.checkbox("🤖 Activer AI Revenue Manager"):
            self.st.sidebar.markdown("---")
            self.st.sidebar.markdown("### 🧠 AI Revenue Manager")
            
            # Initialiser le manager IA s'il n'existe pas déjà
            if 'ai_manager' not in self.st.session_state:
                self.st.session_state['ai_manager'] = self.setup_ai_manager()
            
            # Bouton d'analyse IA
            if self.st.sidebar.button("🔮 Analyser avec IA") and self.st.session_state['ai_manager']:
                with self.st.spinner("L'IA analyse la situation..."):
                    try:
                        # Construire les données pour l'IA
                        hotel_data = {
                            'occupancy_rate': 0.72,  # À adapter selon les données réelles
                            'current_price': 175,
                            'min_price': 80,
                            'max_price': 300
                        }
                        
                        market_data = {
                            'competitor_prices': [180, 190, 165, 185],
                            'events': ['Salon du tourisme'],
                            'weather': 'Ensoleillé'
                        }
                        
                        # Obtenir l'analyse IA
                        ai_analysis = self.st.session_state['ai_manager'].analyze_situation(
                            hotel_data, market_data
                        )
                        
                        # Afficher les résultats
                        self.st.subheader("🤖 Analyse IA Revenue Manager")
                        
                        col1, col2 = self.st.columns(2)
                        
                        with col1:
                            self.st.metric(
                                "Prix Recommandé", 
                                f"{ai_analysis['analysis']['recommended_price']:.0f}€"
                            )
                        
                        with col2:
                            self.st.metric(
                                "Niveau de Confiance", 
                                f"{ai_analysis['analysis']['confidence_score']:.0%}"
                            )
                        
                        # Afficher l'analyse complète
                        self.st.text_area(
                            "Analyse Détaillée",
                            ai_analysis['analysis']['summary'],
                            height=200
                        )
                        
                        # Actions recommandées
                        self.st.subheader("📋 Actions Recommandées")
                        for i, action in enumerate(ai_analysis['analysis']['recommended_actions'], 1):
                            self.st.write(f"{i}. {action}")
                            
                    except Exception as e:
                        safe_st_error(f"Erreur lors de l'analyse IA : {str(e)}")
            elif not self.st.session_state['ai_manager']:
                safe_st_error("Le gestionnaire IA n'est pas initialisé. Vérifiez la configuration.")

def run_app():
    """Fonction principale de l'application."""
    ui = StreamlitUI()
    ui.show_title()
    
    # Charger les données depuis la sidebar
    uploaded_file = ui.show_sidebar()
    
    # Charger les données
    data = None
    if uploaded_file is not None:
        data = load_uploaded_file(uploaded_file)
    else:
        # Charger des données d'exemple
        try:
            if ui.pd is not None:
                data = ui.pd.read_csv("exemple_donnees_historiques.csv")
                if 'date' in data.columns:
                    data['date'] = ui.pd.to_datetime(data['date'], dayfirst=True, errors='coerce')
                    data = data.dropna(subset=['date'])
                safe_st_info("Utilisation des données d'exemple. Téléchargez vos propres données pour commencer.")
        except Exception as e:
            safe_st_error(f"Erreur lors du chargement des données d'exemple : {str(e)}")
            return
    
    if data is not None and not data.empty:
        # Afficher l'aperçu des données et les métriques
        safe_st_markdown("### Aperçu des données")
        if st is not None:
            st.dataframe(data.head())
        else:
            print(data.head())
        
        safe_st_markdown("### Indicateurs clés")
        display_metrics(data)
        
        # Générer et afficher les prédictions
        if len(data) > 7:
            predictions = None
            if st is not None:
                with st.spinner("Génération des prédictions..."):
                    predictions = generate_predictions(data)
            else:
                predictions = generate_predictions(data)
            
            if predictions is not None and not predictions.empty:
                safe_st_markdown("### Prévisions des 30 prochains jours")
                
                # Créer un graphique avec deux axes y
                try:
                    if make_subplots is not None and go is not None:
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        
                        # Ajouter les prédictions de CA
                        fig.add_trace(
                            go.Scatter(
                                x=predictions['Date'],
                                y=predictions['CA Prévu'],
                                name='CA Prévu (€)',
                                line=dict(color='blue')
                            ),
                            secondary_y=False
                        )
                        
                        # Ajouter les prédictions de taux d'occupation
                        fig.add_trace(
                            go.Scatter(
                                x=predictions['Date'],
                                y=predictions['Taux Occupation'],
                                name="Taux d'occupation (%)",
                                line=dict(color='red')
                            ),
                            secondary_y=True
                        )
                        
                        # Mise en forme du graphique
                        fig.update_layout(
                            title="Prévisions du CA et du taux d'occupation",
                            xaxis_title="Date",
                            yaxis_title="CA Prévu (€)",
                            yaxis2_title="Taux d'occupation (%)",
                            hovermode='x unified',
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        
                        # Configuration des axes
                        fig.update_yaxes(
                            title_font=dict(color="blue"),
                            tickfont=dict(color="blue"),
                            secondary_y=False
                        )
                        fig.update_yaxes(
                            title_font=dict(color="red"),
                            tickfont=dict(color="red"),
                            secondary_y=True
                        )
                        
                        safe_st_plotly_chart(fig)
                except Exception as e:
                    safe_st_error(f"Erreur lors de la création du graphique : {str(e)}")
        
        # Analyse avancée
        create_dashboard_analysis(data)
        
        # Section IA
        ui.show_ai_section()
    else:
        safe_st_warning("Aucune donnée à afficher. Veuillez charger un fichier valide.")