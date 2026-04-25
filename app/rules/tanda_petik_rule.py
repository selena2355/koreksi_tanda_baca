import re

from .base_rule import BaseRule


class TandaPetikRule(BaseRule):
    id = "tanda_petik"

    _RE_VERBA_KUTIPAN = re.compile(r"\b(berkata|mengatakan|bertanya)\b", re.IGNORECASE)
    _RE_SPASI_DALAM_PETIK = re.compile(r'"([^"\n]*)"')
    _QUOTE_CHAR = '"'

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        hasil = []
        hasil.extend(self._cek_kutipan_langsung_tanpa_petik(teks))
        hasil.extend(self._cek_tanda_petik_tidak_berpasangan(teks))
        hasil.extend(self._cek_spasi_di_dalam_tanda_petik(teks))
        return hasil

    def _cek_kutipan_langsung_tanpa_petik(self, teks):
        hasil = []
        for match in self._RE_VERBA_KUTIPAN.finditer(teks):
            quote_span = self._find_direct_quote_span(teks, match.end())
            if not quote_span:
                continue

            start, end = quote_span
            quoted_text = teks[start:end]
            if not quoted_text or quoted_text.startswith(self._QUOTE_CHAR):
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="QtD1",
                    jenis="tanda_petik_kutipan_langsung",
                    deskripsi="Petikan langsung tidak diapit tanda petik.",
                    perbaikan='Bungkus kutipan langsung dengan tanda petik.',
                    pengganti=f'"{quoted_text}"',
                    start=start,
                    end=end,
                    rule="QtR1",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    def _cek_tanda_petik_tidak_berpasangan(self, teks):
        hasil = []
        quote_positions = [idx for idx, char in enumerate(teks) if char == self._QUOTE_CHAR]
        if len(quote_positions) % 2 == 0:
            return hasil

        first_quote = quote_positions[0] if quote_positions else -1
        last_quote = quote_positions[-1] if quote_positions else -1
        sentence_end = self._find_sentence_end(teks, last_quote + 1)

        if first_quote == 0 or (first_quote > 0 and teks[first_quote - 1] in " \n\t:;,"):
            hasil.append(
                self._buat_kesalahan(
                    kode="QtD2",
                    jenis="tanda_petik_tidak_berpasangan",
                    deskripsi="Tanda petik tidak berpasangan.",
                    perbaikan='Tambah tanda petik penutup yang hilang.',
                    pengganti=self._QUOTE_CHAR,
                    start=sentence_end,
                    end=sentence_end,
                    rule="QtR2",
                    prioritas="MEDIUM",
                    display_start=max(0, min(len(teks), sentence_end - 1)),
                    display_end=min(len(teks), sentence_end),
                )
            )
            return hasil

        opening_start = self._find_opening_quote_insert_position(teks, first_quote)
        hasil.append(
            self._buat_kesalahan(
                kode="QtD2",
                jenis="tanda_petik_tidak_berpasangan",
                deskripsi="Tanda petik tidak berpasangan.",
                perbaikan='Tambah tanda petik pembuka yang hilang.',
                pengganti=self._QUOTE_CHAR,
                start=opening_start,
                end=opening_start,
                rule="QtR2",
                prioritas="MEDIUM",
                display_start=opening_start,
                display_end=min(len(teks), opening_start + 1),
            )
        )
        return hasil

    def _cek_spasi_di_dalam_tanda_petik(self, teks):
        hasil = []
        for match in self._RE_SPASI_DALAM_PETIK.finditer(teks):
            inner = match.group(1)
            if inner == inner.strip():
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="QtD3",
                    jenis="spasi_di_dalam_tanda_petik",
                    deskripsi="Terdapat spasi di dalam tanda petik.",
                    perbaikan='Hapus spasi setelah pembuka atau sebelum penutup tanda petik.',
                    pengganti=f'"{inner.strip()}"',
                    start=match.start(),
                    end=match.end(),
                    rule="QtR3",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    def _find_direct_quote_span(self, teks, search_start):
        cursor = search_start
        while cursor < len(teks) and teks[cursor].isspace():
            cursor += 1
        if cursor < len(teks) and teks[cursor] in ",:":
            cursor += 1
            while cursor < len(teks) and teks[cursor].isspace():
                cursor += 1
        if cursor >= len(teks):
            return None
        if teks[cursor] == self._QUOTE_CHAR:
            return None
        if not teks[cursor].isupper():
            return None

        sentence_end = self._find_sentence_end(teks, cursor)
        if sentence_end <= cursor:
            return None
        if sentence_end < len(teks) and teks[sentence_end] in ".!?":
            return cursor, sentence_end + 1
        return cursor, sentence_end

    def _find_opening_quote_insert_position(self, teks, quote_index):
        sentence_start = self._find_sentence_start(teks, quote_index)
        match = self._RE_VERBA_KUTIPAN.search(teks, sentence_start, quote_index)
        if match:
            cursor = match.end()
            while cursor < quote_index and teks[cursor].isspace():
                cursor += 1
            return cursor

        cursor = sentence_start
        while cursor < quote_index and teks[cursor].isspace():
            cursor += 1
        return cursor

    @staticmethod
    def _find_sentence_start(teks, idx):
        cursor = idx - 1
        while cursor >= 0:
            if teks[cursor] in ".!?\n":
                return cursor + 1
            cursor -= 1
        return 0

    @staticmethod
    def _find_sentence_end(teks, idx):
        cursor = idx
        while cursor < len(teks):
            if teks[cursor] in ".!?\n":
                return cursor
            cursor += 1
        return len(teks)
