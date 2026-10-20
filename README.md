# DataMorph 🏠

DataMorph est une API intelligente qui extrait automatiquement les données structurées depuis des documents immobiliers français (attestations de vente) en utilisant l'OCR et un LLM.

## 🚀 Stack Technique

- **FastAPI** — Framework API REST
- **Google Gemini** — lecture du PDF (OCR) + LLM pour l'extraction des données
- **Pydantic** — Validation et structuration des données
- **Python 3.11**

## 📁 Structure du Projet

```
datamorph/
├── app/
│   ├── main.py          # Endpoints FastAPI
│   ├── services/
│   │   ├── gemini_client.py # Client Gemini partagé (clé API + modèle)
│   │   ├── ocr_service.py   # PDF → texte via Gemini
│   │   └── llm_service.py   # texte → JSON via Gemini
│   └── models/
│       └── schemas.py   # Modèles Pydantic
├── .env                  # Clés API (non commité)
├── requirements.txt
└── README.md
```

## ⚙️ Installation

```bash
git clone https://github.com/Rajwen-Fakhfakh/datamorph
cd datamorph
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## 🔑 Configuration

Créer un fichier `.env` :
```
GEMINI_API_KEY=ta_clé_api
# Optionnel (défaut : gemini-3.8-flash)
GEMINI_MODEL=gemini-3.8-flash
```

Une clé gratuite s'obtient sur [Google AI Studio](https://aistudio.google.com/apikey).

> 💡 Les quotas du plan gratuit varient selon le modèle. Si l'API répond lentement ou renvoie une erreur 429, essaie un modèle plus léger (ex : `GEMINI_MODEL=gemini-3.5-flash-lite`). Si un modèle n'est plus disponible (erreur 404), consulte la liste à jour dans Google AI Studio.

## ▶️ Lancement

```bash
uvicorn app.main:app --reload
```

Accède à `http://localhost:8000/docs` pour tester l'API via Swagger UI.

## 📤 Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/Health` | Vérifie que l'API tourne |
| POST | `/extract` | Upload PDF(exemple_attestation_vente.pdf) → retourne un JSON structuré |

## 📌 Version Actuelle

**v1.0 — MVP** : supporte uniquement les attestations de vente.
D'autres types de documents seront ajoutés dans les prochaines versions.
