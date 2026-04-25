import re

from .base_rule import BaseRule


class TandaHubungRule(BaseRule):
    id = "tanda_hubung"

    _RE_KATA_ULANG = re.compile(r"\b([A-Za-z]+)\s+([A-Za-z]+)\b", re.IGNORECASE)
    _RE_TANGGAL_ANGKA = re.compile(r"\b(\d{1,2})\s+(\d{1,2})\s+(\d{4})\b")
    _RE_ANGKA_AKHIRAN = re.compile(r"\b(\d{4})\s+(an)\b", re.IGNORECASE)
    _RE_HURUF_ANGKA = re.compile(r"\b(Re)\s+(\d+)\b")
    _RE_SPASI_TANDA_HUBUNG = re.compile(r"(\b\S+)\s*-\s*(\S+\b)")

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        hasil = []
        hasil.extend(self._cek_tanda_hubung_kata_ulang(teks))
        hasil.extend(self._cek_tanda_hubung_tanggal(teks))
        hasil.extend(self._cek_tanda_hubung_unsur_berbeda(teks))
        hasil.extend(self._cek_spasi_di_sekitar_tanda_hubung(teks))
        return hasil

    def _cek_tanda_hubung_kata_ulang(self, teks):
        hasil = []
        for match in self._RE_KATA_ULANG.finditer(teks):
            first = match.group(1)
            second = match.group(2)
            if first.lower() != second.lower():
                continue

            start, end = match.span()
            hasil.append(
                self._buat_kesalahan(
                    kode="HD1",
                    jenis="tanda_hubung_kata_ulang",
                    deskripsi="Kata ulang tidak menggunakan tanda hubung.",
                    perbaikan='Tambah "-" di antara kata ulang.',
                    pengganti=f"{first}-{second}",
                    start=start,
                    end=end,
                    rule="HR1",
                    prioritas="HIGH",
                )
            )
        return hasil

    def _cek_tanda_hubung_tanggal(self, teks):
        hasil = []
        for match in self._RE_TANGGAL_ANGKA.finditer(teks):
            day = match.group(1)
            month = match.group(2)
            year = match.group(3)
            start, end = match.span()
            hasil.append(
                self._buat_kesalahan(
                    kode="HD2",
                    jenis="tanda_hubung_tanggal",
                    deskripsi="Tanggal tidak menggunakan tanda hubung.",
                    perbaikan='Tambah "-" di antara komponen tanggal.',
                    pengganti=f"{day}-{month}-{year}",
                    start=start,
                    end=end,
                    rule="HR2",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    def _cek_tanda_hubung_unsur_berbeda(self, teks):
        hasil = []
        hasil.extend(self._cek_angka_akhiran(teks))
        hasil.extend(self._cek_huruf_angka(teks))
        return hasil

    def _cek_angka_akhiran(self, teks):
        hasil = []
        for match in self._RE_ANGKA_AKHIRAN.finditer(teks):
            angka = match.group(1)
            akhiran = match.group(2)
            start, end = match.span()
            hasil.append(
                self._buat_kesalahan(
                    kode="HD3",
                    jenis="tanda_hubung_unsur_berbeda",
                    deskripsi="Unsur berbeda tidak dihubungkan tanda hubung.",
                    perbaikan='Tambah "-" di antara unsur berbeda.',
                    pengganti=f"{angka}-{akhiran}",
                    start=start,
                    end=end,
                    rule="HR3",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    def _cek_huruf_angka(self, teks):
        hasil = []
        for match in self._RE_HURUF_ANGKA.finditer(teks):
            prefix = match.group(1)
            angka = match.group(2)
            start, end = match.span()
            hasil.append(
                self._buat_kesalahan(
                    kode="HD3",
                    jenis="tanda_hubung_unsur_berbeda",
                    deskripsi="Unsur berbeda tidak dihubungkan tanda hubung.",
                    perbaikan='Tambah "-" di antara unsur berbeda.',
                    pengganti=f"{prefix}-{angka}",
                    start=start,
                    end=end,
                    rule="HR3",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    def _cek_spasi_di_sekitar_tanda_hubung(self, teks):
        hasil = []
        for match in self._RE_SPASI_TANDA_HUBUNG.finditer(teks):
            left = match.group(1)
            right = match.group(2)
            segment = match.group(0)
            if " " not in segment and "\t" not in segment:
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="HD4",
                    jenis="spasi_di_sekitar_tanda_hubung",
                    deskripsi="Terdapat spasi di sekitar tanda hubung.",
                    perbaikan='Hapus spasi di sekitar tanda hubung.',
                    pengganti=f"{left}-{right}",
                    start=match.start(),
                    end=match.end(),
                    rule="HR4",
                    prioritas="HIGH",
                )
            )
        return hasil
