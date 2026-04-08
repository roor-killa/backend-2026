

Pour lancer l'application

Installer les packages requis -> python -m pip install -r requirements.txt
Juste lancer le docker : docker compose up -d

Pour utiliser le chatbot en local avec Ollama:

1. Installer Ollama: https://ollama.com
2. Démarrer le service Ollama sur la machine hote
3. Recuperer un modele: ollama pull llama3.1
4. Garder OLLAMA_BASE_URL=http://host.docker.internal:11434 dans le .env si l'API tourne dans Docker

Route ajoutee pour le frontend interface-scrapping:

- POST /scraping/rci?max_depth=1&max_pages=10&delay=1.5
	- Authentification requise (Bearer token)
	- Lance un scraping RCI a la demande
	- Retourne les articles collectes dans `items`