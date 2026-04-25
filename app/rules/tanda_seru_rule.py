import re

from .base_rule import BaseRule


class TandaSeruRule(BaseRule):
    id = "tanda_seru"

    _RE_BARIS = re.compile(r"(?m)^[^\n]+$")
    _RE_AWAL_SERU = re.compile(r"^(Segera|Jangan|Harap|Tolong|Wajib)\b")
    _STARTERS = {"segera", "jangan", "harap", "tolong", "wajib"}

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        tokens = self._get_tokens(konteks)
        hasil = []
        hasil.extend(self._cek_tanda_seru_akhir_kalimat(teks, tokens))
        return hasil

    def _cek_tanda_seru_akhir_kalimat(self, teks, tokens):
        hasil = []
        for match in self._RE_BARIS.finditer(teks):
            baris = match.group(0)
            baris_strip = baris.strip()
            if not baris_strip:
                continue
            if not self._RE_AWAL_SERU.search(baris_strip):
                continue

            start_offset = match.start()
            end_offset = start_offset + len(baris.rstrip())
            if end_offset <= start_offset:
                continue
            if tokens and not self._is_exclamation_starter(tokens, start_offset, end_offset):
                continue
            if baris_strip.endswith("!"):
                continue

            last_char = teks[end_offset - 1]
            if last_char in ".?":
                hasil.append(
                    self._buat_kesalahan(
                        kode="ED1",
                        jenis="tanda_seru_akhir_kalimat",
                        deskripsi="Perintah dan seruan harus diakhiri dengan tanda seru.",
                        perbaikan='Ganti tanda baca akhir dengan "!".',
                        pengganti="!",
                        start=end_offset - 1,
                        end=end_offset,
                        rule="ER1",
                        prioritas="LOW",
                    )
                )
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="ED1",
                    jenis="tanda_seru_akhir_kalimat",
                    deskripsi="Perintah dan seruan harus diakhiri dengan tanda seru.",
                    perbaikan='Tambah "!" di akhir kalimat.',
                    pengganti="!",
                    start=end_offset,
                    end=end_offset,
                    rule="ER1",
                    prioritas="LOW",
                    display_start=max(start_offset, end_offset - 1),
                    display_end=end_offset,
                )
            )
        return hasil

    def _is_exclamation_starter(self, tokens, start_offset, end_offset):
        first_token = None
        for token in tokens:
            token_start = token.get("start_char", -1)
            if token_start < start_offset or token_start >= end_offset:
                continue
            first_token = token
            break

        if not first_token:
            return False
        return str(first_token.get("text", "")).lower() in self._STARTERS
