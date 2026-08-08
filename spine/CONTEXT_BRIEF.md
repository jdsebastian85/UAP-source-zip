# CONTEXT BRIEF — UAP Dump Analysis (paste into new chat)

## Project
Analyzing a DoD/Department of War UAP declassified release using a fixed "spine":
layered, cite-every-row, no opinions, no assumptions, verbatim-only data files.
Spec is in SPINE.md; pipeline is ingest.py + ocr_fallback.py (both delivered as files).

## Spine layers
0 manifest.csv (per-release provenance, SHA-256) · 1 pages.jsonl (per-page text +
extracted entities) · 2 segments.csv (memos within releases) · 3 entities.csv
(verbatim PERSON/ORG/DATE/LOCATOR/MARKING + page cite) · 4 assertions.csv (manual
claim ledger, not yet started) · 5 relational joins (derived at query time, never
stored) · 6 gaps.csv (NO_TEXT_LAYER / LOW_OCR_QUALITY / REDACTION_MARKER /
ENCLOSURE_REFERENCED). Text provenance tagged TEXT_LAYER vs OCR_RECOVERED.

## Corpus state (as of Aug 7, 2026)
48 items ingested: 42 PDFs + 6 JPGs, 1,018 pages, 101 segments.
Agencies: DOW 14, FBI 17, CIA 5, DOE 5, NASA 3, DOS 2, EOP 1, ODNI 1.
Two sub-corpora: historical (Project Sign 1948 → Blue Book review 1967; Los
Alamos/Sandia/Pantex; 1963 Brazil cable chain DOS+EOP) and modern (FBI FD-302s
with paired digital renderings 2011–2026; three Range Fouler debriefs 2019–2021;
Gulf of Oman IIR 2021; one ODNI USPER narrative).
Source zips: release_02_document_bundle.zip, release_04_documents_071026.zip,
release_05_Aug_07_documents.zip, plus standalone DOW-UAP-D092 PDF (85p, byte-
identical copy also inside a zip — dedupe by SHA-256).

## Known data conditions
- 329/1018 pages have NO text layer; 107 more below 0.90 quality. Concentrated in
  DOW-UAP-D096 (220p, 175 unreadable) and DOW-UAP-D095 (57p, 44 unreadable).
- Five FBI "Digital Rendering" PDFs score 0.0 by design (image content) — not defects.
- Publisher OCR mangles stamps: Docld:34714841 also appears truncated (Docld:347 etc.).
- OCR name-splitting: Dr. LaPaz appears as La.Paz / Le.Paz / LaPa.z — entity index
  needs normalization before any frequency claims. True LaPaz count ~36, not 12.
- Only 3 redaction markers corpus-wide ("sanitizes", p1 of each Range Fouler debrief)
  vs 72 referenced enclosures whose presence in the dump is unverified.
- Markings seen: SECRET ×20, CONFIDENTIAL ×10, TOP SECRET ×7, DECLASSIFIED ×8,
  RESTRICTED ×5.
- Entity leaders: USAF 95, OSI 32 (mostly Sandia file), FBI, ATIC, CIA, Blue Book.
  People: Teller, LaPaz, Lt Col Garrett, Bradbury — densest person-level material is
  the 1948–49 nuclear-installation correspondence, not Blue Book itself.

## Pending next steps
1. OCR recovery run on D096 + D095 (gates ~1/3 of corpus; ~90 sec/page, background job).
2. Entity normalization pass (LaPaz variants, Docld truncations).
3. Visual pass on the 6 JPGs (3 NASA STS-80 frames, 3 FBI renderings) + rendering PDFs.
4. Begin Layer 4 assertion ledger once text recovery is complete.
5. Verify the 72 referenced enclosures against the dump.

## Operating rules (user-set)
No opinions or assumptions in analysis. Every stored value verbatim with
release_id + page cite. Absence recorded, never assumed. Contradictions preserved
side by side, never reconciled. Flag any monetary/commercial angles unprompted.

## IMPORTANT — environment does not persist
A new chat gets a fresh container: the extracted files, spine CSVs, and scripts are
gone. Memory carries the project summary, but to resume work you must re-upload
the source zips (and ideally the spine output files from this chat) and re-run
ingest.py. Download everything from this chat's file links first.
