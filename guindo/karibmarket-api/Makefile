.PHONY: start stop logs migrate seed shell build restart

start:
	docker compose up -d
	@echo "✅ KaribMarket API démarrée sur http://localhost:8000/docs"

stop:
	docker compose down

restart:
	docker compose down
	docker compose up -d

logs:
	docker compose logs -f api

migrate:
	docker compose exec api alembic upgrade head
	@echo "✅ Migrations appliquées"

seed:
	docker compose exec api python scripts/seed.py
	@echo "✅ Base de données peuplée"

shell:
	docker compose exec api bash

build:
	docker compose build --no-cache
	@echo "✅ Image reconstruite"

status:
	docker compose ps