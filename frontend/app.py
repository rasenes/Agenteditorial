from __future__ import annotations

from datetime import datetime

import requests
import streamlit as st

API_URL = "http://localhost:8000/api/v1"
THEMES = [
    "IA",
    "Tech",
    "Science",
    "Sport",
    "Politique",
    "Business",
    "Crypto",
    "Univers",
    "Culture",
    "Humour",
    "Faits surprenants",
    "Philosophie",
    "Futur",
]
STYLES = ["insight", "agressive", "ironique", "minimal", "story", "data"]


st.set_page_config(page_title="Editorial Agent", page_icon="EA", layout="wide")

st.markdown(
    """
<style>
:root {
  --bg: #0d1117;
  --card: #161b22;
  --stroke: #2a3240;
  --txt: #e6edf3;
  --muted: #95a0b5;
  --accent: #2f81f7;
  --ok: #2ea043;
}
.stApp { background: radial-gradient(1200px 500px at 10% -20%, #1f2a44, var(--bg)); color: var(--txt); }
.block-container { padding-top: 1rem; }
.ea-card {
  border: 1px solid var(--stroke);
  background: linear-gradient(180deg, #18202c, var(--card));
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 10px;
}
.ea-title { font-size: 26px; font-weight: 700; letter-spacing: .2px; }
.ea-sub { color: var(--muted); margin-top: -6px; }
.score-pill { color: white; background: var(--ok); border-radius: 999px; padding: 2px 10px; font-size: 12px; }
</style>
""",
    unsafe_allow_html=True,
)

if "trends" not in st.session_state:
    st.session_state.trends = []
if "result" not in st.session_state:
    st.session_state.result = None

st.markdown("<div class='ea-title'>Editorial Agent IA</div>", unsafe_allow_html=True)
st.markdown("<div class='ea-sub'>Tweets viraux pilotés par actualité mondiale + scoring multi-critères</div>", unsafe_allow_html=True)

left, right = st.columns([2, 1])

with right:
    st.markdown("### Paramètres")
    theme = st.selectbox("Thème", THEMES, index=0)
    style = st.selectbox("Style", STYLES, index=0)
    count = st.slider("Nombre de candidats", 3, 30, 9)
    language = st.selectbox("Langue source", ["fr", "en", "es", "de"], index=0)
    include_remix = st.checkbox("Activer remix viral", value=True)
    draft_mode = st.checkbox("Mode brouillon", value=False)

    if st.button("Analyser les tendances", use_container_width=True):
        try:
            response = requests.get(f"{API_URL}/trends/fetch", params={"limit": 30}, timeout=20)
            response.raise_for_status()
            st.session_state.trends = response.json().get("trends", [])
            st.success(f"{len(st.session_state.trends)} tendances chargées")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Erreur tendances: {exc}")

with left:
    trend_text = ""
    selected = None

    if st.session_state.trends:
        labels = [f"[{t['source']}] {t['title']}" for t in st.session_state.trends]
        picked = st.selectbox("Tendance détectée", labels)
        idx = labels.index(picked)
        selected = st.session_state.trends[idx]
        trend_text = selected["title"]

    trend_text = st.text_area("Sujet / actualité", value=trend_text, height=92)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Générer tweets", use_container_width=True):
            payload = {
                "trend_id": selected["id"] if selected else None,
                "trend_text": trend_text,
                "theme": theme,
                "style": style,
                "language": language,
                "count": count,
                "include_remix": include_remix,
                "draft_mode": draft_mode,
            }
            try:
                response = requests.post(f"{API_URL}/generate/", json=payload, timeout=60)
                response.raise_for_status()
                st.session_state.result = response.json()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Erreur génération: {exc}")

    with col_b:
        if st.button("A/B test", use_container_width=True):
            payload = {
                "theme": theme,
                "trend_text": trend_text,
                "variant_a_style": "insight",
                "variant_b_style": "ironique",
                "samples": 6,
            }
            try:
                response = requests.post(f"{API_URL}/generate/ab-test", json=payload, timeout=60)
                response.raise_for_status()
                ab = response.json()
                st.info(f"Winner: Variante {ab['winner']} | A={ab['variant_a_avg_score']} / B={ab['variant_b_avg_score']}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Erreur A/B test: {exc}")

if st.session_state.result:
    result = st.session_state.result
    st.markdown("### TOP 3")

    for idx, tweet in enumerate(result.get("top3", []), start=1):
        st.markdown("<div class='ea-card'>", unsafe_allow_html=True)
        st.markdown(f"**#{idx}** <span class='score-pill'>Score {tweet['score']}</span>", unsafe_allow_html=True)
        st.write(tweet["text"])
        b1, b2, b3 = st.columns([1, 1, 3])
        with b1:
            if st.button(f"Copier {idx}"):
                st.code(tweet["text"], language="text")
        with b2:
            if st.button(f"Favori {idx}"):
                try:
                    requests.post(f"{API_URL}/memory/favorite", json={"tweet_id": tweet["id"]}, timeout=8)
                    st.success("Ajouté")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Erreur favori: {exc}")
        with b3:
            st.caption(f"angle={tweet['angle']} | style={tweet['style']} | provider={tweet['provider_used']}")
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Tous les candidats + score détaillé"):
        for tweet in result.get("all_candidates", []):
            st.write(f"- {tweet['score']} | {tweet['text']}")

st.markdown("---")
st.markdown("### Analytics")
a1, a2, a3 = st.columns(3)

with a1:
    try:
        stats = requests.get(f"{API_URL}/memory/stats", timeout=8).json()
        st.metric("Tweets mémorisés", stats.get("tweets_count", 0))
        st.metric("Favoris", stats.get("favorites_count", 0))
    except Exception:
        st.metric("Tweets mémorisés", "-")

with a2:
    try:
        heatmap = requests.get(f"{API_URL}/memory/heatmap", timeout=8).json().get("items", [])
        st.write("Heatmap thèmes")
        for row in heatmap[:8]:
            st.write(f"{row['theme']}: {row['avg_score']} ({row['count']})")
    except Exception:
        st.write("Heatmap indisponible")

with a3:
    try:
        history = requests.get(f"{API_URL}/memory/history", params={"limit": 8}, timeout=8).json().get("items", [])
        st.write("Historique")
        for row in history:
            timestamp = datetime.fromtimestamp(row["created_at"]).strftime("%Y-%m-%d %H:%M")
            st.write(f"{timestamp} | {row['theme']} | top={row['top_score']}")
    except Exception:
        st.write("Historique indisponible")

ex1, ex2 = st.columns(2)
with ex1:
    if st.button("Exporter JSON", use_container_width=True):
        try:
            payload = requests.get(f"{API_URL}/memory/export/json", timeout=15).json()
            st.download_button("Télécharger JSON", data=str(payload), file_name="memory_export.json")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Export JSON impossible: {exc}")
with ex2:
    if st.button("Exporter CSV", use_container_width=True):
        try:
            path = requests.get(f"{API_URL}/admin/export/csv", timeout=15).json().get("path")
            st.success(f"CSV généré: {path}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Export CSV impossible: {exc}")
