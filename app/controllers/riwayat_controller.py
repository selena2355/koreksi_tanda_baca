from flask import Response, flash, redirect, render_template, session, url_for

from ..services.riwayat_service import RiwayatService


class RiwayatController:
    def __init__(self, riwayat_service=None):
        self.riwayat_service = riwayat_service or RiwayatService()

    def _require_login(self):
        pengguna_id = session.get("user_id")
        if not pengguna_id:
            flash("Silakan login terlebih dahulu untuk melihat riwayat.", "error")
            return None
        return pengguna_id

    def riwayat_page(self):
        pengguna_id = self._require_login()
        if not pengguna_id:
            return redirect(url_for("auth.login_page"))

        riwayat_items = self.riwayat_service.ambil_riwayat_pengguna(pengguna_id)
        return render_template("riwayat.html", riwayat_items=riwayat_items)

    def detail_riwayat_page(self, riwayat_id):
        pengguna_id = self._require_login()
        if not pengguna_id:
            return redirect(url_for("auth.login_page"))

        riwayat = self.riwayat_service.ambil_item_pengguna(pengguna_id, riwayat_id)
        if not riwayat:
            flash("Data riwayat tidak ditemukan.", "error")
            return redirect(url_for("riwayat.riwayat_page"))

        return render_template(
            "hasil.html",
            extracted_text=riwayat.teks_dokumen,
            detection_html=riwayat.hasil_deteksi_html,
            correction_text=riwayat.hasil_koreksi_text,
            correction_html=riwayat.hasil_koreksi_html,
            document_name=riwayat.nama_dokumen,
            auto_save_history=False,
            back_url=url_for("riwayat.riwayat_page"),
            back_label="Kembali ke Riwayat",
            download_url=url_for("riwayat.unduh_riwayat", riwayat_id=riwayat.id),
        )

    def hapus_riwayat(self, riwayat_id):
        pengguna_id = self._require_login()
        if not pengguna_id:
            return redirect(url_for("auth.login_page"))

        is_deleted = self.riwayat_service.hapus_item_pengguna(pengguna_id, riwayat_id)
        if is_deleted:
            flash("Riwayat koreksi berhasil dihapus.", "success")
        else:
            flash("Riwayat koreksi tidak ditemukan.", "error")
        return redirect(url_for("riwayat.riwayat_page"))

    def unduh_riwayat(self, riwayat_id):
        pengguna_id = self._require_login()
        if not pengguna_id:
            return redirect(url_for("auth.login_page"))

        riwayat = self.riwayat_service.ambil_item_pengguna(pengguna_id, riwayat_id)
        if not riwayat:
            flash("Data riwayat tidak ditemukan.", "error")
            return redirect(url_for("riwayat.riwayat_page"))

        response = Response(
            riwayat.hasil_koreksi_text or "",
            mimetype="text/plain; charset=utf-8",
        )
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{riwayat.nama_dokumen}-hasil-koreksi.txt"'
        )
        return response


_riwayat_controller = RiwayatController()


def riwayat_page():
    return _riwayat_controller.riwayat_page()


def detail_riwayat_page(riwayat_id):
    return _riwayat_controller.detail_riwayat_page(riwayat_id)


def hapus_riwayat(riwayat_id):
    return _riwayat_controller.hapus_riwayat(riwayat_id)


def unduh_riwayat(riwayat_id):
    return _riwayat_controller.unduh_riwayat(riwayat_id)
