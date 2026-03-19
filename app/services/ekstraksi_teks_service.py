"""
Text Extraction Service - Fokus DOCX
Simplified & optimized untuk aplikasi koreksi tanda baca
"""
import re

try:
    from docx import Document
    from docx.document import Document as DocxDocument
    from docx.oxml.ns import qn
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    Document = None
    DocxDocument = None
    qn = None
    CT_Tbl = None
    CT_P = None
    Table = None
    Paragraph = None


class TextExtractor:
    """
    Text extractor untuk DOCX
    """
    
    def __init__(self):
        self.supported_formats = self._get_supported_formats()
    
    def _get_supported_formats(self):
        """Deteksi format yang tersedia"""
        formats = []
        if DOCX_AVAILABLE:
            formats.append('.docx')
        return formats
    
    def extract(self, file_path: str) -> dict:
        """
        Extract text dari file DOCX
        
        Returns:
            {
                'text': str,              # Raw text
                'paragraphs': list[str],  # Clean paragraphs (recommended untuk processing)
                'tables': list[str],      # Flattened table rows
                'table_blocks': list[str],# Table text grouped per table
                'metadata': dict,         # File metadata
                'format': str,            # 'docx'
                'quality': str            # 'high', 'medium', or 'low'
            }
        """
        file_path_lower = file_path.lower()
        
        if file_path_lower.endswith('.docx'):
            return self._extract_docx(file_path)

        raise ValueError(f"Format tidak didukung. Supported: {self.supported_formats}")
    
    # ==========================
    # DOCX EXTRACTION (SIMPLE & CLEAN)
    # ==========================
    
    def _extract_docx(self, file_path: str) -> dict:
        """
        Extract dari DOCX - Simple & Clean!
        Paragraf sudah terpisah rapi, tidak perlu merge logic
        """
        if not DOCX_AVAILABLE:
            raise RuntimeError(
                "python-docx belum terinstall. "
                "Install dengan: pip install python-docx"
            )
        
        document = Document(file_path)

        numbering_map = self._build_numbering_map(document)
        counters = {}
        style_counters = {}

        paragraphs = []
        table_texts = []
        table_blocks = []

        for block in self._iter_block_items(document):
            if isinstance(block, Paragraph):
                text = self._prepare_paragraph_text(
                    block,
                    numbering_map,
                    counters,
                    style_counters,
                )
                if text:
                    paragraphs.append(text)
                continue

            if isinstance(block, Table):
                table_lines = self._extract_table_lines(block)
                if not table_lines:
                    continue
                paragraphs.extend(table_lines)
                table_texts.extend(table_lines)
                table_blocks.append("\n".join(table_lines))

        all_text = "\n\n".join(paragraphs)
        
        # Extract metadata
        metadata = {
            'title': document.core_properties.title or '',
            'author': document.core_properties.author or '',
            'created': str(document.core_properties.created) if document.core_properties.created else '',
            'modified': str(document.core_properties.modified) if document.core_properties.modified else '',
            'paragraph_count': len(paragraphs),
            'table_count': len(document.tables),
            'table_row_count': len(table_texts),
        }
        
        return {
            'text': all_text,
            'paragraphs': paragraphs,  # ✅ Clean & ready to use!
            'tables': table_texts,
            'table_blocks': table_blocks,
            'metadata': metadata,
            'format': 'docx',
            'quality': 'high'  # DOCX = high quality extraction
        }

    def _prepare_paragraph_text(self, paragraph, numbering_map, counters, style_counters):
        text = self._extract_paragraph_text(paragraph)
        if not text:
            text = paragraph.text or ""
        text = text.strip()
        if not text:
            return ""

        prefix = self._get_list_prefix(
            paragraph,
            text,
            numbering_map,
            counters,
            style_counters,
        )
        if prefix:
            text = f"{prefix} {text}"

        return text

    def _iter_block_items(self, parent):
        if not DOCX_AVAILABLE:
            return

        if isinstance(parent, DocxDocument):
            parent_element = parent.element.body
        else:
            parent_element = parent._tc

        for child in parent_element.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    def _extract_table_lines(self, table):
        lines = []
        for row in table.rows:
            cells = self._extract_row_cells(row)
            if not any(cell.strip() for cell in cells):
                continue
            lines.append(" | ".join(cells).strip())
        return lines

    def _extract_row_cells(self, row):
        cells = []
        seen = set()

        for cell in row.cells:
            cell_id = id(cell._tc)
            if cell_id in seen:
                continue
            seen.add(cell_id)
            cells.append(self._extract_cell_text(cell))

        return cells

    def _extract_cell_text(self, cell):
        fragments = []

        for block in self._iter_block_items(cell):
            if isinstance(block, Paragraph):
                text = self._extract_paragraph_text(block)
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    fragments.append(text)
                continue

            if isinstance(block, Table):
                nested_lines = self._extract_table_lines(block)
                if nested_lines:
                    fragments.append(" ; ".join(nested_lines))

        return " ".join(fragments).strip()

    def _extract_paragraph_text(self, paragraph):
        if not DOCX_AVAILABLE:
            return ""

        texts = []
        try:
            for node in paragraph._p.iter():
                tag = getattr(node, "tag", "")
                if not tag:
                    continue
                if tag.endswith("}t") and node.text:
                    texts.append(node.text)
                elif tag.endswith("}tab"):
                    texts.append("\t")
                elif tag.endswith("}br") or tag.endswith("}cr"):
                    texts.append("\n")
        except Exception:
            return paragraph.text or ""

        return "".join(texts)

    def _build_numbering_map(self, document):
        if not DOCX_AVAILABLE:
            return {}

        try:
            numbering_part = document.part.numbering_part
            numbering = numbering_part.element
        except Exception:
            return {}

        num_to_abstract = {}
        abstract_levels = {}

        for num in numbering.findall(qn("w:num")):
            num_id = num.get(qn("w:numId"))
            abstract = num.find(qn("w:abstractNumId"))
            if num_id is None or abstract is None:
                continue
            abstract_id = abstract.get(qn("w:val"))
            if abstract_id is None:
                continue
            num_to_abstract[int(num_id)] = int(abstract_id)

        for abstract in numbering.findall(qn("w:abstractNum")):
            abstract_id = abstract.get(qn("w:abstractNumId"))
            if abstract_id is None:
                continue
            abstract_id = int(abstract_id)
            levels = {}
            for lvl in abstract.findall(qn("w:lvl")):
                ilvl = lvl.get(qn("w:ilvl"))
                if ilvl is None:
                    continue
                ilvl = int(ilvl)
                num_fmt_el = lvl.find(qn("w:numFmt"))
                lvl_text_el = lvl.find(qn("w:lvlText"))
                num_fmt = num_fmt_el.get(qn("w:val")) if num_fmt_el is not None else None
                lvl_text = lvl_text_el.get(qn("w:val")) if lvl_text_el is not None else None
                levels[ilvl] = {
                    "numFmt": num_fmt,
                    "lvlText": lvl_text,
                }
            abstract_levels[abstract_id] = levels

        return {"num_to_abstract": num_to_abstract, "abstract_levels": abstract_levels}

    def _get_list_prefix(self, paragraph, text, numbering_map, counters, style_counters):
        if not DOCX_AVAILABLE:
            return ""

        if self._has_inline_numbering(text):
            return ""

        num_pr = self._resolve_numpr(paragraph)
        if num_pr is not None and num_pr.numId is not None:
            num_id = int(num_pr.numId.val)
            ilvl = int(num_pr.ilvl.val) if num_pr.ilvl is not None else 0

            abstract_id = numbering_map.get("num_to_abstract", {}).get(num_id)
            level_info = (
                numbering_map.get("abstract_levels", {})
                .get(abstract_id, {})
                .get(ilvl, {})
                if abstract_id is not None
                else {}
            )
            num_fmt = level_info.get("numFmt")
            lvl_text = level_info.get("lvlText")

            if num_fmt == "bullet":
                return "-"

            for key in list(counters.keys()):
                if key[0] == num_id and key[1] > ilvl:
                    counters[key] = 0
            counters[(num_id, ilvl)] = counters.get((num_id, ilvl), 0) + 1

            if lvl_text:
                label = lvl_text
                for level in range(0, 9):
                    placeholder = f"%{level + 1}"
                    if placeholder in label:
                        value = counters.get((num_id, level), 0)
                        if value == 0 and level == ilvl:
                            value = counters[(num_id, ilvl)]
                        label = label.replace(placeholder, str(value))
                return label

            return f"{counters[(num_id, ilvl)]}."

        style_name = ""
        try:
            style_name = (paragraph.style.name or "").lower()
        except Exception:
            style_name = ""

        if "list bullet" in style_name or "bullet" in style_name:
            return "-"
        if "list number" in style_name or "number" in style_name:
            style_counters[style_name] = style_counters.get(style_name, 0) + 1
            return f"{style_counters[style_name]}."

        return ""

    def _resolve_numpr(self, paragraph):
        ppr = getattr(paragraph._p, "pPr", None)
        num_pr = getattr(ppr, "numPr", None) if ppr is not None else None
        if num_pr is not None and num_pr.numId is not None:
            return num_pr

        style = getattr(paragraph, "style", None)
        return self._get_numpr_from_style(style)

    def _get_numpr_from_style(self, style):
        while style is not None:
            ppr = getattr(getattr(style, "_element", None), "pPr", None)
            num_pr = getattr(ppr, "numPr", None) if ppr is not None else None
            if num_pr is not None and num_pr.numId is not None:
                return num_pr
            style = getattr(style, "base_style", None)
        return None

    @staticmethod
    def _has_inline_numbering(text):
        text = text.strip()
        if re.match(r"^\d+(\.\d+)*\s+", text):
            return True
        if re.match(r"^[A-Za-z]\.\s+", text):
            return True
        if re.match(r"^(BAB|Bab)\s+[IVX\d]+", text):
            return True
        if re.match(r"^[-•]\s+", text):
            return True
        return False

