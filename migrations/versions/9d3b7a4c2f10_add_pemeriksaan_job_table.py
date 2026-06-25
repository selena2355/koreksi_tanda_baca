"""add pemeriksaan job table

Revision ID: 9d3b7a4c2f10
Revises: 7c8c1b2f4f6a
Create Date: 2026-05-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9d3b7a4c2f10"
down_revision = "7c8c1b2f4f6a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pemeriksaan_job",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_token", sa.String(length=64), nullable=False),
        sa.Column("pengguna_id", sa.Integer(), nullable=True),
        sa.Column("nama_dokumen", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("result_token", sa.String(length=64), nullable=True),
        sa.Column("extracted_text_file", sa.String(length=255), nullable=True),
        sa.Column("detection_result_html_file", sa.String(length=255), nullable=True),
        sa.Column("correction_result_file", sa.String(length=255), nullable=True),
        sa.Column("correction_result_html_file", sa.String(length=255), nullable=True),
        sa.Column("debug_normalized_file", sa.String(length=255), nullable=True),
        sa.Column("structured_text_file", sa.String(length=255), nullable=True),
        sa.Column("sbd_file", sa.String(length=255), nullable=True),
        sa.Column("tokens_file", sa.String(length=255), nullable=True),
        sa.Column("pos_file", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["pengguna_id"], ["pengguna.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_token"),
        sa.UniqueConstraint("result_token"),
    )
    op.create_index(op.f("ix_pemeriksaan_job_expires_at"), "pemeriksaan_job", ["expires_at"], unique=False)
    op.create_index(op.f("ix_pemeriksaan_job_pengguna_id"), "pemeriksaan_job", ["pengguna_id"], unique=False)
    op.create_index(op.f("ix_pemeriksaan_job_status"), "pemeriksaan_job", ["status"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_pemeriksaan_job_status"), table_name="pemeriksaan_job")
    op.drop_index(op.f("ix_pemeriksaan_job_pengguna_id"), table_name="pemeriksaan_job")
    op.drop_index(op.f("ix_pemeriksaan_job_expires_at"), table_name="pemeriksaan_job")
    op.drop_table("pemeriksaan_job")
