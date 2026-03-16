"""fix postgres sequences

Revision ID: 48d3d2412026
Revises: 25f8f7fd2026
Create Date: 2026-03-16 11:25:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "48d3d2412026"
down_revision: Union[str, Sequence[str], None] = "25f8f7fd2026"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "utilisateurs" in tables:
        op.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'utilisateurs'
                      AND column_name = 'id'
                      AND column_default IS NULL
                ) THEN
                    CREATE SEQUENCE IF NOT EXISTS utilisateurs_id_seq;
                    ALTER TABLE utilisateurs ALTER COLUMN id SET DEFAULT nextval('utilisateurs_id_seq');
                    PERFORM setval('utilisateurs_id_seq', COALESCE((SELECT MAX(id) FROM utilisateurs), 0) + 1, false);
                END IF;
            END $$;
            """
        )

    if "annonces" in tables:
        op.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'annonces'
                      AND column_name = 'id'
                      AND column_default IS NULL
                ) THEN
                    CREATE SEQUENCE IF NOT EXISTS annonces_id_seq;
                    ALTER TABLE annonces ALTER COLUMN id SET DEFAULT nextval('annonces_id_seq');
                    PERFORM setval('annonces_id_seq', COALESCE((SELECT MAX(id) FROM annonces), 0) + 1, false);
                END IF;
            END $$;
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "annonces" in tables:
        op.execute("ALTER TABLE annonces ALTER COLUMN id DROP DEFAULT")
    if "utilisateurs" in tables:
        op.execute("ALTER TABLE utilisateurs ALTER COLUMN id DROP DEFAULT")
