import re


class Tokenizer:
    def __init__(self, pattern=None):
        self.pattern = re.compile(pattern or r"\b\w+\b|[^\w\s]")

    def tokenize(self, text):
        if not text:
            return []
        return self.pattern.findall(text)

    def tokenize_sentences(self, sentences):
        if not sentences:
            return []
        return [self.tokenize(sentence) for sentence in sentences if sentence]
