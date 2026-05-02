"""
Startup script for the Rhythm game backend.

Follows the steps in STARTUPPROTOCOL.md:
  1. Ensure docker-compose.yml exists (copies from example if missing)
  2. Ensure backend/.env exists (writes dev defaults if missing)
  3. Start the PostgreSQL container
  4. Wait for it to become healthy
  5. Apply database migrations
  6. Launch uvicorn (blocks until Ctrl+C)
"""

import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
COMPOSE_FILE = os.path.join(ROOT, "docker-compose.yml")
COMPOSE_EXAMPLE = os.path.join(ROOT, "docker-compose_example.yml")
ENV_FILE = os.path.join(BACKEND, ".env")
ENV_EXAMPLE = os.path.join(BACKEND, ".env_example")
CONTAINER = "rhythm_postgres"


def step(msg: str) -> None:
    print(f"\n>>> {msg}")


def run(args: list[str], cwd: str | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, check=check)


def ensure_compose_file() -> None:
    if os.path.exists(COMPOSE_FILE):
        return
    if not os.path.exists(COMPOSE_EXAMPLE):
        print("ERROR: docker-compose_example.yml not found. Cannot proceed.")
        sys.exit(1)
    shutil.copy(COMPOSE_EXAMPLE, COMPOSE_FILE)
    print(f"  Created docker-compose.yml from example.")


def ensure_env_file() -> None:
    if os.path.exists(ENV_FILE):
        return
    # Write dev-local defaults (localhost:5433, not the Docker-network hostname)
    dev_env = (
        "DATABASE_URL=postgresql+asyncpg://dev_user:dev_pass@localhost:5433/rhythm_dev\n"
        "SECRET_KEY=change-me-generate-with-openssl-rand-hex-32\n"
        "DEBUG=True\n"
        "SHIELD_PRICE=100\n"
        "PERFECT_HIT_FUNDS=15\n"
        "GOOD_HIT_FUNDS=10\n"
        "BAD_HIT_FUNDS=5\n"
    )
    with open(ENV_FILE, "w") as f:
        f.write(dev_env)
    print("  Created backend/.env with local-dev defaults.")
    print("  NOTE: Update SECRET_KEY before any production use.")


def start_postgres() -> None:
    result = subprocess.run(
        ["docker", "inspect", "--format={{.State.Running}}", CONTAINER],
        capture_output=True, text=True
    )
    if result.returncode == 0 and result.stdout.strip() == "true":
        print(f"  {CONTAINER} is already running.")
        return
    run(["docker-compose", "up", "-d", "postgres"], cwd=ROOT)


def wait_for_healthy(timeout: int = 60) -> None:
    print(f"  Waiting for {CONTAINER} to become healthy (up to {timeout}s)...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = subprocess.run(
            ["docker", "inspect", "--format={{.State.Health.Status}}", CONTAINER],
            capture_output=True, text=True
        )
        status = result.stdout.strip()
        if status == "healthy":
            print(f"  {CONTAINER} is healthy.")
            return
        if status not in ("starting", ""):
            print(f"  WARNING: unexpected health status '{status}' — continuing anyway.")
            return
        time.sleep(2)
    print(f"  ERROR: {CONTAINER} did not become healthy within {timeout}s.")
    print("  Check 'docker ps' and 'docker logs rhythm_postgres' for details.")
    sys.exit(1)


def apply_migrations() -> None:
    # Prefer python -m alembic to avoid PATH issues on Windows
    python = sys.executable
    result = subprocess.run(
        [python, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND, capture_output=True, text=True
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        print(result.stderr.rstrip())
        print("  ERROR: Migration failed. Fix the error above and re-run.")
        sys.exit(1)
    print("  Migrations applied.")


def launch_uvicorn() -> None:
    print("\n" + "=" * 60)
    print("  Backend running at http://localhost:8000")
    print("  Press Ctrl+C to stop.")
    print("=" * 60 + "\n")
    python = sys.executable
    try:
        subprocess.run(
            [python, "-m", "uvicorn", "app.main:app", "--reload"],
            cwd=BACKEND
        )
    except KeyboardInterrupt:
        print("\nShutting down.")


def main() -> None:
    step("Checking docker-compose.yml")
    ensure_compose_file()

    step("Checking backend/.env")
    ensure_env_file()

    step("Starting PostgreSQL container")
    start_postgres()

    step("Waiting for database to be ready")
    wait_for_healthy()

    step("Applying database migrations")
    apply_migrations()

    step("Launching API server")
    launch_uvicorn()


if __name__ == "__main__":
    main()
