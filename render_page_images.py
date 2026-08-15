#!/usr/bin/env python3
"""
Optimized page image renderer for the PURSUE corpus investigator site.

Renders every page of every PDF into small, legible images that the site
can host and display next to transcripts.

Requirements:
  pip install pymupdf pillow

Usage examples:
  # Quick test (first 5 PDFs only)
  python scripts/render_page_images.py \\
      --pdf-dir /path/to/your/downloaded/pdfs \\
      --out site/page_images \\
      --dpi 150 --format webp --quality 80 \\
      --workers 4 --limit 5

  # Full production run (resume-safe)
  python scripts/render_page_images.py \\
      --pdf-dir /path/to/your/downloaded/pdfs \\
      --out site/page_images \\
      --dpi 150 --format webp --quality 80 \\
      --workers 6
"""

from __future__ import annotations

import argparse
import io
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image


def render_one(
    pdf_path: Path,
    out_dir: Path,
    dpi: int,
    fmt: str,
    quality: int,
) -> tuple[str, int, int]:
    """Render all pages of one PDF. Returns (doc_id, pages_rendered, total_pages)."""
    doc_id = pdf_path.stem
    target = out_dir / doc_id
    target.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    rendered = 0
    total = len(doc)

    for i, page in enumerate(doc):
        out_file = target / f"page-{i + 1:03d}.{fmt}"

        # Resume: skip if a reasonable file already exists
        if out_file.exists() and out_file.stat().st_size > 800:
            continue

        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        buf = io.BytesIO()
        if fmt == "webp":
            img.save(buf, format="WEBP", quality=quality, method=6)
        else:
            img.save(buf, format="JPEG", quality=quality, optimize=True)

        out_file.write_bytes(buf.getvalue())
        rendered += 1

    doc.close()
    return doc_id, rendered, total


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render PDF pages to images for the PURSUE investigator site."
    )
    parser.add_argument(
        "--pdf-dir",
        type=Path,
        required=True,
        help="Directory containing the source PDF files",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output directory (usually site/page_images)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Render DPI (140-160 is ideal for scanned docs). Default: 150",
    )
    parser.add_argument(
        "--format",
        choices=["webp", "jpg"],
        default="webp",
        help="Output format. Default: webp",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=80,
        help="Compression quality 1-100. Default: 80",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=6,
        help="Number of parallel workers. Default: 6",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N PDFs (useful for testing)",
    )
    args = parser.parse_args()

    if not args.pdf_dir.is_dir():
        raise SystemExit(f"PDF directory does not exist: {args.pdf_dir}")

    args.out.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(args.pdf_dir.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDF files found in {args.pdf_dir}")

    if args.limit is not None:
        pdfs = pdfs[: args.limit]

    print(
        f"Rendering {len(pdfs)} PDFs → {args.out}\n"
        f"  DPI={args.dpi}  format={args.format}  quality={args.quality}  workers={args.workers}"
    )

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                render_one, pdf, args.out, args.dpi, args.format, args.quality
            ): pdf
            for pdf in pdfs
        }

        for future in as_completed(futures):
            try:
                doc_id, rendered, total = future.result()
                status = f"{rendered}/{total} new" if rendered else "already done"
                print(f"  ✓ {doc_id}: {status}")
            except Exception as exc:
                pdf = futures[future]
                print(f"  ✗ {pdf.name}: {exc}")

    print("\nDone. Next steps:")
    print("  1. Update site/page_images.json with the correct url_template")
    print("  2. Commit + push (use Git LFS if the image folder is large)")
    print("  3. Rebuild / redeploy the site")


if __name__ == "__main__":
    main()
