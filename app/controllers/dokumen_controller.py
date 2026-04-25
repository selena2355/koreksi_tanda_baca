from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    session,
    make_response,
) 
import os 
import secrets # Digunakan untuk generate token unik untuk hasil pemeriksaan saat ini
from io import BytesIO
from docx import Document

from ..config import Config
from ..services.ekstraksi_teks_service import TextExtractor
from ..services.preprocessing_service import PreprocessingService
from ..services.pemeriksaan_dokumen_service import PemeriksaanDokumenService
from ..services.riwayat_service import RiwayatService
from ..services.auth_service import AuthService
from ..utils.file_utils import FileUtils
from ..utils.text_utils import TextNormalizer
from ..utils.docx_utils import DocxUtils


class SistemWeb:
    # Fungsi untuk menginisialisasi layanan pemeriksaan dokumen dengan opsi untuk menyuntikkan layanan preprocessing,
    # koreksi, dan aturan deteksi yang dapat disesuaikan, atau menggunakan default jika tidak diberikan.
    def __init__(
        self,
        pemeriksaan_service=None,
        auth_service=None,
        riwayat_service=None,
        preprocessing_service=None,
        docx_extractor=None,
        file_utils=None,
        docx_utils=None,
        text_normalizer=None,
    ):
        self.text_normalizer = text_normalizer or TextNormalizer()
        self.preprocessing_service = preprocessing_service or PreprocessingService(
            text_normalizer=self.text_normalizer
        )
        self.docx_extractor = docx_extractor or TextExtractor()
        self.file_utils = file_utils or FileUtils()
        self.docx_utils = docx_utils or DocxUtils()
        self.pemeriksaan_service = pemeriksaan_service or PemeriksaanDokumenService(
            preprocessing_service=self.preprocessing_service
        )
        self.auth_service = auth_service or AuthService()
        self.riwayat_service = riwayat_service or RiwayatService()

    # Fungsi untuk membersihkan file hasil pemeriksaan sebelumnya agar tidak menumpuk di server
    def _cleanup_current_result_files(self):
        current_file = session.get("current_file")
        if current_file:
            self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, current_file)
            self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, f"{current_file}.txt")
            self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, f"{current_file}.json")
            self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, f"{current_file}.sbd.json")
            self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, f"{current_file}.tokens.json")
            self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, f"{current_file}.pos.json")
            self.file_utils.remove_file_if_exists(
                Config.DETECTION_RESULT_FOLDER,
                f"{current_file}.txt",
            )
            self.file_utils.remove_file_if_exists(
                Config.DETECTION_RESULT_FOLDER,
                f"{current_file}.highlight.html",
            )
            self.file_utils.remove_file_if_exists(
                Config.CORRECTION_RESULT_FOLDER,
                f"{current_file}.txt",
            )
            self.file_utils.remove_file_if_exists(
                Config.CORRECTION_RESULT_FOLDER,
                f"{current_file}.correction.highlight.html",
            )
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.txt")
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.json")
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.sbd.json")
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.tokens.json")
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.pos.json")

        extracted_text_file = session.get("extracted_text_file")
        if extracted_text_file:
            self.file_utils.remove_file_if_exists(
                Config.DETECTION_RESULT_FOLDER,
                extracted_text_file,
            )

        detection_html_file = session.get("detection_result_html_file")
        if detection_html_file:
            self.file_utils.remove_file_if_exists(
                Config.DETECTION_RESULT_FOLDER,
                detection_html_file,
            )

        correction_result_file = session.get("correction_result_file")
        if correction_result_file:
            self.file_utils.remove_file_if_exists(
                Config.CORRECTION_RESULT_FOLDER,
                correction_result_file,
            )

        correction_result_html_file = session.get("correction_result_html_file")
        if correction_result_html_file:
            self.file_utils.remove_file_if_exists(
                Config.CORRECTION_RESULT_FOLDER,
                correction_result_html_file,
            )

        debug_normalized_file = session.get("debug_normalized_file")
        if debug_normalized_file:
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, debug_normalized_file)

        structured_text_file = session.get("structured_text_file")
        if structured_text_file:
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, structured_text_file)

        sbd_file = session.get("sbd_file")
        if sbd_file:
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, sbd_file)

        tokens_file = session.get("tokens_file")
        if tokens_file:
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, tokens_file)

        pos_file = session.get("pos_file")
        if pos_file:
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, pos_file)

    def _clear_current_result_session(self):
        session["current_file"] = None
        session.pop("preview_filename", None)
        session.pop("extracted_text_file", None)
        session.pop("detection_result_html_file", None)
        session.pop("correction_result_file", None)
        session.pop("correction_result_html_file", None)
        session.pop("koreksi_text", None)
        session.pop("debug_normalized_file", None)
        session.pop("structured_text_file", None)
        session.pop("sbd_file", None)
        session.pop("tokens_file", None)
        session.pop("pos_file", None)
        session.pop("history_saved", None)
        session.pop("saved_history_id", None)
        session.pop("result_token", None)
        session["result_ready"] = False

    def _clear_preview_and_results(self):
        self._cleanup_current_result_files()
        self._clear_current_result_session()

    def _can_save_current_result_to_history(self):
        return bool(
            session.get("user_id")
            and not session.get("history_saved")
            and session.get("result_token")
            and session.get("current_file")
            and session.get("detection_result_html_file")
            and session.get("correction_result_file")
            and session.get("correction_result_html_file")
        )

    def _save_current_result_to_history(self):
        if not self._can_save_current_result_to_history():
            return None

        riwayat = self.riwayat_service.simpan_dari_session(
            pengguna_id=session.get("user_id"),
            session_data=session,
            file_utils=self.file_utils,
        )
        if riwayat:
            session["history_saved"] = True
            session["saved_history_id"] = riwayat.id
        return riwayat

    # Endpoint untuk unggah dokumen dan tampilkan preview
    def unggah_dokumen(self):
        if request.method == "POST":
            if "file" not in request.files:
                flash("Tidak ada file yang diunggah.")
                return redirect(request.url)

            file = request.files["file"]
            if file.filename == "":
                flash("Nama file kosong.")
                return redirect(request.url)

            if file and self.docx_utils.allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
                old_file = session.get("current_file")
                if old_file:
                    self._cleanup_current_result_files()

                self._clear_current_result_session()

                filename = self.docx_utils.secure_filename_safe(file.filename)
                file_path = self.file_utils.remove_file_if_exists(
                    Config.UPLOAD_FOLDER,
                    filename,
                    return_path=True,
                )
                file.save(file_path)

                session["preview_filename"] = filename
                session["current_file"] = filename
                session["show_preview"] = True
                session["result_ready"] = False
                return redirect(url_for("main.upload_dokumen"))

            flash("File harus berformat DOCX.")

        filename = session.get("preview_filename")
        show_preview = session.pop("show_preview", False)
        preview_url = url_for("main.uploaded_file", filename=filename) if (filename and show_preview) else None

        if not show_preview:
            self._save_current_result_to_history()
            self._clear_preview_and_results()

        response = make_response(
            render_template("upload.html", preview_url=preview_url, filename=filename)
        )
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    # Fungsi tambahan untuk mengubah output POS tag dari Stanza menjadi format yang lebih sederhana untuk digunakan dalam pemeriksaan aturan
    def _flatten_pos_tags(self, pos_tags, normalized_text):
        """
        Konversi output POSTagger (list of list of dict) ke format flat
        yang dibutuhkan TitikRule: list of dict dengan key text, upos,
        start_char, end_char.
        """
        flat = []
        search_start = 0
        for sent in pos_tags:
            for tag in sent:
                word = tag["token"]
                # Cari posisi token di teks asli mulai dari search_start
                idx = normalized_text.find(word, search_start)
                if idx == -1:
                    # Kalau tidak ketemu, skip tapi jangan geser search_start
                    flat.append({
                        "text": word,
                        "upos": tag["upos"],
                        "xpos": tag["xpos"],
                        "lemma": tag.get("lemma", ""),
                        "start_char": -1,
                        "end_char": -1,
                    })
                    continue
                flat.append({
                    "text": word,
                    "upos": tag["upos"],
                    "xpos": tag["xpos"],
                    "lemma": tag.get("lemma", ""),
                    "start_char": idx,
                    "end_char": idx + len(word),
                })
                search_start = idx + len(word)
        return flat

    # Endpoint untuk menampilkan hasil deteksi dan koreksi
    def tampilkan_hasil(self):
        if request.method == "POST":
            current_file = session.get("current_file")
            if not current_file:
                flash("Unggah dokumen terlebih dahulu.")
                return redirect(url_for("main.upload_dokumen"))

            file_path = os.path.join(Config.UPLOAD_FOLDER, current_file)
            if not os.path.exists(file_path):
                flash("Dokumen tidak ditemukan, silakan unggah ulang.")
                return redirect(url_for("main.upload_dokumen"))

            text_filename = f"{current_file}.txt"
            detection_html_filename = f"{current_file}.highlight.html"
            correction_html_filename = f"{current_file}.correction.highlight.html"
            json_filename = f"{current_file}.json"
            sbd_filename = f"{current_file}.sbd.json"
            tokens_filename = f"{current_file}.tokens.json"
            pos_filename = f"{current_file}.pos.json"
            try:
                extract_result = self.docx_extractor.extract(file_path)
            except Exception as exc:
                flash(str(exc) or "Gagal mengekstrak teks dari DOCX.")
                return redirect(url_for("main.upload_dokumen"))

            if not isinstance(extract_result, dict) or extract_result.get("format") != "docx":
                flash("Format dokumen tidak didukung. Hanya DOCX yang bisa diproses.")
                return redirect(url_for("main.upload_dokumen"))

            paragraphs = extract_result.get("paragraphs") or []
            extracted_text = "\n\n".join(paragraphs) if paragraphs else extract_result.get("text", "")

            if not extracted_text or not extracted_text.strip():
                flash("Teks DOCX kosong atau tidak terbaca.")
                return redirect(url_for("main.upload_dokumen"))

            # Normalisasi teks hasil ekstraksi (DOCX only)
            normalized_text = self.preprocessing_service.preprocessing(extracted_text)
            analysis_text = self.preprocessing_service.prepare_rule_text(normalized_text)

            sentences = []
            structured_text = []
            tokens = []
            pos_tags = []
            flat_tokens = []
            try:
                sentences = self.preprocessing_service.segment_sentences(analysis_text)
            except Exception:
                sentences = []
                flash("Gagal melakukan Sentence Boundary Detection (SBD).")

            # Strukturisasi teks hasil SBD untuk pemeriksaan lebih akurat
            structured_text = self.text_normalizer.normalize_structured(sentences)
            block_texts = []
            for block in structured_text:
                if not isinstance(block, dict):
                    continue
                text_value = block.get("text")
                if text_value:
                    block_texts.append(text_value)
                    continue
                label_value = block.get("label")
                if label_value:
                    block_texts.append(label_value)
                    continue
                cells_value = block.get("cells")
                if cells_value:
                    block_texts.append(" | ".join(cell for cell in cells_value if cell))

            try:
                tokens = self.preprocessing_service.tokenizer.tokenize_sentences(block_texts)
            except Exception:
                tokens = []
                flash("Gagal melakukan tokenisasi.")

            try:
                pos_tags = self.preprocessing_service.pos_tag_tokens(tokens)
                flat_tokens = self._flatten_pos_tags(pos_tags, normalized_text)
            except Exception as exc:
                pos_tags = []
                flash(str(exc) or "Gagal melakukan POS tagging.")

            deteksi_result = self.pemeriksaan_service.deteksi_dan_koreksi(
                normalized_text,
                konteks={"tokens": flat_tokens}
            )
            koreksi_text = deteksi_result["koreksi_text"]
            detection_html = deteksi_result["detection_html"]
            correction_html = deteksi_result["correction_html"]
            if deteksi_result["error"]:
                flash(deteksi_result["error"])

            # Simpan hasil deteksi (selalu)
            self.file_utils.write_text_file(
                Config.DETECTION_RESULT_FOLDER,
                text_filename,
                normalized_text,
            )
            session["extracted_text_file"] = text_filename
            self.file_utils.write_text_file(
                Config.DETECTION_RESULT_FOLDER,
                detection_html_filename,
                detection_html,
            )
            session["detection_result_html_file"] = detection_html_filename

            # Simpan hasil koreksi (selalu)
            self.file_utils.write_text_file(
                Config.CORRECTION_RESULT_FOLDER,
                text_filename,
                koreksi_text,
            )
            session["correction_result_file"] = text_filename
            session["koreksi_text"] = koreksi_text  # Simpan teks koreksi untuk download DOCX
            self.file_utils.write_text_file(
                Config.CORRECTION_RESULT_FOLDER,
                correction_html_filename,
                correction_html,
            )
            session["correction_result_html_file"] = correction_html_filename

            # Simpan file debug jika DEBUG_SAVE aktif
            if Config.DEBUG_SAVE:
                self.file_utils.write_text_file(Config.DEBUG_FOLDER, text_filename, normalized_text)
                session["debug_normalized_file"] = text_filename
                self.file_utils.write_json_file(Config.DEBUG_FOLDER, json_filename, structured_text)
                session["structured_text_file"] = json_filename
                self.file_utils.write_json_file(Config.DEBUG_FOLDER, sbd_filename, sentences)
                session["sbd_file"] = sbd_filename
                self.file_utils.write_json_file(Config.DEBUG_FOLDER, tokens_filename, tokens)
                session["tokens_file"] = tokens_filename
                self.file_utils.write_json_file(Config.DEBUG_FOLDER, pos_filename, pos_tags)
                session["pos_file"] = pos_filename
            else:
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, text_filename)
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, json_filename)
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, sbd_filename)
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, tokens_filename)
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, pos_filename)
                session.pop("debug_normalized_file", None)
                session.pop("structured_text_file", None)
                session.pop("sbd_file", None)
                session.pop("tokens_file", None)
                session.pop("pos_file", None)
            session["history_saved"] = False
            session.pop("saved_history_id", None)
            session["result_token"] = secrets.token_urlsafe(24)
            session["result_ready"] = True
            return redirect(url_for("main.hasil_koreksi"))

        if not session.get("result_ready"):
            return redirect(url_for("main.upload_dokumen"))

        extracted_text_file = session.get("extracted_text_file")
        extracted_text = (
            self.file_utils.read_text_file(
                Config.DETECTION_RESULT_FOLDER,
                extracted_text_file,
            )
            if extracted_text_file
            else ""
        )
        detection_html_file = session.get("detection_result_html_file")
        detection_html = (
            self.file_utils.read_text_file(
                Config.DETECTION_RESULT_FOLDER,
                detection_html_file,
            )
            if detection_html_file
            else ""
        )
        correction_result_file = session.get("correction_result_file")
        correction_text = (
            self.file_utils.read_text_file(
                Config.CORRECTION_RESULT_FOLDER,
                correction_result_file,
            )
            if correction_result_file
            else ""
        )
        correction_result_html_file = session.get("correction_result_html_file")
        correction_html = (
            self.file_utils.read_text_file(
                Config.CORRECTION_RESULT_FOLDER,
                correction_result_html_file,
            )
            if correction_result_html_file
            else ""
        )
        response = make_response(
            render_template(
                "hasil.html",
                extracted_text=extracted_text,
                detection_html=detection_html,
                correction_text=correction_text,
                correction_html=correction_html,
                document_name=session.get("current_file"),
                auto_save_history=bool(session.get("user_id")),
                back_url=url_for("main.upload_dokumen"),
                back_label="Kembali",
                download_url=url_for("main.unduh_hasil_koreksi"),
                before_unload_url=(
                    url_for("main.simpan_hasil_ke_riwayat")
                    if session.get("user_id")
                    else url_for("main.clear_preview")
                ),
            )
        )

        session["result_ready"] = False
        return response

    def login(self):
        return self.auth_service.login()

    def tampilkan_riwayat(self):
        pengguna_id = session.get("user_id")
        if not pengguna_id:
            return []
        return self.riwayat_service.ambil_riwayat_pengguna(pengguna_id)

    def simpan_hasil_ke_riwayat(self):
        if not session.get("user_id"):
            return {"status": "ignored", "saved": False}

        riwayat = self._save_current_result_to_history()
        self._clear_preview_and_results()
        return {"status": "ok", "saved": bool(riwayat)}


