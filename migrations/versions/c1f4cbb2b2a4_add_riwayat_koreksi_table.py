"""add riwayat koreksi table

Revision ID: c1f4cbb2b2a4
Revises: 5b9a46656636
Create Date: 2026-03-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1f4cbb2b2a4"
down_revision = "5b9a46656636"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "riwayat_koreksi",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pengguna_id", sa.Integer(), nullable=False),
        sa.Column("result_token", sa.String(length=64), nullable=False),
        sa.Column("nama_dokumen", sa.String(length=255), nullable=False),
        sa.Column("teks_dokumen", sa.Text(), nullable=False),
        sa.Column("hasil_deteksi_html", sa.Text(), nullable=False),
        sa.Column("hasil_koreksi_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["pengguna_id"], ["pengguna.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("result_token"),
    )
    op.create_index(
        op.f("ix_riwayat_koreksi_pengguna_id"),
        "riwayat_koreksi",
        ["pengguna_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_riwayat_koreksi_pengguna_id"), table_name="riwayat_koreksi")
    op.drop_table("riwayat_koreksi")
