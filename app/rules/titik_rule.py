import re

from .base_rule import BaseRule


class TitikRule(BaseRule):
    id = "titik"

    # Fallback regex untuk DD2 (dipakai jika konteks POS tag tidak tersedia)
    # Perubahan v1: tambah [a-z] di lookahead untuk menghindari FP pada akronim
    _RE_SINGKATAN_NAMA = re.compile(r"(?<![A-Za-z])([A-Z])(?!\.)(?=\s+[A-Z][a-z])")

    # Fallback regex untuk DD3 (dipakai jika konteks POS tag tidak tersedia)
    # Perubahan v1: hapus "H" karena terlalu ambigu
    _RE_SINGKATAN_GELAR = re.compile(
        r"\b(Dr|Prof|Ir|Drs|Dra|Hj|S\.?\s?Kom|M\.?\s?T|Ph\.?\s?D)(?!\.)\b"
    )

    # DD4: hapus re.IGNORECASE — singkatan konvensi selalu huruf kecil
    # Perubahan v2: tambah sbb, tsb, tgl, ttd yang sebelumnya jadi FN
    _RE_SINGKATAN_UMUM = re.compile(
        r"\b(dll|dsb|dst|hlm|yth|dkk|sbb|tsb|tgl|ttd)(?!\.)\b"
    )

    _RE_BARIS = re.compile(r"(?m)^[^\n]+$")
    _RE_AUTHOR_AFFILIATION = re.compile(
        r"^(\d+\s*)?(Program Studi|Fakultas|Departemen|Jurusan|Universitas|Institut|Sekolah Tinggi)\b",
        re.IGNORECASE,
    )
    _RE_ARTICLE_DATE_LINE = re.compile(
        r"\b(Diterima|Direvisi|Diterbitkan|Submitted|Revised|Published)\s*:",
        re.IGNORECASE,
    )
    _RE_STAT_TABLE_ROW = re.compile(
        r"\b(Pre|Post|Gain|M|SD)\s*=\s*[\d,.]+",
        re.IGNORECASE,
    )

    _INISIAL_YANG_JUGA_GELAR = set()

    # Daftar gelar lengkap untuk DD3 berbasis POS tag.
    # Daftar lengkap gelar untuk DD3.
    # Gelar tidak ambigu seperti inisial, sehingga tidak perlu validasi POS tag.
    # Deteksi cukup berdasarkan kecocokan token dengan daftar ini.
    _GELAR_SET = {
        # Akademik umum — lazim di depan nama
        "Dr", "Prof", "Ir", "Drs", "Dra",
        # Keagamaan — lazim di depan nama
        "Hj", "H",
        # Medis — huruf kecil karena konvensi EYD
        "dr", "drg",
        # Profesi
        "Apt",
        # Sarjana (S1) — lazim di belakang nama
        "S.H", "S.E", "S.T", "S.Pd", "S.Sos", "S.Kom",
        "S.Kep", "S.Farm", "S.Psi", "S.P", "S.Hut",
        "S.I.P", "S.I.Kom",
        # Magister (S2) — lazim di belakang nama
        "M.Si", "M.Pd", "M.Hum", "M.T", "M.H", "M.M",
        "M.Kes", "M.Kom", "M.E", "M.Ak",
        # Doktor & internasional
        "Ph.D",
        # Diploma
        "A.Md", "A.Ma",
        # Spesialis
        "Sp", "SpA", "SpB", "SpOG", "SpPD", "SpJP",
    }

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        tokens = self._get_tokens(konteks)
        hasil = []
        hasil.extend(self._cek_titik_akhir_kalimat(teks, tokens))
        hasil.extend(self._cek_singkatan_nama(teks, konteks))
        hasil.extend(self._cek_singkatan_gelar(teks, konteks))
        hasil.extend(self._cek_singkatan_umum(teks))
        return hasil

    def _cek_titik_akhir_kalimat(self, teks, tokens=None):
        hasil = []
        for match in self._RE_BARIS.finditer(teks):
            baris = match.group(0)
            baris_strip = baris.strip()
            if not baris_strip:
                continue
            if not re.search(r"[A-Za-z]", baris_strip):
                continue
            if self._is_non_kalimat_pernyataan(baris_strip):
                continue
            if self._has_terminal_punctuation(baris_strip):
                continue
            if self._ends_with_special_abbreviation(baris_strip):
                continue
            if self._is_caption_tabel(baris_strip, tokens):
                continue

            insert_pos = match.start() + len(baris.rstrip())
            display_start = max(match.start(), insert_pos - 1)
            hasil.append(
                self._buat_kesalahan(
                    kode="DD1",
                    jenis="titik_akhir_kalimat",
                    deskripsi="Kalimat pernyataan tidak diakhiri dengan titik.",
                    perbaikan='Tambah "." di akhir kalimat.',
                    pengganti=".",
                    start=insert_pos,
                    end=insert_pos,
                    rule="DR1",
                    prioritas="HIGH",
                    display_start=display_start,
                    display_end=insert_pos,
                )
            )
        return hasil

    def _cek_singkatan_nama(self, teks, konteks=None):
        """
        DD2: Deteksi inisial nama orang tanpa titik.

        Strategi:
        - Jika konteks POS tag tersedia (Stanza): gunakan tag PROPN untuk
          memvalidasi bahwa token berikutnya memang nama orang. Ini menghilangkan
          FP seperti "F hitung" (hitung = VERB) dan ambiguitas nama adat.
        - Fallback ke regex jika konteks tidak tersedia.
        """
        tokens = self._get_tokens(konteks)
        if tokens:
            return self._cek_singkatan_nama_pos(tokens)
        return self._cek_singkatan_nama_regex(teks)

    # xpos yang mengindikasikan nama orang:
    # F-- = nama orang yang dikenali model Stanza
    # X-- = nama orang yang tidak dikenali model (unknown proper noun)
    _XPOS_NAMA = {"F--", "X--"}

    def _cek_singkatan_nama_pos(self, tokens):
        hasil = []
        for i, token in enumerate(tokens):
            word = token["text"]

            # Hanya token 1 huruf kapital
            if not (len(word) == 1 and word.isupper()):
                continue

            # Sudah diikuti titik — token berikutnya adalah "."
            next_tok = tokens[i + 1] if i + 1 < len(tokens) else None
            if next_tok and next_tok["text"] == ".":
                continue

            # Inisial di DEPAN nama: token sesudahnya xpos F-- atau X--
            # F-- = nama dikenali, X-- = nama tidak dikenali (unknown proper noun)
            # Lebih presisi dari upos PROPN karena kata kapital biasa di awal
            # kalimat (Tabel, Nilai, Kolom) di-tag upos=PROPN tapi xpos=NSD/VSA
            after_is_name = next_tok and next_tok.get("xpos") in self._XPOS_NAMA

            if not after_is_name:
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="DD2",
                    jenis="titik_singkatan_nama",
                    deskripsi="Singkatan nama orang tidak diakhiri titik.",
                    perbaikan='Tambah "." setelah 1 huruf inisial.',
                    pengganti=f"{word}.",
                    start=token["start_char"],
                    end=token["end_char"],
                    rule="DR2",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    def _cek_singkatan_nama_regex(self, teks):
        """Fallback DD2 tanpa POS tag."""
        hasil = []
        for match in self._RE_SINGKATAN_NAMA.finditer(teks):
            inisial = match.group(1)
            start, end = match.span(1)
            hasil.append(
                self._buat_kesalahan(
                    kode="DD2",
                    jenis="titik_singkatan_nama",
                    deskripsi="Singkatan nama orang tidak diakhiri titik.",
                    perbaikan='Tambah "." setelah 1 huruf inisial.',
                    pengganti=f"{inisial}.",
                    start=start,
                    end=end,
                    rule="DR2",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    def _cek_singkatan_gelar(self, teks, konteks=None):
        """
        DD3: Deteksi singkatan gelar/jabatan tanpa titik.

        Strategi:
        - Jika konteks POS tag tersedia: gunakan token list dari Stanza untuk
          mendeteksi gelar berdasarkan _GELAR_SET tanpa validasi POS tag.
          Gelar tidak ambigu seperti inisial — S.Pd selalu gelar di mana pun posisinya.
        - Fallback ke regex jika konteks tidak tersedia.
        """
        tokens = self._get_tokens(konteks)
        if tokens:
            return self._cek_singkatan_gelar_tokens(tokens)
        return self._cek_singkatan_gelar_regex(teks)

    def _cek_singkatan_gelar_tokens(self, tokens):
        """
        Deteksi gelar dari token list tanpa validasi POS tag.
        Cukup cek: token ada di _GELAR_SET dan belum diikuti titik.
        """
        hasil = []
        for i, token in enumerate(tokens):
            word = token["text"]

            if word not in self._GELAR_SET:
                continue

            # Sudah diikuti titik — gelar sudah benar, skip
            next_tok = tokens[i + 1] if i + 1 < len(tokens) else None
            if next_tok and next_tok["text"] == ".":
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="DD3",
                    jenis="titik_singkatan_gelar",
                    deskripsi="Singkatan gelar/jabatan tidak diakhiri titik.",
                    perbaikan='Tambah "." setelah gelar/jabatan.',
                    pengganti=f"{word}.",
                    start=token["start_char"],
                    end=token["end_char"],
                    rule="DR3",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    def _cek_singkatan_gelar_regex(self, teks):
        """Fallback DD3 tanpa token list."""
        hasil = []
        for match in self._RE_SINGKATAN_GELAR.finditer(teks):
            singkatan = match.group(1)
            start, end = match.span(1)
            hasil.append(
                self._buat_kesalahan(
                    kode="DD3",
                    jenis="titik_singkatan_gelar",
                    deskripsi="Singkatan gelar/jabatan tidak diakhiri titik.",
                    perbaikan='Tambah "." setelah gelar/jabatan.',
                    pengganti=f"{singkatan}.",
                    start=start,
                    end=end,
                    rule="DR3",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    def _cek_singkatan_umum(self, teks):
        hasil = []
        for match in self._RE_SINGKATAN_UMUM.finditer(teks):
            singkatan = match.group(1)
            start, end = match.span(1)
            hasil.append(
                self._buat_kesalahan(
                    kode="DD4",
                    jenis="titik_singkatan_umum",
                    deskripsi="Singkatan umum tidak diakhiri titik.",
                    perbaikan='Tambah "." setelah singkatan umum.',
                    pengganti=f"{singkatan}.",
                    start=start,
                    end=end,
                    rule="DR4",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    _RE_CAPTION = re.compile(
        r"^(Tabel|Gambar|Grafik|Bagan|Lampiran|Diagram)\s+[\d.]+",
        re.IGNORECASE,
    )

    def _is_caption_tabel(self, text, tokens):
        """
        Deteksi caption tabel/gambar menggunakan POS tag.

        Caption  : label + nomor + NOUN/ADJ/PROPN → "Tabel 3. Distribusi Frekuensi"
        Kalimat  : label + nomor + VERB            → "Tabel 3.11 merupakan estimasi"

        Stanza bisa memecah "3." menjadi dua token (NUM + PUNCT), sehingga
        token pertama setelah nomor bisa berupa PUNCT — dilewati dulu.
        Fallback tanpa token: skip kalau <= 6 kata (kemungkinan besar caption).
        """
        m = self._RE_CAPTION.match(text)
        if not m:
            return False

        if not tokens:
            # Fallback tanpa POS tag
            return len(text.split()) <= 6

        # Cari posisi akhir prefix "Tabel 3.11 " di teks
        end_prefix = m.end()

        for token in tokens:
            if token["start_char"] < end_prefix:
                continue
            # Lewati PUNCT (titik setelah nomor, misal "Tabel 3.")
            if token["upos"] == "PUNCT":
                continue
            # Token pertama non-PUNCT setelah nomor
            return token["upos"] != "VERB"

        # Tidak ada token setelah nomor — hanya label, perlakukan sebagai caption
        return True

    def _is_non_kalimat_pernyataan(self, text):
        first_letter = next((char for char in text if char.isalpha()), "")
        if not first_letter or not first_letter.isupper():
            return True

        # Heading bab
        if re.match(r"^(BAB|Bab)\s+[IVX0-9]+", text):
            return True
        # Penomoran (1.2.3 Judul)
        if re.match(r"^\d+(\.\d+)*\s+[A-Z]", text):
            return True
        # Bullet list
        if re.match(r"^[-*•]\s*", text):
            return True
        # List huruf (a. b. c.)
        if re.match(r"^[A-Za-z]\.\s+", text):
            return True
        # Teks all-caps pendek (judul/akronim)
        if text.isupper() and len(text) <= 80:
            return True
        if self._is_title_like_line(text):
            return True
        # Metadata artikel/jurnal yang lazim tidak diakhiri titik.
        if self._is_article_metadata_line(text):
            return True
        # Baris tabel/statistik sering diekstrak sebagai paragraf datar.
        if self._is_statistical_table_row(text):
            return True
        # Label atau field form ("Nama:", "Tanggal Lahir:")
        if re.match(r"^[A-Za-z][\w\s./()-]*\s*:", text):
            return True
        # URL standalone
        if re.match(r"^https?://\S+$", text) or re.match(r"^www\.\S+$", text):
            return True
        # Teks terlalu pendek — bukan kalimat pernyataan yang valid
        if len(text.split()) < 3:
            return True

        return False

    def _is_title_like_line(self, text):
        if any(char in text for char in ".:;|"):
            return False
        words = re.findall(r"\b[\w-]+\b", text)
        if len(words) < 7 or len(words) > 20:
            return False
        lower_allowed = {
            "dan", "atau", "pada", "dalam", "di", "ke", "dari", "terhadap",
            "untuk", "dengan", "sebagai",
        }
        title_words = 0
        for word in words:
            if word.lower() in lower_allowed:
                continue
            if word[:1].isupper() or word.isupper():
                title_words += 1
        return title_words >= max(5, len(words) - 4)

    def _is_article_metadata_line(self, text):
        if "@" in text:
            return True
        if "|" in text and self._RE_ARTICLE_DATE_LINE.search(text):
            return True
        if self._RE_AUTHOR_AFFILIATION.match(text):
            return True
        words = text.split()
        if 3 <= len(words) <= 12 and re.search(r"\d", text):
            capitalized = sum(1 for word in words if word[:1].isupper())
            if capitalized >= max(2, len(words) - 2):
                return True
        return False

    def _is_statistical_table_row(self, text):
        if not self._RE_STAT_TABLE_ROW.search(text):
            return False
        if re.search(r"\b(Kelompok|Grup|Group|Eksperimen|Kontrol)\b", text):
            return True
        metric_count = len(self._RE_STAT_TABLE_ROW.findall(text))
        return metric_count >= 2

    # Label yang mengawali caption tabel/gambar
    _LABEL_CAPTION = {"Tabel", "Gambar", "Grafik", "Bagan", "Lampiran", "Diagram"}

    def _is_caption_tabel(self, text, tokens):
        """
        Deteksi caption tabel/gambar menggunakan POS tag.

        Pola caption: Label + NUM + token bukan VERB
            "Tabel 3. Distribusi..."   → Distribusi (NOUN) → caption, skip
            "Gambar 4.1 Kerangka..."   → Kerangka (NOUN)   → caption, skip

        Pola kalimat: Label + NUM + VERB
            "Tabel 3.11 merupakan..."  → merupakan (VERB)  → kalimat, jangan skip
            "Gambar 4.2 menunjukkan"   → menunjukkan (VERB) → kalimat, jangan skip
        """
        # Cek token pertama: harus label caption
        words = text.split()
        if not words or words[0] not in self._LABEL_CAPTION:
            return False

        if not tokens:
            # Fallback tanpa POS tag: skip kalau pendek (kemungkinan caption)
            return len(words) <= 6

        # Cari posisi NUM di token list — ini adalah nomor tabel/gambar
        # Token sesudah NUM adalah penentu: VERB = kalimat, bukan VERB = caption
        found_num = False
        for i, token in enumerate(tokens):
            if token["upos"] == "NUM" and not found_num:
                found_num = True
                continue
            if found_num:
                # Token pertama setelah NUM
                if token["upos"] == "VERB":
                    # Ada kata kerja — ini kalimat pernyataan, bukan caption
                    return False
                # Bukan VERB — ini caption
                return True

        # Hanya ada label + nomor tanpa konten lain — kemungkinan caption
        return found_num

    def _ends_with_special_abbreviation(self, text):
        # Sinkron dengan _RE_SINGKATAN_UMUM (termasuk tambahan sbb, tsb, tgl, ttd)
        if re.search(r"\b(dll|dsb|dst|hlm|yth|dkk|sbb|tsb|tgl|ttd)\s*$", text):
            return True
        # Sinkron dengan _GELAR_SET — cek token terakhir saja
        last_token = text.split()[-1] if text.split() else ""
        if last_token in self._GELAR_SET:
            return True
        return False

    @staticmethod
    def _has_terminal_punctuation(text):
        if text.endswith(":"):
            return True
        return text.rstrip('"\'”’').endswith((".", "!", "?"))

    @staticmethod
    def _get_tokens(konteks):
        """
        Ekstrak daftar token dari konteks Stanza.

        Format token yang diharapkan (hasil konversi dari Stanza):
            {
                "text": str,
                "upos": str,       # Universal POS tag: PROPN, NOUN, VERB, dll.
                "start_char": int,
                "end_char": int,
            }

        Konversi dari objek Stanza dilakukan di preprocessing sebelum masuk rule:
            tokens = []
            for sent in doc.sentences:
                for word in sent.words:
                    tokens.append({
                        "text": word.text,
                        "upos": word.upos,
                        "start_char": word.start_char,
                        "end_char": word.end_char,
                    })
            konteks = {"tokens": tokens}
        """
        if not konteks:
            return []
        return konteks.get("tokens", [])