import json
import os

# Digunakan untuk operasi file seperti membaca, menulis, dan menghapus file teks dan JSON.
class FileUtils:
    DEFAULT_ENCODING = "utf-8"

    # Menghapus file jika ada, dan mengembalikan path file jika return_path=True
    def remove_file_if_exists(self, folder_path, filename, return_path=False):
        file_path = self._build_path(folder_path, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        return file_path if return_path else None

    # Menulis konten ke file teks, dan mengembalikan path file setelah penulisan
    def write_text_file(self, folder_path, filename, content):
        file_path = self._build_path(folder_path, filename)
        with open(file_path, "w", encoding=self.DEFAULT_ENCODING) as handle:
            handle.write(content or "")
        return file_path

    # Membaca konten dari file teks, mengembalikan string kosong jika file tidak ada
    def read_text_file(self, folder_path, filename):
        file_path = self._build_path(folder_path, filename)
        if not os.path.exists(file_path):
            return ""
        with open(file_path, "r", encoding=self.DEFAULT_ENCODING) as handle:
            return handle.read()

    # Menulis data ke file JSON, dan mengembalikan path file setelah penulisan
    def write_json_file(self, folder_path, filename, data):
        file_path = self._build_path(folder_path, filename)
        with open(file_path, "w", encoding=self.DEFAULT_ENCODING) as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        return file_path

    @staticmethod
    def _build_path(folder_path, filename):
        return os.path.join(folder_path, filename)
