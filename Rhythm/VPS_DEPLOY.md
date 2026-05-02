# VPS Deployment Guide

How to move the Rhythm game backend from your local machine to a VPS so players can connect to it.

---

## What changes between local and VPS

| Thing | Local dev | VPS |
|---|---|---|
| Backend URL in Godot | `http://127.0.0.1:8000` | `http://<YOUR_VPS_IP>:8000` |
| Database host in `.env` | `localhost:5433` | `postgres:5432` (Docker internal) |
| `DEBUG` in `.env` | `True` | `False` |
| `SECRET_KEY` in `.env` | placeholder | strong random key |
| Godot build | debug (editor) | exported release build |

---

## 1. Prepare the VPS

You need a Linux VPS (Ubuntu 22.04 recommended). Run these once after getting SSH access:

```bash
# Update the system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose plugin (if not bundled)
sudo apt install -y docker-compose-plugin

# Verify
docker --version
docker compose version
```

---

## 2. Open the firewall

Port 8000 must be reachable from the internet so Godot clients can connect.

```bash
sudo ufw allow 22      # SSH — keep this or you'll lock yourself out
sudo ufw allow 8000    # Backend API
sudo ufw enable
```

> Port 5432 (PostgreSQL) does **not** need to be opened — it stays internal to Docker.

---

## 3. Upload the project

From your local machine, copy the project to the VPS:

```bash
# Replace user@YOUR_VPS_IP and the path as needed
scp -r "c:/Users/steph/OneDrive/Desktop/My personnal projects/Rhythm" user@YOUR_VPS_IP:~/rhythm
```

Or use Git if the project is in a repo:

```bash
git clone <your-repo-url> ~/rhythm
```

---

## 4. Configure the environment

SSH into the VPS, then edit `backend/.env`:

```bash
cd ~/rhythm
nano backend/.env
```

Set it to:

```env
DATABASE_URL=postgresql+asyncpg://prod_user:CHANGE_THIS_PASSWORD@postgres:5432/rhythm_prod
SECRET_KEY=GENERATE_THIS_WITH_COMMAND_BELOW
DEBUG=False
SHIELD_PRICE=100
PERFECT_HIT_FUNDS=15
GOOD_HIT_FUNDS=10
BAD_HIT_FUNDS=5
```

Generate a strong SECRET_KEY:

```bash
openssl rand -hex 32
```

Copy the output and paste it as the value of `SECRET_KEY`.

---

## 5. Update docker-compose.yml for production

The `docker-compose.yml` at the project root uses dev credentials. Update the `postgres` service to match the credentials you put in `.env`:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: rhythm_postgres
    environment:
      POSTGRES_USER: prod_user
      POSTGRES_PASSWORD: CHANGE_THIS_PASSWORD
      POSTGRES_DB: rhythm_prod
    volumes:
      - rhythm_pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U prod_user -d rhythm_prod"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - app-network

  backend:
    build: ./backend
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - app-network

volumes:
  rhythm_pg_data:

networks:
  app-network:
    driver: bridge
```

> The `nginx` service is not needed for a basic VPS test — remove it or leave it commented out.

---

## 6. Start the backend

```bash
cd ~/rhythm
docker compose up -d --build
```

Check it started correctly:

```bash
docker compose logs -f backend
```

You should see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test it from your local machine:

```bash
curl http://YOUR_VPS_IP:8000/health
# Expected: {"status":"ok"}
```

---

## 7. Update the Godot client

In `rhythm/scripts/network/api_client.gd`, replace `YOUR_VPS_IP` with the actual IP:

```gdscript
const BASE_URL_DEV  = "http://127.0.0.1:8000"
const BASE_URL_PROD = "http://YOUR_VPS_IP:8000"   # ← put the real IP here
const BASE_URL = BASE_URL_DEV if OS.is_debug_build() else BASE_URL_PROD
```

When you export the game in Godot (**Project → Export → Release**), it will automatically use `BASE_URL_PROD`. Running from the Godot editor still hits your local backend.

---

## 8. Keeping the backend running after logout

By default `docker compose up -d` keeps containers running. To also survive a VPS reboot, add a restart policy to the compose file:

```yaml
  backend:
    restart: unless-stopped

  postgres:
    restart: unless-stopped
```

Then run `docker compose up -d` again to apply.

---

## Quick command reference

```bash
# Start
docker compose up -d --build

# Stop
docker compose down

# View logs
docker compose logs -f backend

# Restart backend only (after a code change)
docker compose up -d --build backend

# Check running containers
docker compose ps
```

---

## Troubleshooting

**Godot gets no response / times out**
- Check `sudo ufw status` — port 8000 must show ALLOW
- Run `curl http://YOUR_VPS_IP:8000/health` from another machine to confirm the API is up
- Check `docker compose logs backend` for errors

**Database connection refused**
- Make sure the `DATABASE_URL` in `.env` uses `postgres` (the Docker service name) as the host, not `localhost`
- Check `docker compose ps` — the `postgres` container must be healthy before the backend starts

**Migrations failed on startup**
- Run manually: `docker compose exec backend alembic upgrade head`
- Check logs: `docker compose logs backend`

**Wrong password / auth errors after deploy**
- Passwords hashed locally won't work against a fresh production DB — users need to re-register
