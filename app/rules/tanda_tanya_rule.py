import re

from .base_rule import BaseRule


class TandaTanyaRule(BaseRule):
    id = "tanda_tanya"

    _RE_BARIS = re.compile(r"(?m)^[^\n]+$")
    _RE_AWAL_TANYA = re.compile(
        r"^(Apa|Apakah|Siapa|Kapan|Di mana|Dimana|Mengapa|Bagaimana|Berapa)\b"
    )
    _RE_TANYA_TAK_LANGSUNG = re.compile(
        r"\b(bertanya|mempertanyakan|menanyakan)\b",
        re.IGNORECASE,
    )
    _QUOTE_CHARS = "\"'"
    _QUESTION_STARTERS = {"apa", "apakah", "siapa", "kapan", "mengapa", "bagaimana", "berapa"}
    _INDIRECT_VERBS = {"bertanya", "mempertanyakan", "menanyakan", "tanya"}

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        tokens = self._get_tokens(konteks)
        hasil = []
        hasil.extend(self._cek_tanda_tanya_akhir_kalimat(teks, tokens))
        hasil.extend(self._cek_tanda_tanya_tak_langsung(teks, tokens))
        return hasil

    def _cek_tanda_tanya_akhir_kalimat(self, teks, tokens):
        hasil = []
        for match in self._RE_BARIS.finditer(teks):
            baris = match.group(0)
            baris_strip = baris.strip()
            if not baris_strip:
                continue
            if not self._RE_AWAL_TANYA.search(baris_strip):
                continue

            start_offset = match.start()
            end_offset = start_offset + len(baris.rstrip())
            if end_offset <= start_offset:
                continue
            if tokens and not self._is_question_starter(tokens, start_offset, end_offset):
                continue
            if baris_strip.endswith("?"):
                continue

            last_char = teks[end_offset - 1]
            if last_char in ".!":
                hasil.append(
                    self._buat_kesalahan(
                        kode="QsD1",
                        jenis="tanda_tanya_akhir_kalimat",
                        deskripsi="Kalimat tanya tidak diakhiri tanda tanya.",
                        perbaikan='Ganti tanda baca akhir dengan "?".',
                        pengganti="?",
                        start=end_offset - 1,
                        end=end_offset,
                        rule="QsR1",
                        prioritas="HIGH",
                    )
                )
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="QsD1",
                    jenis="tanda_tanya_akhir_kalimat",
                    deskripsi="Kalimat tanya tidak diakhiri tanda tanya.",
                    perbaikan='Tambah "?" di akhir kalimat tanya.',
                    pengganti="?",
                    start=end_offset,
                    end=end_offset,
                    rule="QsR1",
                    prioritas="HIGH",
                    display_start=max(start_offset, end_offset - 1),
                    display_end=end_offset,
                )
            )
        return hasil

    def _cek_tanda_tanya_tak_langsung(self, teks, tokens):
        hasil = []
        for match in self._RE_TANYA_TAK_LANGSUNG.finditer(teks):
            start, end = match.span(1)
            sentence_start = self._find_sentence_start(teks, start)
            sentence_end = self._find_sentence_end(teks, end)
            if sentence_end <= start:
                continue
            if teks[sentence_end - 1] != "?":
                continue

            sentence_text = teks[sentence_start:sentence_end]
            if self._contains_direct_quote(sentence_text):
                continue
            if tokens and not self._is_indirect_question_verb(tokens, start, match.group(1)):
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="QsD2",
                    jenis="tanda_tanya_kalimat_tak_langsung",
                    deskripsi="Tanda tanya pada kalimat tanya tak langsung.",
                    perbaikan='Ganti "?" dengan ".".',
                    pengganti=".",
                    start=sentence_end - 1,
                    end=sentence_end,
                    rule="QsR2",
                    prioritas="LOW",
                )
            )
        return hasil

    def _is_question_starter(self, tokens, start_offset, end_offset):
        first_token = None
        for token in tokens:
            token_start = token.get("start_char", -1)
            if token_start < start_offset or token_start >= end_offset:
                continue
            first_token = token
            break

        if not first_token:
            return False

        token_text = self._token_text(first_token).lower()
        if token_text in self._QUESTION_STARTERS:
            return True

        if token_text == "di":
            next_token = self._find_next_token(tokens, first_token)
            return bool(next_token and self._token_text(next_token).lower() == "mana")
        return token_text == "dimana"

    def _is_indirect_question_verb(self, tokens, start_char, matched_text):
        token = self._find_token_by_start(tokens, start_char, matched_text)
        if not token:
            return False

        upos = str(token.get("upos", "")).upper()
        lemma = str(token.get("lemma", "")).lower()
        text_lower = self._token_text(token).lower()
        if upos and upos != "VERB":
            return False
        return lemma in self._INDIRECT_VERBS or text_lower in self._INDIRECT_VERBS

    @classmethod
    def _contains_direct_quote(cls, sentence_text):
        if ":" in sentence_text:
            return True
        return any(char in sentence_text for char in cls._QUOTE_CHARS)

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
                return cursor + 1
            cursor += 1
        return len(teks)

    @staticmethod
    def _token_text(token):
        return str(token.get("text", ""))

    def _find_next_token(self, tokens, current_token):
        current_start = current_token.get("start_char", -1)
        for token in tokens:
            token_start = token.get("start_char", -1)
            if token_start > current_start:
                return token
        return None

    def _find_token_by_start(self, tokens, start_char, matched_text):
        matched_text = matched_text.lower()
        for token in tokens:
            token_start = token.get("start_char", -1)
            if token_start != start_char:
                continue
            if self._token_text(token).lower() != matched_text:
                continue
            return token
        return None
