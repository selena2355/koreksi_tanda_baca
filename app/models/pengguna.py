class Pengguna:
    def __init__(self, pengguna_id=None, email=""):
        self.id = pengguna_id
        self.email = email
        self.riwayat = []

    def tambah_riwayat(self, riwayat):
        self.riwayat.append(riwayat)
