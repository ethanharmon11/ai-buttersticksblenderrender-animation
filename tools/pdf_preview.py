"""Render logo PDFs to PNG previews to inspect their content."""
from pathlib import Path

import fitz

ASSETS = Path(r"C:\Users\harmo\OneDrive\Butter Sticks Golf 1\Merchandise\Merchandise Designs\Logo Assets")
OUT = Path(__file__).resolve().parent.parent / "vectors"

for pdf in sorted(ASSETS.glob("*.pdf")):
    doc = fitz.open(pdf)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=100)
        out = OUT / f"preview_{pdf.stem.replace(' ', '_')}_p{i + 1}.png"
        pix.save(out)
        print(f"{out.name}  {pix.width}x{pix.height}  drawings={len(page.get_drawings())}")
    doc.close()
