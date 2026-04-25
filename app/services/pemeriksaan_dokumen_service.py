import html as html_lib

from ..models.dokumen import Dokumen
from ..models.hasil_koreksi import HasilKoreksi
from ..rules.base_rule import BaseRule
from ..rules.koma_rule import KomaRule
from ..rules.tanda_hubung_rule import TandaHubungRule
from ..rules.tanda_petik_rule import TandaPetikRule
from ..rules.tanda_seru_rule import TandaSeruRule
from ..rules.tanda_tanya_rule import TandaTanyaRule
from ..rules.titik_dua_rule import TitikDuaRule
from ..rules.titik_rule import TitikRule
from ..services.preprocessing_service import PreprocessingService
from ..services.koreksi_service import KoreksiService


class PemeriksaanDokumenService:
    # Fungsi untuk menginisialisasi layanan pemeriksaan dokumen dengan opsi untuk menyuntikkan layanan preprocessing,
    # koreksi, dan aturan deteksi yang dapat disesuaikan, atau menggunakan default jika tidak diberikan.
    def __init__(self, preprocessing_service=None, koreksi_service=None, rules=None):
        self.preprocessing_service = preprocessing_service or PreprocessingService()
        self.koreksi_service = koreksi_service or KoreksiService()
        self.rules = rules or self._build_rules()

    # Fungsi utama untuk memproses dokumen, yang mencakup validasi, ekstraksi teks, preprocessing,
    # deteksi kesalahan, koreksi teks, dan pengembalian hasil koreksi dalam format yang terstruktur.
    def proses_dokumen(self, dokumen: Dokumen) -> HasilKoreksi:
        teks_bersih = self.preprocessing(dokumen.teks_asli)
        hasil = self.deteksi_dan_koreksi(teks_bersih)
        return HasilKoreksi(
            teks_koreksi=hasil["koreksi_text"],
            jumlah_koreksi=len(hasil["kesalahan_list"]),
        )

    # Fungsi untuk memvalidasi dokumen, memastikan bahwa dokumen tidak kosong,
    # dan memiliki teks asli yang dapat diproses.
    def validasi_dokumen(self, dokumen: Dokumen) -> bool:
        return bool(dokumen and dokumen.teks_asli)

    def ekstraksi_teks(self, teks: str) -> str:
        return teks

    def preprocessing(self, teks: str) -> str:
        return self.preprocessing_service.preprocessing(teks)

    def terapkan_aturan(self, teks: str) -> str:
        hasil = self.deteksi_dan_koreksi(teks)
        return hasil["koreksi_text"]

    def deteksi_dan_koreksi(self, teks: str, konteks: dict = None):
        source_text = teks or ""
        analysis_text = self.preprocessing_service.prepare_rule_text(source_text)

        try:
            kesalahan_list = self._collect_kesalahan(analysis_text,konteks)
            koreksi_text = self.koreksi_service.koreksi(source_text, kesalahan_list)
            detection_html = self._build_detection_html(source_text, kesalahan_list)
            correction_html = self._build_correction_html(source_text, kesalahan_list)
            return {
                "kesalahan_list": kesalahan_list,
                "koreksi_text": koreksi_text,
                "detection_html": detection_html,
                "correction_html": correction_html,
                "error": None,
            }
        except Exception as exc:
            fallback_text = source_text
            return {
                "kesalahan_list": [],
                "koreksi_text": fallback_text,
                "detection_html": html_lib.escape(fallback_text),
                "correction_html": html_lib.escape(fallback_text),
                "error": str(exc) or "Gagal melakukan deteksi/koreksi.",
            }


    def _build_rules(self):
        return [
            BaseRule(),
            TitikRule(),
            KomaRule(),
            TandaTanyaRule(),
            TandaSeruRule(),
            TandaPetikRule(),
            TitikDuaRule(),
            TandaHubungRule(),
        ]

    def _collect_kesalahan(self, teks, konteks=None):
        hasil = []
        for rule in self.rules:
            hasil.extend(rule.cek(teks, konteks=konteks))
        hasil = self._merge_kesalahan_spasi(hasil)
        return self._filter_overlapping_kesalahan(hasil)

    @staticmethod
    # Fungsi untuk menggabungkan kesalahan BD1 dan BD2 yang terjadi pada posisi yang sama atau sangat berdekatan
    def _merge_kesalahan_spasi(kesalahan_list):
        if not kesalahan_list:
            return []

        items = sorted(
            kesalahan_list,
            key=lambda k: (
                getattr(k, "start", 0),
                getattr(k, "end", 0),
            ),
        )
        merged = []
        i = 0
        while i < len(items):
            current = items[i]
            if i + 1 < len(items):
                nxt = items[i + 1]
                if PemeriksaanDokumenService._should_merge_bd1_bd2(current, nxt):
                    merged.append(PemeriksaanDokumenService._merge_bd1_bd2(current, nxt))
                    i += 2
                    continue
            merged.append(current)
            i += 1
        return merged

    @staticmethod
    # Fungsi untuk menentukan apakah dua kesalahan BD1 dan BD2 harus digabungkan berdasarkan posisi dan jenisnya
    def _should_merge_bd1_bd2(first, second):
        start1 = getattr(first, "start", None)
        end1 = getattr(first, "end", None)
        start2 = getattr(second, "start", None)
        end2 = getattr(second, "end", None)
        if start1 is None or end1 is None or start2 is None or end2 is None:
            return False
        if start2 >= end1:
            return False
        codes = {getattr(first, "kode", ""), getattr(second, "kode", "")}
        return codes == {"BD1", "BD2"}

    @staticmethod
    # Fungsi untuk menggabungkan dua kesalahan spasi menjadi satu kesalahan yang lebih komprehensif
    def _merge_bd1_bd2(first, second):
        base = first if getattr(first, "kode", "") == "BD1" else second
        other = second if base is first else first
        base.start = min(getattr(first, "start", 0), getattr(second, "start", 0))
        base.end = max(getattr(first, "end", 0), getattr(second, "end", 0))
        if getattr(other, "kode", "") == "BD2":
            base.pengganti = getattr(other, "pengganti", base.pengganti)
        base.jenis = "spasi_tidak_tepat"
        base.deskripsi = (
            "Terdapat spasi sebelum tanda baca dan tidak ada spasi setelah tanda baca."
        )
        base.perbaikan = "Hapus spasi sebelum tanda baca dan tambahkan spasi setelahnya."
        base.kode = "BD1+BD2"
        base.rule = "BR1+BR2"
        base.prioritas = "HIGH"
        return base

    @staticmethod
    # Fungsi untuk menentukan peringkat prioritas berdasarkan atribut 'prioritas' pada objek kesalahan, dengan default peringkat rendah jika tidak ada atau tidak dikenali
    def _priority_rank(item):
        ranks = {
            "HIGH": 0,
            "MEDIUM": 1,
            "LOW": 2,
        }
        return ranks.get(str(getattr(item, "prioritas", "")).upper(), 99)

    @classmethod
    # Fungsi untuk menyaring kesalahan yang tumpang tindih berdasarkan posisi dan prioritas, sehingga hanya kesalahan dengan prioritas tertinggi yang dipertahankan dalam kasus tumpang tindih
    def _filter_overlapping_kesalahan(cls, kesalahan_list):
        if not kesalahan_list:
            return []

        items = sorted(
            kesalahan_list,
            key=lambda item: (
                getattr(item, "start", 0),
                getattr(item, "end", 0),
                cls._priority_rank(item),
                -(getattr(item, "end", 0) - getattr(item, "start", 0)),
            ),
        )

        resolved = []
        for item in items:
            start = getattr(item, "start", None)
            end = getattr(item, "end", None)
            if start is None or end is None:
                continue

            if not resolved:
                resolved.append(item)
                continue

            prev = resolved[-1]
            prev_start = getattr(prev, "start", 0)
            prev_end = getattr(prev, "end", 0)
            if start < prev_end and end > prev_start:
                if cls._priority_rank(item) < cls._priority_rank(prev):
                    resolved[-1] = item
                continue

            resolved.append(item)

        return resolved

    # Fungsi untuk membangun representasi HTML dari teks dengan menyoroti kesalahan yang ditemukan, menggunakan elemen <mark> untuk menandai bagian teks yang mengandung kesalahan dan menambahkan tooltip yang berisi deskripsi kesalahan dan perbaikan yang disarankan
    def _build_detection_html(self, teks, kesalahan_list):
        if teks is None:
            return ""
        if not kesalahan_list:
            return html_lib.escape(teks)

        items = self._sorted_render_items(kesalahan_list)
        output_html = []
        cursor = 0
        for idx, item in enumerate(items, start=1):
            start = getattr(item, "start", None)
            end = getattr(item, "end", None)
            display_start = getattr(item, "display_start", start)
            display_end = getattr(item, "display_end", end)
            if start is None or end is None or display_start is None or display_end is None:
                continue
            if display_start < cursor:
                continue
            output_html.append(html_lib.escape(teks[cursor:display_start]))

            tooltip = self._format_tooltip(item)
            snippet = teks[display_start:display_end]
            pair_id = self._pair_id(idx)
            output_html.append(
                (
                    "<mark id=\"detection-{}\" class=\"error-highlight linked-highlight\" "
                    "data-link-target=\"correction-{}\" tabindex=\"0\" role=\"button\" "
                    "title=\"{}\">{}</mark>"
                ).format(
                    pair_id,
                    pair_id,
                    html_lib.escape(tooltip),
                    html_lib.escape(snippet),
                )
            )
            cursor = display_end

        output_html.append(html_lib.escape(teks[cursor:]))
        return "".join(output_html)

    def _build_correction_html(self, teks, kesalahan_list):
        if teks is None:
            return ""
        if not kesalahan_list:
            return html_lib.escape(teks)

        items = self._sorted_render_items(kesalahan_list)
        output_html = []
        cursor = 0
        for idx, item in enumerate(items, start=1):
            start = getattr(item, "start", None)
            end = getattr(item, "end", None)
            if start is None or end is None:
                continue
            if start < cursor:
                continue

            output_html.append(html_lib.escape(teks[cursor:start]))

            replacement = getattr(item, "pengganti", "")
            if replacement is None:
                replacement = ""
            pair_id = self._pair_id(idx)
            output_html.append(
                (
                    "<mark id=\"correction-{}\" class=\"correction-highlight linked-highlight\" "
                    "data-link-target=\"detection-{}\" tabindex=\"0\" role=\"button\">{}</mark>"
                ).format(
                    pair_id,
                    pair_id,
                    html_lib.escape(replacement),
                )
            )
            cursor = end

        output_html.append(html_lib.escape(teks[cursor:]))
        return "".join(output_html)

    @staticmethod
    def _sorted_render_items(kesalahan_list):
        return sorted(
            kesalahan_list,
            key=lambda item: (
                getattr(item, "start", 0),
                getattr(item, "end", 0),
            ),
        )

    @staticmethod
    def _pair_id(index):
        return f"issue-{index}"

    @staticmethod
    # Fungsi untuk memformat tooltip yang akan ditampilkan saat pengguna mengarahkan kursor ke bagian teks yang disorot, dengan menyertakan kode kesalahan, deskripsi masalah, dan perbaikan yang disarankan jika tersedia
    def _format_tooltip(kesalahan):
        kode = getattr(kesalahan, "kode", "")
        deskripsi = getattr(kesalahan, "deskripsi", "")
        perbaikan = getattr(kesalahan, "perbaikan", "")
        prefix = f"{kode} - " if kode else ""
        if perbaikan:
            return f"{prefix}\nDeskripsi: {deskripsi} \nPerbaikan: {perbaikan}"
        return f"{prefix}\nDeskripsi: {deskripsi}"
