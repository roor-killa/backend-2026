"""rename users to utilisateurs

Revision ID: 25f8f7fd2026
Revises: 1e846742c141
Create Date: 2026-03-16 11:10:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "25f8f7fd2026"
down_revision: Union[str, Sequence[str], None] = "1e846742c141"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "users" in tables and "utilisateurs" not in tables:
        op.rename_table("users", "utilisateurs")
        op.execute("ALTER INDEX IF EXISTS ix_users_id RENAME TO ix_utilisateurs_id")
        op.execute("ALTER INDEX IF EXISTS ix_users_email RENAME TO ix_utilisateurs_email")

    tables = set(sa.inspect(bind).get_table_names())
    if "utilisateurs" in tables:
        columns = {col["name"] for col in sa.inspect(bind).get_columns("utilisateurs")}
        if "mot_de_passe" in columns and "hashed_password" not in columns:
            with op.batch_alter_table("utilisateurs") as batch_op:
                batch_op.alter_column("mot_de_passe", new_column_name="hashed_password")

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
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "utilisateurs" in tables:
        columns = {col["name"] for col in inspector.get_columns("utilisateurs")}
        if "hashed_password" in columns and "mot_de_passe" not in columns:
            with op.batch_alter_table("utilisateurs") as batch_op:
                batch_op.alter_column("hashed_password", new_column_name="mot_de_passe")

    tables = set(sa.inspect(bind).get_table_names())
    if "utilisateurs" in tables and "users" not in tables:
        op.rename_table("utilisateurs", "users")
        op.execute("ALTER INDEX IF EXISTS ix_utilisateurs_id RENAME TO ix_users_id")
        op.execute("ALTER INDEX IF EXISTS ix_utilisateurs_email RENAME TO ix_users_email")
