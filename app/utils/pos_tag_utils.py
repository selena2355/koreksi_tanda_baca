import os

try:
    import stanza
except Exception:
    stanza = None

from ..config import ROOT_DIR


class POSTagger:
    def __init__(self, lang=None, model_dir=None, auto_download=None, batch_size=None):
        if stanza is None:
            raise RuntimeError("Stanza belum terpasang. Install dengan: pip install stanza")

        self.lang = lang or os.getenv("STANZA_LANG", "id")
        self.model_dir = model_dir or os.getenv(
            "STANZA_DIR",
            os.path.join(ROOT_DIR, "models", "stanza"),
        )
        if auto_download is None:
            env_auto = os.getenv("STANZA_AUTO_DOWNLOAD")
            if env_auto is None:
                resources_path = os.path.join(self.model_dir, "resources.json")
                auto_download = not os.path.exists(resources_path)
            else:
                auto_download = env_auto == "1"
        self.auto_download = bool(auto_download)
        if batch_size is None:
            env_batch = os.getenv("POS_BATCH_SIZE", "0")
            try:
                batch_size = int(env_batch)
            except ValueError:
                batch_size = 0
        self.batch_size = batch_size if batch_size and batch_size > 0 else None
        self._pipeline = None

    def tag_tokens(self, token_lists):
        token_lists = self._normalize_token_lists(token_lists)
        if not token_lists:
            return []

        pipeline = self._get_pipeline()
        results = []
        if self.batch_size and len(token_lists) > self.batch_size:
            for idx in range(0, len(token_lists), self.batch_size):
                batch = token_lists[idx: idx + self.batch_size]
                results.extend(self._tag_batch(pipeline, batch))
            return results

        return self._tag_batch(pipeline, token_lists)

    def _get_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        resources_path = os.path.join(self.model_dir, "resources.json")
        if self.auto_download:
            stanza.download(self.lang, model_dir=self.model_dir, processors="tokenize,pos")
        elif not os.path.exists(resources_path):
            raise RuntimeError(
                "Model Stanza tidak ditemukan. Jalankan: "
                "python -c \"import stanza; stanza.download('id', processors='tokenize,pos', "
                f"model_dir=r'{self.model_dir}')\" "
                "atau set STANZA_AUTO_DOWNLOAD=1."
            )

        self._pipeline = stanza.Pipeline(
            lang=self.lang,
            processors="tokenize,pos",
            tokenize_pretokenized=True,
            use_gpu=False,
            dir=self.model_dir,
            verbose=False,
        )
        return self._pipeline

    def _normalize_token_lists(self, token_lists):
        if not token_lists:
            return []
        if isinstance(token_lists, (list, tuple)) and token_lists and isinstance(token_lists[0], str):
            token_lists = [token_lists]

        cleaned = []
        for sent in token_lists:
            if not sent:
                continue
            if isinstance(sent, str):
                tokens = [tok for tok in sent.split() if tok]
            else:
                tokens = [str(tok) for tok in sent if tok is not None and str(tok).strip()]
            if tokens:
                cleaned.append(tokens)
        return cleaned

    def _tag_batch(self, pipeline, token_lists):
        try:
            doc = pipeline(token_lists)
        except Exception:
            doc = pipeline(stanza.Document(token_lists))

        if not getattr(doc, "sentences", None):
            raise RuntimeError("POS tagging menghasilkan 0 kalimat. Format token tidak terbaca.")

        results = []
        for sent in doc.sentences:
            sent_tags = []
            for word in sent.words:
                sent_tags.append(
                    {
                        "token": word.text,
                        "upos": word.upos,
                        "xpos": word.xpos,
                        "lemma": word.lemma,
                    }
                )
            results.append(sent_tags)
        return results
