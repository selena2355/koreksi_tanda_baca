import os
import re

try:
    import stanza
except Exception:
    stanza = None

from ..config import ROOT_DIR


class SentenceBoundaryDetector:
    ABBREVIATIONS = {
        "dr",
        "drs",
        "prof",
        "ir",
        "mr",
        "mrs",
        "ms",
        "no",
        "tgl",
        "th",
        "spt",
        "yg",
        "dll",
        "dsb",
        "dst",
        "etc",
        "dkk",
        "sd",
        "s.d",
        "a.n",
        "u.p",
        "s.pd",
        "s.h",
        "s.kom",
        "s.si",
        "s.t",
        "m",
        "m.si",
        "m.kom",
        "m.hum",
        "m.pd",
        "m.t",
    }

    TITLE_ABBREVIATIONS = {
        "dr",
        "drs",
        "prof",
        "ir",
        "mr",
        "mrs",
        "ms",
    }

    CLOSING_CHARS = set(")]}'\"")

    # Inisialisasi dengan memilih engine (rule-based atau stanza)
    def __init__(self, engine=None):
        self.engine = (engine or os.getenv("SBD_ENGINE", "rule")).strip().lower()
        self._pipeline = None
        self._stanza_lang = os.getenv("STANZA_LANG", "id")
        self._stanza_dir = os.getenv("STANZA_DIR", os.path.join(ROOT_DIR, "models", "stanza"))
        self._auto_download = os.getenv("STANZA_AUTO_DOWNLOAD", "0") == "1"

    # Deteksi kalimat menggunakan engine yang dipilih
    def segment_sentences(self, text):
        if not text:
            return []
        if self.engine == "stanza":
            pipeline = self._get_stanza_pipeline()
            doc = pipeline(text)
            return [sent.text for sent in doc.sentences]
        return self._segment_with_rules(text)

    # Mendapatkan atau membuat pipeline Stanza untuk tokenisasi
    def _get_stanza_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        if stanza is None:
            raise RuntimeError("Stanza belum terpasang. Tambahkan ke requirements dan install.")

        if self._auto_download:
            stanza.download(self._stanza_lang, model_dir=self._stanza_dir, processors="tokenize")

        self._pipeline = stanza.Pipeline(
            lang=self._stanza_lang,
            processors="tokenize",
            tokenize_no_ssplit=False,
            use_gpu=False,
            dir=self._stanza_dir,
            verbose=False,
        )
        return self._pipeline

    # Deteksi kalimat menggunakan aturan berbasis heuristik
    def _segment_with_rules(self, text):
        sentences = []
        n = len(text)
        start = 0
        i = 0
        while i < n:
            ch = text[i]
            if ch in ".!?":
                if ch == ".":
                    j = i
                    while j + 1 < n and text[j + 1] == ".":
                        j += 1
                    is_ellipsis = j > i

                    if not is_ellipsis and self._is_number_period(text, i):
                        i += 1
                        continue

                    if not is_ellipsis and self._is_list_marker(text, start, i):
                        i = j + 1
                        continue

                    next_idx, has_space = self._next_non_space(text, j + 1)
                    next_char = text[next_idx] if next_idx < n else ""

                    prev_token = self._get_prev_token(text, i)
                    token_clean = prev_token.lower().strip(".")
                    is_abbrev = token_clean in self.ABBREVIATIONS

                    if is_abbrev:
                        if next_char and next_char.islower():
                            i = j + 1
                            continue
                        if next_char and next_char.isupper() and token_clean in self.TITLE_ABBREVIATIONS:
                            i = j + 1
                            continue
                        if next_char and next_char.isdigit():
                            i = j + 1
                            continue

                    boundary = False
                    if next_idx >= n:
                        boundary = True
                    elif has_space and next_char.isupper():
                        boundary = True

                    if boundary:
                        end = j + 1
                        while end < n and text[end] in self.CLOSING_CHARS:
                            end += 1
                        sentence = text[start:end].strip()
                        if sentence:
                            sentences.append(sentence)
                        start = end
                        while start < n and text[start].isspace():
                            start += 1
                        i = start
                        continue

                    i = j + 1
                    continue

                next_idx, has_space = self._next_non_space(text, i + 1)
                boundary = False
                if next_idx >= n:
                    boundary = True
                elif has_space:
                    boundary = True

                if boundary:
                    end = i + 1
                    while end < n and text[end] in self.CLOSING_CHARS:
                        end += 1
                    sentence = text[start:end].strip()
                    if sentence:
                        sentences.append(sentence)
                    start = end
                    while start < n and text[start].isspace():
                        start += 1
                    i = start
                    continue
            i += 1

        tail = text[start:].strip()
        if tail:
            sentences.append(tail)
        return sentences

    # Mencari indeks karakter berikutnya yang bukan spasi, dan apakah ada spasi di antaranya
    def _next_non_space(self, text, start):
        n = len(text)
        idx = start
        saw_space = False
        while idx < n:
            ch = text[idx]
            if ch.isspace():
                saw_space = True
                idx += 1
                continue
            if ch in self.CLOSING_CHARS:
                idx += 1
                continue
            break
        return idx, saw_space

    @staticmethod
    # Mendapatkan token sebelum indeks tertentu, untuk keperluan deteksi singkatan
    def _get_prev_token(text, idx):
        j = idx - 1
        while j >= 0 and text[j].isspace():
            j -= 1
        end = j
        while j >= 0 and (text[j].isalnum() or text[j] in "._"):
            j -= 1
        return text[j + 1 : end + 1]

    @staticmethod
    # Cek apakah titik merupakan bagian dari angka (misalnya 3.14)
    def _is_number_period(text, idx):
        return (
            idx > 0
            and idx + 1 < len(text)
            and text[idx - 1].isdigit()
            and text[idx + 1].isdigit()
        )

    @staticmethod
    # Cek apakah titik merupakan marker list (misalnya "1. ", "a. ", "i. ", "IV. ", dll.)
    def _is_list_marker(text, start, dot_idx):
        if dot_idx < start:
            return False
        prefix = text[start: dot_idx + 1].strip()
        if not prefix.endswith("."):
            return False
        if re.match(r"^\d+(\.\d+)*\.$", prefix):
            return True
        if re.match(r"^[A-Za-z]\.$", prefix):
            return True
        if re.match(r"^[IVXLCDM]+\.$", prefix, re.IGNORECASE):
            return True
        return False