# ==========================
# CONVENIENCE FUNCTIONS
# ==========================

def extract_text(file_path: str) -> dict:
    """
    Convenience function untuk extract text dari file
    
    Usage:
        result = extract_text("document.docx")
        paragraphs = result['paragraphs']  # Ready to process!
    """
    extractor = TextExtractor()
    return extractor.extract(file_path)


def extract_paragraphs(file_path: str) -> list:
    """
    Extract hanya paragraphs (untuk processing tanda baca)
    
    Usage:
        paragraphs = extract_paragraphs("document.docx")
        for para in paragraphs:
            # Process each paragraph
            pass
    """
    result = extract_text(file_path)
    
    if result['format'] == 'docx':
        return result['paragraphs']

    raise ValueError("Format tidak didukung. Hanya DOCX yang tersedia.")


# ==========================
# USAGE EXAMPLES
# ==========================

if __name__ == "__main__":
    import sys
    import json
    
    print("="*80)
    print("TEXT EXTRACTOR - DOCX Priority")
    print("="*80)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python ekstraksi_teks_service.py <file.docx>")
        print("\nExample:")
        print("  python ekstraksi_teks_service.py document.docx")
        sys.exit(0)
    
    file_path = sys.argv[1]
    
    try:
        # Extract
        print(f"\n📄 Processing: {file_path}")
        result = extract_text(file_path)
        
        # Show summary
        print(f"\n✅ Extraction successful!")
        print(f"   Format: {result['format']}")
        print(f"   Quality: {result['quality']}")
        print(f"   Paragraphs: {len(result['paragraphs'])}")
        
        # Show metadata
        if result['metadata']:
            print(f"\n📊 Metadata:")
            for key, value in result['metadata'].items():
                print(f"   {key}: {value}")
        
        # Show sample
        print(f"\n📝 Sample paragraphs (first 3):")
        for i, para in enumerate(result['paragraphs'][:3], 1):
            preview = para[:100] + "..." if len(para) > 100 else para
            print(f"\n   {i}. {preview}")
        
        # Save result
        output_file = file_path + "_extracted.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Result saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
