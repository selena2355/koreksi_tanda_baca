# ========== IMPORT LIBRARY ==========
# Flask: Framework web untuk membuat aplikasi
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, make_response
# fitz (PyMuPDF): Library untuk membaca dan memanipulasi file PDF
import fitz
# os: Library untuk operasi file system (membuat folder, cek file, dll)
import os
# werkzeug.utils: Utility untuk keamanan file, misal secure_filename
from werkzeug.utils import secure_filename

# ========== KONFIGURASI DASAR ==========
# Mendapatkan path folder aplikasi (folder tempat file app.py berada)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Inisialisasi aplikasi Flask dengan konfigurasi folder template dan static
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),  # Folder HTML templates
    static_folder=os.path.join(BASE_DIR, "static"),        # Folder CSS, JS, gambar
)

# Secret key untuk enkripsi session data (gunakan string yang lebih aman di production)
app.secret_key = "secret-key-skripsi"

# ========== KONFIGURASI UPLOAD ==========
# Path folder tempat file PDF akan disimpan
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
# File extension yang diizinkan untuk diupload
ALLOWED_EXTENSIONS = {"pdf"}
# Batas ukuran file maksimal yang bisa diupload (50 MB)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Membuat folder upload jika belum ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Menerapkan konfigurasi ke Flask app
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Batas ukuran konten yang dikirim ke server (membantu mencegah upload file besar)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


