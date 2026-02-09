from flask import Blueprint

from ..controllers.riwayat_controller import riwayat_page

riwayat_bp = Blueprint("riwayat", __name__)

riwayat_bp.add_url_rule("/riwayat", view_func=riwayat_page, methods=["GET"])
