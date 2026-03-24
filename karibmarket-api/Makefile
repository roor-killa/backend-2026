.PHONY: help up down build logs shell migrate restart

help:
	@echo "Commandes disponibles :"
	@echo "  make up        — Démarre tous les services (build si nécessaire)"
	@echo "  make down      — Arrête et supprime les conteneurs"
	@echo "  make build     — Reconstruit les images Docker"
	@echo "  make logs      — Affiche les logs en temps réel"
	@echo "  make shell     — Ouvre un shell dans le conteneur API"
	@echo "  make migrate   — Applique les migrations Alembic"
	@echo "  make restart   — Redémarre l'API"

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

shell:
	docker compose exec api bash

migrate:
	docker compose exec api alembic upgrade head

restart:
	docker compose restart api
