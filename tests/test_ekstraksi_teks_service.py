import importlib.util
from pathlib import Path

import pytest

docx = pytest.importorskip("docx")

MODULE_PATH = Path(__file__).resolve().parents[1] / "app" / "services" / "ekstraksi_teks_service.py"
SPEC = importlib.util.spec_from_file_location("ekstraksi_teks_service", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
TextExtractor = MODULE.TextExtractor


def test_extract_docx_includes_table_rows_in_document_order(tmp_path):
    document = docx.Document()
    document.add_paragraph("Paragraf pembuka.")

    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Nama"
    table.cell(0, 1).text = "Nilai"
    table.cell(1, 0).text = "Budi"
    table.cell(1, 1).text = "90"

    document.add_paragraph("Paragraf penutup.")

    file_path = tmp_path / "sample.docx"
    document.save(file_path)

    result = TextExtractor().extract(str(file_path))

    assert result["paragraphs"] == [
        "Paragraf pembuka.",
        "Nama | Nilai",
        "Budi | 90",
        "Paragraf penutup.",
    ]
    assert result["tables"] == ["Nama | Nilai", "Budi | 90"]
    assert result["metadata"]["table_count"] == 1
    assert result["metadata"]["table_row_count"] == 2
    assert result["text"] == (
        "Paragraf pembuka.\n\n"
        "Nama | Nilai\n\n"
        "Budi | 90\n\n"
        "Paragraf penutup."
    )
