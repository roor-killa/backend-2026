"""create produits kiprix

Revision ID: 5c1e8a222026
Revises: 48d3d2412026
Create Date: 2026-03-18 10:30:00

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "5c1e8a222026"
down_revision: Union[str, Sequence[str], None] = "48d3d2412026"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS produits_kiprix (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url TEXT NOT NULL,
            price_france VARCHAR(50),
            price_dom VARCHAR(50),
            difference VARCHAR(50),
            quantity_value FLOAT,
            quantity_unit VARCHAR(20),
            unit_reference VARCHAR(20),
            unit_price_france FLOAT,
            unit_price_dom FLOAT,
            territory VARCHAR(10) NOT NULL,
            territory_name VARCHAR(100),
            scraped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_produits_kiprix_id ON produits_kiprix (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_produits_kiprix_name ON produits_kiprix (name)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_produits_kiprix_territory ON produits_kiprix (territory)")
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_produits_kiprix_url_territory
        ON produits_kiprix (url, territory)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS produits_kiprix")
