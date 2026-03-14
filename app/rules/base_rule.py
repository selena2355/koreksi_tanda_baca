import re

from ..models.kesalahan import Kesalahan


class BaseRule:
    """
    Base detection rule (BR1, BR2, BR3).
    """

    id = "base"

    _RE_SPACE_BEFORE = re.compile(r"\s+([.,;:?!])")
    _RE_MISSING_SPACE_AFTER = re.compile(r"([.,;:])(?=[A-Za-z0-9])")
    _RE_REPEATED_PUNCT = re.compile(r"([.!?])\1+")

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        hasil = []
        hasil.extend(self._cek_spasi_sebelum_tanda_baca(teks))
        hasil.extend(self._cek_spasi_setelah_tanda_baca(teks))
        hasil.extend(self._cek_tanda_baca_berulang(teks))
        return hasil

    def _cek_spasi_sebelum_tanda_baca(self, teks):
        hasil = []
        for match in self._RE_SPACE_BEFORE.finditer(teks):
            punct = match.group(1)
            start, end = match.span()
            hasil.append(
                self._buat_kesalahan(
                    kode="BD1",
                    jenis="spasi_sebelum_tanda_baca",
                    deskripsi="Terdapat spasi sebelum tanda baca.",
                    perbaikan="Hapus spasi sebelum tanda baca.",
                    pengganti=punct,
                    start=start,
                    end=end,
                    rule="BR1",
                    prioritas="HIGH",
                )
            )
        return hasil

    def _cek_spasi_setelah_tanda_baca(self, teks):
        hasil = []
        for match in self._RE_MISSING_SPACE_AFTER.finditer(teks):
            punct = match.group(1)
            idx = match.start(1)
            if self._is_exception_missing_space(teks, idx, punct):
                continue
            hasil.append(
                self._buat_kesalahan(
                    kode="BD2",
                    jenis="spasi_setelah_tanda_baca",
                    deskripsi="Tidak ada spasi setelah tanda baca.",
                    perbaikan="Tambah spasi setelah tanda baca.",
                    pengganti=f"{punct} ",
                    start=idx,
                    end=idx + 1,
                    rule="BR2",
                    prioritas="HIGH",
                )
            )
        return hasil

    def _cek_tanda_baca_berulang(self, teks):
        hasil = []
        for match in self._RE_REPEATED_PUNCT.finditer(teks):
            punct = match.group(1)
            start, end = match.span()
            hasil.append(
                self._buat_kesalahan(
                    kode="BD3",
                    jenis="tanda_baca_berulang",
                    deskripsi="Tanda baca ganda/berlebihan terdeteksi.",
                    perbaikan="Ganti dengan tanda baca tunggal.",
                    pengganti=punct,
                    start=start,
                    end=end,
                    rule="BR3",
                    prioritas="HIGH",
                )
            )
        return hasil

    # Deteksi pengecualian untuk kasus di mana tidak diperlukan spasi setelah tanda baca.
    def _is_exception_missing_space(self, teks, idx, punct):
        # Jika tanda baca berada di awal atau akhir teks, abaikan (tidak perlu spasi).
        if idx < 0 or idx >= len(teks) - 1:
            return True

        prev_char = teks[idx - 1] if idx > 0 else ""
        next_char = teks[idx + 1] if idx + 1 < len(teks) else ""

        if not next_char or not next_char.isalnum():
            return True

        token = self._extract_token(teks, idx)
        if self._looks_like_url(token):
            return True
        if punct == ".":  # gelar/abrev bertitik (koma tetap harus diikuti spasi)
            if self._looks_like_gelar_token(token):
                return True

        if punct in ".,":  # desimal / ribuan
            if prev_char.isdigit() and next_char.isdigit():
                return True

        if punct == ":":  # skala / perbandingan / waktu
            # Contoh: "Rasio 1:2", "Pukul 12:30", "Skala 1:1000"
            if prev_char.isdigit() and next_char.isdigit():
                return True

        return False

    @staticmethod
    def _extract_token(teks, idx):
        left = idx
        while left > 0 and not teks[left - 1].isspace():
            left -= 1
        right = idx + 1
        while right < len(teks) and not teks[right].isspace():
            right += 1
        return teks[left:right]

    @staticmethod
    def _looks_like_url(token):
        token_lower = token.lower()
        if "://" in token_lower:
            return True
        if token_lower.startswith("www."):
            return True
        if re.search(
            r"\b\w+\.(com|net|org|id|co|ac|go|edu|gov|io|app)(/|$)",
            token_lower,
        ):
            return True
        return False

    @staticmethod
    def _looks_like_gelar_token(token):
        if not token or not re.search(r"[A-Za-z]", token):
            return False
        if not re.fullmatch(r"[A-Za-z.,]+", token):
            return False
        dot_count = token.count(".")
        if dot_count >= 2:
            return True
        if dot_count >= 1 and "," in token:
            return True
        return False

    @staticmethod
    def _buat_kesalahan(
        kode,
        jenis,
        deskripsi,
        perbaikan,
        pengganti,
        start,
        end,
        rule,
        prioritas,
    ):
        kesalahan = Kesalahan(
            jenis=jenis,
            deskripsi=deskripsi,
            perbaikan=perbaikan,
            pengganti=pengganti,
        )
        kesalahan.start = start
        kesalahan.end = end
        kesalahan.kode = kode
        kesalahan.rule = rule
        kesalahan.prioritas = prioritas
        return kesalahan
