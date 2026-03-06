# DOKUMENTASI APLIKASI KOREKSI TANDA BACA

## ALUR SISTEM UTAMA

Aplikasi ini mengikuti arsitektur berlapis (layered architecture):

```
Request → Routes → Controllers → Services → Utils/Rules → Models
                   ↓
              Responses
```

### 1. FLOW UPLOAD & KOREKSI

#### User Upload File PDF
```
GET / 
├─ render upload form (templates/upload.html)
└─ show preview area
```

#### POST /upload/dokumen
```
POST /upload/dokumen
├─ DokumenController.upload()
│  ├─ validasi file (format, ukuran)
│  ├─ secure_filename()
│  └─ simpan ke folder 'uploads/'
│
├─ EkstraksiTeksService.ekstrak_dari_pdf()
│  └─ gunakan PyMuPDF untuk ambil text
│
├─ PreprocessingService.bersihkan()
│  └─ normalisasi text
│
├─ KoreksiService.koreksi()
│  ├─ loop semua rule di app/rules/
│  ├─ setiap rule apply check() → deteksi kesalahan
│  └─ setiap rule apply fix() → perbaiki text
│
├─ RiwayatService.simpan()
│  └─ simpan hasil ke file/DB
│
└─ return response (JSON atau render hasil.html)
```

---

## STRUKTUR FOLDER & TANGGUNG JAWAB

### `app/`
Root aplikasi Flask

**File penting:**
- `__init__.py` - Factory function `create_app()`, setup blueprint
- `config.py` - Konfigurasi (path, folder, env vars)

### `app/routes/`
Endpoint routing (GET, POST, dll)

**Files:**
- `main_routes.py` - upload, preview, hasil
- `auth_routes.py` - login, register
- `riwayat_routes.py` - history list

Setiap file adalah Blueprint yang di-register di `app/__init__.py`

### `app/controllers/`
Business logic tingkat tinggi

**Files:**
- `dokumen_controller.py` - upload, validasi, ekstraksi
- `auth_controller.py` - login, logout, register
- `riwayat_controller.py` - list riwayat

Dipanggil oleh routes, memanggil services

### `app/services/`
Logika bisnis & utilitas kompleks

**Files:**
- `ekstraksi_teks_service.py` - extract text dari PDF
- `preprocessing_service.py` - clean text (normalize, dll)
- `koreksi_service.py` - apply semua rule
- `riwayat_service.py` - CRUD riwayat koreksi
- `auth_service.py` - auth logic
- `pemeriksaan_dokumen_service.py` - validasi dokumen

### `app/rules/`
Aturan-aturan koreksi tanda baca (extensible)

**Base:**
- `base_rule.py` - Interface `BaseRule` dengan method `check()` & `fix()`

**Implementasi:**
- `koma_rule.py`
- `titik_rule.py`
- `tanda_tanya_rule.py`
- `tanda_seru_rule.py`
- `tanda_petik_rule.py`
- `tanda_hubung_rule.py`
- `titik_dua_rule.py`

Setiap rule independently check & fix kesalahan tertentu

### `app/models/`
Kelas data sederhana (DTO / Value Objects)

**Files:**
- `dokumen.py` - Dokumen class
- `hasil_koreksi.py` - HasilKoreksi class
- `hasil_deteksi.py` - HasilDeteksi class
- `kesalahan.py` - Kesalahan class
- `pengguna.py` - Pengguna class
- `riwayat_koreksi.py` - RiwayatKoreksi class

### `app/utils/`
Fungsi-fungsi utilitas helper

**Files:**
- `file_utils.py` - file operations
- `pdf_utils.py` - PDF utilities (secure_filename, dll)
- `docx_utils.py` - DOCX file handling
- `text_utils.py` - text operations
- `tokenize_utils.py` - tokenization
- `sbd_utils.py` - sentence boundary detection (Stanza)
- `pos_tag_utils.py` - POS tagging (Stanza)

### `app/templates/`
HTML dengan Jinja2 templating

**Files:**
- `base.html` - template dasar
- `upload.html` / `preview.html` - form & preview
- `hasil.html` - display hasil koreksi
- `login.html`, `register.html` - auth pages
- `riwayat.html` - history
- `tentang.html` - about

### `app/static/`
Static files (CSS, JS, images)

---

## KONSEP PENTING

### Session
Penyimpanan data temporary per user:
```python
session["key"] = "value"          # Simpan
data = session.get("key")         # Ambil
data = session.pop("key")         # Ambil & hapus
```

Kapan hilang? Saat browser tutup atau `session.pop()` dipanggil.

