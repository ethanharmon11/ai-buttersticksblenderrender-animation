"""Convert Butter Sticks logo PDFs to SVG for Blender import."""
import sys
from pathlib import Path

import fitz  # PyMuPDF

ASSETS = Path(r"C:\Users\harmo\OneDrive\Butter Sticks Golf 1\Merchandise\Merchandise Designs\Logo Assets")
OUT = Path(__file__).resolve().parent.parent / "vectors"
OUT.mkdir(exist_ok=True)

SOURCES = {
    "bsg_badge": ASSETS / "2025-12-15 - Butter Ball Logo.pdf",
    "script_wordmark": ASSETS / "2025-12-15 - ButterSticks Logo Only.pdf",
    "logo_assets_sheet": ASSETS / "2025-12-15 - ButterSticks Logo Assets.pdf",
}

for name, src in SOURCES.items():
    if not src.exists():
        print(f"MISSING: {src}")
        continue
    doc = fitz.open(src)
    for i, page in enumerate(doc):
        suffix = f"_p{i + 1}" if doc.page_count > 1 else ""
        svg = page.get_svg_image()
        out_path = OUT / f"{name}{suffix}.svg"
        out_path.write_text(svg, encoding="utf-8")
        print(f"OK: {out_path.name}  page_size={page.rect.width:.0f}x{page.rect.height:.0f}  bytes={len(svg)}")
    doc.close()
