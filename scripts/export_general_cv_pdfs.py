"""Generate current general CV PDFs directly from the single-column ATS HTML."""
from pathlib import Path
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = [
    (ROOT / "ats" / "ogolne-pl.html", ROOT / "Witold_Grzesiak_PL.pdf"),
    (ROOT / "ats" / "ogolne-en.html", ROOT / "Witold_Grzesiak_EN.pdf"),
]

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for source, output in OUTPUTS:
                page = browser.new_page(locale="pl-PL" if "pl" in source.stem else "en-GB")
                page.goto(source.resolve().as_uri(), wait_until="load")
                page.emulate_media(media="print")
                page.pdf(path=str(output), format="A4", print_background=True, prefer_css_page_size=True)
                page.close()
                print(f"Created {output.name} from {source.name}: {output.stat().st_size} bytes")
        finally:
            browser.close()
    shutil.copyfile(ROOT / "Witold_Grzesiak_PL.pdf", ROOT / "Witold_Grzesiak.pdf")
    print("Updated Witold_Grzesiak.pdf (Polish default)")

if __name__ == "__main__":
    main()
