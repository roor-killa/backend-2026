"""create utilisateurs

Revision ID: 0a3c3439d999
Revises: 
Create Date: 2026-03-11 14:03:35.264447

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0a3c3439d999'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id SERIAL PRIMARY KEY,
            nom VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            telephone VARCHAR(13),
            hashed_password VARCHAR(255) NOT NULL,
            actif BOOLEAN NOT NULL DEFAULT TRUE
        )
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_utilisateurs_id ON utilisateurs (id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_utilisateurs_email ON utilisateurs (email)")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS utilisateurs")
