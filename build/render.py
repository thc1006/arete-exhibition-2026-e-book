# -*- coding: utf-8 -*-
"""
render.py - Rasterize the four portfolio PDFs into web-ready square page images
for the StPageFlip e-book, plus thumbnails and a numbered contact sheet used to
identify artwork boundaries inside the 60-page main book.

Design note: this script is PURE COMPUTE. It only renders/encodes images and
records a mechanical page<->source mapping. It deliberately makes NO judgement
about where artworks begin/end -- that conclusion is made by a human reading the
contact sheet it produces.
"""
import json
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent  # .../e-book
SITE = ROOT / "docs"   # served as the GitHub Pages site root (Pages source: main /docs)
PAGES_DIR = SITE / "pages"
THUMBS_DIR = SITE / "thumbs"
BUILD = ROOT / "build"

TARGET_PX = 2000   # rendered square page edge (quality headroom for pinch-zoom)
THUMB_PX = 360     # thumbnail edge
JPEG_Q = 86
WEBP_Q = 82

# Combined book order (Bopomofo order). `label` marks the source artwork-group.
SOURCES = [
    ("ㄅ.pdf", "ㄅ"),  # ㄅ  single-side plastic sheet (1 page)
    ("ㄆ.pdf", "ㄆ"),  # ㄆ  one sheet front+back (2 pages)
    ("ㄇ.pdf", "ㄇ"),  # ㄇ  main book, contains multiple artworks (60 pages)
    ("ㄈ.pdf", "ㄈ"),  # ㄈ  one sheet front+back (2 pages)
]


def render_page(page, px):
    zoom = px / max(page.rect.width, page.rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)  # white bg
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def build_contact_sheet(thumbs, out_path, cols=6):
    pad, label_h = 12, 30
    cell = THUMB_PX + pad
    rows = (len(thumbs) + cols - 1) // cols
    W = cols * cell + pad
    H = rows * (cell + label_h) + pad
    sheet = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    for i, (gidx, label, spno, th) in enumerate(thumbs):
        r, c = divmod(i, cols)
        x = c * cell + pad
        y = r * (cell + label_h) + pad
        tx = x + (THUMB_PX - th.width) // 2
        ty = y + (THUMB_PX - th.height) // 2
        sheet.paste(th, (tx, ty))
        draw.rectangle([x - 1, y - 1, x + THUMB_PX, y + THUMB_PX], outline="#bbbbbb")
        draw.text((x + 2, y + THUMB_PX + 4), f"P{gidx}  [{label}-{spno}]", fill="black", font=font)
    sheet.save(out_path)
    print(f"contact sheet -> {out_path} ({W}x{H})")


def main():
    for d in (PAGES_DIR, THUMBS_DIR, BUILD):
        d.mkdir(parents=True, exist_ok=True)

    manifest_pages, thumbs_for_sheet = [], []
    gidx = 0
    for fname, label in SOURCES:
        doc = fitz.open(str(ROOT / fname))
        n_pages = doc.page_count
        for spno in range(n_pages):
            gidx += 1
            img = render_page(doc[spno], TARGET_PX)
            stem = f"page-{gidx:03d}"
            img.save(PAGES_DIR / f"{stem}.jpg", "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
            img.save(PAGES_DIR / f"{stem}.webp", "WEBP", quality=WEBP_Q, method=6)
            th = img.copy()
            th.thumbnail((THUMB_PX, THUMB_PX))
            th.save(THUMBS_DIR / f"{stem}.webp", "WEBP", quality=80, method=6)
            thumbs_for_sheet.append((gidx, label, spno + 1, th))
            manifest_pages.append({
                "page": gidx, "source": label, "sourcePage": spno + 1,
                "img": f"pages/{stem}.webp", "imgJpg": f"pages/{stem}.jpg",
                "thumb": f"thumbs/{stem}.webp",
            })
        doc.close()
        print(f"{label}: rendered {n_pages} pages (through global P{gidx})")

    (BUILD / "manifest_pages.json").write_text(
        json.dumps({"targetPx": TARGET_PX, "totalPages": gidx, "pages": manifest_pages},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    build_contact_sheet(thumbs_for_sheet, BUILD / "contact_sheet.png")
    print(f"DONE: {gidx} pages -> {PAGES_DIR}")


if __name__ == "__main__":
    main()
