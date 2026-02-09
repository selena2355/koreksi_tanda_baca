# DOKUMENTASI APLIKASI KOREKSI TANDA BACA
# =======================================

## ALUR APLIKASI SECARA UMUM

1. USER MEMBUKA HALAMAN
   - Browser request GET / ke server
   - Server render template index.html
   - Form upload dan preview placeholder ditampilkan

2. USER PILIH FILE PDF
   - Event listener JavaScript mendeteksi file selection
   - JavaScript panggil /clear-preview untuk hapus file lama
   - Setelah clear selesai, form submit secara otomatis

3. SERVER TERIMA FILE (POST REQUEST)
   - Validasi: apakah ada file? file kosong? format pdf?
   - Validasi: ukuran file <= 50MB?
   - Hapus file lama (jika ada upload sebelumnya)
   - Simpan file baru ke folder /uploads/
   - Ekstrak text dari PDF (jika < 10MB)
   - Simpan nama file ke session["preview_filename"]
   - Redirect ke / (GET request)

4. SERVER RETURN KE HALAMAN UTAMA (GET REQUEST)
   - Ambil preview_filename dari session
   - Generate URL preview: /uploads/{filename}
   - POP preview_filename dari session (hapus)
   - Render index.html dengan preview_url
   - Browser menampilkan iframe dengan PDF preview

5. IFRAME LOAD PDF
   - Iframe request GET /uploads/{filename} ke server
   - Server send file PDF
   - Browser display PDF di iframe

6. USER RELOAD HALAMAN
   - Session kosong, preview_filename tidak ada
   - Render index.html tanpa preview_url
   - Tampil preview placeholder kosong
   - File di folder uploads sudah dihapus


## KONSEP PENTING

### SESSION (Penyimpanan Data Temporary)
Session adalah penyimpanan data yang tied ke user/browser tertentu
Dienkripsi menggunakan secret_key, disimpan di cookie user
Contoh penggunaan:
```python
session["key"] = "value"  # Simpan data
data = session.get("key")  # Ambil data
data = session.pop("key")  # Ambil dan HAPUS data
```

Kapan data hilang?
- Saat browser ditutup (default Flask)
- Saat session.pop() dipanggil
- Saat browser clear cookies

### REQUEST METHOD (GET vs POST)
GET:
  - Untuk mengambil/menampilkan data
  - Parameter dikirim di URL
  - Data terlihat di address bar
  - Tidak cocok untuk data sensitif

POST:
  - Untuk mengirim/mengubah data
  - Data dikirim di body request (tidak terlihat di URL)
  - Cocok untuk file upload
  - Cocok untuk data sensitif

### REDIRECT
```python
return redirect(url_for("function_name"))
# atau
return redirect(request.url)
```
Memberitahu browser untuk membuat request baru ke URL lain
Berguna untuk:
- Menampilkan halaman setelah POST (prevent duplicate submit)
- Mengubah GET parameter
- Flow kontrol di aplikasi

### FLASH MESSAGE
```python
flash("Pesan untuk user")
```
Menyimpan pesan dalam session yang ditampilkan 1x di template
Cocok untuk notifikasi success/error

### FILE HANDLING
file.seek(0, os.SEEK_END) - Pindah pointer ke akhir file
file.tell()               - Dapat posisi pointer (= ukuran file)
file.seek(0)              - Pindah pointer ke awal file
file.save(path)           - Simpan file ke disk


## FITUR UTAMA

1. UPLOAD DOKUMEN
   - Validasi format (harus .pdf)
   - Validasi ukuran (max 50MB)
   - secure_filename() untuk keamanan
   - Hapus file lama sebelum simpan yang baru

2. PREVIEW DOKUMEN
   - Tampil di iframe
   - Header cache control untuk prevent caching
   - Pop dari session setelah ditampilkan (1x display only)

3. EKSTRAKSI TEXT
   - Gunakan library fitz (PyMuPDF)
   - Hanya untuk file < 10MB
   - Extract dari setiap halaman kemudian gabung
   - Simpan di session untuk nanti digunakan di halaman hasil

4. PEMBERSIHAN FILE
   - Hapus file lama saat upload file baru
   - Hapus file saat user select file baru (via /clear-preview)
   - Hapus file saat user reload halaman


## DEBUGGING TIPS

Untuk melihat apa yang terjadi di server, lihat console terminal:
- print(f"Debug message: {variable}")
- Gunakan debug print untuk trace alur aplikasi

Untuk melihat request/response di browser:
- Buka Developer Tools (F12)
- Tab "Network" untuk lihat HTTP requests
- Tab "Console" untuk lihat JavaScript errors


## FILE STRUCTURE
app.py              - Main application (route, logic)
app_commented.py    - Versi app.py dengan komentar lengkap
templates/
  index.html        - Halaman upload & preview
  result.html       - Halaman hasil pemeriksaan
static/
  styles.css        - Styling
uploads/            - Folder untuk menyimpan PDF temporary


## NEXT STEPS (Yang perlu dikembangkan)
1. Implement logic pemeriksaan tanda baca
2. Tampilkan hasil pemeriksaan di halaman result.html
3. Tambah fitur download hasil pemeriksaan
4. Tambah fitur history upload
5. UI/UX improvement
