from werkzeug.utils import secure_filename

# Kelas DocxUtils menyediakan utilitas untuk memeriksa ekstensi file dan mengamankan nama file menggunakan secure_filename dari werkzeug.utils.
class DocxUtils:
    # Memeriksa apakah file memiliki ekstensi yang diizinkan
    def allowed_file(self, filename, allowed_extensions):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

    # Menggunakan secure_filename untuk memastikan nama file aman untuk digunakan di filesystem
    def secure_filename_safe(self, filename):
        return secure_filename(filename)
