from app.utils.sbd_utils import SentenceBoundaryDetector


def test_segment_sentences_basic():
    detector = SentenceBoundaryDetector(engine="rule")
    text = "Halo. Apa kabar? Baik!"
    assert detector.segment_sentences(text) == ["Halo.", "Apa kabar?", "Baik!"]


def test_segment_sentences_title_abbreviation():
    detector = SentenceBoundaryDetector(engine="rule")
    text = "Saya bertemu dr. Andi hari ini."
    assert detector.segment_sentences(text) == ["Saya bertemu dr. Andi hari ini."]


def test_segment_sentences_number_period():
    detector = SentenceBoundaryDetector(engine="rule")
    text = "Nilai pi 3.14 penting. Selesai."
    assert detector.segment_sentences(text) == ["Nilai pi 3.14 penting.", "Selesai."]


def test_segment_sentences_includes_closing_chars():
    detector = SentenceBoundaryDetector(engine="rule")
    text = "Dia berkata (ya). Lalu pergi."
    assert detector.segment_sentences(text) == ["Dia berkata (ya).", "Lalu pergi."]


def test_segment_sentences_empty_text():
    detector = SentenceBoundaryDetector(engine="rule")
    assert detector.segment_sentences("") == []
