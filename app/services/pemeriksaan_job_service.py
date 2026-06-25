import os
import secrets
from datetime import datetime

from ..config import Config
from ..extensions import db
from ..models import PemeriksaanJob
from ..services.ekstraksi_teks_service import TextExtractor
from ..services.preprocessing_service import PreprocessingService
from ..services.pemeriksaan_dokumen_service import PemeriksaanDokumenService
from ..utils.docx_utils import DocxUtils
from ..utils.file_utils import FileUtils
from ..utils.text_utils import TextNormalizer


class JobCancelled(Exception):
    pass


class PemeriksaanJobService:
    ERROR_TYPE_MAPPING = {
        "BD": "Tanda Baca Dasar",
        "DD": "Tanda Titik",
        "CmD": "Tanda Koma",
        "QtD": "Tanda Petik",
        "QsD": "Tanda Tanya",
        "HD": "Tanda Hubung",
        "CnD": "Titik Dua",
    }

    def __init__(
        self,
        docx_extractor=None,
        preprocessing_service=None,
        pemeriksaan_service=None,
        file_utils=None,
        text_normalizer=None,
    ):
        self.text_normalizer = text_normalizer or TextNormalizer()
        self.preprocessing_service = preprocessing_service or PreprocessingService(
            text_normalizer=self.text_normalizer
        )
        self.docx_extractor = docx_extractor or TextExtractor()
        self.file_utils = file_utils or FileUtils()
        self.docx_utils = DocxUtils()
        self.pemeriksaan_service = pemeriksaan_service or PemeriksaanDokumenService(
            preprocessing_service=self.preprocessing_service
        )

    def buat_job(self, nama_dokumen, pengguna_id=None):
        job = PemeriksaanJob(
            job_token=secrets.token_urlsafe(24),
            pengguna_id=pengguna_id,
            nama_dokumen=nama_dokumen,
            status=PemeriksaanJob.STATUS_PENDING,
            progress=0,
        )
        db.session.add(job)
        db.session.commit()
        return job

    def ambil_job_berikutnya(self):
        # MySQL REPEATABLE READ can keep an old snapshot open between polling loops.
        db.session.rollback()
        return (
            PemeriksaanJob.query.filter_by(status=PemeriksaanJob.STATUS_PENDING)
            .order_by(PemeriksaanJob.created_at.asc(), PemeriksaanJob.id.asc())
            .first()
        )

    def proses_job_berikutnya(self):
        job = self.ambil_job_berikutnya()
        if not job:
            return None
        self.proses_job(job)
        return job

    def cleanup_expired_jobs(self, now=None):
        now = now or datetime.utcnow()
        db.session.rollback()
        expired_jobs = (
            PemeriksaanJob.query.filter(
                PemeriksaanJob.status.in_(
                    [
                        PemeriksaanJob.STATUS_DONE,
                        PemeriksaanJob.STATUS_FAILED,
                        PemeriksaanJob.STATUS_CANCELLED,
                    ]
                ),
                PemeriksaanJob.expires_at <= now,
            )
            .order_by(PemeriksaanJob.expires_at.asc(), PemeriksaanJob.id.asc())
            .all()
        )

        for job in expired_jobs:
            self._hapus_file_job(job)
            db.session.delete(job)

        if expired_jobs:
            db.session.commit()

        return len(expired_jobs)

    def proses_job(self, job):
        if self._is_cancelled(job):
            return

        self._update_job(job, status=PemeriksaanJob.STATUS_PROCESSING, progress=5, error_message=None)

        try:
            result = self._proses_dokumen(job)
            if self._is_cancelled(job):
                return
            self._update_job(
                job,
                status=PemeriksaanJob.STATUS_DONE,
                progress=100,
                result_token=secrets.token_urlsafe(24),
                **result,
            )
        except JobCancelled:
            self._update_job(job, status=PemeriksaanJob.STATUS_CANCELLED, progress=100)
        except Exception as exc:
            self._update_job(
                job,
                status=PemeriksaanJob.STATUS_FAILED,
                progress=100,
                error_message=str(exc) or "Gagal memproses dokumen.",
            )

    def _proses_dokumen(self, job):
        self._raise_if_cancelled(job)
        file_path = os.path.join(Config.UPLOAD_FOLDER, job.nama_dokumen)
        if not os.path.exists(file_path):
            raise FileNotFoundError("Dokumen tidak ditemukan, silakan unggah ulang.")

        self._set_progress(job, 15)
        self._raise_if_cancelled(job)
        extract_result = self.docx_extractor.extract(file_path)
        if not isinstance(extract_result, dict) or extract_result.get("format") != "docx":
            raise ValueError("Format dokumen tidak didukung. Hanya DOCX yang bisa diproses.")

        paragraphs = extract_result.get("paragraphs") or []
        extracted_text = "\n\n".join(paragraphs) if paragraphs else extract_result.get("text", "")
        if not extracted_text or not extracted_text.strip():
            raise ValueError("Teks DOCX kosong atau tidak terbaca.")

        self._set_progress(job, 30)
        self._raise_if_cancelled(job)
        normalized_text = self.preprocessing_service.preprocessing(extracted_text)
        analysis_text = self.preprocessing_service.prepare_rule_text(normalized_text)

        sentences = self._safe_segment_sentences(analysis_text)
        structured_text = self.text_normalizer.normalize_structured(sentences)
        block_texts = self._build_block_texts(structured_text)

        self._set_progress(job, 50)
        self._raise_if_cancelled(job)
        tokens = self._safe_tokenize(block_texts)

        self._set_progress(job, 70)
        self._raise_if_cancelled(job)
        pos_tags = self._safe_pos_tag(tokens)
        flat_tokens = self._flatten_pos_tags(pos_tags, normalized_text)

        self._set_progress(job, 85)
        self._raise_if_cancelled(job)
        deteksi_result = self.pemeriksaan_service.deteksi_dan_koreksi(
            normalized_text,
            konteks={"tokens": flat_tokens},
        )

        return self._simpan_hasil(
            job,
            normalized_text=normalized_text,
            structured_text=structured_text,
            sentences=sentences,
            tokens=tokens,
            pos_tags=pos_tags,
            koreksi_text=deteksi_result["koreksi_text"],
            detection_html=deteksi_result["detection_html"],
            correction_html=deteksi_result["correction_html"],
            kesalahan_list=deteksi_result["kesalahan_list"],
        )

    def _simpan_hasil(
        self,
        job,
        normalized_text,
        structured_text,
        sentences,
        tokens,
        pos_tags,
        koreksi_text,
        detection_html,
        correction_html,
        kesalahan_list=None,
    ):
        text_filename = f"{job.nama_dokumen}.txt"
        detection_html_filename = f"{job.nama_dokumen}.highlight.html"
        correction_html_filename = f"{job.nama_dokumen}.correction.highlight.html"
        json_filename = f"{job.nama_dokumen}.json"
        sbd_filename = f"{job.nama_dokumen}.sbd.json"
        tokens_filename = f"{job.nama_dokumen}.tokens.json"
        pos_filename = f"{job.nama_dokumen}.pos.json"

        self.file_utils.write_text_file(Config.DETECTION_RESULT_FOLDER, text_filename, normalized_text)
        self.file_utils.write_text_file(
            Config.DETECTION_RESULT_FOLDER,
            detection_html_filename,
            detection_html,
        )
        self.file_utils.write_text_file(Config.CORRECTION_RESULT_FOLDER, text_filename, koreksi_text)
        self.file_utils.write_text_file(
            Config.CORRECTION_RESULT_FOLDER,
            correction_html_filename,
            correction_html,
        )

        # Buat ringkasan kesalahan
        error_summary = self._buat_error_summary(kesalahan_list)
        summary_filename = f"{job.nama_dokumen}.summary.json"
        self.file_utils.write_json_file(
            Config.DETECTION_RESULT_FOLDER,
            summary_filename,
            error_summary,
        )

        result = {
            "extracted_text_file": text_filename,
            "detection_result_html_file": detection_html_filename,
            "correction_result_file": text_filename,
            "correction_result_html_file": correction_html_filename,
        }

        if Config.DEBUG_SAVE:
            self.file_utils.write_text_file(Config.DEBUG_FOLDER, text_filename, normalized_text)
            self.file_utils.write_json_file(Config.DEBUG_FOLDER, json_filename, structured_text)
            self.file_utils.write_json_file(Config.DEBUG_FOLDER, sbd_filename, sentences)
            self.file_utils.write_json_file(Config.DEBUG_FOLDER, tokens_filename, tokens)
            self.file_utils.write_json_file(Config.DEBUG_FOLDER, pos_filename, pos_tags)
            result.update(
                {
                    "debug_normalized_file": text_filename,
                    "structured_text_file": json_filename,
                    "sbd_file": sbd_filename,
                    "tokens_file": tokens_filename,
                    "pos_file": pos_filename,
                }
            )
        else:
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, text_filename)
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, json_filename)
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, sbd_filename)
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, tokens_filename)
            self.file_utils.remove_file_if_exists(Config.DEBUG_FOLDER, pos_filename)

        return result

    def _buat_error_summary(self, kesalahan_list):
        """Membuat ringkasan kesalahan yang dikelompokkan berdasarkan tanda baca."""
        if not kesalahan_list:
            return {
                "total": 0,
                "by_type": {},
                "items": [],
            }

        error_groups = {}
        by_type = {}
        for kesalahan in kesalahan_list:
            kode = getattr(kesalahan, "kode", "unknown")
            jenis = getattr(kesalahan, "jenis", "unknown")
            if kode not in error_groups:
                error_groups[kode] = {"count": 0, "jenis": jenis}
            error_groups[kode]["count"] += 1

            type_key = self._type_key_from_kode(kode)
            type_name = self._nama_tipe_kesalahan(type_key)
            if type_key not in by_type:
                by_type[type_key] = {"name": type_name, "count": 0}
            by_type[type_key]["count"] += 1

        items = [
            {"type_key": type_key, "name": info["name"], "count": info["count"]}
            for type_key, info in sorted(by_type.items(), key=lambda item: item[1]["name"])
        ]

        return {
            "total": len(kesalahan_list),
            "by_type": {info["name"]: info["count"] for info in by_type.values()},
            "by_code": error_groups,
            "items": items,
        }

    @classmethod
    def _type_key_from_kode(cls, kode):
        kode = str(kode or "")
        for prefix in sorted(cls.ERROR_TYPE_MAPPING, key=len, reverse=True):
            if kode.startswith(prefix):
                return prefix
        return "unknown"

    @classmethod
    def _nama_tipe_kesalahan(cls, type_key):
        if type_key in cls.ERROR_TYPE_MAPPING:
            return cls.ERROR_TYPE_MAPPING[type_key]
        return "Lainnya"

    def _safe_segment_sentences(self, analysis_text):
        try:
            return self.preprocessing_service.segment_sentences(analysis_text)
        except Exception:
            return []

    def _safe_tokenize(self, block_texts):
        try:
            return self.preprocessing_service.tokenizer.tokenize_sentences(block_texts)
        except Exception:
            return []

    def _safe_pos_tag(self, tokens):
        try:
            return self.preprocessing_service.pos_tag_tokens(tokens)
        except Exception:
            return []

    @staticmethod
    def _build_block_texts(structured_text):
        block_texts = []
        for block in structured_text:
            if not isinstance(block, dict):
                continue
            text_value = block.get("text")
            if text_value:
                block_texts.append(text_value)
                continue
            label_value = block.get("label")
            if label_value:
                block_texts.append(label_value)
                continue
            cells_value = block.get("cells")
            if cells_value:
                block_texts.append(" | ".join(cell for cell in cells_value if cell))
        return block_texts

    @staticmethod
    def _flatten_pos_tags(pos_tags, normalized_text):
        flat = []
        search_start = 0
        for sent in pos_tags:
            for tag in sent:
                word = tag["token"]
                idx = normalized_text.find(word, search_start)
                if idx == -1:
                    flat.append(
                        {
                            "text": word,
                            "upos": tag["upos"],
                            "xpos": tag["xpos"],
                            "lemma": tag.get("lemma", ""),
                            "start_char": -1,
                            "end_char": -1,
                        }
                    )
                    continue
                flat.append(
                    {
                        "text": word,
                        "upos": tag["upos"],
                        "xpos": tag["xpos"],
                        "lemma": tag.get("lemma", ""),
                        "start_char": idx,
                        "end_char": idx + len(word),
                    }
                )
                search_start = idx + len(word)
        return flat

    def _set_progress(self, job, progress):
        self._update_job(job, progress=progress)

    def _hapus_file_job(self, job):
        self.file_utils.remove_file_if_exists(Config.UPLOAD_FOLDER, job.nama_dokumen)

        self._remove_if_present(Config.DETECTION_RESULT_FOLDER, job.extracted_text_file)
        self._remove_if_present(Config.DETECTION_RESULT_FOLDER, job.detection_result_html_file)
        self._remove_if_present(Config.DETECTION_RESULT_FOLDER, f"{job.nama_dokumen}.summary.json")
        self._remove_if_present(Config.CORRECTION_RESULT_FOLDER, job.correction_result_file)
        self._remove_if_present(Config.CORRECTION_RESULT_FOLDER, job.correction_result_html_file)
        self._remove_if_present(Config.DEBUG_FOLDER, job.debug_normalized_file)
        self._remove_if_present(Config.DEBUG_FOLDER, job.structured_text_file)
        self._remove_if_present(Config.DEBUG_FOLDER, job.sbd_file)
        self._remove_if_present(Config.DEBUG_FOLDER, job.tokens_file)
        self._remove_if_present(Config.DEBUG_FOLDER, job.pos_file)

    def _remove_if_present(self, folder_path, filename):
        if filename:
            self.file_utils.remove_file_if_exists(folder_path, filename)

    @staticmethod
    def _is_cancelled(job):
        job_id = job.id
        db.session.rollback()
        fresh_job = db.session.get(PemeriksaanJob, job_id)
        return fresh_job and fresh_job.status == PemeriksaanJob.STATUS_CANCELLED

    def _raise_if_cancelled(self, job):
        if self._is_cancelled(job):
            raise JobCancelled()

    @staticmethod
    def _update_job(job, **values):
        for key, value in values.items():
            setattr(job, key, value)
        job.updated_at = datetime.utcnow()
        db.session.commit()
