import re

from .base_rule import BaseRule


class TitikDuaRule(BaseRule):
    id = "titik_dua"

    
    _RE_TITIK_DUA_SETELAH_PREDIKAT = re.compile(
        r"\b("
        r"adalah|merupakan|ialah|meliputi|yaitu|yakni|mencakup|mengandung|"
        r"terdiri\s+(?:dari|atas)|antara\s+lain|di\s+antaranya"
        r")\b(\s*):(\s*)",
        re.IGNORECASE,
    )

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        return self._cek_titik_dua_salah_setelah_predikat(teks)

    def _cek_titik_dua_salah_setelah_predikat(self, teks):
        hasil = []
        for match in self._RE_TITIK_DUA_SETELAH_PREDIKAT.finditer(teks):
            after = teks[match.end():]
            # Titik dua diperbolehkan jika diikuti baris baru (awal daftar/perincian)
            if re.match(
                r"\s*(?:\r?\n\s*)?(?:\d+\.|[A-Za-z]\.|[IVXLCDM]+\.|[-•])",
                after,
                re.IGNORECASE,
            ):
                continue

            colon_pos = teks.find(":", match.start(), match.end())
            hasil.append(
                self._buat_kesalahan(
                    kode="CnD1",
                    jenis="titik_dua_setelah_predikat",
                    deskripsi="Titik dua tidak digunakan setelah kata kerja/predikat langsung.",
                    perbaikan="Hapus ':' setelah predikat.",
                    pengganti=" ",
                    start=match.end(1),
                    end=match.end(),
                    rule="CnR1",
                    prioritas="CRITICAL",
                    display_start=colon_pos,
                    display_end=colon_pos + 1,
                )
            )
        return hasil
