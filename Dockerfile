# Image de base légère avec Python 3.11 (même version que la CI et le dev local)
FROM python:3.11-slim

WORKDIR /app

# On copie d'abord uniquement requirements.txt : Docker met en cache cette étape
# tant que ce fichier ne change pas, donc les rebuilds sont plus rapides si seul
# le code applicatif change (pas les dépendances).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Puis on copie le reste du code
COPY app/ ./app/

# Render fournit dynamiquement le port à écouter via la variable d'env PORT
# (10000 par défaut) : uvicorn doit s'y adapter, pas utiliser un port fixe.
# 8080 n'est que la valeur par défaut en local.
ENV PORT=8080
EXPOSE 8080

CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}