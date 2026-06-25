import re

from .base_rule import BaseRule


class TandaPetikRule(BaseRule):
    id = "tanda_petik"

    _RE_VERBA_KUTIPAN = re.compile(
        r"\b("
        # asli
        r"berkata|mengatakan|bertanya"
        r"|"
        # tambahan
        r"menyatakan|menjelaskan|mengungkapkan|menegaskan|"
        r"menuturkan|menambahkan|memaparkan|mengutarakan|"
        r"menyampaikan|menanggapi|menjawab|membenarkan"
        r")\b",
        re.IGNORECASE,
    )

    _RE_SPASI_DALAM_PETIK = re.compile(r'"([^"\n]*)"')
    _QUOTE_CHAR = '"'

    # Kata-kata yang sering diikuti titik tapi bukan akhir kalimat
    _SINGKATAN = re.compile(
        r"\b(H|Dr|dr|Prof|Ir|Drs|Mr|Mrs|Ms|St|dll|dsb|dst|hlm|hal|no|vol|yth|a\.n|u\.p)\.$",
        re.IGNORECASE,
    )

    def cek(self, teks, konteks=None):
        if not teks:
            return []

        hasil = []
        hasil.extend(self._cek_kutipan_langsung_tanpa_petik(teks))
        hasil.extend(self._cek_spasi_di_dalam_tanda_petik(teks))
        return hasil

    # ─────────────────────────────────────────────────────────────────────────
    # QtD1 — Kutipan langsung tanpa tanda petik
    # ─────────────────────────────────────────────────────────────────────────

    def _cek_kutipan_langsung_tanpa_petik(self, teks):
        hasil = []
        for match in self._RE_VERBA_KUTIPAN.finditer(teks):
            quote_span = self._find_direct_quote_span(teks, match.end())
            if not quote_span:
                continue

            # _find_direct_quote_span mengembalikan 4-tuple:
            # (replace_start, replace_end, text_start, had_separator)
            replace_start, replace_end, text_start, had_separator = quote_span

            quoted_text = teks[text_start:replace_end]
            if not quoted_text:
                continue

            # Cek apakah kutipan sudah diapit tanda petik
            char_before = teks[text_start - 1] if text_start > 0 else ""
            if char_before == self._QUOTE_CHAR:
                continue

            if self._QUOTE_CHAR in quoted_text:
                continue

            # replace_start mencakup spasi + pemisah asli (jika ada),
            # sehingga pengganti selalu menyertakan ", " yang bersih.
            prefix = ", "

            hasil.append(
                self._buat_kesalahan(
                    kode="QtD1",
                    jenis="tanda_petik_kutipan_langsung",
                    deskripsi="Petikan langsung tidak diapit tanda petik.",
                    perbaikan=(
                        "Bungkus kutipan langsung dengan tanda petik"
                        + ("." if had_separator else ", lalu tambahkan koma setelah verba kutipan.")
                    ),
                    pengganti=f'{prefix}"{quoted_text}"',
                    start=replace_start,
                    end=replace_end,
                    rule="QtR1",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    # ─────────────────────────────────────────────────────────────────────────
    # QtD2 — Spasi di dalam tanda petik
    # ─────────────────────────────────────────────────────────────────────────

    def _cek_spasi_di_dalam_tanda_petik(self, teks):
        hasil = []
        for match in self._RE_SPASI_DALAM_PETIK.finditer(teks):
            inner = match.group(1)
            if inner == inner.strip():
                continue

            hasil.append(
                self._buat_kesalahan(
                    kode="QtD2",
                    jenis="spasi_di_dalam_tanda_petik",
                    deskripsi="Terdapat spasi di dalam tanda petik.",
                    perbaikan="Hapus spasi setelah pembuka atau sebelum penutup tanda petik.",
                    pengganti=f'"{inner.strip()}"',
                    start=match.start(),
                    end=match.end(),
                    rule="QtR2",
                    prioritas="MEDIUM",
                )
            )
        return hasil

    # ─────────────────────────────────────────────────────────────────────────
    # Helper — QtD1
    # ─────────────────────────────────────────────────────────────────────────

    def _find_direct_quote_span(self, teks, search_start):
        """
        Cari span kutipan langsung setelah verba kutipan.

        Mengembalikan (replace_start, replace_end, text_start, had_separator) atau None.

        - replace_start : posisi tepat setelah verba (search_start); mencakup
                          spasi dan pemisah asli sehingga semuanya tergantikan bersih.
        - replace_end   : posisi akhir span kutipan (inklusif tanda baca penutup)
        - text_start    : posisi huruf pertama kutipan murni
        - had_separator : True jika ada koma/titik dua pemisah di teks asli
        """
        cursor = search_start  # tepat setelah verba

        # Lewati spasi setelah verba
        while cursor < len(teks) and teks[cursor].isspace():
            cursor += 1

        # Deteksi pemisah (koma atau titik dua)
        had_separator = False
        if cursor < len(teks) and teks[cursor] in ",:":
            had_separator = True
            cursor += 1                               # lewati pemisah
            while cursor < len(teks) and teks[cursor].isspace():
                cursor += 1                           # lewati spasi setelah pemisah

        if cursor >= len(teks):
            return None
        if teks[cursor] == self._QUOTE_CHAR:
            return None

        # Karakter pertama harus huruf kapital agar dianggap kutipan langsung
        if not teks[cursor].isupper():
            return None

        # replace_start dimulai dari search_start (tepat setelah verba),
        # sehingga spasi + pemisah asli ikut tergantikan bersama pengganti.
        replace_start = search_start
        text_start = cursor

        sentence_end = self._find_sentence_end(teks, cursor)
        if sentence_end <= cursor:
            return None

        if sentence_end < len(teks) and teks[sentence_end] in ".!?":
            replace_end = sentence_end + 1
        else:
            replace_end = sentence_end

        return replace_start, replace_end, text_start, had_separator

    def _find_sentence_end(self, teks, idx):
        """
        Cari akhir kalimat mulai dari idx.

        Titik (.) dianggap akhir kalimat hanya jika:
        - diikuti spasi + huruf kapital, ATAU
        - berada di ujung string / diikuti newline,
        DAN token sebelum titik bukan singkatan yang dikenal.

        Tanda ! dan ? selalu dianggap akhir kalimat.
        Newline juga dianggap batas akhir.
        """
        cursor = idx
        while cursor < len(teks):
            ch = teks[cursor]

            if ch in "!?\n":
                return cursor

            if ch == ".":
                # Cek apakah ini singkatan
                token_before = teks[idx:cursor + 1]  # substring dari awal s.d. titik ini
                if self._SINGKATAN.search(token_before):
                    cursor += 1
                    continue

                # Titik akhir kalimat: diikuti spasi+kapital, atau ujung/newline
                next_pos = cursor + 1
                if next_pos >= len(teks):
                    return cursor          # ujung string
                if teks[next_pos] == "\n":
                    return cursor
                if teks[next_pos] == " ":
                    # Lewati spasi, lalu cek kapital
                    look = next_pos + 1
                    while look < len(teks) and teks[look] == " ":
                        look += 1
                    if look < len(teks) and teks[look].isupper():
                        return cursor     # akhir kalimat
                # Titik tapi bukan akhir kalimat (mis. singkatan tak dikenal) — lanjut
                cursor += 1
                continue

            cursor += 1

        return len(teks)