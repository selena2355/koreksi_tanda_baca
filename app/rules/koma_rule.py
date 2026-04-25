import re

from .base_rule import BaseRule


class KomaRule(BaseRule):
    id = "koma"

    _RE_PERINCIAN = re.compile(r"\b(dan|atau)\b")
    _RE_KONJUNGSI_TENGAH = re.compile(r"\b(tetapi|melainkan|sedangkan)\b")
    _RE_PENGHUBUNG_ANTARKALIMAT = re.compile(
        r"\b(Oleh karena itu|Dengan demikian|Namun|Jadi)\b"
    )
    _RE_PEMBUKA_ANAK_KALIMAT = re.compile(
        r"\b(Ketika|Jika|Karena|Meskipun|Setelah|Sebelum)\b"
    )
    _RE_CALON_INDUK_KALIMAT = re.compile(
        r"\b("
        r"saya|aku|kami|kita|dia|ia|beliau|mereka|anda|"
        r"tim|sistem|penelitian|aplikasi|dokumen|hasil|program|"
        r"mahasiswa|guru|dosen|pemerintah|pengguna|penulis|"
        r"data|informasi|temuan|kesimpulan|Budi|Andi|[A-Z][a-z]+"
        r")\b"
    )

    _ITEM_UPOS = {"NOUN", "PROPN", "ADJ", "NUM", "PRON", "VERB"}
    _SUBJECT_UPOS = {"PRON", "PROPN", "NOUN"}
    _PREDICATE_UPOS = {"VERB", "ADJ", "AUX"}
    _CLAUSE_UPOS = {"PRON", "PROPN", "NOUN", "VERB", "ADJ", "ADV", "NUM"}

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        tokens = self._get_tokens(konteks)
        hasil = []
        hasil.extend(self._cek_koma_dalam_perincian(teks, tokens))
        hasil.extend(self._cek_koma_setelah_anak_kalimat(teks, tokens))
        hasil.extend(self._cek_koma_sebelum_kata_penghubung(teks, tokens))
        hasil.extend(self._cek_koma_setelah_kata_penghubung_antarkalimat(teks, tokens))
        return hasil

    def _cek_koma_dalam_perincian(self, teks, tokens):
        hasil = []
        for match in self._RE_PERINCIAN.finditer(teks):
            start, end = match.span(1)
            if not self._has_following_word(teks, end):
                continue
            if self._is_already_prefixed_by_comma(teks, start):
                continue
            if tokens and not self._is_valid_perincian_context(tokens, start, match.group(1)):
                continue

            sentence_start = self._find_sentence_start(teks, start)
            left_segment = teks[sentence_start:start]
            if "," not in left_segment:
                continue

            replacement_start = self._find_leading_space_start(teks, start)
            hasil.append(
                self._buat_kesalahan(
                    kode="CmD1",
                    jenis="koma_dalam_perincian",
                    deskripsi="Koma hilang sebelum kata hubung dalam perincian.",
                    perbaikan='Tambah "," sebelum "dan/atau" dalam perincian.',
                    pengganti=f", {match.group(1)}",
                    start=replacement_start,
                    end=end,
                    rule="CmR1",
                    prioritas="HIGH",
                    display_start=start,
                    display_end=end,
                )
            )
        return hasil

    def _cek_koma_setelah_anak_kalimat(self, teks, tokens):
        hasil = []
        for match in self._RE_PEMBUKA_ANAK_KALIMAT.finditer(teks):
            start, end = match.span(1)
            if not self._is_sentence_or_line_start(teks, start):
                continue

            sentence_end = self._find_sentence_end(teks, end)
            sentence_segment = teks[start:sentence_end]
            if "," in sentence_segment:
                continue

            boundary_start = None
            if tokens:
                boundary_start = self._find_anak_kalimat_boundary_pos(
                    tokens=tokens,
                    start_char=start,
                    trigger_text=match.group(1),
                )
            if boundary_start is None:
                boundary_start = self._find_anak_kalimat_boundary_regex(teks, end, sentence_end)
            if boundary_start is None:
                continue

            replacement_start = self._find_leading_space_start(teks, boundary_start)
            hasil.append(
                self._buat_kesalahan(
                    kode="CmD2",
                    jenis="koma_setelah_anak_kalimat",
                    deskripsi="Koma hilang setelah anak kalimat di awal.",
                    perbaikan='Tambah "," setelah anak kalimat.',
                    pengganti=", ",
                    start=replacement_start,
                    end=boundary_start,
                    rule="CmR2",
                    prioritas="MEDIUM",
                    display_start=start,
                    display_end=replacement_start,
                )
            )
        return hasil

    def _cek_koma_sebelum_kata_penghubung(self, teks, tokens):
        hasil = []
        for match in self._RE_KONJUNGSI_TENGAH.finditer(teks):
            start, end = match.span(1)
            if not self._has_following_word(teks, end):
                continue
            if self._is_sentence_or_line_start(teks, start):
                continue
            if self._is_already_prefixed_by_comma(teks, start):
                continue
            if tokens and not self._is_valid_konjungsi_context(tokens, start, match.group(1)):
                continue

            replacement_start = self._find_leading_space_start(teks, start)
            hasil.append(
                self._buat_kesalahan(
                    kode="CmD3",
                    jenis="koma_sebelum_konjungsi",
                    deskripsi="Koma hilang sebelum kata hubung pertentangan.",
                    perbaikan='Tambah "," sebelum kata penghubung.',
                    pengganti=f", {match.group(1)}",
                    start=replacement_start,
                    end=end,
                    rule="CmR3",
                    prioritas="MEDIUM",
                    display_start=start,
                    display_end=end,
                )
            )
        return hasil

    def _cek_koma_setelah_kata_penghubung_antarkalimat(self, teks, tokens):
        hasil = []
        for match in self._RE_PENGHUBUNG_ANTARKALIMAT.finditer(teks):
            start, end = match.span(1)
            if not self._is_sentence_or_line_start(teks, start):
                continue
            if end < len(teks) and teks[end] == ",":
                continue
            if tokens and not self._is_valid_penghubung_antarkalimat(tokens, start, match.group(1)):
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="CmD4",
                    jenis="koma_setelah_penghubung_antarkalimat",
                    deskripsi="Koma hilang setelah kata penghubung antarkalimat.",
                    perbaikan='Tambah "," setelah kata penghubung antarkalimat.',
                    pengganti=f"{match.group(1)},",
                    start=start,
                    end=end,
                    rule="CmR4",
                    prioritas="HIGH",
                )
            )
        return hasil

    def _is_valid_perincian_context(self, tokens, start_char, conjunction_text):
        idx = self._find_token_index(tokens, start_char, conjunction_text)
        if idx is None:
            return False

        sentence_start, sentence_end = self._find_sentence_bounds(tokens, idx)
        if not any(self._token_text(tokens[i]) == "," for i in range(sentence_start, idx)):
            return False

        prev_content = self._find_prev_content_token(tokens, idx, sentence_start)
        next_content = self._find_next_content_token(tokens, idx, sentence_end)
        if not prev_content or not next_content:
            return False

        return (
            self._token_upos(prev_content) in self._ITEM_UPOS
            and self._token_upos(next_content) in self._ITEM_UPOS
        )

    def _is_valid_konjungsi_context(self, tokens, start_char, conjunction_text):
        idx = self._find_token_index(tokens, start_char, conjunction_text)
        if idx is None:
            return False

        sentence_start, sentence_end = self._find_sentence_bounds(tokens, idx)
        prev_content = self._find_prev_content_token(tokens, idx, sentence_start)
        next_content = self._find_next_content_token(tokens, idx, sentence_end)
        if not prev_content or not next_content:
            return False

        return (
            self._token_upos(prev_content) in self._CLAUSE_UPOS
            and self._token_upos(next_content) in self._CLAUSE_UPOS
        )

    def _is_valid_penghubung_antarkalimat(self, tokens, start_char, connector_text):
        phrase_tokens = [part.lower() for part in connector_text.split()]
        idx = self._find_token_index(tokens, start_char, phrase_tokens[0])
        if idx is None:
            return False

        sentence_start, sentence_end = self._find_sentence_bounds(tokens, idx)
        if idx != sentence_start:
            return False

        for offset, expected in enumerate(phrase_tokens):
            cursor = idx + offset
            if cursor >= sentence_end:
                return False
            if self._token_text(tokens[cursor]).lower() != expected:
                return False

        next_idx = idx + len(phrase_tokens)
        if next_idx < len(tokens) and self._token_text(tokens[next_idx]) == ",":
            return False
        return True

    def _find_anak_kalimat_boundary_pos(self, tokens, start_char, trigger_text):
        idx = self._find_token_index(tokens, start_char, trigger_text)
        if idx is None:
            return None

        sentence_start, sentence_end = self._find_sentence_bounds(tokens, idx)
        if idx != sentence_start:
            return None

        seen_predicate = False
        content_count = 0
        for cursor in range(idx + 1, sentence_end):
            token = tokens[cursor]
            if self._token_text(token) == ",":
                return None

            upos = self._token_upos(token)
            if upos == "PUNCT":
                continue
            if upos in self._PREDICATE_UPOS:
                seen_predicate = True
            if upos in self._CLAUSE_UPOS:
                content_count += 1

            prev_content = self._find_prev_content_token(tokens, cursor, idx)
            if (
                seen_predicate
                and content_count >= 3
                and upos in self._SUBJECT_UPOS
                and prev_content
                and self._token_upos(prev_content) in self._PREDICATE_UPOS
                and token.get("start_char", -1) >= 0
            ):
                return token["start_char"]
        return None

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

    @staticmethod
    def _find_leading_space_start(teks, idx):
        cursor = idx
        while cursor > 0 and teks[cursor - 1].isspace() and teks[cursor - 1] != "\n":
            cursor -= 1
        return cursor

    @staticmethod
    def _find_prev_non_space(teks, idx):
        cursor = idx
        while cursor >= 0 and teks[cursor].isspace():
            cursor -= 1
        return cursor

    def _is_sentence_or_line_start(self, teks, start):
        cursor = start - 1
        while cursor >= 0:
            if teks[cursor] == "\n":
                return True
            if not teks[cursor].isspace():
                return teks[cursor] in ".!?"
            cursor -= 1
        return True

    def _is_already_prefixed_by_comma(self, teks, start):
        prev_idx = self._find_prev_non_space(teks, start - 1)
        if prev_idx < 0:
            return False
        return teks[prev_idx] == ","

    @staticmethod
    def _has_following_word(teks, end):
        cursor = end
        while cursor < len(teks) and teks[cursor].isspace():
            if teks[cursor] == "\n":
                return False
            cursor += 1
        return cursor < len(teks) and teks[cursor].isalnum()

    def _find_anak_kalimat_boundary_regex(self, teks, clause_start, sentence_end):
        local_segment = teks[clause_start:sentence_end]
        candidates = []
        for candidate in self._RE_CALON_INDUK_KALIMAT.finditer(local_segment):
            absolute_start = clause_start + candidate.start(1)
            before_candidate = teks[clause_start:absolute_start].strip()
            if len(before_candidate.split()) < 2:
                continue
            candidates.append(absolute_start)

        return candidates[-1] if candidates else None

    @staticmethod
    def _token_text(token):
        return str(token.get("text", ""))

    @staticmethod
    def _token_upos(token):
        return str(token.get("upos", "")).upper()

    def _find_token_index(self, tokens, start_char, expected_text=None):
        expected_text = expected_text.lower() if expected_text else None
        for idx, token in enumerate(tokens):
            token_start = token.get("start_char", -1)
            if token_start != start_char:
                continue
            if expected_text and self._token_text(token).lower() != expected_text:
                continue
            return idx
        return None

    def _find_sentence_bounds(self, tokens, idx):
        start = idx
        while start > 0 and self._token_text(tokens[start - 1]) not in ".!?":
            start -= 1

        end = idx + 1
        while end < len(tokens) and self._token_text(tokens[end]) not in ".!?":
            end += 1
        return start, end

    def _find_prev_content_token(self, tokens, idx, lower_bound):
        for cursor in range(idx - 1, lower_bound - 1, -1):
            token = tokens[cursor]
            if self._token_upos(token) == "PUNCT":
                continue
            if token.get("start_char", -1) < 0:
                continue
            return token
        return None

    def _find_next_content_token(self, tokens, idx, upper_bound):
        for cursor in range(idx + 1, upper_bound):
            token = tokens[cursor]
            if self._token_upos(token) == "PUNCT":
                continue
            if token.get("start_char", -1) < 0:
                continue
            return token
        return None
