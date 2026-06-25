import re

from .base_rule import BaseRule


class TandaHubungRule(BaseRule):
    id = "tanda_hubung"

    _RE_KATA_ULANG = re.compile(r"\b([A-Za-z]+)\s+([A-Za-z]+)\b", re.IGNORECASE)
    _RE_TANGGAL_ANGKA = re.compile(r"\b(\d{1,2})\s+(\d{1,2})\s+(\d{4})\b")
    _RE_ANGKA_AKHIRAN = re.compile(r"\b(\d{4})\s+(an)\b", re.IGNORECASE)
    _RE_HURUF_ANGKA = re.compile(r"\b(Re)\s+(\d+)\b")
    _RE_KE_ANGKA = re.compile(r"\b(ke)\s+(\d+)\b")
    _RE_PREFIKS_KATA = re.compile(
        r"\b(non|anti|pro|pra|pasca|antar|multi|sub|e|a)\s+([A-Za-z][a-z]+)\b"
    )
    _RE_SPASI_TANDA_HUBUNG = re.compile(r"(\b\S+)\s+-\s+(\S+\b)|(\b\S+)\s+-(\S+\b)|(\b\S+)-\s+(\S+\b)")

    # Pasangan kata ulang berubah bunyi yang umum di karya ilmiah
    _KATA_ULANG_BERUBAH = {
        ("sayur", "mayur"), ("lauk", "pauk"), ("warna", "warni"),
        ("ramah", "tamah"), ("teka", "teki"), ("compang", "camping"),
        ("mondar", "mandir"), ("gerak", "gerik"), ("tunggang", "langgang"),
        ("hiruk", "pikuk"), ("pontang", "panting"),
    }

    # Prefiks yang TIDAK memerlukan tanda hubung sebelum huruf kecil
    # (hanya perlu tanda hubung jika diikuti huruf kapital atau angka)
    _PREFIKS_BUTUH_KAPITAL = {"non", "anti", "pro", "pra", "pasca", "antar", "multi", "sub"}
    # Prefiks yang selalu butuh tanda hubung
    _PREFIKS_SELALU = {"e", "a"}

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        hasil = []
        hasil.extend(self._cek_tanda_hubung_kata_ulang(teks))
        hasil.extend(self._cek_tanda_hubung_kata_ulang_berubah(teks))
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

    def _cek_tanda_hubung_kata_ulang_berubah(self, teks):
        """Deteksi kata ulang berubah bunyi menggunakan whitelist pasangan."""
        hasil = []
        for match in self._RE_KATA_ULANG.finditer(teks):
            first = match.group(1).lower()
            second = match.group(2).lower()
            if (first, second) not in self._KATA_ULANG_BERUBAH:
                continue

            start, end = match.span()
            hasil.append(
                self._buat_kesalahan(
                    kode="HD1",
                    jenis="tanda_hubung_kata_ulang",
                    deskripsi="Kata ulang berubah bunyi tidak menggunakan tanda hubung.",
                    perbaikan='Tambah "-" di antara kata ulang.',
                    pengganti=f"{match.group(1)}-{match.group(2)}",
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
            day = int(match.group(1))
            month = int(match.group(2))
            # Validasi rentang hari dan bulan
            if not (1 <= day <= 31 and 1 <= month <= 12):
                continue
            start, end = match.span()
            hasil.append(
                self._buat_kesalahan(
                    kode="HD2",
                    jenis="tanda_hubung_tanggal",
                    deskripsi="Tanggal tidak menggunakan tanda hubung.",
                    perbaikan='Tambah "-" di antara komponen tanggal.',
                    pengganti=f"{match.group(1)}-{match.group(2)}-{match.group(3)}",
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
        hasil.extend(self._cek_ke_angka(teks))
        hasil.extend(self._cek_prefiks_kata(teks))
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

    def _cek_ke_angka(self, teks):
        """Deteksi 'ke N' yang seharusnya 'ke-N' (bilangan ordinal)."""
        hasil = []
        for match in self._RE_KE_ANGKA.finditer(teks):
            prefix = match.group(1)
            angka = match.group(2)
            start, end = match.span()
            hasil.append(
                self._buat_kesalahan(
                    kode="HD3",
                    jenis="tanda_hubung_unsur_berbeda",
                    deskripsi="Bilangan ordinal 'ke-' tidak menggunakan tanda hubung.",
                    perbaikan='Tambah "-" setelah "ke".',
                    pengganti=f"{prefix}-{angka}",
                    start=start,
                    end=end,
                    rule="HR3",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    def _cek_prefiks_kata(self, teks):
        """Deteksi prefiks (non, anti, e, sub, dll.) yang tidak dirangkai tanda hubung."""
        hasil = []
        for match in self._RE_PREFIKS_KATA.finditer(teks):
            prefiks = match.group(1).lower()
            kata = match.group(2)
            start, end = match.span()

            # Prefiks yang hanya butuh tanda hubung jika kata berikutnya kapital
            if prefiks in self._PREFIKS_BUTUH_KAPITAL and not kata[0].isupper():
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="HD3",
                    jenis="tanda_hubung_unsur_berbeda",
                    deskripsi=f"Prefiks '{prefiks}' tidak dirangkai dengan tanda hubung.",
                    perbaikan=f'Tambah "-" setelah "{prefiks}".',
                    pengganti=f"{match.group(1)}-{kata}",
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
            # Ekstrak sisi kiri dan kanan dari grup yang aktif
            if match.group(1) and match.group(2):
                left, right = match.group(1), match.group(2)   # spasi di kedua sisi
            elif match.group(3) and match.group(4):
                left, right = match.group(3), match.group(4)   # spasi hanya di kiri
            elif match.group(5) and match.group(6):
                left, right = match.group(5), match.group(6)   # spasi hanya di kanan
            else:
                continue

            # Skip jika salah satu sisi adalah variabel/ekspresi (1-2 karakter)
            if len(left.strip()) <= 2 and len(right.strip()) <= 2:
                continue

            # Skip jika bagian dari URL
            segment_start = max(0, match.start() - 10)
            konteks_kiri = teks[segment_start:match.start()]
            if any(proto in konteks_kiri for proto in ("http", "https", "ftp", "://")):
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="HD4",
                    jenis="spasi_di_sekitar_tanda_hubung",
                    deskripsi="Terdapat spasi di sekitar tanda hubung.",
                    perbaikan="Hapus spasi di sekitar tanda hubung.",
                    pengganti=f"{left}-{right}",
                    start=match.start(),
                    end=match.end(),
                    rule="HR4",
                    prioritas="HIGH",
                )
            )
        return hasil