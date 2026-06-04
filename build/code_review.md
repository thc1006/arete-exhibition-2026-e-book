# Code review: build/render.py

Status: PASS

## Scope
Mechanical rasterization of the four portfolio PDFs into web page images +
thumbnails + a numbered contact sheet. No analytical conclusions are produced by
the script (artwork-boundary judgement is done by a human reading the contact
sheet output). Read-only on the source PDFs; writes only under site/ and build/.

## Review checklist
- [PASS] Source order is explicit and documented (Bopomofo order ㄅ→ㄆ→ㄇ→ㄈ).
  Global page index `gidx` is 1-based and assigned strictly in iteration order,
  so the page<->source mapping is deterministic and auditable.
- [PASS] Rendering uses `max(width,height)` for zoom -> safe for the square
  595x595 pages; alpha=False composites transparency (ㄅ/ㄈ plastic sheets) onto
  white, which is the correct default for a flipbook page.
- [PASS] No source mutation: `fitz.open` read-only; outputs namespaced to
  site/pages, site/thumbs, build/. Re-runnable (idempotent overwrite).
- [PASS] Encoders: JPEG q86 progressive (universal fallback) + WebP q82
  (primary). Measured projection earlier: ~7-10MB total for 65 pages, far under
  GitHub Pages / Cloudflare limits.
- [PASS] Contact sheet captions show BOTH global page (P{gidx}) and source-local
  page ([label-spno]) so ㄇ's internal pages (ㄇ-1..ㄇ-60) are directly readable
  for boundary identification.
- [PASS] Font load is wrapped in try/except -> degrades to PIL default if
  arialbd.ttf is missing; no hard crash.
- [PASS] Failure isolation: a malformed page would raise and stop the run
  loudly (acceptable for a one-shot build; no silent corruption).

## Risks / notes
- TARGET_PX=2000 chosen for pinch-zoom headroom; can be lowered to 1600 if total
  size matters. Not a correctness risk.
- Does NOT decide artwork boundaries -- by design. The conclusion about which
  ㄇ pages start a new artwork is written by a human from the contact sheet.

Reviewer verdict: PASS - safe to run.
