from flask import Blueprint

from ..controllers.dokumen_controller import (
    simpan_hasil_ke_riwayat,
    upload_dokumen,
    hasil_koreksi,
    uploaded_file,
    unduh_hasil_koreksi,
    clear_preview,
    tentang_page,
)

main_bp = Blueprint("main", __name__)

main_bp.add_url_rule("/", view_func=upload_dokumen, methods=["GET", "POST"])
main_bp.add_url_rule("/hasil", view_func=hasil_koreksi, methods=["GET", "POST"])
main_bp.add_url_rule("/unduh-hasil", view_func=unduh_hasil_koreksi, methods=["GET"])
main_bp.add_url_rule("/simpan-hasil-ke-riwayat", view_func=simpan_hasil_ke_riwayat, methods=["POST"])
main_bp.add_url_rule("/uploads/<path:filename>", view_func=uploaded_file, methods=["GET"])
main_bp.add_url_rule("/clear-preview", view_func=clear_preview, methods=["POST"])
main_bp.add_url_rule("/tentang", view_func=tentang_page, methods=["GET"])
