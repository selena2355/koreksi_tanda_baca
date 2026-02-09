# API Documentation

Dokumentasi lengkap semua endpoint/route yang tersedia di aplikasi.

## Overview

Aplikasi menggunakan Flask sebagai web framework. Semua route di-define menggunakan `@app.route()` decorator.

### HTTP Methods

- **GET** - Mengambil/menampilkan data
- **POST** - Mengirim/mengubah data
- **DELETE** - Menghapus data

---

## Endpoints

### 1. Upload & Preview

#### `GET /`
**Deskripsi:** Menampilkan halaman upload dan preview

**Response:**
- HTML page dengan form upload
- Preview dokumen (jika ada)

**Contoh:**
```bash
curl http://localhost:5000/
```

---

#### `POST /`
**Deskripsi:** Receive file upload

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (PDF file)

**Response:**
- Redirect ke `/` dengan preview_url

**Contoh (cURL):**
```bash
curl -X POST \
  -F "file=@dokumen.pdf" \
  http://localhost:5000/
```

**Validasi:**
- File harus ada
- Nama file tidak boleh kosong
- Format harus `.pdf`
- Ukuran <= 50 MB

**Error Messages:**
```
- "Tidak ada file yang diunggah."
- "Nama file kosong."
- "File harus berformat PDF."
- "Ukuran file terlalu besar. Maksimal 50 MB."
```

---

### 2. File Preview

#### `GET /uploads/<filename>`
**Deskripsi:** Tampilkan file PDF untuk preview

**Path Parameters:**
- `filename` (string) - Nama file PDF

**Response:**
- PDF file binary
- Header cache-control untuk prevent caching

**Contoh:**
```bash
curl http://localhost:5000/uploads/dokumen.pdf
```

**Status Codes:**
- `200 OK` - File ditemukan dan ditampilkan
- `404 Not Found` - File tidak ada
- `400 Bad Request` - Filename tidak valid

---

### 3. Clear Preview

#### `POST /clear-preview`
**Deskripsi:** Hapus file preview sebelum upload file baru

**Request:**
- Content-Type: `application/json`

**Response:**
```json
{"status": "ok"}
```

**Contoh (JavaScript):**
```javascript
fetch("/clear-preview", { method: "POST" })
  .then(r => r.json())
  .then(data => console.log(data))
```

**Catatan:**
- Dipanggil otomatis dari JavaScript saat file dipilih
- Menghapus file lama sebelum upload yang baru

---

### 4. Hasil Pemeriksaan

#### `GET /hasil`
**Deskripsi:** Menampilkan halaman hasil pemeriksaan

**Query Parameters:**
- (None saat ini)

**Response:**
- HTML page dengan hasil pemeriksaan
- Data extracted text dari session

**Contoh:**
```bash
curl http://localhost:5000/hasil
```

**Session Requirements:**
- `extracted_text` harus ada di session (dari upload sebelumnya)

**Catatan:**
- Halaman ini mengambil data dari session
- User harus upload file terlebih dahulu

---

## Data Flow

### Upload Dokumen

```
1. User buka halaman
   GET /
   ↓
2. User pilih file
   Form submit dengan file
   ↓
3. Server terima
   POST /
   ↓
4. Server proses
   - Validasi file
   - Simpan file
   - Ekstrak text
   - Simpan ke session
   ↓
5. Server redirect
   302 redirect ke GET /
   ↓
6. Halaman kembali
   GET /
   Browser tampilkan preview
   ↓
7. Browser load preview
   GET /uploads/{filename}
   Server send PDF file
   ↓
8. Preview tampil
   Iframe menampilkan PDF
```

### Clear Preview

```
1. User pilih file baru
   Input file berubah
   ↓
2. JavaScript detect
   File input event listener trigger
   ↓
3. Fetch clear-preview
   POST /clear-preview
   ↓
4. Server hapus file lama
   DELETE file dari disk
   ↓
5. Return response
   {"status": "ok"}
   ↓
6. Submit form
   Form di-submit ke POST /
```

---

## Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK - Request berhasil | File dikirim |
| 302 | Redirect - Arahkan ke URL lain | Upload berhasil, redirect ke / |
| 400 | Bad Request - Request invalid | File format salah |
| 404 | Not Found - Resource tidak ada | File dihapus |
| 413 | Payload Too Large - File terlalu besar | > 50 MB |
| 500 | Server Error - Error di server | Exception di kode |

---

## Response Headers

### Cache Control (Prevent Caching)

Semua response dari `/` dan `/uploads/` mengirim:

```
Cache-Control: no-store, no-cache, must-revalidate, max-age=0
Pragma: no-cache
Expires: 0
```

**Tujuan:** Memastikan browser tidak cache file lama

---

## Error Handling

### Flash Messages

Pesan error ditampilkan di halaman menggunakan Flask flash:

```html
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <div class="alert">{{ messages[0] }}</div>
  {% endif %}
{% endwith %}
```

### Console Logging

Untuk debugging, check console output di terminal:

```
File saved successfully: dokumen.pdf, size: 1048576 bytes
GET request. preview_filename=dokumen.pdf
```

---

## Session Management

### Session Variables

| Variable | Purpose | Lifetime |
|----------|---------|----------|
| `preview_filename` | Nama file untuk preview | 1x display (di-pop setelah dipakai) |
| `current_file` | File yang sedang ditampilkan | Sampai upload file baru |
| `extracted_text` | Text dari PDF | Sampai halaman reload |

### Session Security

- Dienkripsi menggunakan `SECRET_KEY`
- Disimpan di cookie client
- Expired saat browser ditutup

---

## Rate Limiting

Saat ini tidak ada rate limiting. Untuk production, tambahkan:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route("/", methods=["POST"])
@limiter.limit("10 per minute")
def upload_dokumen():
    ...
```

---

## Future Endpoints (Planned)

```
GET  /history              - Lihat history upload
GET  /history/<id>         - Detail hasil pemeriksaan
POST /check                - API untuk pemeriksaan
GET  /export/<id>          - Download hasil
```

---

**Last Updated:** 7 Februari 2026
