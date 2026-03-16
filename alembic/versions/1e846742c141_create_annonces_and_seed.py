"""create annonces

Revision ID: 1e846742c141
Revises: 0a3c3439d999
Create Date: 2026-03-11 14:18:58.444719

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1e846742c141'
down_revision: Union[str, Sequence[str], None] = '0a3c3439d999'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS annonces (
            id SERIAL PRIMARY KEY,
            titre VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            prix FLOAT NOT NULL,
            commune VARCHAR(100) NOT NULL,
            categorie VARCHAR(20) NOT NULL,
            actif BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP,
            proprietaire_id INTEGER NOT NULL,
            FOREIGN KEY(proprietaire_id) REFERENCES utilisateurs(id)
        )
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_annonces_id ON annonces (id)")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS annonces")
