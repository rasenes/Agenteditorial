# Editorial Agent IA

Agent IA professionnel pour générer des tweets viraux à partir de l'actualité mondiale.

## 🚀 Démarrage Rapide

### Installation

```bash
# Cloner le repo
git clone <repo-url>
cd agent-editorial

# Installer les dépendances
pip install -r requirements.txt

# Configurer Ollama (local)
# https://ollama.ai - installer et lancer : ollama serve

# Copier la config
cp settings.yaml.example settings.yaml
```

### Lancer l'application

**Backend (FastAPI)**:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Streamlit)**:
```bash
cd frontend
streamlit run app.py
```

Accédez à:
- 🎨 UI: http://localhost:8501
- 📚 API Docs: http://localhost:8000/docs

## 🏗️ Architecture

```
backend/
    ├── main.py                 # FastAPI app
    ├── core/                   # Modules core (config, logger, cache, utils)
    ├── models/                 # Modèles de données
    ├── providers/              # Clients LLM (Ollama, OpenAI, Groq)
    ├── agent/                  # Pipeline IA
    │   ├── orchestrator.py      # Orchestrateur principal
    │   ├── generator.py         # Générateur de tweets
    │   ├── scoring.py           # Scoring avancé
    │   ├── remix_engine.py      # Remixes (court, agressif, etc.)
    │   ├── memory_engine.py     # Mémoire persistante
    │   ├── trend_analyzer.py    # Analyse des tendances
    │   ├── translator.py        # Traduction multilingue
    │   └── sources.py           # Sources de tendances
    └── api/                    # Routes FastAPI

frontend/
    └── app.py                  # Streamlit dashboard
```

## 🎯 Fonctionnalités

### ✍️ Agent Editorial
- ✅ Génération de tweets multi-styles (normal, agressif, humoristique, minimal, data)
- ✅ Analyse d'angles viraux automatique
- ✅ Support multi-thèmes (IA, Tech, Science, Sport, etc.)

### 📊 Moteur de Scoring
- ✅ Score sur 7 dimensions (longueur, clarté, émotion, miroir, punchline, contradiction, viral)
- ✅ Tri automatique TOP 3
- ✅ Détail complet du scoring

### 🔁 Remix Viral Engine
- ✅ Version ultra-courte (< 100 chars)
- ✅ Version agressive et provocante
- ✅ Version ironique et spirituelle
- ✅ Version sous forme de question
- ✅ Version avec stats/chiffres
- ✅ Version avec hook accrocheur

### 🌍 Sources Multi-Langue
- ✅ RSS globaux (HackerNews, TechCrunch, TheVerge)
- ✅ Reddit trending
- ✅ NewsAPI
- ✅ Support: Anglais, Français, Espagnol, Allemand
- ✅ Traduction automatique vers FR

### 🧠 Mémoire Intelligente
- ✅ Stockage des tweets performants
- ✅ Évite la redondance (fuzzy matching)
- ✅ Apprentissage des styles efficaces par thème
- ✅ Persistance en JSON

### 🤖 Multi-LLM Router
- ✅ Priorité Ollama (local & rapide)
- ✅ Fallback automatique OpenAI / Groq
- ✅ Retry avec backoff exponentiel
- ✅ Timeout protection

### ⚡ Performance
- ✅ Cache mémoire TTL
- ✅ Requêtes async
- ✅ Génération parallèle
- ✅ Timeout protection

### 🎨 UI Streamlit
- Minimal et moderne
- Dark mode
- Affichage des scores
- Actions: Copier, Favoris, Export JSON/CSV
- Gestion des tendances

## 📖 API Endpoints

### Generation
- `POST /api/v1/generate/` - Générer des tweets
- `POST /api/v1/generate/batch` - Génération batch
- `POST /api/v1/generate/score` - Scorer des tweets

### Trends
- `GET /api/v1/trends/fetch` - Récupérer tendances
- `GET /api/v1/trends/analyze/{id}` - Analyser une tendance

### Memory
- `GET /api/v1/memory/stats` - Stats mémoire
- `GET /api/v1/memory/tweets` - Tweets mémorisés
- `POST /api/v1/memory/clear` - Vider la mémoire

### Admin
- `POST /api/v1/admin/pipeline` - Lancer le pipeline complet
- `GET /api/v1/admin/status` - Status du système

## 🔧 Configuration

Éditer `settings.yaml`:

```yaml
llm:
  provider: "ollama"  # ou "openai", "groq"
  model: "mistral"

sources:
  rss_feeds:
    - "https://..."
  newsapi_key: "YOUR_KEY"
```

Variables d'environnement:
```bash
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export OPENAI_API_KEY=sk-...
export GROQ_API_KEY=gsk-...
```

## 📊 Utilisation Avancée

### Pipeline Complet (async)
```python
from backend.agent.orchestrator import orchestrator

await orchestrator.initialize()
result = await orchestrator.full_pipeline(
    num_trends=5,
    tweets_per_trend=3,
    create_remixes=True,
)
```

### Générer pour une tendance
```python
from backend.models.tweet import Trend, GenerationRequest
from backend.agent.generator import generator

trend = Trend(
    title="IA Générative",
    description="Nouvelles capacités des modèles..."
)

request = GenerationRequest(
    trend=trend,
    theme="IA",
    count=5,
    style="aggressive"
)

response = await generator.generate(request)
```

### Scorer des tweets
```python
from backend.agent.scoring import scorer

tweets = [...]
scored = scorer.sort_tweets(tweets)
top_3 = scorer.get_top(tweets, n=3)
```

## 🎓 Best Practices

### Pour des tweets viraux
1. ✅ Utiliser le style "aggressive" pour débat
2. ✅ Créer des remixes (formats variés)
3. ✅ Analyser les angles avant génération
4. ✅ Affiner le thème (plus précis = meilleur)
5. ✅ Utiliser l'effet miroir (vous, on, nous)

### Performance
- Limiter à 5 tendances max par pipeline
- Cache activé pour sources RSS
- Parallel generation à max 3 concurrent
- Memory size limité à 10k tweets

## 🚀 Déploiement Production

### Docker
```bash
docker build -t editorial-agent .
docker run -p 8000:8000 -p 8501:8501 editorial-agent
```

### Scaling
- Backend: Déployer sur Gunicorn/hypercorn
- Frontend: Déployer sur Streamlit Cloud
- LLM: Utiliser OpenAI/Groq pour scalabilité
- Cache: Utiliser Redis pour distribué

## 📝 Roadmap

- [ ] Auto-post sur Twitter/X
- [ ] A/B testing tweets
- [ ] Heatmap des thèmes performants
- [ ] Historique avec graphiques
- [ ] Mode brouillon et scheduling
- [ ] Multi-comptes support
- [ ] SaaS API publique

## 📄 License

MIT - Libre d'utilisation

## 👥 Support

Issues: GitHub Issues
Email: support@editorial-agent.io
