import html as html_lib

from ..models.dokumen import Dokumen
from ..models.hasil_koreksi import HasilKoreksi
from ..rules.base_rule import BaseRule
from ..services.preprocessing_service import PreprocessingService
from ..services.koreksi_service import KoreksiService


class PemeriksaanDokumenService:
    def __init__(self, preprocessing_service=None, koreksi_service=None):
        self.preprocessing_service = preprocessing_service or PreprocessingService()
        self.koreksi_service = koreksi_service or KoreksiService()

    def proses_dokumen(self, dokumen: Dokumen) -> HasilKoreksi:
        teks_bersih = self.preprocessing(dokumen.teks_asli)
        teks_koreksi = self.terapkan_aturan(teks_bersih)
        return HasilKoreksi(teks_koreksi=teks_koreksi, jumlah_koreksi=0)

    def validasi_dokumen(self, dokumen: Dokumen) -> bool:
        return bool(dokumen and dokumen.teks_asli)

    def ekstraksi_teks(self, teks: str) -> str:
        return teks

    def preprocessing(self, teks: str) -> str:
        return self.preprocessing_service.preprocessing(teks)

    def terapkan_aturan(self, teks: str) -> str:
        return self.koreksi_service.koreksi(teks)

    def deteksi_dan_koreksi(self, teks: str):
        try:
            rule_engine = BaseRule()
            kesalahan_list = rule_engine.cek(teks)
            kesalahan_list = self._merge_kesalahan_spasi(kesalahan_list)
            koreksi_text = self._apply_kesalahan(teks, kesalahan_list)
            detection_html = self._build_detection_html(teks, kesalahan_list)
            return {
                "kesalahan_list": kesalahan_list,
                "koreksi_text": koreksi_text,
                "detection_html": detection_html,
                "error": None,
            }
        except Exception as exc:
            fallback_text = teks or ""
            return {
                "kesalahan_list": [],
                "koreksi_text": fallback_text,
                "detection_html": html_lib.escape(fallback_text),
                "error": str(exc) or "Gagal melakukan deteksi/koreksi.",
            }

    @staticmethod
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
    def _apply_kesalahan(teks, kesalahan_list):
        if teks is None:
            return ""
        if not kesalahan_list:
            return teks

        items = sorted(
            kesalahan_list,
            key=lambda k: getattr(k, "start", 0),
        )
        output = []
        cursor = 0
        for item in items:
            start = getattr(item, "start", None)
            end = getattr(item, "end", None)
            if start is None or end is None:
                continue
            if start < cursor:
                continue
            output.append(teks[cursor:start])
            replacement = getattr(item, "pengganti", "")
            if replacement == "":
                replacement = getattr(item, "perbaikan", "")
            output.append(replacement)
            cursor = end

        output.append(teks[cursor:])
        return "".join(output)

    def _build_detection_html(self, teks, kesalahan_list):
        if teks is None:
            return ""
        if not kesalahan_list:
            return html_lib.escape(teks)

        items = sorted(
            kesalahan_list,
            key=lambda k: getattr(k, "start", 0),
        )
        output_html = []
        cursor = 0
        for item in items:
            start = getattr(item, "start", None)
            end = getattr(item, "end", None)
            if start is None or end is None:
                continue
            if start < cursor:
                continue
            output_html.append(html_lib.escape(teks[cursor:start]))

            tooltip = self._format_tooltip(item)
            snippet = teks[start:end]
            output_html.append(
                "<mark class=\"error-highlight\" title=\"{}\">{}</mark>".format(
                    html_lib.escape(tooltip),
                    html_lib.escape(snippet),
                )
            )
            cursor = end

        output_html.append(html_lib.escape(teks[cursor:]))
        return "".join(output_html)

    @staticmethod
    def _format_tooltip(kesalahan):
        kode = getattr(kesalahan, "kode", "")
        deskripsi = getattr(kesalahan, "deskripsi", "")
        perbaikan = getattr(kesalahan, "perbaikan", "")
        prefix = f"{kode} - " if kode else ""
        if perbaikan:
            return f"{prefix}\nDeskripsi: {deskripsi} \nPerbaikan: {perbaikan}"
        return f"{prefix}\nDeskrispsi: {deskripsi}"
