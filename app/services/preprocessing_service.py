import re

from ..utils.text_utils import TextNormalizer
from ..utils.sbd_utils import SentenceBoundaryDetector
from ..utils.tokenize_utils import Tokenizer
from ..utils.pos_tag_utils import POSTagger


class PreprocessingService:
    def __init__(self, text_normalizer=None, sbd_detector=None, tokenizer=None, pos_tagger=None):
        self.text_normalizer = text_normalizer or TextNormalizer()
        self.sbd_detector = sbd_detector or SentenceBoundaryDetector()
        self.tokenizer = tokenizer or Tokenizer()
        self.pos_tagger = pos_tagger or POSTagger()

    def preprocessing(self, teks):
        return self.text_normalizer.normalize(teks)

    def prepare_rule_text(self, teks):
        if not teks:
            return ""

        prepared_lines = []
        for line in teks.splitlines(keepends=True):
            prepared_lines.append(self._prepare_table_line_for_rules(line))
        return "".join(prepared_lines)

    def _prepare_table_line_for_rules(self, line):
        if not line:
            return line

        content = line.rstrip("\r\n")
        line_ending = line[len(content):]

        if not self._looks_like_table_row(content):
            return line

        # " | " -> "\n\n\n" supaya tiap sel jadi blok terpisah,
        # tapi panjang string tetap sama untuk menjaga offset error.
        return content.replace(" | ", "\n\n\n") + line_ending

    @staticmethod
    # Fungsi untuk mendeteksi apakah sebuah baris teks terlihat seperti baris tabel, dengan heuristik sederhana berdasarkan adanya pemisah " | ",
    # minimal dua sel yang tidak kosong, dan tidak mengandung URL, untuk menghindari kesalahan deteksi pada teks yang sebenarnya bukan tabel.
    def _looks_like_table_row(line):
        if not line or " | " not in line:
            return False

        if re.search(r"https?://|www\.", line):
            return False

        cells = [part.strip() for part in line.split(" | ")]
        non_empty_cells = [cell for cell in cells if cell]
        return len(non_empty_cells) >= 2

    def segment_sentences(self, teks):
        return self._segment_sentences_by_paragraph(teks)

    def tokenize_paragraph_sentences(self, teks):
        sentences = self._segment_sentences_by_paragraph(teks)
        return self.tokenizer.tokenize_sentences(sentences)

    def pos_tag_tokens(self, token_lists):
        if not token_lists:
            return []
        if self.pos_tagger is None:
            self.pos_tagger = POSTagger()
        return self.pos_tagger.tag_tokens(token_lists)

    def _segment_sentences_by_paragraph(self, teks):
        if not teks:
            return []

        if "\f" not in teks:
            paragraphs = re.split(r"\n\s*\n", teks)
            if len(paragraphs) > 1:
                sentences = []
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    sentences.extend(self.sbd_detector.segment_sentences(para))
                return sentences

        return self.sbd_detector.segment_sentences(teks)
