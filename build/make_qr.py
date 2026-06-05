# -*- coding: utf-8 -*-
"""
make_qr.py - Generate STATIC QR codes (error-correction level H) for every
artwork + sheet, each encoding the FINAL deployed deep-link URL (?page=N, zero
redirect). Outputs vector SVG (large-format print) + high-res PNG + a printable
placement guide (HTML) + a CSV index.

Targets come from build/works.json (the adversarially-verified work->page table).
Pure generation: no judgement, just encode the canonical URLs.
"""
import csv
import html
import json
from pathlib import Path

import segno

ROOT = Path(__file__).resolve().parent.parent
QRDIR = ROOT / "qr"
SVGDIR = QRDIR / "svg"
PNGDIR = QRDIR / "png"
BASE = "https://thc1006.github.io/arete-exhibition-2026-e-book/"


def url_for(page):
    return f"{BASE}?page={page}"


def gen(stem, url):
    q = segno.make(url, error="h")          # level H = 30% recovery (robust on walls)
    q.save(str(SVGDIR / f"{stem}.svg"), scale=10, border=4)   # vector -> any print size
    q.save(str(PNGDIR / f"{stem}.png"), scale=20, border=4)   # ~1000px raster
    return q.version


def main():
    for d in (SVGDIR, PNGDIR):
        d.mkdir(parents=True, exist_ok=True)
    data = json.loads((ROOT / "build" / "works.json").read_text(encoding="utf-8"))

    rows = []  # (stem, kind, label, sub, page, url)
    # Whole-book QR: the landing page (no ?page) for the exhibition entrance / general signage.
    gen("book-full", BASE)
    rows.append(("book-full", "book", "整本書 Whole catalogue", "ANTI-AUTOBIOGRAPHY 反自傳 · landing", "首頁", BASE))
    for s in data["sheets"]:
        stem = f"sheet-{s['role']}_p{s['page']}"
        url = url_for(s["page"])
        gen(stem, url)
        rows.append((stem, "sheet", s["label"], s["id"], s["page"], url))

    for w in data["works"]:
        stem = f"w{w['n']:02d}_p{w['page']}"
        url = url_for(w["page"])
        gen(stem, url)
        title = (w["titleZh"] or w["titleEn"] or "(untitled)").strip()
        sub = f"{w['artist']} / {w['alias']}".strip(" /")
        rows.append((stem, "work", title, sub, w["page"], url))

    # CSV index (utf-8-sig so Excel opens Chinese correctly)
    with open(QRDIR / "qr-list.csv", "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f)
        wr.writerow(["file_svg", "kind", "label", "artist/id", "page", "url"])
        for stem, kind, label, sub, page, url in rows:
            wr.writerow([f"svg/{stem}.svg", kind, label, sub, page, url])

    build_guide(rows, QRDIR / "placement-guide.html")
    print(f"generated {len(rows)} QR codes (1 whole-book + {sum(r[1]=='work' for r in rows)} works + "
          f"{sum(r[1]=='sheet' for r in rows)} sheets) -> {QRDIR}")


def build_guide(rows, out):
    cells = []
    for stem, kind, label, sub, page, url in rows:
        cells.append(
            f'<div class="card {kind}">'
            f'<img src="png/{stem}.png" alt="{html.escape(stem)}">'
            f'<div class="meta">'
            f'<div class="label">{html.escape(label)}</div>'
            f'<div class="sub">{html.escape(sub)}</div>'
            f'<div class="pg">page {page} &middot; <span class="file">{stem}</span></div>'
            f'<div class="url">{html.escape(url)}</div>'
            f'</div></div>'
        )
    doc = (
        '<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<title>QR placement guide - ANTI-AUTOBIOGRAPHY</title><style>'
        'body{font-family:-apple-system,"Microsoft JhengHei","Noto Sans TC",sans-serif;margin:24px;color:#111}'
        'h1{font-size:18px;margin:0 0 4px}.note{color:#666;font-size:12px;margin-bottom:16px;max-width:720px}'
        '.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}'
        '.card{border:1px solid #ddd;border-radius:8px;padding:10px;display:flex;gap:10px;align-items:center;break-inside:avoid}'
        '.card.sheet{background:#fff7ef;border-color:#e3c79f}'
        '.card img{width:104px;height:104px;flex:none;image-rendering:pixelated}'
        '.meta{font-size:12px;min-width:0}.label{font-weight:700;font-size:13px;line-height:1.25}'
        '.sub{color:#444}.pg{color:#666;margin-top:2px}.file{font-family:monospace;color:#aaa}'
        '.url{color:#aaa;font-size:10px;word-break:break-all;margin-top:2px}'
        '@media print{body{margin:8mm}.card{border-color:#ccc}}'
        '</style></head><body>'
        '<h1>QR placement guide &mdash; ANTI-AUTOBIOGRAPHY 反自傳</h1>'
        f'<div class="note">每個 QR 為靜態、容錯等級 H、直連 {html.escape(BASE)}?page=N（零轉址、永久有效）。'
        '橙底為封面/插頁/封底（ㄅㄆㄈ）。大圖輸出請用 qr/svg/ 的向量檔。'
        '依藝術家/作品名把每張 QR 貼到對應牆面即可。</div>'
        f'<div class="grid">{"".join(cells)}</div></body></html>'
    )
    out.write_text(doc, encoding="utf-8")


if __name__ == "__main__":
    main()
