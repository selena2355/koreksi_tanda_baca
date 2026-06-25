import re

from .base_rule import BaseRule


class KomaRule(BaseRule):
    id = "koma"

    _RE_PERINCIAN = re.compile(r"\b(dan|atau)\b")
    _RE_KONJUNGSI_TENGAH = re.compile(
        r"\b(tetapi|melainkan|sedangkan|namun|padahal)\b|akan tetapi"
    )
    _RE_PENGHUBUNG_ANTARKALIMAT = re.compile(
        r"\b("
        r"Oleh karena itu|Oleh sebab itu|Dengan demikian|Dengan kata lain|"
        r"Meskipun demikian|Namun|Jadi|Selain itu|Sebaliknya|Akan tetapi|"
        r"Di samping itu|Adapun|Lebih lanjut|Sehubungan dengan itu|"
        r"Karena itu|Karena ini"
        r")\b"
    )
    _RE_PEMBUKA_ANAK_KALIMAT = re.compile(
        r"\b(Ketika|Jika|Karena|Meskipun|Setelah|Sebelum|"
        r"Apabila|Walaupun|Selama|Sejak|Sementara|Andai|Kendati|"
        r"Bilamana|Manakala|Seandainya|Asal|Asalkan)\b"
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
    _CLAUSE_UPOS = {"PRON", "PROPN", "NOUN", "VERB", "ADJ", "ADV", "NUM", "PART", "AUX"}
    _PREDICATE_WORDS = {
        "ada", "hadir", "hilang", "lanjut", "muncul", "tersedia", "terbatas",
        "terjadi", "turun", "berlangsung", "selesai", "cukup", "penting",
        "perlu", "dapat", "bisa", "mampu",
    }
    _PREDICATE_AUX_WORDS = {
        "tidak", "belum", "sudah", "telah", "sedang", "akan", "dapat",
        "bisa", "harus", "perlu",
    }


    def cek(self, teks, konteks=None):
        if not teks:
            return []

        tokens = self._get_tokens(konteks)
        hasil = []
        hasil.extend(self._cek_koma_setelah_anak_kalimat(teks, tokens))
        hasil.extend(self._cek_koma_sebelum_kata_penghubung(teks, tokens))
        hasil.extend(self._cek_koma_setelah_kata_penghubung_antarkalimat(teks, tokens))
        return hasil
    
    def _cek_koma_setelah_anak_kalimat(self, teks, tokens):
        hasil = []
        for match in self._RE_PEMBUKA_ANAK_KALIMAT.finditer(teks):
            start, end = match.span(1)
            if not self._is_sentence_or_line_start(teks, start):
                continue

            trigger = match.group(1).lower()
            pos_after = teks[end:end + 6].strip().lower()
            if trigger == "karena" and pos_after.startswith(("itu", "ini")):
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
                    rule="CmR1",
                    prioritas="MEDIUM",
                    display_start=start,
                    display_end=replacement_start,
                )
            )
        return hasil

    _RE_KORELATIF = re.compile(
        r"\b(tidak hanya|bukan hanya|bukan saja|tak hanya|tidak saja)\b"
    )

    def _cek_koma_sebelum_kata_penghubung(self, teks, tokens):
        hasil = []
        for match in self._RE_KONJUNGSI_TENGAH.finditer(teks):
            konjungsi = match.group(1) if match.group(1) else match.group(0)
            start = match.start(1) if match.group(1) else match.start(0)
            end = match.end(1) if match.group(1) else match.end(0)

            if not self._has_following_word(teks, end):
                continue
            if self._is_sentence_or_line_start(teks, start):
                continue
            if self._is_already_prefixed_by_comma(teks, start):
                continue
            if self._is_already_prefixed_by_colon(teks, start):
                continue
            sentence_start_pos = self._find_sentence_start(teks, start)
            left_segment = teks[sentence_start_pos:start]
            if self._RE_KORELATIF.search(left_segment):
                continue
            if tokens and not self._is_valid_konjungsi_context(tokens, start, konjungsi):
                continue

            replacement_start = self._find_leading_space_start(teks, start)
            hasil.append(
                self._buat_kesalahan(
                    kode="CmD3",
                    jenis="koma_sebelum_konjungsi",
                    deskripsi="Koma hilang sebelum kata hubung pertentangan.",
                    perbaikan='Tambah "," sebelum kata penghubung.',
                    pengganti=f", {konjungsi}",
                    start=replacement_start,
                    end=end,
                    rule="CmR2",
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
                    rule="CmR3",
                    prioritas="HIGH",
                )
            )
        return hasil

    @staticmethod
    def _normalized_item(text):
        # Bersihkan konten kurung sebelum ekstraksi kata
        text = re.sub(r"\([^)]*\)", "", text)
        words = re.findall(r"\b[\w-]+\b", text)
        if not words:
            return ""
        return " ".join(words)

    def _is_valid_konjungsi_context(self, tokens, start_char, conjunction_text):
        phrase_parts = conjunction_text.lower().split()
        idx = self._find_token_index(tokens, start_char, phrase_parts[0])
        if idx is None:
            return False

        end_idx = idx + len(phrase_parts)

        sentence_start, sentence_end = self._find_sentence_bounds(tokens, idx)
        prev_content = self._find_prev_content_token(tokens, idx, sentence_start)
        next_content = self._find_next_content_token(tokens, end_idx - 1, sentence_end)
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
        if not self._is_effective_sentence_start(tokens, idx, sentence_start):
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
        if not self._is_effective_sentence_start(tokens, idx, sentence_start):
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

            if (
                seen_predicate
                and content_count >= 2
                and upos in self._SUBJECT_UPOS
                and self._has_predicate_nearby(tokens, cursor, idx)
                and token.get("start_char", -1) >= 0
            ):
                return token["start_char"]
        return None

    def _has_predicate_nearby(self, tokens, subj_idx, lower_bound, window=3):
        for cursor in range(subj_idx - 1, max(lower_bound, subj_idx - window) - 1, -1):
            token = tokens[cursor]
            upos = self._token_upos(token)
            if upos == "PUNCT":
                continue
            if upos in self._PREDICATE_UPOS:
                return True
            if upos in self._CLAUSE_UPOS:
                return False
        return False

    def _is_effective_sentence_start(self, tokens, idx, sentence_start):
        for cursor in range(sentence_start, idx):
            token = tokens[cursor]
            upos = self._token_upos(token)
            text = self._token_text(token)
            if upos in {"PUNCT", "NUM", "SYM"}:
                continue
            if len(text) <= 2:
                continue
            return False
        return True

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
                return teks[cursor] in ".!?|"
            cursor -= 1
        return True

    def _is_already_prefixed_by_comma(self, teks, start):
        prev_idx = self._find_prev_non_space(teks, start - 1)
        if prev_idx < 0:
            return False
        return teks[prev_idx] == ","

    def _is_already_prefixed_by_colon(self, teks, start):
        prev_idx = self._find_prev_non_space(teks, start - 1)
        if prev_idx < 0:
            return False
        return teks[prev_idx] == ":"

    @staticmethod
    def _has_following_word(teks, end):
        cursor = end
        while cursor < len(teks) and teks[cursor].isspace():
            if teks[cursor] == "\n":
                return False
            cursor += 1
        return cursor < len(teks) and teks[cursor].isalnum()

    def _find_anak_kalimat_boundary_regex(self, teks, clause_start, sentence_end):
        predicate_boundary = self._find_boundary_after_subordinate_predicate(
            teks, clause_start, sentence_end
        )
        if predicate_boundary is not None:
            return predicate_boundary

        local_segment = teks[clause_start:sentence_end]
        candidates = []
        for candidate in self._RE_CALON_INDUK_KALIMAT.finditer(local_segment):
            absolute_start = clause_start + candidate.start(1)
            before_candidate = teks[clause_start:absolute_start].strip()
            if len(before_candidate.split()) < 2:
                continue
            candidates.append(absolute_start)

        return candidates[-1] if candidates else None

    def _find_boundary_after_subordinate_predicate(self, teks, clause_start, sentence_end):
        local_segment = teks[clause_start:sentence_end]
        words = list(re.finditer(r"\b[\w-]+\b", local_segment))
        if len(words) < 3:
            return None

        for idx, word_match in enumerate(words[:-1]):
            word = word_match.group(0).lower()
            prev_word = words[idx - 1].group(0).lower() if idx > 0 else ""
            if idx < 1:
                continue
            if not self._looks_like_clause_predicate(word, prev_word):
                continue

            return clause_start + words[idx + 1].start()
        return None

    def _looks_like_clause_predicate(self, word, prev_word):
        if word in self._PREDICATE_WORDS:
            return True
        if prev_word in self._PREDICATE_AUX_WORDS and len(word) > 3:
            return True
        return word.startswith(("ber", "me", "mem", "men", "meng", "meny", "di", "ter"))

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
            if abs(token_start - start_char) > 2:
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
            if self._token_upos(token) in {"PUNCT", "PART"}:
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