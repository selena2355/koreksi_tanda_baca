# Aplikasi Koreksi Tanda Baca

Aplikasi web untuk memeriksa dan memperbaiki tanda baca dalam dokumen PDF Bahasa Indonesia.

## 📋 Fitur

- ✅ Upload dokumen PDF
- ✅ Preview dokumen langsung di browser
- ✅ Ekstraksi text dari PDF
- ✅ Pemeriksaan tanda baca (sedang dikembangkan)
- ✅ Download hasil pemeriksaan

## 🚀 Quick Start

### Prerequisites
- Python 3.8 atau lebih baru
- pip (Python package manager)
- Git (optional)

### Instalasi

1. **Clone atau download repository**
```bash
git clone <repository-url>
cd koreksi_tanda_baca
```

2. **Buat virtual environment**
```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS/Linux
python3 -m venv env
source env/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
# Copy file contoh
cp .env.example .env

# Edit .env sesuai kebutuhan (optional)
# Untuk development, default sudah cukup
```

5. **Jalankan aplikasi**
```bash
python run.py
```

6. **Buka browser**
```
http://localhost:5000
```

---

## 📁 Struktur Folder

```
koreksi_tanda_baca/
├── app/                    # Main application folder
│   ├── __init__.py
│   ├── config.py          # Konfigurasi aplikasi
│   ├── models/            # Data models
│   ├── routes/            # URL routing
│   ├── controllers/       # Business logic
│   ├── services/          # Service layer / helpers
│   ├── rules/             # Aturan koreksi tanda baca
│   ├── utils/             # Utility functions
│   ├── static/            # CSS, JS, images
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/         # HTML templates
│
├── tests/                 # Unit tests
├── uploads/               # Folder untuk upload PDF (temporary)
├── logs/                  # Log files
├── docs/                  # Dokumentasi
│
├── .gitignore            # Git ignore file
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── run.py               # Application entry point
├── config.py            # Global configuration (optional)
└── README.md            # File ini
```

---

## 🛠️ Development

### Struktur File Penting

- **`run.py`** - Jalankan aplikasi dari sini
- **`app/config.py`** - Pengaturan aplikasi
- **`app/__init__.py`** - Inisialisasi Flask app
- **`requirements.txt`** - List semua library yang digunakan

### Menambah Route Baru

1. Buat file di `app/routes/` dengan nama deskriptif
2. Buat function dengan decorator `@app.route()`
3. Import di `app/__init__.py`

Contoh:
```python
# app/routes/document.py
from flask import Blueprint

doc_bp = Blueprint('document', __name__)

@doc_bp.route('/dokumen', methods=['GET'])
def list_dokumen():
    return "List dokumen"
```

### Menambah Rule Koreksi Baru

1. Buat file di `app/rules/` dengan nama rule
2. Inherit dari `BaseRule`
3. Implement method `check()` dan `fix()`

Contoh:
```python
# app/rules/custom_rule.py
from app.rules.base_rule import BaseRule

class CustomRule(BaseRule):
    def check(self, text):
        # Cek kesalahan
        return errors
    
    def fix(self, text):
        # Perbaiki kesalahan
        return fixed_text
```

---

## 📦 Dependencies

Semua library yang digunakan tercantum di `requirements.txt`:
- **Flask** - Web framework
- **PyMuPDF (fitz)** - PDF processing
- **Werkzeug** - WSGI utilities
- dll

Untuk lihat versi lengkapnya:
```bash
pip list
```

---

## 🧪 Testing

Jalankan unit tests:
```bash
pytest tests/
```

Dengan coverage report:
```bash
pytest --cov=app tests/
```

---

## 📝 Logging

Log files disimpan di folder `logs/`:
- Error akan tercatat otomatis
- Lihat `logs/app.log` untuk debug

---

## 🐛 Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'flask'`
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Problem: Port 5000 sudah digunakan
**Solution:** Ubah port di `run.py`
```python
app.run(debug=True, port=5001)
```

### Problem: File upload tidak bisa
**Solution:** 
- Cek folder `uploads/` ada dan bisa ditulis
- Cek ukuran file tidak lebih dari 50MB
- Lihat console untuk error message

---

## 🔐 Security Notes

⚠️ **PENTING UNTUK PRODUCTION:**

1. **Ganti `SECRET_KEY`**
   - Generate key yang aman
   - Jangan hardcode di kode

2. **Disable Debug Mode**
   - Set `FLASK_DEBUG=False` di `.env`

3. **Setup HTTPS**
   - Gunakan reverse proxy (nginx, Apache)
   - Setup SSL certificate

4. **File Upload**
   - Validasi semua file yang diupload
   - Scan untuk malware

5. **Environment Variables**
   - Jangan commit `.env` ke git
   - Gunakan `.env.example` sebagai template

---

## 📖 Dokumentasi Lanjutan

Untuk penjelasan lebih detail tentang kode:
- Lihat [DOKUMENTASI.md](DOKUMENTASI.md) - Flow aplikasi dan konsep
- Lihat [BELAJAR_PYTHON_DARI_NOL.md](BELAJAR_PYTHON_DARI_NOL.md) - Tutorial Python dasar
- Lihat `app/app_commented.py` - Kode dengan komentar lengkap

---

## 🤝 Kontribusi

Untuk kontribusi:
1. Fork repository
2. Buat branch baru (`git checkout -b feature/nama-fitur`)
3. Commit changes (`git commit -am 'Add fitur baru'`)
4. Push ke branch (`git push origin feature/nama-fitur`)
5. Create Pull Request

---

## 📄 License

[Tentukan license yang sesuai]

---

## 👨‍💻 Author

Created with ❤️

---

## 📞 Support

Jika ada pertanyaan atau masalah:
1. Buka GitHub Issues
2. Cek dokumentasi di folder `docs/`
3. Lihat console untuk error messages

---

## 🎯 Roadmap

- [ ] Implementasi rule pemeriksaan tanda baca
- [ ] Menambah lebih banyak rule
- [ ] Export hasil ke berbagai format
- [ ] Dashboard untuk history
- [ ] User authentication
- [ ] API documentation
- [ ] Performance optimization

---

**Last Updated:** 7 Februari 2026
# koreksi_tanda_baca
