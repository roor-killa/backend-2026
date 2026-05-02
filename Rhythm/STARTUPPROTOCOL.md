# Rhythm Game — Startup Protocol

How to run the project from a fresh machine and from a daily restart.

---

## Prerequisites (install once)

- **Python 3.14+** — backend runtime
- **Docker Desktop** — provides PostgreSQL via container
- **Godot 4.5** — game engine

---

## First-time setup

Run these once after cloning the repo.

### 1. Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start PostgreSQL

```bash
cd backend
docker-compose up -d
```

This launches `rhythm_postgres` on **host port 5433** (not the default 5432, which may collide with other Postgres instances on your machine).

Verify it's healthy:

```bash
docker ps --filter name=rhythm_postgres
```

You should see `Up X minutes (healthy)`.

### 3. Apply database migrations

```bash
cd backend
alembic upgrade head
```

This creates the `users`, `scores`, and `purchases` tables. The initial migration is already checked in at `alembic/versions/` — do **not** run `alembic revision --autogenerate` on a fresh setup.

### 4. Start the API server

```bash
cd backend
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`. Confirm with:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 5. Open Godot

Open `rhythm/` as a Godot 4.5 project. Press **F5** to run.

Controls: arrow keys or WASD | **Esc** to pause.

---

## Daily startup

After a reboot or after closing things down. In **two separate terminals**:

**Terminal 1 — Database + API**
```bash
cd backend
docker-compose up -d            # bring DB back up
uvicorn app.main:app --reload   # start API on :8000
```

**Terminal 2 — Godot**
Open the Godot editor, load the `rhythm/` project, and press F5.

---

## Shutdown

```bash
cd backend
# Ctrl+C in the uvicorn terminal to stop the API
docker-compose down              # stop DB (data persists in named volume)
```

To wipe the database entirely:
```bash
docker-compose down -v           # -v also removes the volume
```

---

## Common issues

### "Port 5432 is already allocated" when running `docker-compose up`
Another Postgres is already on 5432 (a different project's container, or a local install). The compose file uses **5433** specifically to avoid this — if you still see this error, something else is already on 5433. Check with:

```bash
netstat -ano | grep ":5433"
```

### Backend logs `ConnectionRefusedError [WinError 1225]`
The API can't reach the DB. Causes, in order of likelihood:
1. The Postgres container isn't running — `docker ps` to check, `docker-compose up -d` to fix.
2. You edited `.env` while the server was running — `--reload` only watches `.py` files, so you must **stop and restart uvicorn** (Ctrl+C, then `uvicorn app.main:app --reload` again).

### Game shows "Error 0" or "Cannot reach server"
The Godot client can't reach `http://localhost:8000`. The API isn't running, or it crashed. Check the uvicorn terminal for traceback.

### Login returns 401 "Invalid username or password"
That username isn't in the DB, or the password is wrong. Click **Register** first to create the account.

To inspect the user list:
```bash
docker exec rhythm_postgres psql -U dev_user -d rhythm_dev -c "SELECT username, account_funds, shields_owned FROM users;"
```

### Orphan uvicorn process holds port 8000
Sometimes a previous server doesn't fully exit and `uvicorn` fails with `[Errno 10048] only one usage of each socket address`. Find the PID and force-kill it:

```bash
netstat -ano | grep ":8000"          # note the PID in the last column
taskkill.exe //PID <PID> //F          # force-kill it
```

(Use `//PID` and `//F` from Git Bash to avoid path-mangling. From `cmd.exe`, use `/PID` and `/F`.)

### `alembic` command not found
Use `python -m alembic upgrade head` instead — Python's script directory may not be on PATH.

---

## File reference

| Path | Purpose |
|------|---------|
| `backend/.env` | DATABASE_URL and game-balance settings |
| `backend/docker-compose.yml` | PostgreSQL container definition (port 5433) |
| `backend/alembic/versions/` | Database migration scripts |
| `backend/app/main.py` | FastAPI app entry point |
| `rhythm/project.godot` | Godot project root |
| `rhythm/scripts/network/api_client.gd` | HTTP client (BASE_URL = `http://localhost:8000`) |
