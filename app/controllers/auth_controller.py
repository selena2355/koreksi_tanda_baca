from flask import render_template, request, redirect, url_for, flash, session
from ..extensions import db
from ..models import Pengguna
from ..services.riwayat_service import RiwayatService
from ..utils.file_utils import FileUtils


class AuthController:
    # Inisialisasi controller dengan service dan utilitas yang diperlukan
    def __init__(self, riwayat_service=None, file_utils=None):
        self.riwayat_service = riwayat_service or RiwayatService()
        self.file_utils = file_utils or FileUtils()

    def login_page(self):
        return render_template("login.html")

    def register_page(self):
        return render_template("register.html")

    def register_post(self):
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Semua field wajib diisi.", "error")
            return redirect(url_for("auth.register_page"))

        existing_user = (
            Pengguna.query.filter(
                (Pengguna.username == username) | (Pengguna.email == email)
            ).first()
        )
        if existing_user:
            flash("Username atau email sudah terdaftar.", "error")
            return redirect(url_for("auth.register_page"))

        user = Pengguna(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["username"] = user.username

        flash("Registrasi berhasil. Selamat datang!", "success")
        return redirect(url_for("main.upload_dokumen"))

    def login_post(self):
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier or not password:
            flash("Username/email dan password wajib diisi.", "error")
            return redirect(url_for("auth.login_page"))

        user = Pengguna.query.filter(
            (Pengguna.username == identifier) | (Pengguna.email == identifier)
        ).first()

        if not user or not user.check_password(password):
            flash("Login gagal. Cek username/email dan password.", "error")
            return redirect(url_for("auth.login_page"))

        session["user_id"] = user.id
        session["username"] = user.username

        flash("Login berhasil.", "success")
        return redirect(url_for("main.upload_dokumen"))

    def logout(self):
        if session.get("user_id") and not session.get("history_saved"):
            riwayat = self.riwayat_service.simpan_dari_session(
                pengguna_id=session.get("user_id"),
                session_data=session,
                file_utils=self.file_utils,
            )
            if riwayat:
                session["history_saved"] = True

        session.pop("user_id", None)
        session.pop("username", None)
        flash("Kamu sudah logout.", "success")
        return redirect(url_for("main.upload_dokumen"))


_auth_controller = AuthController()


def login_page():
    return _auth_controller.login_page()


def register_page():
    return _auth_controller.register_page()


def register_post():
    return _auth_controller.register_post()


def login_post():
    return _auth_controller.login_post()


def logout():
    return _auth_controller.logout()

