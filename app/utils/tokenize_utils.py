import re


_GELAR_SET = {
    "Dr", "Prof", "Ir", "Drs", "Dra",
    "Hj",
    "dr", "drg",
    "Apt",
    "S.H", "S.E", "S.T", "S.Pd", "S.Sos", "S.Kom",
    "S.Kep", "S.Farm", "S.Psi", "S.P", "S.Hut",
    "S.I.P", "S.I.Kom",
    "M.Si", "M.Pd", "M.Hum", "M.T", "M.H", "M.M",
    "M.Kes", "M.Kom", "M.E", "M.Ak",
    "Ph.D",
    "A.Md", "A.Ma",
    "Sp", "SpA", "SpB", "SpOG", "SpPD", "SpJP",
}

_GELAR_PREFIX = {}
for _g in _GELAR_SET:
    _parts = _g.split(".")
    _GELAR_PREFIX.setdefault(_parts[0], set()).add(_g)


def _merge_gelar(tokens):
    merged = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]

        if tok in _GELAR_PREFIX:
            # Coba pola 3 bagian dulu: X.Y.Z (S.I.Kom, S.I.P)
            # Harus dicek lebih dulu karena S.I tidak ada di set
            if (i + 4 < len(tokens)
                    and tokens[i + 1] == "."
                    and tokens[i + 3] == "."
                    and f"{tok}.{tokens[i+2]}.{tokens[i+4]}" in _GELAR_SET):
                merged.append(f"{tok}.{tokens[i+2]}.{tokens[i+4]}")
                i += 5
                continue
            # Coba pola 2 bagian: X.Y (S.Pd, M.Si, A.Md, dll.)
            if (i + 2 < len(tokens)
                    and tokens[i + 1] == "."
                    and f"{tok}.{tokens[i+2]}" in _GELAR_SET):
                merged.append(f"{tok}.{tokens[i+2]}")
                i += 3
                continue

        merged.append(tok)
        i += 1
    return merged


class Tokenizer:
    def __init__(self, pattern=None):
        self.pattern = re.compile(pattern or r"\b\w+\b|[^\w\s]")

    def tokenize(self, text):
        if not text:
            return []
        tokens = self.pattern.findall(text)
        return _merge_gelar(tokens)

    def tokenize_sentences(self, sentences):
        if not sentences:
            return []
        return [self.tokenize(sentence) for sentence in sentences if sentence]