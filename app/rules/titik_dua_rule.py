import re

from .base_rule import BaseRule


class TitikDuaRule(BaseRule):
    id = "titik_dua"

    _RE_KATA_KUNCI_PERINCIAN = re.compile(
        r"\b(meliputi|yaitu|adalah|terdiri)\b(\s+)(?!:)",
        re.IGNORECASE,
    )
    _RE_LABEL_PEMERIAN = re.compile(
        r"(?m)^[ \t]*(Nama|Tempat|Waktu|Tanggal)\b(?!\s*:)(\s+)",
        re.IGNORECASE,
    )
    _RE_TITIK_DUA_SETELAH_PREDIKAT = re.compile(
        r"\b(adalah|merupakan|ialah)\b(\s*):(\s*)",
        re.IGNORECASE,
    )
    _RE_KONEKTOR_DAFTAR = re.compile(r"\b(dan|atau)\b", re.IGNORECASE)

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        hasil = []
        hasil.extend(self._cek_titik_dua_sebelum_perincian(teks))
        hasil.extend(self._cek_titik_dua_setelah_label_pemerian(teks))
        hasil.extend(self._cek_titik_dua_salah_setelah_predikat(teks))
        return hasil

    def _cek_titik_dua_sebelum_perincian(self, teks):
        hasil = []
        for match in self._RE_KATA_KUNCI_PERINCIAN.finditer(teks):
            keyword = match.group(1)
            segmen = self._ambil_segmen_setelah(teks, match.end())
            if not self._looks_like_perincian(segmen):
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="CnD1",
                    jenis="titik_dua_sebelum_perincian",
                    deskripsi="Titik dua hilang sebelum perincian.",
                    perbaikan="Tambah ':' setelah kata kunci perincian.",
                    pengganti=": ",
                    start=match.start(2),
                    end=match.end(2),
                    rule="CnR1",
                    prioritas="MEDIUM",
                    display_start=match.start(1),
                    display_end=match.end(1),
                )
            )
        return hasil

    def _cek_titik_dua_setelah_label_pemerian(self, teks):
        hasil = []
        for match in self._RE_LABEL_PEMERIAN.finditer(teks):
            hasil.append(
                self._buat_kesalahan(
                    kode="CnD2",
                    jenis="titik_dua_untuk_pemerian",
                    deskripsi="Titik dua hilang setelah kata pemerian.",
                    perbaikan="Tambah ':' setelah kata pemerian.",
                    pengganti=": ",
                    start=match.start(2),
                    end=match.end(2),
                    rule="CnR2",
                    prioritas="MEDIUM",
                    display_start=match.start(1),
                    display_end=match.end(1),
                )
            )
        return hasil

    def _cek_titik_dua_salah_setelah_predikat(self, teks):
        hasil = []
        for match in self._RE_TITIK_DUA_SETELAH_PREDIKAT.finditer(teks):
            colon_pos = teks.find(":", match.start(), match.end())
            hasil.append(
                self._buat_kesalahan(
                    kode="CnD3",
                    jenis="titik_dua_setelah_predikat",
                    deskripsi="Titik dua tidak digunakan setelah kata kerja/predikat langsung.",
                    perbaikan="Hapus ':' setelah predikat.",
                    pengganti=" ",
                    start=match.end(1),
                    end=match.end(),
                    rule="CnR3",
                    prioritas="LOW",
                    display_start=colon_pos,
                    display_end=colon_pos + 1,
                )
            )
        return hasil

    def _ambil_segmen_setelah(self, teks, idx):
        cursor = idx
        while cursor < len(teks):
            if teks[cursor] in ".!?\n":
                return teks[idx:cursor].strip()
            cursor += 1
        return teks[idx:].strip()

    def _looks_like_perincian(self, segmen):
        if not segmen:
            return False
        if segmen.startswith(":"):
            return False
        if "," in segmen:
            return True
        return bool(self._RE_KONEKTOR_DAFTAR.search(segmen))
