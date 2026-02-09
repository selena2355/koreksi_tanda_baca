# Setup Guide

Panduan lengkap untuk setup dan menjalankan aplikasi Koreksi Tanda Baca.

## 📋 Prasyarat

- Python 3.8+
- pip (included dengan Python)
- Git (optional)

## 🚀 Setup Awal (First Time)

### Step 1: Download Project

**Jika menggunakan Git:**
```bash
git clone <repository-url>
cd koreksi_tanda_baca
```

**Jika menggunakan ZIP:**
```bash
# Extract ZIP file
cd koreksi_tanda_baca
```

### Step 2: Buat Virtual Environment

Virtual environment adalah folder terpisah untuk menyimpan semua library project.
Gunakan ini supaya library project tidak bentrok dengan library lain.

**Windows:**
```bash
python -m venv env
env\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

**Setelah berhasil, terminal akan terlihat seperti ini:**
```
(env) C:\koreksi_tanda_baca>
```

Tanda `(env)` menunjukkan virtual environment sudah aktif ✅

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Ini akan install semua library yang dibutuhkan (Flask, PyMuPDF, dll)

### Step 4: Setup Environment Variables

```bash
# Copy file template
cp .env.example .env
```

**File `.env` berisi:**
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production
MAX_FILE_SIZE=52428800
```

Untuk development, setting default sudah cukup.

### Step 5: Run Aplikasi

```bash
python run.py
```

**Berhasil jika melihat output seperti ini:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 6: Buka di Browser

```
http://localhost:5000
```

Selesai! ✅

---

## 🔄 Setup Berikutnya (Next Time)

Kalau sudah pernah setup, cukup:

```bash
# 1. Navigate ke folder project
cd koreksi_tanda_baca

# 2. Aktifkan virtual environment
env\Scripts\activate  # Windows
# atau
source env/bin/activate  # macOS/Linux

# 3. Run aplikasi
python app.py
```

---

## ⚙️ Konfigurasi Lanjutan

### Mengubah Port

Default port adalah `5000`. Untuk mengubahnya:

**Buka `app.py`:**
```python
if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Ubah port di sini
```

Sekarang akses di `http://localhost:5001`

### Mengubah Secret Key

Untuk production, generate secret key baru yang aman:

**Python:**
```python
import secrets
print(secrets.token_hex(32))
```

Copy output dan paste di `.env`:
```
SECRET_KEY=abc123...xyz789
```

### Mengubah MAX_FILE_SIZE

Di `.env`:
```
MAX_FILE_SIZE=104857600  # 100 MB (dalam bytes)
```

Konversi:
- 1 MB = 1,048,576 bytes
- 10 MB = 10,485,760 bytes
- 50 MB = 52,428,800 bytes (default)
- 100 MB = 104,857,600 bytes

---

## 🐛 Common Issues

### Error: `ModuleNotFoundError: No module named 'flask'`

**Penyebab:** Virtual environment tidak aktif atau belum install dependencies

**Solusi:**
```bash
# Pastikan virtual environment aktif (ada (env) di terminal)
env\Scripts\activate

# Install ulang
pip install -r requirements.txt
```

### Error: `Port 5000 already in use`

**Penyebab:** Port 5000 sudah digunakan aplikasi lain

**Solusi:**
```bash
# Ubah port di app.py
python app.py  # Default akan coba port 5001, 5002, dst
```

### Error: `Cannot connect to localhost:5000`

**Penyebab:** Aplikasi tidak running atau belum fully startup

**Solusi:**
```bash
# Buka terminal baru dan cek
curl http://localhost:5000

# Atau cek di browser setelah beberapa detik
```

### Error: `The upload folder does not exist`

**Penyebab:** Folder `uploads/` tidak ada

**Solusi:**
```bash
# Aplikasi harusnya buat sendiri
# Jika tidak, buat manual:
mkdir uploads
```

---

## 🔍 Troubleshooting Advanced

### Lihat Error Detail di Console

Saat run `python app.py`, semua error akan ditampilkan di terminal. Baca dengan seksama!

Contoh error:
```
Traceback (most recent call last):
  File "app.py", line 10, in <module>
    from missing_module import something
ModuleNotFoundError: No module named 'missing_module'
```

**Artinya:** Module `missing_module` tidak terinstall

**Solusi:** `pip install missing_module`

### Debugging dengan Print

Tambahkan `print()` di kode untuk lihat apa yang terjadi:

```python
@app.route("/", methods=["POST"])
def upload():
    print("DEBUG: File diterima")  # Tambah ini
    print(f"DEBUG: Nama file = {file.filename}")  # Atau ini
    ...
```

Hasilnya akan muncul di terminal saat aplikasi running.

### Lihat Log File

```bash
# Buka file log
logs/app.log  # Atau gunakan text editor favorit
```

---

## ✅ Checklist Setup

- [ ] Python 3.8+ terinstall (`python --version`)
- [ ] Git terinstall (optional, `git --version`)
- [ ] Project di-download/di-clone
- [ ] Virtual environment dibuat (`env/` folder exists)
- [ ] Virtual environment aktif (`(env)` terlihat di terminal)
- [ ] Dependencies terinstall (`pip list` menampilkan Flask, etc)
- [ ] `.env` file dibuat dari `.env.example`
- [ ] `uploads/` folder exists
- [ ] `logs/` folder exists
- [ ] Aplikasi running (`python app.py`)
- [ ] Browser bisa akses `http://localhost:5000`

---

## 🎓 Next Steps

1. **Baca dokumentasi:**
   - [README.md](../README.md) - Overview aplikasi
   - [DOKUMENTASI.md](../DOKUMENTASI.md) - Flow aplikasi
   - [BELAJAR_PYTHON_DARI_NOL.md](../BELAJAR_PYTHON_DARI_NOL.md) - Tutorial Python

2. **Coba fitur:**
   - Upload PDF
   - Lihat preview
   - Periksa console untuk log

3. **Mulai develop:**
   - Baca kode di `app/`
   - Coba modifikasi template HTML
   - Tambahkan route baru

---

**Happy coding! 🚀**
