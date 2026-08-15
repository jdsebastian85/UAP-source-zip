#!/usr/bin/env python3
"""T2.5 — render one image per page so a transcript can be checked against the page.

Usage:
  python3 scripts/render_page_images.py sources/pdf/*.pdf --out page_images
  python3 scripts/render_page_images.py sources/pdf --out page_images --dpi 150

A transcript is a claim about a page. This makes the claim checkable in one tap.

Uses PyMuPDF rather than the `pdftoppm` in the spec. Same output, but poppler is
not installable in the sandbox (apt archives 404) while PyMuPDF ships its own
binaries through pip, so this runs anywhere Python does.

Output layout, one directory per release:

    <out>/<release_id>/p0001.jpg

which is exactly what the investigator's `url_template` in site/page_images.json
expands to. Nothing is written to spine/ — page images are assets, not evidence,
and at roughly a gigabyte they do not belong in this repo. Host them per T2.5:
an Internet Archive item first, a separate assets repo second, a local directory
for offline work third.

Idempotent: a page whose image already exists is skipped, so an interrupted run
resumes. Pass --force to re-render.
"""
import argparse, glob, os, sys

try:
    import pymupdf
except ImportError:                                   # pragma: no cover
    sys.exit("PyMuPDF is required:  pip install pymupdf")


def release_id(pdf_path):
    """Match manifest.csv, which keys on the file name including .pdf for the
    long-form releases. The caller can override with --id when they disagree."""
    return os.path.basename(pdf_path)


def render(pdf_path, out_root, dpi, force, quality):
    rid = release_id(pdf_path)
    out_dir = os.path.join(out_root, rid)
    os.makedirs(out_dir, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    zoom = dpi / 72.0
    mat = pymupdf.Matrix(zoom, zoom)
    made = skipped = 0
    written = 0
    for i, page in enumerate(doc, 1):
        dst = os.path.join(out_dir, f"p{i:04d}.jpg")
        if os.path.exists(dst) and not force:
            skipped += 1
            continue
        pix = page.get_pixmap(matrix=mat)
        pix.save(dst, jpg_quality=quality)
        written += os.path.getsize(dst)
        made += 1
    n = doc.page_count
    doc.close()
    return rid, n, made, skipped, written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="PDF files, or directories of them")
    ap.add_argument("--out", default="page_images")
    ap.add_argument("--dpi", type=int, default=150, help="150 per T2.5")
    ap.add_argument("--quality", type=int, default=80, help="JPEG quality 0-100")
    ap.add_argument("--force", action="store_true", help="re-render existing images")
    a = ap.parse_args()

    pdfs = []
    for p in a.paths:
        if os.path.isdir(p):
            pdfs += sorted(glob.glob(os.path.join(p, "**", "*.pdf"), recursive=True))
        else:
            pdfs += sorted(glob.glob(p))
    if not pdfs:
        sys.exit("no PDFs matched")

    tot_pages = tot_made = tot_skipped = tot_bytes = 0
    failed = []
    for p in pdfs:
        try:
            rid, n, made, skipped, written = render(p, a.out, a.dpi, a.force, a.quality)
        except Exception as e:
            # A PDF that will not open is recorded, not silently dropped: a
            # missing page image must never be mistaken for a page with none.
            failed.append((os.path.basename(p), type(e).__name__, str(e)[:80]))
            continue
        tot_pages += n; tot_made += made; tot_skipped += skipped; tot_bytes += written
        print(f"{rid}: {n}p  rendered {made}  skipped {skipped}")

    print(f"\n{len(pdfs)-len(failed)} documents, {tot_pages} pages, "
          f"{tot_made} rendered, {tot_skipped} already present, "
          f"{tot_bytes/1e6:.1f} MB written at {a.dpi} dpi")
    if failed:
        print(f"\n{len(failed)} FAILED — recorded, not skipped silently:")
        for name, kind, msg in failed:
            print(f"  {name}: {kind}: {msg}")
    print("\nNext: host <out>/ (Internet Archive item, assets repo, or locally) and set "
          "url_template in site/page_images.json to point at it.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
