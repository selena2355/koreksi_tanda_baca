from flask import Blueprint

from ..controllers.riwayat_controller import (
    detail_riwayat_page,
    hapus_riwayat,
    riwayat_page,
    unduh_riwayat,
)

riwayat_bp = Blueprint("riwayat", __name__)

riwayat_bp.add_url_rule("/riwayat", view_func=riwayat_page, methods=["GET"])
riwayat_bp.add_url_rule("/riwayat/<int:riwayat_id>", view_func=detail_riwayat_page, methods=["GET"])
riwayat_bp.add_url_rule("/riwayat/<int:riwayat_id>/unduh", view_func=unduh_riwayat, methods=["GET"])
riwayat_bp.add_url_rule(
    "/riwayat/<int:riwayat_id>/hapus",
    view_func=hapus_riwayat,
    methods=["POST"],
)
