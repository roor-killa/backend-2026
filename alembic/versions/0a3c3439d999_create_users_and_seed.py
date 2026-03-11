"""create users and seed

Revision ID: 0a3c3439d999
Revises: 
Create Date: 2026-03-11 14:03:35.264447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a3c3439d999'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER NOT NULL PRIMARY KEY,
            nom VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            telephone VARCHAR(13),
            mot_de_passe VARCHAR(255) NOT NULL,
            actif BOOLEAN NOT NULL DEFAULT TRUE
        )
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)")

    op.execute(
        """
        INSERT INTO users (id, nom, email, telephone, mot_de_passe, actif)
        VALUES
            (1, 'Marie Louise', 'marie@example.com', '+596696123456', 'MotDePasseDemo', TRUE),
            (2, 'Jean-Pierre', 'jeanpierre@example.com', '+596696654321', 'MotDePasseDemo', TRUE)
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS users")
