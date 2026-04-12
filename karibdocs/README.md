

Pour lancer l'application

Installer les packages requis -> python -m pip install -r requirements.txt
Juste lancer le docker : docker compose up -d

Pour utiliser le chatbot en local avec Ollama:

1. Installer Ollama: https://ollama.com
2. Démarrer le service Ollama sur la machine hote
3. Recuperer un modele: ollama pull llama3.1
4. Garder OLLAMA_BASE_URL=http://host.docker.internal:11434 dans le .env si l'API tourne dans Docker

Configuration LLM du backend (`.env`):

- `LLM_PROVIDER=ollama` (par defaut) ou `LLM_PROVIDER=mistral`
- `LLM_TEMPERATURE=0.1`
- Si `ollama`:
	- `OLLAMA_BASE_URL=http://host.docker.internal:11434`
	- `OLLAMA_MODEL=ollama pull qwen2.5:3b`
- Si `mistral`:
	- `MISTRAL_API_KEY=...`
	- `MISTRAL_MODEL=mistral-small-latest`

Configuration embeddings RAG (`.env`):

- `EMBEDDING_PROVIDER=huggingface` (defaut) ou `EMBEDDING_PROVIDER=ollama`
- Si `ollama`:
	- `OLLAMA_BASE_URL=http://host.docker.internal:11434`
	- `OLLAMA_EMBEDDING_MODEL=nomic-embed-text`
	- Recuperer le modele une fois: `ollama pull nomic-embed-text`

Route chatbot backend:

- `POST /chat/ask`
	- Authentification Bearer requise
	- Corps: `{"question": "...", "session_id": null}`
- `GET /chat/sessions`
- `GET /chat/sessions/{session_id}/messages`

Route ajoutee pour le frontend interface-scrapping:

- POST /scraping/rci?max_depth=1&max_pages=10&delay=1.5
	- Authentification requise (Bearer token)
	- Lance un scraping RCI a la demande
	- Retourne les articles collectes dans `items`




