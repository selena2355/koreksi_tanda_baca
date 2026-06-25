from datetime import datetime, timedelta

from ..extensions import db


class PemeriksaanJob(db.Model):
    __tablename__ = "pemeriksaan_job"

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    id = db.Column(db.Integer, primary_key=True)
    job_token = db.Column(db.String(64), unique=True, nullable=False)
    pengguna_id = db.Column(db.Integer, db.ForeignKey("pengguna.id"), nullable=True, index=True)
    nama_dokumen = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(24), nullable=False, default=STATUS_PENDING, index=True)
    progress = db.Column(db.Integer, nullable=False, default=0)
    error_message = db.Column(db.Text, nullable=True)
    result_token = db.Column(db.String(64), unique=True, nullable=True)

    extracted_text_file = db.Column(db.String(255), nullable=True)
    detection_result_html_file = db.Column(db.String(255), nullable=True)
    correction_result_file = db.Column(db.String(255), nullable=True)
    correction_result_html_file = db.Column(db.String(255), nullable=True)
    debug_normalized_file = db.Column(db.String(255), nullable=True)
    structured_text_file = db.Column(db.String(255), nullable=True)
    sbd_file = db.Column(db.String(255), nullable=True)
    tokens_file = db.Column(db.String(255), nullable=True)
    pos_file = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    expires_at = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow() + timedelta(hours=24),
        nullable=False,
        index=True,
    )

    pengguna = db.relationship("Pengguna", backref="pemeriksaan_jobs")

    @property
    def is_finished(self):
        return self.status in {self.STATUS_DONE, self.STATUS_FAILED, self.STATUS_CANCELLED}