_sistem_web = SistemWeb()


def upload_dokumen():
    return _sistem_web.unggah_dokumen()


def hasil_koreksi():
    return _sistem_web.tampilkan_hasil()


def simpan_hasil_ke_riwayat():
    return _sistem_web.simpan_hasil_ke_riwayat()


def uploaded_file(filename):
    response = send_from_directory(Config.UPLOAD_FOLDER, filename)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def unduh_hasil_koreksi():
    koreksi_text = session.get("koreksi_text")
    if not koreksi_text:
        flash("Hasil koreksi tidak tersedia.")
        return redirect(url_for("main.upload_dokumen"))

    # Generate DOCX in memory
    doc = Document()
    
    # Split text by lines and add to document
    lines = koreksi_text.split('\n')
    for line in lines:
        if line.strip():  # Only add non-empty lines
            doc.add_paragraph(line)
        else:
            doc.add_paragraph()  # Add empty paragraph to preserve spacing
    
    # Save to BytesIO buffer
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    # Create response with DOCX file
    response = make_response(buffer.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=hasil_koreksi.docx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Endpoint untuk membersihkan preview dan hasil terkait (opsional, bisa dipanggil via AJAX)
def clear_preview():
    _sistem_web._clear_preview_and_results()
    return {"status": "ok"}


def tentang_page():
    return render_template("tentang.html")
