# DataMorph 🏠

DataMorph est une API intelligente qui extrait automatiquement les données structurées depuis des documents immobiliers français (attestations de vente) en utilisant l'OCR et un LLM.

## 🚀 Stack Technique

- **FastAPI** — Framework API REST
- **Mistral AI** — OCR + LLM pour l'extraction des données
- **Pydantic** — Validation et structuration des données
- **Python 3.11**

## 📁 Structure du Projet

\```
datamorph/
├── app/
│   ├── main.py              # Endpoints FastAPI
│   ├── services/
│   │   ├── ocr_service.py   # PDF → texte via Mistral OCR
│   │   └── llm_service.py   # texte → JSON via Mistral LLM
│   └── models/
│       └── schemas.py       # Modèles Pydantic
├── .env                     # Clés API (non commité)
├── requirements.txt
└── README.md
\```

## ⚙️ Installation

\```bash
git clone https://github.com/Rajwen-Fakhfakh/datamorph
cd datamorph
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
\```

## 🔑 Configuration

Créer un fichier `.env` :
\```
MISTRAL_API_KEY=ta_clé_api
\```

## ▶️ Lancement

\```bash
uvicorn app.main:app --reload
\```

Accède à `http://localhost:8000/docs` pour tester l'API via Swagger UI.

## 📤 Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Vérifie que l'API tourne |
| POST | `/extract` | Upload PDF → retourne un JSON structuré |

## 📌 Version Actuelle

**v1.0 — MVP** : supporte uniquement les attestations de vente.
D'autres types de documents seront ajoutés dans les prochaines versions.