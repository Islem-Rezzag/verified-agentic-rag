from verified_agentic_rag.cite import make_label, parse_labels_from_text, validate_citations


def test_make_label():
    lab = make_label("docs/a.md", 10, 20)
    assert lab == "docs/a.md:10-20"


def test_parse_labels_from_text():
    text = "Hello. This is a claim. [docs/a.md:10-20] Another claim. [docs/b.md:1-5]"
    labels = parse_labels_from_text(text)
    assert labels == ["docs/a.md:10-20", "docs/b.md:1-5"]


def test_validate_citations():
    allowed = {"docs/a.md:10-20"}
    ok, invalid = validate_citations("Claim. [docs/a.md:10-20]", allowed)
    assert ok is True
    assert invalid == []

    ok2, invalid2 = validate_citations("Claim. [docs/x.md:1-2]", allowed)
    assert ok2 is False
    assert invalid2 == ["docs/x.md:1-2"]

