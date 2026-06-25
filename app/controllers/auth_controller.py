from flask import render_template, request, redirect, url_for, flash, session
import re
from ..extensions import db
from ..models import Pengguna
from ..services.riwayat_service import RiwayatService
from ..utils.file_utils import FileUtils


class AuthController:
    # Konstanta validasi
    MIN_PASSWORD_LENGTH = 8
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 20
    
    # Inisialisasi controller dengan service dan utilitas yang diperlukan
    def __init__(self, riwayat_service=None, file_utils=None):
        self.riwayat_service = riwayat_service or RiwayatService()
        self.file_utils = file_utils or FileUtils()

    def login_page(self):
        return render_template("login.html", errors={}, form_data={})

    def register_page(self):
        return render_template("register.html", errors={}, form_data={})

    def _validate_username(self, username):
        """Validasi username dan return error jika ada"""
        errors = {}
        
        if not username:
            errors["username"] = "Username wajib diisi."
            return errors
        
        username = username.strip()
        
        if len(username) < self.MIN_USERNAME_LENGTH:
            errors["username"] = f"Username minimal {self.MIN_USERNAME_LENGTH} karakter."
            return errors
        
        if len(username) > self.MAX_USERNAME_LENGTH:
            errors["username"] = f"Username maksimal {self.MAX_USERNAME_LENGTH} karakter."
            return errors
        
        if " " in username:
            errors["username"] = "Username tidak boleh mengandung spasi."
            return errors
        
        if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
            errors["username"] = "Username hanya boleh berisi huruf, angka, underscore, titik, dan dash."
            return errors
        
        return errors

    def _validate_password(self, password):
        """Validasi password dan return error jika ada"""
        errors = {}
        
        if not password:
            errors["password"] = "Password wajib diisi."
            return errors
        
        if len(password) < self.MIN_PASSWORD_LENGTH:
            errors["password"] = f"Password minimal {self.MIN_PASSWORD_LENGTH} karakter."
            return errors
        
        return errors

    def _validate_email(self, email):
        """Validasi email dan return error jika ada"""
        errors = {}
        
        if not email:
            errors["email"] = "Email wajib diisi."
            return errors
        
        email = email.strip()
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        if not re.match(email_pattern, email):
            errors["email"] = "Format email tidak valid."
            return errors
        
        return errors

    def register_post(self):
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validasi setiap field
        errors = {}
        errors.update(self._validate_username(username))
        errors.update(self._validate_email(email))
        errors.update(self._validate_password(password))

        if errors:
            # Pastikan error ditampilkan seperti "field error" di bawah masing-masing field
            return render_template(
                "register.html",
                errors=errors,
                form_data={"username": username, "email": email},
            )

        # Cek apakah username atau email sudah terdaftar
        existing_user = (
            Pengguna.query.filter(
                (Pengguna.username == username) | (Pengguna.email == email)
            ).first()
        )
        if existing_user:
            if existing_user.username == username:
                errors["username"] = "Username sudah terdaftar."
            if existing_user.email == email:
                errors["email"] = "Email sudah terdaftar."
            return render_template("register.html", errors=errors, 
                                 form_data={"username": username, "email": email})

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

        errors = {}
        
        if not identifier:
            errors["identifier"] = "Email atau username wajib diisi."
        
        if not password:
            errors["password"] = "Password wajib diisi."

        if errors:
            return render_template(
                "login.html",
                errors=errors,
                form_data={"identifier": identifier},
            )

        user = Pengguna.query.filter(
            (Pengguna.username == identifier) | (Pengguna.email == identifier)
        ).first()

        if not user:
            errors["identifier"] = "Username/email tidak ditemukan."
            return render_template("login.html", errors=errors, 
                                 form_data={"identifier": identifier})

        if not user.check_password(password):
            errors["password"] = "Password salah."
            return render_template("login.html", errors=errors, 
                                 form_data={"identifier": identifier})

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

