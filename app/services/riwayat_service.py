from ..config import Config
from ..extensions import db
from ..models import RiwayatKoreksi
from sqlalchemy.exc import IntegrityError


class RiwayatService:
    def simpan_riwayat(
        self,
        pengguna_id,
        result_token,
        nama_dokumen,
        teks_dokumen,
        hasil_deteksi_html,
        hasil_koreksi_text,
        hasil_koreksi_html,
    ):
        riwayat = RiwayatKoreksi.query.filter_by(result_token=result_token).first()
        if riwayat:
            return riwayat

        riwayat = RiwayatKoreksi(
            pengguna_id=pengguna_id,
            result_token=result_token,
            nama_dokumen=nama_dokumen,
            teks_dokumen=teks_dokumen or "",
            hasil_deteksi_html=hasil_deteksi_html or "",
            hasil_koreksi_text=hasil_koreksi_text or "",
            hasil_koreksi_html=hasil_koreksi_html or "",
        )
        db.session.add(riwayat)
        
        try:
            db.session.commit()
            return riwayat
        except IntegrityError:
            db.session.rollback()
            return RiwayatKoreksi.query.filter_by(result_token=result_token).first()

    def simpan_dari_session(self, pengguna_id, session_data, file_utils):
        nama_dokumen = session_data.get("current_file") or session_data.get("preview_filename")
        result_token = session_data.get("result_token")
        extracted_text_file = session_data.get("extracted_text_file")
        detection_html_file = session_data.get("detection_result_html_file")
        correction_result_file = session_data.get("correction_result_file")
        correction_result_html_file = session_data.get("correction_result_html_file")

        if (
            not result_token
            or not nama_dokumen
            or not detection_html_file
            or not correction_result_file
            or not correction_result_html_file
        ):
            return None

        teks_dokumen = (
            file_utils.read_text_file(Config.DETECTION_RESULT_FOLDER, extracted_text_file)
            if extracted_text_file
            else ""
        )
        hasil_deteksi_html = file_utils.read_text_file(
            Config.DETECTION_RESULT_FOLDER,
            detection_html_file,
        )
        hasil_koreksi_text = file_utils.read_text_file(
            Config.CORRECTION_RESULT_FOLDER,
            correction_result_file,
        )
        hasil_koreksi_html = file_utils.read_text_file(
            Config.CORRECTION_RESULT_FOLDER,
            correction_result_html_file,
        )

        if not hasil_deteksi_html and not hasil_koreksi_text and not hasil_koreksi_html:
            return None

        return self.simpan_riwayat(
            pengguna_id=pengguna_id,
            result_token=result_token,
            nama_dokumen=nama_dokumen,
            teks_dokumen=teks_dokumen,
            hasil_deteksi_html=hasil_deteksi_html,
            hasil_koreksi_text=hasil_koreksi_text,
            hasil_koreksi_html=hasil_koreksi_html,
        )

    def ambil_riwayat_pengguna(self, pengguna_id):
        return (
            RiwayatKoreksi.query.filter_by(pengguna_id=pengguna_id)
            .order_by(RiwayatKoreksi.created_at.desc(), RiwayatKoreksi.id.desc())
            .all()
        )

    def ambil_item_pengguna(self, pengguna_id, riwayat_id):
        return RiwayatKoreksi.query.filter_by(id=riwayat_id, pengguna_id=pengguna_id).first()

    def hapus_item_pengguna(self, pengguna_id, riwayat_id):
        riwayat = self.ambil_item_pengguna(pengguna_id, riwayat_id)
        if not riwayat:
            return False
        db.session.delete(riwayat)
        db.session.commit()
        return True
