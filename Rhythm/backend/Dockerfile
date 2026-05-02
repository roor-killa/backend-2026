FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Lancer les migrations puis démarrer le serveur
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000