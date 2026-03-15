from flask import Blueprint

from ..controllers.auth_controller import (
    login_page,
    register_page,
    login_post,
    register_post,
    logout,
    )

auth_bp = Blueprint("auth", __name__)

auth_bp.add_url_rule("/login", view_func=login_page, methods=["GET"])
auth_bp.add_url_rule("/login", view_func=login_post, methods=["POST"])

auth_bp.add_url_rule("/register", view_func=register_page, methods=["GET"])
auth_bp.add_url_rule("/register", view_func=register_post, methods=["POST"])

auth_bp.add_url_rule("/logout", view_func=logout, methods=["GET"])
