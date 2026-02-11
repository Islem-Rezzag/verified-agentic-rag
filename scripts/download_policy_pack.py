from __future__ import annotations

import argparse
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import List, Sequence, Set
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from pypdf import PdfReader

URLS = [
    "https://modern.saltash.gov.uk/documents/s17006/Employee%20Handbook.pdf",
    "https://modern.saltash.gov.uk/documents/s17014/Provision%20of%20IT%20Acceptable%20Use%20Policy%20Employees%20Members.pdf",
    "https://modern.saltash.gov.uk/documents/s17009/Data%20Protection%20-%20Employees.pdf",
    "https://modern.saltash.gov.uk/documents/s17016/Recruitment%20and%20Selection%20Policy.pdf",
    "https://modern.saltash.gov.uk/documents/s17011/Equality%20Diversity.pdf",
]

BASE_DIR = Path("data/source_repos/saltash_policy_pack")
DOCS_DIR = BASE_DIR / "docs"
PDF_DIR = DOCS_DIR / "pdf"
TXT_DIR = DOCS_DIR / "txt"

HEADER_FOOTER_WINDOW_LINES = 6
HEADER_FOOTER_MIN_PAGES = 3
HEADER_FOOTER_MIN_PAGE_RATIO = 0.6
MAX_MARGIN_LINE_LEN = 140

UNICODE_TRANSLATIONS = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "*",
        "\u00a0": " ",
    }
)


def _safe_name(url: str) -> str:
    name = unquote(urlparse(url).path.split("/")[-1])
    return name.replace(" ", "_")


def download(url: str, path: Path) -> None:
    if path.exists():
        return
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=60) as resp:
        path.write_bytes(resp.read())


def _line_fingerprint(line: str) -> str:
    line = re.sub(r"\s+", " ", line).strip().lower()
    # Normalize pagination lines like "Page 1 of 30" -> "page <n> of <n>".
    # We only do this when "page" appears to avoid false matches in body text.
    if "page" in line:
        line = re.sub(r"\d+", "<n>", line)
    return line


def _normalize_page_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(UNICODE_TRANSLATIONS)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00ad", "")  # soft hyphen

    # Re-join PDF line-wrap hyphenations such as "fre-\nquency".
    text = re.sub(r"(?<=\w)[-\u2010\u2011]\n(?=[a-z])", "", text)

    normalized_lines: List[str] = []
    blank_run = 0
    for raw_line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if not line:
            blank_run += 1
            if blank_run <= 1:
                normalized_lines.append("")
            continue

        blank_run = 0
        normalized_lines.append(line)

    return "\n".join(normalized_lines).strip()


def _is_margin_candidate(fingerprint: str) -> bool:
    if not fingerprint:
        return False
    if len(fingerprint) > MAX_MARGIN_LINE_LEN:
        return False
    if re.fullmatch(r"[-_=*#<>:\s]+", fingerprint):
        return False
    return True


def _detect_repeated_margin_lines(pages: Sequence[List[str]]) -> Set[str]:
    if len(pages) < HEADER_FOOTER_MIN_PAGES:
        return set()

    page_counts: Counter[str] = Counter()
    for lines in pages:
        margin_lines = lines[:HEADER_FOOTER_WINDOW_LINES] + lines[-HEADER_FOOTER_WINDOW_LINES:]
        unique_in_page: Set[str] = set()

        for line in margin_lines:
            fp = _line_fingerprint(line)
            if _is_margin_candidate(fp):
                unique_in_page.add(fp)

        for fp in unique_in_page:
            page_counts[fp] += 1

    min_pages = max(HEADER_FOOTER_MIN_PAGES, math.ceil(len(pages) * HEADER_FOOTER_MIN_PAGE_RATIO))
    return {fp for fp, count in page_counts.items() if count >= min_pages}


def _strip_margin_repeats(lines: List[str], repeated_fingerprints: Set[str]) -> List[str]:
    if not repeated_fingerprints:
        return [line for line in lines if line]

    stripped = list(lines)
    n = len(stripped)

    for i in range(min(HEADER_FOOTER_WINDOW_LINES, n)):
        if _line_fingerprint(stripped[i]) in repeated_fingerprints:
            stripped[i] = ""

    for i in range(max(0, n - HEADER_FOOTER_WINDOW_LINES), n):
        if _line_fingerprint(stripped[i]) in repeated_fingerprints:
            stripped[i] = ""

    cleaned: List[str] = []
    blank_run = 0
    for line in stripped:
        line = line.strip()
        if not line:
            blank_run += 1
            if blank_run <= 1:
                cleaned.append("")
            continue

        blank_run = 0
        cleaned.append(line)

    while cleaned and not cleaned[0]:
        cleaned.pop(0)
    while cleaned and not cleaned[-1]:
        cleaned.pop()

    return cleaned


def _extract_page_text(page) -> str:
    try:
        return page.extract_text(
            extraction_mode="layout",
            layout_mode_space_vertically=True,
        ) or ""
    except TypeError:
        # Older pypdf versions may not support layout kwargs.
        return page.extract_text() or ""


def pdf_to_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    page_lines: List[List[str]] = []

    for page in reader.pages:
        text = _extract_page_text(page)
        normalized = _normalize_page_text(text)
        page_lines.append(normalized.splitlines())

    repeated_margins = _detect_repeated_margin_lines(page_lines)
    parts = []

    for i, lines in enumerate(page_lines, start=1):
        cleaned_lines = _strip_margin_repeats(lines, repeated_margins)
        page_text = "\n".join(cleaned_lines).strip()
        parts.append(f"\n\n=== Page {i} ===\n{page_text}")

    return "\n".join(parts).strip() + "\n"


def main(refresh_text: bool = False) -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TXT_DIR.mkdir(parents=True, exist_ok=True)

    extracted_count = 0
    for url in URLS:
        name = _safe_name(url)
        pdf_path = PDF_DIR / name
        download(url, pdf_path)

        txt_path = TXT_DIR / (pdf_path.stem + ".txt")
        if txt_path.exists() and not refresh_text:
            continue
        txt = pdf_to_text(pdf_path)
        txt_path.write_text(txt, encoding="utf-8")
        extracted_count += 1

    print(
        "Done. Extracted/updated",
        extracted_count,
        "text files. Index the .txt files in data/source_repos/saltash_policy_pack/docs/txt",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Saltash policy PDFs and build cleaned TXT corpus.")
    parser.add_argument(
        "--refresh-text",
        action="store_true",
        help="Re-extract text for all PDFs even if corresponding .txt files already exist.",
    )
    args = parser.parse_args()
    main(refresh_text=args.refresh_text)
