from werkzeug.utils import secure_filename


class DocxUtils:
    def allowed_file(self, filename, allowed_extensions):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

    def secure_filename_safe(self, filename):
        return secure_filename(filename)
