
import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh



# Configuration de la page
st.set_page_config(
    page_title="Dashboard Capteurs IoT",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour le style
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px );
    }
    
    .metric-card-danger {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        animation: pulse 1s infinite;
    }
    
    .metric-card-success {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .main-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.2rem;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        padding: 1rem 2rem;
        margin: 0.5rem;
        border-radius: 10px;
        background-color: #f2f2f2;
        color: #333;
        border: 2px solid #ccc;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease-in-out;
        text-align: center;
}

    .stTabs [aria-selected="true"] {
        background-color: #4CAF50 !important;
        color: white !important;
        border-color: #4CAF50;
    }

</style>
""", unsafe_allow_html=True)

# Classe pour simuler les données de capteur
class SensorDataSimulator:
    def __init__(self):
        self.temp_range = (15.0, 35.0)
        self.hum_range = (30.0, 70.0)
        self.pres_range = (950.0, 1050.0)
    
    def generate_sensor_data(self):
        """Génère des données aléatoires comme le publisher ROS2"""
        temp = random.uniform(10.0, 40.0)  # Élargi pour avoir des valeurs hors plage parfois
        hum = random.uniform(20.0, 80.0)
        pres = random.uniform(940.0, 1060.0)
        
        return {
            'temperature': temp,
            'humidity': hum,
            'pressure': pres,
            'timestamp': datetime.now()
        }
    
    def is_in_range(self, value, range_tuple):
        """Vérifie si une valeur est dans la plage acceptable"""
        return range_tuple[0] <= value <= range_tuple[1]


# Initialisation des données de session
def initialize_session_state():
    if 'sensor_data_history' not in st.session_state:
        st.session_state.sensor_data_history = []
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'simulator' not in st.session_state:
        st.session_state.simulator = SensorDataSimulator()

# Fonction pour afficher une métrique avec indicateur de statut
def display_metric_card(title, value, unit, emoji, is_normal, threshold_info=""):
    card_class = "metric-card-success" if is_normal else "metric-card-danger"
    status_emoji = "✅" if is_normal else "⚠️"
    
    st.markdown(f"""
    <div class="metric-card {card_class}">
        <h3>{emoji} {title}</h3>
        <h1>{value:.2f} {unit}</h1>
        <p>{status_emoji} {threshold_info}</p>
    </div>
    """, unsafe_allow_html=True)

# Fonction pour créer les graphiques
def create_charts(data_history):
    if len(data_history) < 2:
        return None
    
    df = pd.DataFrame(data_history)
    
    # Créer un graphique avec 3 sous-graphiques
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('🌡️ Température (°C)', '💧 Humidité (%)', '🌪️ Pression (hPa)'),
        vertical_spacing=0.3
    )
    
    # Température
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['temperature'], 
                  mode='lines+markers', name='Température',
                  line=dict(color='#e74c3c', width=3)),
        row=1, col=1
    )
    
    # Humidité
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['humidity'], 
                  mode='lines+markers', name='Humidité',
                  line=dict(color='#3498db', width=3)),
        row=2, col=1
    )
    
    # Pression
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['pressure'], 
                  mode='lines+markers', name='Pression',
                  line=dict(color='#9b59b6', width=3)),
        row=3, col=1
    )
    
    fig.update_layout(height=600, showlegend=False, 
                     title_text="Évolution des capteurs en temps réel")
    
    return fig

# Fonction pour calculer les statistiques
def calculate_stats(data_history):
    if not data_history:
        return None
    
    df = pd.DataFrame(data_history)
    
    stats = {
        'temperature': {
            'mean': df['temperature'].mean(),
            'max': df['temperature'].max(),
            'min': df['temperature'].min()
        },
        'humidity': {
            'mean': df['humidity'].mean(),
            'max': df['humidity'].max(),
            'min': df['humidity'].min()
        },
        'pressure': {
            'mean': df['pressure'].mean(),
            'max': df['pressure'].max(),
            'min': df['pressure'].min()
        }
    }
    
    return stats

# Interface principale
def main():
    initialize_session_state()
    
    # Titre principal
    st.markdown('<h1 class="main-title">🌡️ Dashboard Capteurs IoT</h1>', unsafe_allow_html=True)
    
    # Sidebar pour les contrôles
    with st.sidebar:
        st.header("⚙️ Contrôles")
        
        # Bouton start/stop
        if st.button("🟢 Démarrer" if not st.session_state.running else "🔴 Arrêter"):
            st.session_state.running = not st.session_state.running
        
        # Option pour effacer l'historique
        if st.button("🗑️ Effacer historique"):
            st.session_state.sensor_data_history = []
            st.success("Historique effacé!")
        
        # Configuration des seuils
        st.subheader("🎯 Configuration des seuils")
        temp_min = st.slider("Température min (°C)", 0, 20, 15)
        temp_max = st.slider("Température max (°C)", 25, 50, 35)
        hum_min = st.slider("Humidité min (%)", 0, 40, 30)
        hum_max = st.slider("Humidité max (%)", 50, 100, 70)
        pres_min = st.slider("Pression min (hPa)", 900, 1000, 950)
        pres_max = st.slider("Pression max (hPa)", 1000, 1100, 1050)
        
        # Mettre à jour les plages
        st.session_state.simulator.temp_range = (temp_min, temp_max)
        st.session_state.simulator.hum_range = (hum_min, hum_max)
        st.session_state.simulator.pres_range = (pres_min, pres_max)
        
        # Informations sur l'état
        st.subheader("📊 État du système")
        st.write(f"**Statut:** {'🟢 Actif' if st.session_state.running else '🔴 Inactif'}")
        st.write(f"**Données collectées:** {len(st.session_state.sensor_data_history)}")
    
    # Boucle principale pour l'affichage en temps réel
    if st.session_state.running:
        # Placeholder pour les données temps réel (en haut, visible immédiatement)
        realtime_placeholder = st.empty()
        
        # Onglets pour les autres données (en dessous)
        tab1, tab2, tab3 = st.tabs(["📈 Graphiques", "📋 Historique", "📊 Statistiques"])
        
        # Placeholders pour les onglets
        chart_placeholder = st.empty()
        history_placeholder = st.empty()
        stats_placeholder = st.empty()
        
        while st.session_state.running:
            # Générer nouvelles données
            new_data = st.session_state.simulator.generate_sensor_data()
            
            # Ajouter à l'historique (garder seulement les 50 dernières valeurs)
            st.session_state.sensor_data_history.append(new_data)
            if len(st.session_state.sensor_data_history) > 50:
                st.session_state.sensor_data_history.pop(0)
            
            # Vérifier les plages
            temp_ok = st.session_state.simulator.is_in_range(
                new_data['temperature'], st.session_state.simulator.temp_range)
            hum_ok = st.session_state.simulator.is_in_range(
                new_data['humidity'], st.session_state.simulator.hum_range)
            pres_ok = st.session_state.simulator.is_in_range(
                new_data['pressure'], st.session_state.simulator.pres_range)
            
            # AFFICHAGE TEMPS RÉEL EN HAUT (visible immédiatement)
            with realtime_placeholder.container():
                st.subheader("📊 Données en temps réel")
                
                # Affichage en colonnes
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    temp_emoji = "🔥" if new_data['temperature'] > 35 else "🌡️"
                    temp_info = f"Normal ({temp_min}-{temp_max}°C)" if temp_ok else "⚠️ HORS PLAGE"
                    display_metric_card("Température", new_data['temperature'], "°C", 
                                      temp_emoji, temp_ok, temp_info)
                
                with col2:
                    hum_info = f"Normal ({hum_min}-{hum_max}%)" if hum_ok else "⚠️ HORS PLAGE"
                    display_metric_card("Humidité", new_data['humidity'], "%", 
                                      "💧", hum_ok, hum_info)
                
                with col3:
                    pres_info = f"Normal ({pres_min}-{pres_max}hPa)" if pres_ok else "⚠️ HORS PLAGE"
                    display_metric_card("Pression", new_data['pressure'], "hPa", 
                                      "🌪️", pres_ok, pres_info)
                
                # Alerte générale
                if not (temp_ok and hum_ok and pres_ok):
                    st.error("🚨 ATTENTION: Certaines valeurs sont hors des plages acceptables!")
                else:
                    st.success("✅ Toutes les valeurs sont dans les plages normales")
                
                # Dernière mise à jour
                st.info(f"🕐 Dernière mise à jour: {new_data['timestamp'].strftime('%H:%M:%S')}")
            
            # Mise à jour des onglets (contenu statique, pas besoin de boucle)
            with tab1:
                if len(st.session_state.sensor_data_history) > 1:
                    st.subheader("📈 Évolution en temps réel")
                    chart = create_charts(st.session_state.sensor_data_history)
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                else:
                    st.info("Collecte de données en cours... Les graphiques apparaîtront bientôt.")
            
            with tab2:
                st.subheader("📋 Historique des 10 dernières mesures")
                if st.session_state.sensor_data_history:
                    recent_data = st.session_state.sensor_data_history[-10:]
                    df_display = pd.DataFrame(recent_data)
                    df_display['timestamp'] = df_display['timestamp'].dt.strftime('%H:%M:%S')
                    df_display = df_display.round(2)
                    st.dataframe(df_display, use_container_width=True)
                else:
                    st.info("Aucune donnée disponible")
            
            with tab3:
                st.subheader("📊 Statistiques de la session")
                stats = calculate_stats(st.session_state.sensor_data_history)
                if stats:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("🌡️ Temp Moyenne", f"{stats['temperature']['mean']:.1f}°C")
                        st.metric("🌡️ Temp Max", f"{stats['temperature']['max']:.1f}°C")
                        st.metric("🌡️ Temp Min", f"{stats['temperature']['min']:.1f}°C")
                    
                    with col2:
                        st.metric("💧 Hum Moyenne", f"{stats['humidity']['mean']:.1f}%")
                        st.metric("💧 Hum Max", f"{stats['humidity']['max']:.1f}%")
                        st.metric("💧 Hum Min", f"{stats['humidity']['min']:.1f}%")
                    
                    with col3:
                        st.metric("🌪️ Pres Moyenne", f"{stats['pressure']['mean']:.1f}hPa")
                        st.metric("🌪️ Pres Max", f"{stats['pressure']['max']:.1f}hPa")
                        st.metric("🌪️ Pres Min", f"{stats['pressure']['min']:.1f}hPa")
                else:
                    st.info("Aucune statistique disponible")
            
            # Attendre 0.5 secondes avant la prochaine mise à jour
            time.sleep(0.5)
    
    else:
        # Système arrêté - affichage statique
        st.info("🔴 Système arrêté. Cliquez sur 'Démarrer' dans la barre latérale pour commencer la collecte de données.")
        
        # Onglets pour les données existantes (même quand arrêté)
        if st.session_state.sensor_data_history:
            tab1, tab2, tab3 = st.tabs(["📈 Graphiques", "📋 Historique", "📊 Statistiques"])
            
            with tab1:
                chart = create_charts(st.session_state.sensor_data_history)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
            
            with tab2:
                recent_data = st.session_state.sensor_data_history[-10:]
                df_display = pd.DataFrame(recent_data)
                df_display['timestamp'] = df_display['timestamp'].dt.strftime('%H:%M:%S')
                df_display = df_display.round(2)
                st.dataframe(df_display, use_container_width=True)
            
            with tab3:
                stats = calculate_stats(st.session_state.sensor_data_history)
                if stats:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("🌡️ Temp Moyenne", f"{stats['temperature']['mean']:.1f}°C")
                        st.metric("🌡️ Temp Max", f"{stats['temperature']['max']:.1f}°C")
                        st.metric("🌡️ Temp Min", f"{stats['temperature']['min']:.1f}°C")
                    
                    with col2:
                        st.metric("💧 Hum Moyenne", f"{stats['humidity']['mean']:.1f}%")
                        st.metric("💧 Hum Max", f"{stats['humidity']['max']:.1f}%")
                        st.metric("💧 Hum Min", f"{stats['humidity']['min']:.1f}%")
                    
                    with col3:
                        st.metric("🌪️ Pres Moyenne", f"{stats['pressure']['mean']:.1f}hPa")
                        st.metric("🌪️ Pres Max", f"{stats['pressure']['max']:.1f}hPa")
                        st.metric("🌪️ Pres Min", f"{stats['pressure']['min']:.1f}hPa")

if __name__ == "__main__":
    main()