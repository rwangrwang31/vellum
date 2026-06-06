# Optional local OCR for scanned PDFs

Use this when the PDF is image-only (scan), and text extraction returns little or nothing.

Default for this local OpenCode plan: do not install local OCR dependencies. For scanned or low-text PDFs, first render page images and use the model's multimodal capability to read, summarize, or extract visible content.

Use local OCR only when the user explicitly needs a searchable PDF, offline deterministic OCR, or an OCR text layer.

---

## Default no-local-OCR path

```bash
python /home/oai/skills/pdfs/scripts/render_pdf.py scanned.pdf --out_dir /mnt/data/_renders/scanned --dpi 200
```

Then inspect the rendered page images with the multimodal model and store extracted notes/text under `/mnt/data` or the local `outputs/` equivalent.

---

## Optional golden path (ocrmypdf)

```bash
python -m pip install ocrmypdf
python /home/oai/skills/pdfs/scripts/ocr_pdf.py scanned.pdf -o searchable.pdf --lang eng
```

Defaults (safe in this runtime):

- `--skip-text` (won't re-OCR PDFs that already contain text)
- `--deskew` (on)
- `--optimize 1` (higher levels depend on extra system binaries that are not available here)

If local OCR is required but `ocrmypdf` is unavailable, use the explicit fallback pipeline:

```bash
python /home/oai/skills/pdfs/scripts/ocr_pdf.py scanned.pdf -o searchable.pdf --lang eng --fallback
```

Verify:

```bash
python /home/oai/skills/pdfs/scripts/render_pdf.py searchable.pdf --out_dir /mnt/data/_renders/ocr --pages 1
python /home/oai/skills/pdfs/scripts/pdf_extract.py text searchable.pdf --method pdfplumber --out /mnt/data/_tmp/text.txt
```

If it still doesn't extract well:

- try `--force` to OCR anyway
- increase DPI by pre-rendering and using different OCR pipeline (rare)
