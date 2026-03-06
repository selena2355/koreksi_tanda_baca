"""
Text Utils - DOCX only
Fokus: normalisasi ringan untuk teks DOCX
"""

import re
import unicodedata
from typing import List, Dict


class TextNormalizer:
    """
    Text normalizer khusus DOCX.
    """

    ZERO_WIDTH_CHARS = [
        "\u200b",  # Zero-width space
        "\u200c",  # Zero-width non-joiner
        "\u200d",  # Zero-width joiner
        "\u200e",  # Left-to-right mark
        "\u200f",  # Right-to-left mark
        "\ufeff",  # Byte order mark (BOM)
        "\u00ad",  # Soft hyphen
    ]

    def normalize_docx(self, text: str) -> str:
        """
        Normalize text dari DOCX - ringan & aman.
        """
        if not text:
            return ""

        for char in self.ZERO_WIDTH_CHARS:
            text = text.replace(char, "")

        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\s+([,.;:?!])", r"\1", text)
        text = re.sub(r"\(\s+", "(", text)
        text = re.sub(r"\s+\)", ")", text)

        return text.strip()

    def normalize(self, text: str) -> str:
        """
        Alias untuk normalize_docx (karena hanya DOCX).
        """
        return self.normalize_docx(text)

    def normalize_structured_docx(self, paragraphs: List[str]) -> List[Dict]:
        """
        Convert DOCX paragraphs ke structured blocks.
        """
        blocks = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if self._is_heading(para):
                block_type = "heading"
            elif self._is_list_item(para):
                block_type = "list_item"
            else:
                block_type = "paragraph"

            blocks.append(
                {
                    "type": block_type,
                    "text": self.normalize_docx(para),
                }
            )
        return blocks

    def normalize_structured(self, text_or_paragraphs) -> List[Dict]:
        """
        Structured output untuk DOCX.
        Accepts:
        - list[str] paragraphs
        - raw text (split by double newline)
        """
        if isinstance(text_or_paragraphs, list):
            paragraphs = text_or_paragraphs
        else:
            paragraphs = [
                p.strip()
                for p in str(text_or_paragraphs).split("\n\n")
                if p.strip()
            ]
        return self.normalize_structured_docx(paragraphs)

    def _is_heading(self, line: str) -> bool:
        if re.match(r"^\d+(\.\d+)*\s+", line):
            return True
        if line.isupper() and len(line) < 80:
            return True
        words = [w for w in line.split() if w.isalpha()]
        if words and len(words) <= 10:
            capital_ratio = sum(1 for w in words if w[0].isupper()) / len(words)
            if capital_ratio >= 0.7 and len(line) < 80:
                return True
        return False

    def _is_list_item(self, line: str) -> bool:
        if re.match(r"^\d+\.\s+", line):
            return True
        if re.match(r"^[-\u2022*\u2013]\s+", line):
            return True
        if re.match(r"^[a-z]\.\s+", line):
            return True
        return False


def detect_sentences(text: str) -> List[str]:
    """
    Simple sentence boundary detection.
    """
    sentences = []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    for part in parts:
        part = part.strip()
        if part:
            sentences.append(part)
    return sentences


def tokenize(text: str) -> List[str]:
    """
    Simple tokenization: words + punctuation.
    """
    return re.findall(r"\b\w+\b|[^\w\s]", text)


_DEFAULT_NORMALIZER = TextNormalizer()


def normalize_text(text: str) -> str:
    """
    Convenience function untuk normalisasi DOCX.
    """
    return _DEFAULT_NORMALIZER.normalize_docx(text)


def normalize_paragraphs(paragraphs: List[str]) -> List[str]:
    """
    Normalize list of paragraphs (DOCX).
    """
    return [
        _DEFAULT_NORMALIZER.normalize_docx(p)
        for p in paragraphs
        if p.strip()
    ]


def normalize_structured(text_or_paragraphs) -> List[Dict]:
    """
    Get structured output (type + text) untuk DOCX.
    """
    return _DEFAULT_NORMALIZER.normalize_structured(text_or_paragraphs)
