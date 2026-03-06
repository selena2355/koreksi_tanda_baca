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
        self.pos_tagger = pos_tagger

    def preprocessing(self, teks):
        return self.text_normalizer.normalize(teks)

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

        # DOCX output is paragraph-friendly; avoid cross-paragraph merging.
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
