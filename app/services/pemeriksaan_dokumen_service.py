from ..models.dokumen import Dokumen
from ..models.hasil_koreksi import HasilKoreksi
from ..services.preprocessing_service import PreprocessingService
from ..services.koreksi_service import KoreksiService


class PemeriksaanDokumenService:
    def __init__(self, preprocessing_service=None, koreksi_service=None):
        self.preprocessing_service = preprocessing_service or PreprocessingService()
        self.koreksi_service = koreksi_service or KoreksiService()

    def proses_dokumen(self, dokumen: Dokumen) -> HasilKoreksi:
        teks_bersih = self.preprocessing(dokumen.teks_asli)
        teks_koreksi = self.terapkan_aturan(teks_bersih)
        return HasilKoreksi(teks_koreksi=teks_koreksi, jumlah_koreksi=0)

    def validasi_dokumen(self, dokumen: Dokumen) -> bool:
        return bool(dokumen and dokumen.teks_asli)

    def ekstraksi_teks(self, teks: str) -> str:
        return teks

    def preprocessing(self, teks: str) -> str:
        return self.preprocessing_service.preprocessing(teks)

    def terapkan_aturan(self, teks: str) -> str:
        return self.koreksi_service.koreksi(teks)
