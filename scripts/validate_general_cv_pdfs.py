"""Validate new PDF CVs using two independent extractors; not a vendor ATS ranking."""
from pathlib import Path
from pypdf import PdfReader
from pdfminer.high_level import extract_text

ROOT = Path(__file__).resolve().parent.parent
FIELDS = {
    "Witold_Grzesiak_PL.pdf": [
        "Witold Grzesiak", "witold.g83@gmail.com", "WSKZ", "Pomoc Administracyjna",
        "Ekoenergetyka", "Retail Sales BI Dashboard", "Ki-67", "Kompetencje interpersonalne"
    ],
    "Witold_Grzesiak_EN.pdf": [
        "Witold Grzesiak", "witold.g83@gmail.com", "WSKZ", "Administrative Assistant",
        "Ekoenergetyka", "Retail Sales BI Dashboard", "Ki-67", "Interpersonal skills"
    ],
}
def normalize(x):
    return " ".join((x or "").lower().split())
def check_pdf(path, expected):
    reader=PdfReader(str(path))
    if reader.is_encrypted or not 1 <= len(reader.pages) <= 4:
        raise ValueError(f"PDF invalid or unexpected page count: {path}")
    engines={
        "pypdf":"\n".join(page.extract_text() or "" for page in reader.pages),
        "pdfminer":extract_text(str(path)),
    }
    for name, text in engines.items():
        if len(text)<2000:
            raise ValueError(f"Very little extractable text in {path} via {name}")
        normalized=normalize(text)
        missing=[field for field in expected if normalize(field) not in normalized]
        if missing:
            raise ValueError(f"{path.name}: {name} missing {missing}")
        if text.count("\ufffd"):
            raise ValueError(f"{path.name}: malformed replacement glyphs via {name}")
    print(f"OK {path.name}: {len(reader.pages)} pages; both parsers recovered contact, experience, education and projects")
def main():
    for name, fields in FIELDS.items():
        check_pdf(ROOT / name, fields)
    if (ROOT/"Witold_Grzesiak.pdf").read_bytes() != (ROOT/"Witold_Grzesiak_PL.pdf").read_bytes():
        raise ValueError("Default PDF must match PL PDF")
if __name__=="__main__":
    main()
