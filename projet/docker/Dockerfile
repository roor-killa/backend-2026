FROM python:3.12-slim

# Installer Chrome (requis pour Selenium/Cloudflare bypass)
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl \
    chromium chromium-driver \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer les dossiers de données
RUN mkdir -p data/raw data/processed data/cache

# Variable d'environnement pour que webdriver-manager utilise Chromium déjà installé
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

ENTRYPOINT ["python", "main.py"]
