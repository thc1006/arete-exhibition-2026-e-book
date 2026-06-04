# Code review: build/make_qr.py

Status: PASS

## Scope
Generate static QR codes for the 26 verified works + 3 sheets (ㄅㄆㄈ), each
encoding the final deployed deep-link URL. Read-only on build/works.json; writes
only under qr/. No analytical judgement -- it encodes the canonical URLs.

## Review checklist
- [PASS] URL form: `BASE + "?page=" + page`. BASE is the live, verified Pages URL
  (https://thc1006.github.io/arete-exhibition-2026-e-book/). Query parameter (not
  #fragment) -> survives any redirect; the URL is direct (zero redirect) -> safe
  in iOS Safari / Android Chrome / in-app webviews (matches the deep-research
  conclusion).
- [PASS] STATIC QR (segno.make of the literal URL) -- no dynamic/short-link
  redirect, no expiry, no third-party dependency. Correct for permanent wall use.
- [PASS] Error level H (30% recovery) -- robust to glare/scuffs/angle at arm's
  length on a wall. URL is short (~60 chars) so level H stays a low version
  (~v5-6), keeping modules large enough to scan.
- [PASS] Outputs both SVG (vector, any print size, no pixelation) and PNG
  (~1000px raster for quick use). Quiet zone border=4 modules (spec minimum is 4).
- [PASS] Page numbers come straight from works.json, which was adversarially
  verified (offset +10, the 蔡潔希/賴柏蓁 swap fixed). Stems encode the page
  (`w23_p51`) so the file name itself is auditable against the table.
- [PASS] Shared pages (works 4/5 -> p19, 9/10 -> p27, 18/19 -> p43) intentionally
  produce two files with identical QR content (same URL); the placement guide
  distinguishes them by title so each can be placed at its own wall position.
- [PASS] Filenames are ASCII-safe (`w01_p13`, `sheet-cover_p1`); Chinese labels
  live only in the HTML guide / CSV content, avoiding filesystem encoding issues.
- [PASS] CSV written utf-8-sig so Excel renders Chinese; HTML guide escapes all
  interpolated text via html.escape.
- [PASS] Idempotent: fixed stems overwrite; re-runnable.

## Risks / notes
- If the site URL ever changes (custom domain / repo rename), QRs must be
  regenerated -- by design, static QR encodes the URL directly. BASE is a single
  constant at the top for easy change.
- No emoji anywhere (per project rule).

Reviewer verdict: PASS - safe to run.
