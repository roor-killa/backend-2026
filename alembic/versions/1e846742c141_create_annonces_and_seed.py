"""create annonces and seed

Revision ID: 1e846742c141
Revises: 0a3c3439d999
Create Date: 2026-03-11 14:18:58.444719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


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
            id INTEGER NOT NULL PRIMARY KEY,
            titre VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            prix FLOAT NOT NULL,
            commune VARCHAR(100) NOT NULL,
            categorie VARCHAR(20) NOT NULL,
            actif BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP,
            proprietaire_id INTEGER NOT NULL,
            FOREIGN KEY(proprietaire_id) REFERENCES users(id)
        )
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_annonces_id ON annonces (id)")

    op.execute(
        """
        INSERT INTO annonces
            (id, titre, description, prix, commune, categorie, actif, created_at, updated_at, proprietaire_id)
        VALUES
            (
                1,
                'Vente mangues Julie bio',
                'Mangues fraichement recoltees, lot de 5 kg.',
                3.5,
                'Le Lamentin',
                'alimentaire',
                    TRUE,
                CURRENT_TIMESTAMP,
                NULL,
                1
            ),
            (
                2,
                'Cours de yoga face a la mer',
                'Seance collective de 60 minutes sur la plage.',
                25.0,
                'Sainte-Anne',
                'services',
                    TRUE,
                CURRENT_TIMESTAMP,
                NULL,
                1
            ),
            (
                3,
                'Scooter 125cc occasion',
                'Scooter en bon etat, entretien a jour.',
                1600.0,
                'Fort-de-France',
                'vehicules',
                    TRUE,
                CURRENT_TIMESTAMP,
                NULL,
                2
            )
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS annonces")
