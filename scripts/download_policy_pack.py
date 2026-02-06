from __future__ import annotations

from pathlib import Path
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


def _safe_name(url: str) -> str:
    name = unquote(urlparse(url).path.split("/")[-1])
    return name.replace(" ", "_")


def download(url: str, path: Path) -> None:
    if path.exists():
        return
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=60) as resp:
        path.write_bytes(resp.read())


def pdf_to_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    parts = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        parts.append(f"\n\n=== Page {i} ===\n{text}")
    return "\n".join(parts)


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TXT_DIR.mkdir(parents=True, exist_ok=True)

    for url in URLS:
        name = _safe_name(url)
        pdf_path = PDF_DIR / name
        download(url, pdf_path)

        txt_path = TXT_DIR / (pdf_path.stem + ".txt")
        if txt_path.exists():
            continue
        txt = pdf_to_text(pdf_path)
        txt_path.write_text(txt, encoding="utf-8")

    print("Done. Index the .txt files in data/source_repos/saltash_policy_pack/docs/txt")


if __name__ == "__main__":
    main()