### Request Method
- **GET**: Ambil data, parameter di URL, tidak aman untuk sensitif
- **POST**: Kirim data, parameter di body, cocok untuk file/sensitif

### Redirect
```python
return redirect(url_for("function_name"))
```
Memberitahu browser untuk request ulang ke URL lain (prevent duplicate submit).

### Flash Message
```python
flash("Success!", "success")  # Simpan pesan di session (1x display)
```
di template:
```html
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for category, message in messages %}
    <div class="alert alert-{{ category }}">{{ message }}</div>
  {% endfor %}
{% endwith %}
```

### Environment Variables
File `.env`:
```
FLASK_ENV=development
SECRET_KEY=your-secret-here
STANZA_LANG=id
STANZA_DIR=./models/stanza
```

Dibaca viapy-dotenv termasuk app startup di `app/config.py`.

---

## MENAMBAH RULE KOREKSI BARU

1. Buat file `app/rules/nama_rule.py`:
```python
from app.rules.base_rule import BaseRule

class NamaRule(BaseRule):
    def __init__(self):
        super().__init__()
        self.nama_rule = "nama_rule"
        self.deskripsi = "Penjelasan singkat"
    
    def check(self, text):
        """Deteksi kesalahan di text, return list Kesalahan"""
        errors = []
        # Regex atau logika deteksi
        # ...
        return errors
    
    def fix(self, text):
        """Perbaiki kesalahan, return text terperbaiki"""
        # Regex/replace logic
        return fixed_text
```

2. Import di `app/rules/__init__.py` atau di service yang menggunakan

3. Register di `KoreksiService.koreksi()`:
```python
from app.rules.nama_rule import NamaRule

rules = [
    KomaRule(),
    TitikRule(),
    NamaRule(),  # <-- Add here
]
```

---

## MENAMBAH ROUTE BARU

1. Buat file `app/routes/nama_routes.py`:
```python
from flask import Blueprint, render_template

nama_bp = Blueprint('nama', __name__, url_prefix='/nama')

@nama_bp.route('/', methods=['GET'])
def index():
    return render_template('nama.html')

@nama_bp.route('/process', methods=['POST'])
def process():
    # logic
    return jsonify({"status": "ok"})
```

2. Register di `app/__init__.py`:
```python
from app.routes.nama_routes import nama_bp

app.register_blueprint(nama_bp)
```

---

## TESTING

### Unit Tests
```bash
pytest tests/
pytest tests/test_rules.py -v
pytest tests/ --cov=app --cov-report=html
```

### Manual Testing
Jalankan server:
```bash
python app.py
```

Buka `http://localhost:5000` di browser.

---

## DEBUGGING TIPS

### Server Console
```python
print(f"Debug: {variable}")
import logging
logger.debug("message")
```

### Browser DevTools
- F12 → Network tab (lihat request/response)
- F12 → Console tab (lihat JS errors)

### Log Files
Folder `logs/` berisi file log aplikasi.

---

## TEKNOLOGI YANG DIPAKAI

### Backend
- **Flask** - Web framework
- **Werkzeug** - WSGI, security utilities
- **Jinja2** - Template engine

### NLP / Text Processing
- **Stanza** - SBD & POS tagging
- **PyMuPDF (fitz)** - PDF extraction
- **python-docx** - DOCX handling

### Environment & Config
- **python-dotenv** - Environment variables

### Utilities
- Regex (Python built-in)
- JSON (Flask)/Pickle untuk serialisasi

---

## .GITIGNORE & DEPLOYMENT

File besar yang di-ignore:
```
__pycache__/
*.pyc
env/
venv/
.env
logs/
uploads/
models/stanza/        # <-- Model Stanza sangat besar, di-cache local
```

Saat deploy:
1. Clone repo
2. Setup venv & install `requirements.txt`
3. Model Stanza di-download otomatis (lihat `app/utils/pos_tag_utils.py`) atau manual: 
   ```python
   import stanza
   stanza.download('id', processors='tokenize,pos', model_dir='./models/stanza')
   ```

---

## NEXT STEPS / TODO

- [ ] Implementasi lebih banyak rule koreksi
- [ ] Connect ke database (SQLite/PostgreSQL)
- [ ] User authentication (login/register)
- [ ] Riwayat koreksi per user
- [ ] Export hasil (PDF/DOCX)
- [ ] Performance optimization (caching, async processing)
- [ ] API documentation (Swagger/OpenAPI)
- [ ] CI/CD setup (GitHub Actions)

---

**Last Updated:** 6 Maret 2026
