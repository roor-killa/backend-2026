# backend-2026 — KaribMarket API

API FastAPI du projet fil rouge L2 — Université des Antilles.

Ce dépôt est le **moteur central** de l'architecture multi-projets : il orchestre le scraper POO-2026 et expose les données au frontend Web3-2026.

---

## Architecture globale

```
kiprix.com
    │
    │  Selenium / BeautifulSoup
    ▼
groupe_scp2  (poo-2026)          ← scraper Python CLI
    │
    │  INSERT INTO produits
    ▼
kiprix_db  (PostgreSQL :5433)    ← base partagée
    │
    │  SQLAlchemy ORM
    ▼
karibmarket-api  (ce projet)     ← FastAPI :8000
    │   ↑
    │   └── lance groupe_scp2 en subprocess
    │
    │  HTTP REST  /api/v1/prix  /api/v1/admin/scrape*
    ▼
Next.js frontend  (web3-2026)    ← :3000
```

---

## Projets liés

| Projet | Rôle | Lien |
|--------|------|------|
| **poo-2026 / groupe_scp2** | Scraper kiprix.com → `kiprix_db` | Lancé en subprocess par ce projet |
| **web3-2026 / frontend-nextjs** | Dashboard et visualisation des prix | Consomme ce projet via `lib/fastapi.ts` |

---

## Contenu du dépôt

```
backend-2026/
└── guindo/
    └── karibmarket-api/    # API FastAPI — voir README dédié
```

Voir le [README complet de l'API](./guindo/karibmarket-api/README.md) pour l'installation, les endpoints et la configuration.
