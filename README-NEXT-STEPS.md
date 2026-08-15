# PURSUE Corpus — Page Images Next Steps

## Important

The file `scripts/render_page_images.py` is **already in your GitHub repo**.
You do **not** need to re-commit it unless you want a local copy.

`site/page_images.json` is also already in the repo (with empty `url_template`).

## What you need to do

### 1. Download the PDFs
From the Google Drive folder "Scanned Paper Docs":
https://drive.google.com/drive/folders/1Uc8dM2UM94DFysQInpRoDRNrZ9yBZnSa

### 2. Install the dependency (one time)
```bash
pip install pymupdf
```

### 3. Render the page images (on your computer)
```bash
cd /path/to/your/pursue-corpus/repo

python3 scripts/render_page_images.py \
  /path/to/downloaded/Scanned\ Paper\ Docs \
  --out page_images \
  --dpi 150 \
  --quality 80
```

This creates folders like:
```
page_images/
  65_HS1-834228961_62-HQ-83894_Section_1.pdf/
    p0001.jpg
    p0002.jpg
    ...
```

### 4. Host the images
Do **not** commit the `page_images/` folder into the main repo (it will be ~1 GB).

Upload the whole `page_images/` folder to:
- A separate GitHub repo + GitHub Pages, or
- Cloudflare R2 / any static host, or
- Internet Archive

### 5. Update site/page_images.json
Once you have a public URL, edit `site/page_images.json` to:

```json
{
  "url_template": "https://YOUR-HOST.example.com/page_images/{release_id}/p{page04}.jpg",
  "verified_on": "2026-08-15",
  "note": "T2.5 page images..."
}
```

### 6. Rebuild and commit
```bash
python3 scripts/build_investigator.py
git add site/page_images.json
git commit -m "Enable page images host"
git push
```

That's the full process.
