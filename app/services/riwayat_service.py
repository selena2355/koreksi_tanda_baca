class RiwayatService:
    def __init__(self):
        self._riwayat = []

    def simpan_riwayat(self, riwayat):
        self._riwayat.append(riwayat)

    def ambil_riwayat(self):
        return list(self._riwayat)
