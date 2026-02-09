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

from ..config import Config
from ..services.ekstraksi_teks_service import extract_text_from_pdf
from ..services.preprocessing_service import preprocessing
from ..utils.file_utils import remove_file_if_exists, write_text_file, read_text_file
from ..utils.pdf_utils import allowed_file, secure_filename_safe


def upload_dokumen():
    if request.method == "POST":
        if "file" not in request.files:
            flash("Tidak ada file yang diunggah.")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("Nama file kosong.")
            return redirect(request.url)

        if file and allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
            old_file = session.get("current_file")
            if old_file:
                remove_file_if_exists(Config.UPLOAD_FOLDER, old_file)
                remove_file_if_exists(Config.UPLOAD_FOLDER, f"{old_file}.txt")

            filename = secure_filename_safe(file.filename)
            file_path = remove_file_if_exists(Config.UPLOAD_FOLDER, filename, return_path=True)
            file.save(file_path)

            text_filename = f"{filename}.txt"
            try:
                extracted_text = extract_text_from_pdf(file_path)
                normalized_text = preprocessing(extracted_text)
            except Exception:
                normalized_text = ""
                flash("Gagal mengekstrak teks dari PDF.")

            write_text_file(Config.UPLOAD_FOLDER, text_filename, normalized_text)
            session["extracted_text_file"] = text_filename

            session["preview_filename"] = filename
            session["current_file"] = filename
            session["show_preview"] = True
            session["result_ready"] = True
            return redirect(url_for("main.upload_dokumen"))

        flash("File harus berformat PDF.")

    filename = session.get("preview_filename")
    show_preview = session.pop("show_preview", False)
    preview_url = url_for("main.uploaded_file", filename=filename) if (filename and show_preview) else None

    if not show_preview:
        current_file = session.get("current_file")
        if current_file:
            remove_file_if_exists(Config.UPLOAD_FOLDER, current_file)
        session["current_file"] = None
        session.pop("preview_filename", None)
        extracted_text_file = session.get("extracted_text_file")
        if extracted_text_file:
            remove_file_if_exists(Config.UPLOAD_FOLDER, extracted_text_file)
        session.pop("extracted_text_file", None)
        session["result_ready"] = False

    response = make_response(render_template("upload.html", preview_url=preview_url))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def hasil_koreksi():
    if not session.get("result_ready"):
        return redirect(url_for("main.upload_dokumen"))

    extracted_text_file = session.get("extracted_text_file")
    extracted_text = read_text_file(Config.UPLOAD_FOLDER, extracted_text_file) if extracted_text_file else ""
    response = make_response(render_template("hasil.html", extracted_text=extracted_text))

    current_file = session.get("current_file")
    if current_file:
        remove_file_if_exists(Config.UPLOAD_FOLDER, current_file)

    session["current_file"] = None
    session.pop("preview_filename", None)
    if extracted_text_file:
        remove_file_if_exists(Config.UPLOAD_FOLDER, extracted_text_file)
    session.pop("extracted_text_file", None)
    session["result_ready"] = False
    return response


def uploaded_file(filename):
    response = send_from_directory(Config.UPLOAD_FOLDER, filename)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def clear_preview():
    current_file = session.get("current_file")
    if current_file:
        remove_file_if_exists(Config.UPLOAD_FOLDER, current_file)
    session["current_file"] = None
    session.pop("preview_filename", None)
    extracted_text_file = session.get("extracted_text_file")
    if extracted_text_file:
        remove_file_if_exists(Config.UPLOAD_FOLDER, extracted_text_file)
    session.pop("extracted_text_file", None)
    session["result_ready"] = False
    return {"status": "ok"}


def tentang_page():
    return render_template("tentang.html")
