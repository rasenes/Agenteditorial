"""
Interface Streamlit pour Editorial Agent.
Dashboard simple et propre.
"""

import streamlit as st
import requests
import json
from typing import List, Dict
import asyncio
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="Editorial Agent IA",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styles
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    .stButton > button {
        background-color: #238636;
        color: white;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #2ea043;
    }
    .tweet-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
    .score-badge {
        background-color: #238636;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# API Base URL
API_URL = "http://localhost:8000/api/v1"

def init_session():
    """Initialize session state."""
    if "tweets" not in st.session_state:
        st.session_state.tweets = []
    if "trends" not in st.session_state:
        st.session_state.trends = []
    if "selected_theme" not in st.session_state:
        st.session_state.selected_theme = "general"

init_session()

# Header
st.title("✍️ Editorial Agent IA")
st.subtitle("Générez des tweets viraux assistés par l'IA")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Theme selection
    theme = st.selectbox(
        "Thème",
        ["general", "IA", "Tech", "Science", "Sport", "Politique", 
         "Business", "Crypto", "Univers", "Culture", "Humour", 
         "Fait", "Philosophie", "Futur"],
        index=0,
    )
    
    # Style selection
    style = st.selectbox(
        "Style",
        ["normal", "aggressive", "funny", "minimal", "data"],
        index=0,
    )
    
    # Number of tweets
    num_tweets = st.slider("Tweets à générer", 1, 10, 3)
    
    # Options
    st.markdown("---")
    st.subheader("Options")
    create_remixes = st.checkbox("Créer des remixes", value=False)
    include_analysis = st.checkbox("Analyser les angles", value=True)
    
    # Pipeline control
    st.markdown("---")
    st.subheader("Pipeline")
    if st.button("🚀 Lancer Pipeline Complet", use_container_width=True):
        with st.spinner("Pipeline en cours..."):
            try:
                response = requests.post(
                    f"{API_URL}/admin/pipeline",
                    params={
                        "num_trends": 5,
                        "tweets_per_trend": num_tweets,
                    },
                    timeout=120,
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Pipeline complété en {result.get('execution_time', 0):.2f}s")
                else:
                    st.error(f"❌ Erreur: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Génération de Tweets")
    
    # Trends section
    if st.button("📡 Récupérer les Tendances", use_container_width=True):
        with st.spinner("Récupération des tendances..."):
            try:
                response = requests.get(
                    f"{API_URL}/trends/fetch",
                    params={"limit": 10},
                    timeout=30,
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.trends = data.get("trends", [])
                    st.success(f"✅ Récupéré {len(st.session_state.trends)} tendances")
                else:
                    st.error(f"❌ Erreur: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    # Display trends
    if st.session_state.trends:
        st.subheader("Tendances Disponibles")
        selected_trend = st.selectbox(
            "Sélectionner une tendance",
            [t["title"] for t in st.session_state.trends],
        )
        
        if st.button("✍️ Générer Tweets", use_container_width=True):
            with st.spinner(f"Génération de {num_tweets} tweets..."):
                try:
                    trend = next(
                        (t for t in st.session_state.trends if t["title"] == selected_trend),
                        None,
                    )
                    if trend:
                        response = requests.post(
                            f"{API_URL}/generate/",
                            json={
                                "trend": trend,
                                "theme": theme,
                                "count": num_tweets,
                                "style": style,
                            },
                            timeout=60,
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.tweets = data.get("tweets", [])
                            st.success(f"✅ Généré {len(st.session_state.tweets)} tweets")
                        else:
                            st.error(f"❌ Erreur: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

with col2:
    st.header("📈 Stats")
    
    # Memory stats
    try:
        response = requests.get(
            f"{API_URL}/memory/stats",
            timeout=10,
        )
        if response.status_code == 200:
            stats = response.json()
            st.metric("Tweets Mémorisés", stats.get("tweets_count", 0))
            st.metric("Score Moyen", f"{stats.get('avg_tweet_score', 0):.2f}")
    except:
        pass

# Generated tweets display
if st.session_state.tweets:
    st.markdown("---")
    st.header("🎯 Tweets Générés")
    
    # Sort by score
    sorted_tweets = sorted(
        st.session_state.tweets,
        key=lambda t: t.get("score", 0),
        reverse=True,
    )
    
    # Display tweets
    for i, tweet in enumerate(sorted_tweets):
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                    <div class="tweet-card">
                    <strong>{tweet.get('theme', 'N/A')}</strong><br>
                    {tweet.get('content', 'N/A')}<br>
                    <small style="color: #8b949e;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                score = tweet.get("score", 0)
                st.markdown(f"<span class='score-badge'>{score:.2f}</span>", unsafe_allow_html=True)
                
                # Actions
                if st.button("📋 Copier", key=f"copy-{i}"):
                    st.write(tweet.get("content"))
                
                if st.button("⭐ Favoris", key=f"fav-{i}"):
                    st.success("Ajouté aux favoris!")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📄 Exporter JSON"):
        st.json(st.session_state.tweets)

with col2:
    if st.button("🔄 Rafraîchir"):
        st.rerun()

with col3:
    if st.button("🗑️ Effacer"):
        st.session_state.tweets = []
        st.rerun()

st.caption("Editorial Agent IA v1.0 | Alimenté par FastAPI + Streamlit")
