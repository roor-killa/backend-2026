# Rhythm Game — Project Progress

## Phase 1: Backend Foundation
- [x] Set up FastAPI project structure (all folders + `__init__.py` files)
- [x] Create `config.py` with Pydantic settings and `.env` file
- [x] Create `database.py` with async engine and connection pooling
- [x] Define SQLAlchemy ORM models: `User`, `Score`, `Purchase`
- [x] Configure Alembic (`alembic.ini` + async `env.py` + `script.py.mako`)
- [x] Create Pydantic v2 schemas for all domains
- [x] Install dependencies (`pip install -r requirements.txt`) — bumped versions for Python 3.14 compatibility
- [x] Set up local PostgreSQL database via `docker-compose up -d`
- [x] Run initial migration (`alembic revision --autogenerate -m "initial schema"`)
- [x] Apply migration (`alembic upgrade head`) — `users`, `scores`, `purchases` tables created

## Phase 2: Core Services
- [x] `UserService`: register, login, get_user, update_funds, update_shields
- [x] `ScoreService`: submit_score (atomic), get_leaderboard, get_user_best_score, get_user_score_history
- [x] `ShopService`: purchase_shields (atomic), get_shop_items, get_purchase_history
- [x] `security.py`: bcrypt password hashing + JWT token helpers
- [x] `exceptions.py`: custom exception types
- [ ] Write unit tests for each service (real DB, no mocks)

## Phase 3: API Endpoints
- [x] `POST /users/register` — create account
- [x] `POST /users/login` — authenticate
- [x] `GET /users/{user_id}` — get profile
- [x] `GET /users/{user_id}/best-score` — personal best
- [x] `POST /scores` — submit score + update funds atomically
- [x] `GET /leaderboard` — top N scores with usernames
- [x] `GET /shop/items` — list shop items
- [x] `POST /shop/purchase` — buy shields
- [x] Exception handlers wired in `main.py`
- [x] CORS middleware configured
- [x] Manual endpoint testing — verified `/health`, `POST /users/register` (returns 201 with user payload incl. bcrypt hash persisted)

## Phase 4: Godot Core Gameplay
- [x] `game_manager.gd` — score/funds/shields tracking, timing windows
- [x] `note.gd` — note movement, direction colors, group registration
- [x] `note_spawner.gd` — timed note spawning from screen edges
- [x] `hit_detector.gd` — input handling and proximity-based hit detection
- [x] `game.gd` — game scene root: HUD updates, pause toggle, game-over handler
- [x] `circle_visual.gd` — draws center circle with 4 colored sections
- [x] `game.tscn` — game scene with circle, spawner, detector, HUD, pause menu
- [x] `note.tscn` — Area2D + ColorRect + CollisionShape2D
- [x] Autoloads wired in `project.godot` (GameManager, UserSession, ApiClient)
- [x] Input actions registered (move_up/down/left/right = WASD)
- [ ] Test local gameplay loop (open project in Godot editor)

## Phase 5: Integration
- [x] `api_client.gd` — HTTPRequest wrapper for all backend endpoints
- [x] `user_session.gd` — global session singleton
- [x] `login.tscn` — dedicated login/register screen
- [x] `main_menu.tscn` — post-login home screen
- [x] `music_select.tscn` — song selection screen before gameplay
- [x] Login/register buttons connected to `ApiClient`
- [x] End-of-game submits score via `ApiClient.submit_score()`
- [x] Leaderboard scene fetches from `GET /leaderboard`
- [ ] Full loop test: login → play → submit score → view leaderboard

## Phase 6: Shop & Shields
- [x] `shop.gd` — UI logic for viewing funds/shields and buying
- [x] `shop.tscn` — shop scene with quantity input and buy button
- [x] Shield purchase wired to `ApiClient.purchase_shields()`
- [x] Shield consumption in gameplay (activation spends one owned shield; miss uses active shield or triggers game-over)
- [ ] Test economy loop: earn funds → buy shields → use in game

## Phase 7: Menus & Polish
- [x] `login.tscn` — login/register screen
- [x] `main_menu.tscn` — post-login home screen
- [x] `music_select.tscn` — song selection screen
- [x] `game.tscn` — gameplay with HUD (score/funds/shields/timing feedback)
- [x] `leaderboard.tscn` — scrollable top-score list
- [x] `shop.tscn` — funds display and purchase flow
- [x] `pause_menu.tscn` — resume/restart/main-menu/quit (Escape to toggle)
- [x] `quit_dialog.tscn` — confirm before exiting

---

## To Run the Game

### Backend Setup (one-time)
```bash
cd backend
pip install -r requirements.txt
# Start PostgreSQL via Docker (creds match the .env file):
docker-compose up -d
# Apply migrations (initial migration already in alembic/versions/):
alembic upgrade head
uvicorn app.main:app --reload
```

### Daily startup
```bash
cd backend
docker-compose up -d           # bring DB back up
uvicorn app.main:app --reload  # start API on :8000
```

### Godot
Open `rhythm/` folder as a Godot 4.5 project. Press F5 to run.

Controls: Arrow keys or WASD | Escape = pause

---

## Bugs / Known Issues
- `passlib 1.7.4` is incompatible with `bcrypt >= 5.0` on Python 3.14 (raises `ValueError: password cannot be longer than 72 bytes` from a backend probe). Replaced `passlib` with direct `bcrypt.hashpw` / `bcrypt.checkpw` calls in `app/utils/security.py`; removed `passlib` from `requirements.txt`.
- The original pinned versions in `requirements.txt` (e.g. `pydantic-core==2.18.2`, `asyncpg==0.30.0`) had no Python 3.14 wheels and failed to build from source. Loosened pins to `>=` minimum versions; `asyncpg>=0.31.0` is the first version with cp314 wheels.
- Alembic's `script.py.mako` template was missing from the repo — autogenerate would create the migration metadata but fail when writing the file. Added the standard template at `backend/alembic/script.py.mako`.

## Notes
- Backend is fully running end-to-end against a real PostgreSQL DB. Verified a fresh user registers successfully (bcrypt-hashed password persisted, 201 response with user payload).
- PostgreSQL is provided via `backend/docker-compose.yml` (image `postgres:16-alpine`, exposed on `localhost:5432`, named volume `rhythm_pg_data` for persistence).
- All Godot scenes and scripts are wired; open in Godot editor to test the gameplay loop.
- Initial Alembic migration is checked in at `alembic/versions/` — no `--autogenerate` step needed on fresh setup.
