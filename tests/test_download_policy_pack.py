from pathlib import Path

import scripts.download_policy_pack as dpp


def test_normalize_page_text_repairs_unicode_hyphenation_and_whitespace():
    raw = "\u201cData\u201d pro-\ntection \u00ad policy\t\tupdated\r\n\r\n\r\nnow"
    out = dpp._normalize_page_text(raw)

    assert '"Data" protection policy updated' in out
    assert "\u00ad" not in out
    assert "\n\n\n" not in out


def test_detect_and_strip_repeated_margin_lines():
    pages = [
        ["Saltash Town Council", "Policy Pack", "Body line A", "Page 1 of 3"],
        ["Saltash Town Council", "Policy Pack", "Body line B", "Page 2 of 3"],
        ["Saltash Town Council", "Policy Pack", "Body line C", "Page 3 of 3"],
    ]

    repeated = dpp._detect_repeated_margin_lines(pages)

    assert dpp._line_fingerprint("Saltash Town Council") in repeated
    assert dpp._line_fingerprint("Policy Pack") in repeated
    assert dpp._line_fingerprint("Page 1 of 3") in repeated

    cleaned = [dpp._strip_margin_repeats(lines, repeated) for lines in pages]

    assert cleaned[0] == ["Body line A"]
    assert cleaned[1] == ["Body line B"]
    assert cleaned[2] == ["Body line C"]


def test_pdf_to_text_uses_layout_mode_and_page_markers(monkeypatch):
    class FakePage:
        def __init__(self, text: str):
            self._text = text
            self.calls = []

        def extract_text(self, **kwargs):
            self.calls.append(kwargs)
            return self._text

    pages = [
        FakePage("Header\nBody A\nPage 1 of 3"),
        FakePage("Header\nBody B\nPage 2 of 3"),
        FakePage("Header\nBody C\nPage 3 of 3"),
    ]

    class FakeReader:
        def __init__(self, _path: str):
            self.pages = pages

    monkeypatch.setattr(dpp, "PdfReader", FakeReader)

    text = dpp.pdf_to_text(Path("dummy.pdf"))

    for page in pages:
        assert page.calls
        assert page.calls[0]["extraction_mode"] == "layout"
        assert page.calls[0]["layout_mode_space_vertically"] is True

    assert "=== Page 1 ===" in text
    assert "=== Page 2 ===" in text
    assert "=== Page 3 ===" in text
    assert "Header" not in text
    assert "Body A" in text
    assert "Body B" in text
    assert "Body C" in text