# ========== FUNGSI HELPER ==========
def allowed_file(filename):
    """
    Fungsi untuk validasi apakah file extension diizinkan
    
    Parameter:
        filename (str): Nama file yang akan dicek
    
    Return:
        bool: True jika extension .pdf, False jika tidak
    
    Contoh:
        allowed_file("dokumen.pdf") -> True
        allowed_file("gambar.jpg") -> False
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path):
    """
    Fungsi untuk mengekstrak semua text dari file PDF
    Membaca text dari setiap halaman PDF dan menggabungnya
    
    Parameter:
        file_path (str): Path lengkap ke file PDF
    
    Return:
        str: Semua text dari PDF yang digabung dengan newline
    
    Catatan:
        - Hanya untuk file < 10MB (lihat di route upload_dokumen)
        - Jika file > 10MB akan di-skip untuk performa
    """
    text_chunks = []  # List untuk menyimpan text dari setiap halaman
    # Buka file PDF
    with fitz.open(file_path) as doc:
        # Loop melalui setiap halaman
        for page in doc:
            # Ekstrak text dari halaman dan tambahkan ke list
            text_chunks.append(page.get_text("text"))
    # Gabung semua text dengan newline dan hapus whitespace di awal/akhir
    return "\n".join(text_chunks).strip()


# ========== ROUTE / ENDPOINT ==========
@app.route("/", methods=["GET", "POST"])
def upload_dokumen():
    """
    Route utama untuk upload dan preview dokumen PDF
    
    GET Request:
        - Menampilkan form upload dan preview dokumen (jika ada)
        - Menghapus preview_filename dari session setelah ditampilkan
    
    POST Request:
        - Menerima file PDF dari form upload
        - Memvalidasi file (format, ukuran)
        - Menyimpan file ke folder uploads
        - Mengekstrak text dari PDF (jika file < 10MB)
        - Redirect kembali ke halaman utama untuk menampilkan preview
    """
    if request.method == "POST":
        # ===== VALIDASI FORM =====
        # Cek apakah form berisi field 'file'
        if "file" not in request.files:
            flash("Tidak ada file yang diunggah.")
            return redirect(request.url)

        # Ambil file dari form
        file = request.files["file"]

        # Cek apakah user memilih file
        if file.filename == "":
            flash("Nama file kosong.")
            return redirect(request.url)

        # ===== PROSES UPLOAD JIKA VALID =====
        if file and allowed_file(file.filename):
            # --- CEK UKURAN FILE ---
            # Mencari ukuran file dengan memindahkan pointer ke akhir file
            file.seek(0, os.SEEK_END)
            file_size = file.tell()  # Posisi pointer = ukuran file
            file.seek(0)  # Kembalikan pointer ke awal
            
            # Jika file lebih besar dari MAX_FILE_SIZE, tolak upload
            if file_size > MAX_FILE_SIZE:
                flash(f"Ukuran file terlalu besar. Maksimal {MAX_FILE_SIZE / 1024 / 1024:.0f} MB.")
                return redirect(request.url)
            
            # --- HAPUS FILE LAMA ---
            # Jika user sudah upload file sebelumnya, hapus file lama tersebut
            old_file = session.get("current_file")
            if old_file:
                old_file_path = os.path.join(app.config["UPLOAD_FOLDER"], old_file)
                try:
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                except OSError:
                    pass  # Abaikan error jika gagal hapus
            
            # --- SIMPAN FILE BARU ---
            # secure_filename(): Membersihkan nama file dari karakter berbahaya
            # Contoh: "my file (1).pdf" -> "my_file_1.pdf"
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            
            # Coba simpan file ke disk
            try:
                file.save(file_path)
                print(f"File saved successfully: {filename}, size: {file_size} bytes")
            except Exception as e:
                flash(f"Gagal menyimpan file: {str(e)}")
                print(f"Error saving file: {str(e)}")
                return redirect(request.url)

            # --- EKSTRAKSI TEXT DARI PDF ---
            # Hanya ekstrak text jika file < 10MB (untuk performa)
            if file_size < 10 * 1024 * 1024:
                try:
                    # Ekstrak text dan simpan di session
                    session["extracted_text"] = extract_text_from_pdf(file_path)
                except Exception as e:
                    session["extracted_text"] = ""
                    flash(f"Gagal mengekstrak teks dari PDF: {str(e)}")
                    print(f"Error extracting PDF text: {str(e)}")
            else:
                # Untuk file besar, skip ekstraksi
                session["extracted_text"] = ""
                print(f"File terlalu besar untuk ekstraksi text, skip text extraction")

            # --- SIMPAN NAMA FILE KE SESSION ---
            # preview_filename: Digunakan untuk menampilkan preview setelah redirect
            # current_file: Digunakan untuk tracking file mana yang sedang ditampilkan
            session["preview_filename"] = filename
            session["current_file"] = filename
            print(f"Redirecting to preview page. Session: preview_filename={session.get('preview_filename')}, current_file={session.get('current_file')}")
            
            # Redirect ke halaman utama (GET request) untuk menampilkan preview
            return redirect(url_for("upload_dokumen"))

        else:
            # File bukan PDF atau extension tidak diizinkan
            flash("File harus berformat PDF.")

    # ===== RENDER HALAMAN (GET REQUEST) =====
    # Ambil preview_filename dari session dan HAPUS dari session (pop)
    # Ini memastikan preview hanya ditampilkan sekali
    filename = session.pop("preview_filename", None)
    
    # Jika ada filename, generate URL untuk preview
    preview_url = url_for("uploaded_file", filename=filename) if filename else None
    
    # Cetak debug info ke console server
    print(f"GET request. preview_filename={filename}, preview_url={preview_url}")
    
    # Render template HTML dan berikan preview_url
    response = make_response(render_template("index.html", preview_url=preview_url))
    
    # --- HEADER CACHE CONTROL ---
    # Instruksi ini memberitahu browser JANGAN cache halaman ini
    # Tujuan: Agar halaman selalu fresh dan tidak ada file lama yang tertinggal
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """
    Route untuk menampilkan file PDF yang sudah diupload
    File ini akan ditampilkan di dalam <iframe> di halaman preview
    
    Parameter:
        filename (str): Nama file PDF yang akan ditampilkan
    
    Return:
        Response: File PDF dengan header cache control
    """
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
    # Kirim file dari folder uploads
    response = send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    
    # Sama seperti route sebelumnya, set header cache control
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response


@app.route("/clear-preview", methods=["POST"])
def clear_preview():
    """
    Route untuk menghapus file preview ketika user memilih file baru
    
    Dipanggil dari JavaScript saat user klik file input
    Sebelum file baru diupload, file lama akan dihapus terlebih dahulu
    
    Return:
        dict: JSON {"status": "ok"} untuk konfirmasi
    """
    # Ambil nama file yang sedang ditampilkan
    current_file = session.get("current_file")
    
    # Jika ada file, hapus dari disk
    if current_file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], current_file)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass  # Abaikan error jika gagal hapus
        
        # Clear session
        session["current_file"] = None
    
    # Hapus juga preview_filename dari session
    session.pop("preview_filename", None)
    
    # Return JSON untuk JavaScript
    return {"status": "ok"}


@app.route("/hasil")
def hasil():
    """
    Route untuk halaman hasil pemeriksaan dokumen
    
    Menampilkan text yang sudah diekstrak dari PDF
    (Tahap pemrosesan koreksi tanda baca akan ditambahkan kemudian)
    
    Return:
        HTML: Halaman result.html dengan extracted_text
    """
    # Ambil text yang sudah diekstrak sebelumnya dari session
    extracted_text = session.get("extracted_text", "")
    
    # Render halaman hasil dengan data text
    return render_template("result.html", extracted_text=extracted_text)


# ========== JALANKAN SERVER ==========
if __name__ == "__main__":
    # debug=True: Server akan restart otomatis jika ada perubahan kode
    # Gunakan debug=False untuk production
    app.run(debug=True)
