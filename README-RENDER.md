# Page Image Rendering for PURSUE Corpus

These files fix the "No page-image host is configured" error on the investigator page.

## Files to commit

```
scripts/render_page_images.py   ← the renderer
site/page_images.json           ← configuration the site reads
```

## One-time setup

```bash
pip install pymupdf pillow
```

## How to run

1. Download the PDFs from your Google Drive folder into a local directory (example: `~/pdfs`).

2. Test on a few files first:

```bash
python scripts/render_page_images.py \
  --pdf-dir ~/pdfs \
  --out site/page_images \
  --dpi 150 \
  --format webp \
  --quality 80 \
  --workers 4 \
  --limit 5
```

3. Full run (safe to re-run — it skips already-rendered pages):

```bash
python scripts/render_page_images.py \
  --pdf-dir ~/pdfs \
  --out site/page_images \
  --dpi 150 \
  --format webp \
  --quality 80 \
  --workers 6
```

4. Commit the two files above + the generated `site/page_images/` folder (or host the images externally and only commit the JSON).

5. Push and let GitHub Pages rebuild. The investigator page should now show the page scans.

## Notes

- 150 DPI + WebP q=80 is the recommended balance of legibility vs size.
- Expected size: roughly 80–180 KB per page.
- The script is fully resume-safe.
