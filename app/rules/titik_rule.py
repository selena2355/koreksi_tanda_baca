import re

from .base_rule import BaseRule


class TitikRule(BaseRule):
    id = "titik"

    _RE_AWAL_TANYA = re.compile(
        r"^(Apa|Apakah|Siapa|Kapan|Di mana|Dimana|Mengapa|Bagaimana|Berapa)\b"
    )
    _RE_AWAL_SERU = re.compile(r"^(Segera|Jangan|Harap|Tolong|Wajib)\b")
    _RE_AWAL_PEMERIAN = re.compile(r"^(Nama|Tempat|Waktu|Tanggal)\b", re.IGNORECASE)

    # Fallback regex untuk DD2 (dipakai jika konteks POS tag tidak tersedia)
    _RE_SINGKATAN_NAMA = re.compile(r"(?<![A-Za-z])([A-Z])(?!\.)(?=\s+[A-Z][a-z])")

    # Fallback regex untuk DD3 (dipakai jika konteks POS tag tidak tersedia)
    _RE_SINGKATAN_GELAR = re.compile(
        r"\b(Dr|Prof|Ir|Drs|Dra|Hj|S\.?\s?Kom|M\.?\s?T|Ph\.?\s?D)(?!\.)\b"
    )

    # DD4: hapus re.IGNORECASE — singkatan konvensi selalu huruf kecil
    _RE_SINGKATAN_UMUM = re.compile(
        r"\b(dll|dsb|dst|hlm|yth|dkk|sbb|tsb|tgl|ttd)(?!\.)\b"
    )

    # Regex untuk mendeteksi baris yang berpotensi merupakan kalimat pernyataan (untuk DD1)
    # (?m)^[^\n]+$ digunakan untuk memeriksa setiap baris teks secara terpisah, mencari baris yang tidak kosong dan mengandung huruf.
    _RE_BARIS = re.compile(r"(?m)^[^\n]+$")

    _INISIAL_YANG_JUGA_GELAR = set()

    # Daftar gelar lengkap untuk DD3 berbasis POS tag.
    # Dipisah dari regex agar mudah diperluas tanpa urusan escape karakter.
    _GELAR_SET = {
        # Gelar akademik umum
        "Dr", "Prof", "Ir", "Drs", "Dra",
        # Gelar keagamaan
        "Hj", "H",
        # Gelar medis — huruf kecil karena konvensi EYD
        "dr", "drg",
        # Gelar profesi
        "Apt",
        # Sarjana (S1)
        "S.H", "S.E", "S.T", "S.Pd", "S.Sos", "S.Kom",
        "S.Kep", "S.Farm", "S.Psi", "S.P", "S.Hut",
        "S.I.P", "S.I.Kom",
        # Magister (S2)
        "M.Si", "M.Pd", "M.Hum", "M.T", "M.H", "M.M",
        "M.Kes", "M.Kom", "M.E", "M.Ak",
        # Doktor & Internasional
        "Ph.D",
        # Diploma
        "A.Md", "A.Ma",
        # Spesialis
        "Sp", "SpA", "SpB", "SpOG", "SpPD", "SpJP",
    }

    # Fungsi utama untuk memeriksa teks dan mengembalikan daftar kesalahan yang ditemukan berdasarkan aturan titik.
    def cek(self, teks, konteks=None):
        if not teks:
            return []

        hasil = []
        hasil.extend(self._cek_titik_akhir_kalimat(teks))
        hasil.extend(self._cek_singkatan_nama(teks, konteks))
        hasil.extend(self._cek_singkatan_gelar(teks, konteks))
        hasil.extend(self._cek_singkatan_umum(teks))
        return hasil

    def _cek_titik_akhir_kalimat(self, teks):
        hasil = []
        # perulangan
        for match in self._RE_BARIS.finditer(teks):
            baris = match.group(0)
            baris_strip = baris.strip()
            if not baris_strip:
                continue
            if not re.search(r"[A-Za-z]", baris_strip):
                continue
            if self._is_non_kalimat_pernyataan(baris_strip):
                continue
            if baris_strip.endswith((".", "!", "?", ":")):
                continue
            if self._ends_with_special_abbreviation(baris_strip):
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

    # Fungsi untuk memeriksa singkatan nama orang yang tidak diakhiri dengan titik, 
    # dengan strategi berbasis POS tag jika tersedia, dan fallback ke regex jika tidak.
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

            # Jika token bukan 1 huruf kapital, skip (bukan kandidat inisial)
            if not (len(word) == 1 and word.isupper()):
                continue

            # Sudah diikuti titik — token berikutnya adalah "."
            next_tok = tokens[i + 1] if i + 1 < len(tokens) else None
            if next_tok and next_tok["text"] == ".":
                continue

            # Inisial di DEPAN nama: token sesudahnya xpos F-- (nama orang)
            # Menggunakan xpos F-- lebih presisi dari upos PROPN karena
            # kata kapital biasa di awal kalimat (Tabel, Nilai, Kolom)
            # di-tag upos=PROPN oleh Stanza tapi xpos-nya NSD/VSA, bukan F--
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
        - Jika konteks POS tag tersedia: validasi token setelah gelar adalah PROPN.
          Menghilangkan FP seperti "Dr op" (op = NOUN, bukan nama orang).
          Juga memungkinkan daftar gelar diperluas tanpa batas tanpa urusan regex.
        - Fallback ke regex jika konteks tidak tersedia.
        """
        tokens = self._get_tokens(konteks)
        if tokens:
            return self._cek_singkatan_gelar_pos(tokens)
        return self._cek_singkatan_gelar_regex(teks)

    def _cek_singkatan_gelar_pos(self, tokens):
        hasil = []
        for i, token in enumerate(tokens):
            word = token["text"]

            if word not in self._GELAR_SET:
                continue

            next_tok = tokens[i + 1] if i + 1 < len(tokens) else None

            # Sudah diikuti titik — cek token setelah titik
            if next_tok and next_tok["text"] == ".":
                after_dot = tokens[i + 2] if i + 2 < len(tokens) else None
                # Gelar bertitik + PROPN = benar, skip
                if after_dot and after_dot["upos"] == "PROPN":
                    continue
                # Gelar bertitik tapi bukan PROPN sesudahnya = bukan konteks gelar
                # Ini bisa jadi akhir kalimat atau konteks lain, skip juga
                continue

            # Tidak diikuti titik — validasi konteks dengan PROPN
            if not next_tok or next_tok["upos"] != "PROPN":
                # Bukan konteks gelar (misal: "Dr op", "nilai H"), skip
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
        """Fallback DD3 tanpa POS tag."""
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

    def _is_non_kalimat_pernyataan(self, text):
        first_letter = next((char for char in text if char.isalpha()), "")
        if not first_letter or not first_letter.isupper():
            return True
        if self._RE_AWAL_TANYA.search(text):
            return True
        if self._RE_AWAL_SERU.search(text):
            return True
        if self._RE_AWAL_PEMERIAN.search(text):
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
