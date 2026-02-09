import fitz


def extract_text_from_pdf(file_path):
    text_chunks = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text_chunks.append(page.get_text("text"))
    # Gunakan pemisah halaman agar normalisasi bisa menghapus header/footer berulang.
    return "\f".join(text_chunks).strip()
