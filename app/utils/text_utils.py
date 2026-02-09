import re
import unicodedata
from collections import Counter


LIGATURE_MAP = {
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬀ": "ff",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "ﬅ": "ft",
    "ﬆ": "st",
}


def _normalize_unicode(teks):
    teks = unicodedata.normalize("NFKC", teks)
    teks = teks.replace("\u00a0", " ")
    teks = teks.replace("\u00ad", "")
    for ligature, replacement in LIGATURE_MAP.items():
        teks = teks.replace(ligature, replacement)
    return teks


def _split_pages(teks):
    if "\f" in teks:
        return teks.split("\f")
    return [teks]


def _strip_lines(lines):
    return [line.strip() for line in lines]


def _detect_repeating_lines(pages_lines, threshold_ratio=0.6, top_n=2, bottom_n=2):
    page_count = len(pages_lines)
    if page_count <= 1:
        return set(), set()

    header_counter = Counter()
    footer_counter = Counter()

    for lines in pages_lines:
        non_empty = [line for line in lines if line]
        if not non_empty:
            continue
        header_counter.update(non_empty[:top_n])
        footer_counter.update(non_empty[-bottom_n:])

    threshold = max(2, int(page_count * threshold_ratio + 0.5))
    header_to_remove = {line for line, count in header_counter.items() if count >= threshold}
    footer_to_remove = {line for line, count in footer_counter.items() if count >= threshold}
    return header_to_remove, footer_to_remove


def _remove_page_numbers(line):
    if re.match(r"^\d+$", line):
        return True
    if re.match(r"^(halaman|page)\s+\d+$", line, re.IGNORECASE):
        return True
    if re.match(r"^[ivxlcdm]+$", line, re.IGNORECASE):
        return True
    return False


def _merge_lines(lines):
    paragraphs = []
    buffer = ""

    for line in lines:
        if not line:
            if buffer:
                paragraphs.append(buffer.strip())
                buffer = ""
            continue

        if not buffer:
            buffer = line
            continue

        if buffer.endswith("-") and line and line[0].islower():
            buffer = buffer[:-1] + line
        else:
            buffer = f"{buffer} {line}"

    if buffer:
        paragraphs.append(buffer.strip())

    return "\n\n".join(paragraphs)


def normalize_text(teks):
    if not teks:
        return ""

    teks = _normalize_unicode(teks)
    teks = teks.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")

    pages = _split_pages(teks)
    pages_lines = [_strip_lines(page.split("\n")) for page in pages]

    header_to_remove, footer_to_remove = _detect_repeating_lines(pages_lines)

    cleaned_pages = []
    for lines in pages_lines:
        cleaned = []
        for line in lines:
            if not line:
                cleaned.append("")
                continue
            if line in header_to_remove or line in footer_to_remove:
                continue
            if _remove_page_numbers(line):
                continue
            cleaned.append(line)
        cleaned_pages.append(cleaned)

    merged_pages = [_merge_lines(lines) for lines in cleaned_pages if lines]
    merged_text = "\n\n".join([page for page in merged_pages if page.strip()])

    merged_text = re.sub(r"[ \t]+", " ", merged_text)
    merged_text = re.sub(r"\s+([,.;:?!])", r"\1", merged_text)
    merged_text = re.sub(r"\(\s+", "(", merged_text)
    merged_text = re.sub(r"\s+\)", ")", merged_text)
    merged_text = re.sub(r"\n{3,}", "\n\n", merged_text)

    return merged_text.strip()
