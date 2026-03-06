class HasilDeteksi:
    def __init__(self, daftar_kesalahan=None):
        self.daftar_kesalahan = daftar_kesalahan or []

    def tambah_kesalahan(self, kesalahan):
        self.daftar_kesalahan.append(kesalahan)
