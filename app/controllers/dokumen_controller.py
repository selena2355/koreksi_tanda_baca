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
                    self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, old_file)
                    # Legacy artifacts in uploads (cleanup if present)
                    self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, f"{old_file}.txt")
                    self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, f"{old_file}.json")
                    self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, f"{old_file}.sbd.json")
                    self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, f"{old_file}.tokens.json")
                    self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, f"{old_file}.pos.json")
                    # Detection/correction results
                    self.file_utils.remove_file_if_exists(
                        Config.DETECTION_RESULT_FOLDER,
                        f"{old_file}.txt",
                    )
                    self.file_utils.remove_file_if_exists(
                        Config.CORRECTION_RESULT_FOLDER,
                        f"{old_file}.txt",
                    )
                    # Debug artifacts
                    self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{old_file}.txt")
                    self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{old_file}.json")
                    self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{old_file}.sbd.json")
                    self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{old_file}.tokens.json")
                    self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{old_file}.pos.json")

                session.pop("extracted_text_file", None)
                session.pop("correction_result_file", None)
                session.pop("debug_normalized_file", None)
                session.pop("structured_text_file", None)
                session.pop("sbd_file", None)
                session.pop("tokens_file", None)
                session.pop("pos_file", None)

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
            current_file = session.get("current_file")
            if current_file:
                self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, current_file)
                self.file_utils.remove_file_if_exists(
                    Config.DETECTION_RESULT_FOLDER,
                    f"{current_file}.txt",
                )
                self.file_utils.remove_file_if_exists(
                    Config.CORRECTION_RESULT_FOLDER,
                    f"{current_file}.txt",
                )
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.txt")
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.json")
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.sbd.json")
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.tokens.json")
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.pos.json")
            session["current_file"] = None
            session.pop("preview_filename", None)
            extracted_text_file = session.get("extracted_text_file")
            if extracted_text_file:
                self.file_utils.remove_file_if_exists(
                    Config.DETECTION_RESULT_FOLDER,
                    extracted_text_file,
                )
            session.pop("extracted_text_file", None)
            correction_result_file = session.get("correction_result_file")
            if correction_result_file:
                self.file_utils.remove_file_if_exists(
                    Config.CORRECTION_RESULT_FOLDER,
                    correction_result_file,
                )
            session.pop("correction_result_file", None)
            debug_normalized_file = session.get("debug_normalized_file")
            if debug_normalized_file:
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, debug_normalized_file)
            session.pop("debug_normalized_file", None)
            structured_text_file = session.get("structured_text_file")
            if structured_text_file:
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, structured_text_file)
            session.pop("structured_text_file", None)
            sbd_file = session.get("sbd_file")
            if sbd_file:
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, sbd_file)
            session.pop("sbd_file", None)
            tokens_file = session.get("tokens_file")
            if tokens_file:
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, tokens_file)
            session.pop("tokens_file", None)
            pos_file = session.get("pos_file")
            if pos_file:
                self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, pos_file)
            session.pop("pos_file", None)
            session["result_ready"] = False

        response = make_response(
            render_template("upload.html", preview_url=preview_url, filename=filename)
        )
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

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

            sentences = []
            structured_text = []
            tokens = []
            pos_tags = []
            try:
                sentences = self.preprocessing_service.segment_sentences(normalized_text)
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
            except Exception as exc:
                pos_tags = []
                flash(str(exc) or "Gagal melakukan POS tagging.")

            try:
                koreksi_text = self.pemeriksaan_service.terapkan_aturan(normalized_text)
            except Exception as exc:
                koreksi_text = ""
                flash(str(exc) or "Gagal melakukan koreksi.")

            # Simpan hasil deteksi (selalu)
            self.file_utils.write_text_file(
                Config.DETECTION_RESULT_FOLDER,
                text_filename,
                normalized_text,
            )
            session["extracted_text_file"] = text_filename

            # Simpan hasil koreksi (selalu)
            self.file_utils.write_text_file(
                Config.CORRECTION_RESULT_FOLDER,
                text_filename,
                koreksi_text,
            )
            session["correction_result_file"] = text_filename

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
        response = make_response(render_template("hasil.html", extracted_text=extracted_text))

        session["result_ready"] = False
        return response

    def login(self):
        return self.auth_service.login()

    def tampilkan_riwayat(self):
        return self.riwayat_service.ambil_riwayat()


_sistem_web = SistemWeb()


def upload_dokumen():
    return _sistem_web.unggah_dokumen()


def hasil_koreksi():
    return _sistem_web.tampilkan_hasil()


def uploaded_file(filename):
    response = send_from_directory(Config.UPLOAD_FOLDER, filename)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def clear_preview():
    current_file = session.get("current_file")
    if current_file:
        _sistem_web.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, current_file)
        _sistem_web.file_utils.remove_file_if_exists(
            Config.DETECTION_RESULT_FOLDER,
            f"{current_file}.txt",
        )
        _sistem_web.file_utils.remove_file_if_exists(
            Config.CORRECTION_RESULT_FOLDER,
            f"{current_file}.txt",
        )
        _sistem_web.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.txt")
        _sistem_web.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.json")
        _sistem_web.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.sbd.json")
        _sistem_web.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.tokens.json")
        _sistem_web.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, f"{current_file}.pos.json")
    session["current_file"] = None
    session.pop("preview_filename", None)
    extracted_text_file = session.get("extracted_text_file")
    if extracted_text_file:
        _sistem_web.file_utils.remove_file_if_exists(
            Config.DETECTION_RESULT_FOLDER,
            extracted_text_file,
        )
    session.pop("extracted_text_file", None)
    correction_result_file = session.get("correction_result_file")
    if correction_result_file:
        _sistem_web.file_utils.remove_file_if_exists(
            Config.CORRECTION_RESULT_FOLDER,
            correction_result_file,
        )
    session.pop("correction_result_file", None)
    debug_normalized_file = session.get("debug_normalized_file")
    if debug_normalized_file:
        _sistem_web.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, debug_normalized_file)
    session.pop("debug_normalized_file", None)
    structured_text_file = session.get("structured_text_file")
    if structured_text_file:
        _sistem_web.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, structured_text_file)
    session.pop("structured_text_file", None)
    sbd_file = session.get("sbd_file")
    if sbd_file:
        _sistem_web.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, sbd_file)
    session.pop("sbd_file", None)
    tokens_file = session.get("tokens_file")
    if tokens_file:
        _sistem_web.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, tokens_file)
    session.pop("tokens_file", None)
    pos_file = session.get("pos_file")
    if pos_file:
        _sistem_web.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, pos_file)
    session.pop("pos_file", None)
    session["result_ready"] = False
    return {"status": "ok"}


def tentang_page():
    return render_template("tentang.html")
