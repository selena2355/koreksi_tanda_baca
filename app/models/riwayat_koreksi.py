from datetime import datetime

from ..extensions import db


class RiwayatKoreksi(db.Model):
    __tablename__ = "riwayat_koreksi"

    id = db.Column(db.Integer, primary_key=True)
    pengguna_id = db.Column(db.Integer, db.ForeignKey("pengguna.id"), nullable=False, index=True)
    result_token = db.Column(db.String(64), unique=True, nullable=False)
    nama_dokumen = db.Column(db.String(255), nullable=False)
    teks_dokumen = db.Column(db.Text, nullable=False)
    hasil_deteksi_html = db.Column(db.Text, nullable=False)
    hasil_koreksi_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    pengguna = db.relationship("Pengguna", back_populates="riwayat_koreksi")
