"""Single entrypoint to run all test defs from the tests package.

Usage:
    python -m pytest -q tests/test_everything.py
"""

# Re-export tests so pytest can collect everything from one file.
# Support both direct pytest runs and package-relative imports.
try:
    from .test_auth_service import *  # type: ignore[F401,F403]
    from .test_document_service import *  # type: ignore[F401,F403]
    from .test_drive_routes import *  # type: ignore[F401,F403]
    from .test_scraping_routes import *  # type: ignore[F401,F403]
    from .test_chatbot_routes import *  # type: ignore[F401,F403]
except ImportError:
    from test_auth_service import *  # type: ignore[F401,F403]
    from test_document_service import *  # type: ignore[F401,F403]
    from test_drive_routes import *  # type: ignore[F401,F403]
    from test_scraping_routes import *  # type: ignore[F401,F403]
    from test_chatbot_routes import *  # type: ignore[F401,F403]
