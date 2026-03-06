# Aplikasi Koreksi Tanda Baca

Sebuah aplikasi web berbasis **Flask** untuk memeriksa dan memperbaiki
berbagai kesalahan tanda baca pada dokumen PDF Bahasa Indonesia. Semua
logika dipisahkan ke _routes_, _controllers_, _services_, dan _rules_ agar
mudah dikembangkan dan diuji.

## 🚀 Fitur Utama

- Unggah & pratinjau file PDF
- Ekstraksi teks menggunakan PyMuPDF (`fitz`)
- Deteksi batas kalimat (SBD) dan POS tagging dengan **Stanza**
- Lajur koreksi yang dapat diperluas (`app/rules`)
- Penyimpanan riwayat koreksi
- Blueprint terpisah untuk auth, riwayat, dan fitur utama
- API internal untuk pemrosesan terprogram

> **Catatan:** model Stanza berukuran besar disimpan di `models/stanza/` dan
> diabaikan oleh Git (lihat `.gitignore`).

---

## 📦 Instalasi & Setup

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd koreksi_tanda_baca
   ```
2. **Virtual environment**
   ```bash
   python -m venv env
   env\Scripts\activate          # Windows
   # atau: source env/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Variabel lingkungan** (opsional)
   - Buat file `.env` di root jika perlu.
   - Atur `SECRET_KEY`, `STANZA_LANG`, dsb. Default sudah cocok untuk development.

---

## ▶️ Menjalankan Aplikasi

```bash
python app.py
```

Akses `http://localhost:5000` di browser.

---

## 🗂️ Struktur Proyek

```
├── app/
│   ├── __init__.py        # create_app()
│   ├── config.py          # konfigurasi
│   ├── controllers/       # logika bisnis (dokumen, auth, riwayat)
│   ├── routes/            # blueprint dan route Flask
│   ├── services/          # ekstraksi, preprocessing, koreksi, riwayat
│   ├── rules/             # aturan koreksi tanda baca
│   ├── models/            # kelas data sederhana
│   ├── utils/             # utilitas (file, pdf, sbd, pos, dll)
│   ├── static/
│   └── templates/
├── docs/                  # dokumentasi (lihat DOKUMENTASI.md)
├── tests/                 # unit tests
├── uploads/               # file sementara
├── logs/                  # file log
├── models/stanza/         # model Stanza (di-ignore Git)
├── requirements.txt
├── app.py                 # entry point
└── README.md
```

---

## 🧠 Alur Sistem (singkat)

1. **GET /** → `main_routes.index` menampilkan formulir upload.
2. **POST /upload** → file disimpan di `uploads/` oleh `main_routes` / `DokumenController`.
3. Teks diekstrak oleh `EkstraksiTeksService` dan dibersihkan oleh `PreprocessingService`.
4. `KoreksiService` menerapkan semua rule yang ada di `app/rules` untuk mendeteksi dan memperbaiki kesalahan.
5. Hasil dikemas ke objek model (`HasilKoreksi`) dan ditampilkan di `/hasil`.
6. Riwayat ditangani oleh `RiwayatService` dan tersimpan (sederhana, bisa diperpanjang ke DB).

Semua lapisan dapat diuji secara independen; lihat `tests/`.

---

## 🧪 Testing

```bash
pytest tests/
```

Masukkan `--cov=app` untuk laporan coverage.

---

## 📦 Dependensi

Tergantung pada isi `requirements.txt` (minimal):

- flask
- python-dotenv
- stanza
- python-docx
- PyMuPDF

Paket lain diinstal secara otomatis sebagai dependensi Flask.

---

## ⚠️ Tips & Catatan

- Model Stanza sangat besar; jangan commit ke repo.
- Perbarui `.gitignore` jika menambahkan folder lain yang tidak ingin dilacak.
- Server dijalankan dengan `debug=True` hanya untuk pengembangan.

---

## 📖 Dokumentasi Lanjutan

Lihat [DOKUMENTASI.md](DOKUMENTASI.md) untuk alur dan konsep lebih lengkap.

---

## 🤝 Kontribusi

Ikuti alur kerja GitHub standar: fork → branch → PR.

---

**Last updated:** 6 Maret 2026
