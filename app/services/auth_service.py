from ..models.pengguna import Pengguna


class AuthService:
    def login(self, email="", password=""):
        return Pengguna(pengguna_id=1, email=email)

    def registrasi(self, email="", password=""):
        return Pengguna(pengguna_id=1, email=email)
