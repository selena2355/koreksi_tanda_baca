"""add hasil koreksi html to riwayat

Revision ID: 7c8c1b2f4f6a
Revises: c1f4cbb2b2a4
Create Date: 2026-04-24 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c8c1b2f4f6a"
down_revision = "c1f4cbb2b2a4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "riwayat_koreksi",
        sa.Column("hasil_koreksi_html", sa.Text(), nullable=False, server_default=""),
    )
    op.alter_column("riwayat_koreksi", "hasil_koreksi_html", server_default=None)


def downgrade():
    op.drop_column("riwayat_koreksi", "hasil_koreksi_html")
