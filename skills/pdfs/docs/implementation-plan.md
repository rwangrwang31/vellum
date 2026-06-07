# Implementation Plan

The goal is a local, tool-callable, functionally equivalent PDF workbench. It follows the recovered CLI contracts where possible, but it does not claim to be OpenAI's original implementation.

Use `docs/recovered-script-heads.md` as source-context for the recovered script path inventory. Use `docs/script-inventory.json` for function names, imports, CLI arguments, and subcommands.

## Phase 1: Core verification loop

- `render_pdf.py`: implemented; renders pages to PNG/JPEG using Poppler `pdftoppm` or `pypdfium2`.
- `pdf_inspect.py`: implemented; page count, metadata, encryption status, page boxes, forms, attachments.
- `compare_renders.py`: implemented; render both PDFs and produce changed-page summary plus diff PNGs.
- `renderer_parity.py`: implemented; renders with Poppler and PDFium, then diffs outputs.
- `pdf_preflight.py`: implemented; triage corruption, scan-likeness, fonts, encryption, and renderer issues.

## Phase 2: Extraction

- `pdf_extract.py text`: implemented; `pdfplumber`, `pymupdf`.
- `pdf_extract.py words`: implemented; CSV with `page,text,x0,top,x1,bottom`.
- `pdf_extract.py chars`: implemented; fine-grained CSV via `pdfplumber`.
- `pdf_extract.py tables`: implemented; per-table CSV and optional XLSX.
- `pdf_extract.py images`: implemented; embedded image extraction.
- `pdf_extract.py attachments`: implemented; embedded files.
- `pdf_extract.py annotations`: implemented; annotations JSON.
- `pdf_extract.py forms`: implemented; AcroForm fields and widgets.

## Phase 3: Editing

- `pdf_edit.py merge`: implemented.
- `pdf_edit.py split`: implemented.
- `pdf_edit.py select`: implemented.
- `pdf_edit.py extract`: implemented.
- `pdf_edit.py rotate`: implemented.
- `pdf_edit.py crop`: implemented.
- `make_watermark_pdf.py`: implemented.
- `pdf_edit.py watermark`: implemented.
- `pdf_edit.py paginate`: implemented.
- `pdf_edit.py encrypt`: implemented.
- `pdf_edit.py decrypt`: implemented.
- `pdf_edit.py repair`: implemented.
- `pdf_edit.py optimize`: implemented.

## Phase 4: Forms

- `js/install_deps.sh`: recovered; installs JS dependencies from the `js/` folder.
- `js/package.json`: package metadata for `pdf-lib` and `pdfjs-dist`; required by `js/install_deps.sh` because it runs `npm install` without package arguments.
- `js/extract_form_fields.mjs`: recovered and implemented.
- `js/fill_form.mjs` with `--flatten`: recovered and implemented.
- `js/extract_text_pdfjs.mjs`: recovered and implemented.
- `pdf_extract.py forms --include_widgets`: implemented.
- `box_picker_html.py`: implemented.
- `place_text_by_boxes.py`: implemented.
- `forms_debugging.md` docs are recovered and should drive field/widget introspection behavior.
- `forms_nonfillable.md` docs are recovered and should drive box picker + stamping behavior.

## Phase 5: Scanned pages, optional OCR, and redaction

- `ocr_pdf.py`: implemented; `ocrmypdf` wrapper with fallback, but local OCR dependencies are optional and not required for the default plan.
- Scanned/low-text page fallback: render pages with `render_pdf.py` and use the multimodal model to read, summarize, or extract visible content from page images.
- `pdf_redact.py text`: implemented; text search + true redaction.
- `pdf_redact.py boxes`: implemented; coordinate-based redaction.
- scanned/image redaction mode: implemented; `--image_mode remove|pixels`.

## Phase 6: Conversion

- `lo_convert_to_pdf.py`: implemented; LibreOffice headless wrapper.
- `html_to_pdf.py`: implemented; Playwright Chromium wrapper.
- `md_to_pdf.py`: implemented; Pandoc wrapper.
- `latex_to_pdf.py`: implemented; latex/xelatex wrapper.
- `tasks/create.md` and `tasks/js_tools.md` docs are recovered.

## Phase 7: Batch operations

- `batch_pdf.py render`: implemented; render corpora into a clean output root.
- `batch_pdf.py inspect`: implemented; write one JSON inspection file per PDF.
- `batch_pdf.py normalize`: implemented; normalize/repair many PDFs without overwriting inputs.
- `create_montage.py`: implemented; generate quick visual spot-check montages.
- `crop_rendered_pages.py`: implemented; generate repeatable focused QA crops from rendered page PNGs using a JSON crop spec.

## Phase 8: Smoke tests

- `edit_smoketest.py`: implemented; create/edit/render/compare smoke path.
- `forms_smoketest.py`: implemented; fillable and non-fillable form smoke paths.
- `redact_smoketest.py`: implemented; true redaction smoke path.
- `examples/smoke_test.md` docs are recovered and should remain the top-level sanity checklist.

## Phase 9: Platform replacements

- OpenCode local capability mapping: documented in `docs/platform-local-replacements.md`.
- `artifact_registry.py`: implemented; registers existing files under `outputs/` in `outputs/artifacts/registry.jsonl` with stable artifact IDs, repo-relative paths, hashes, size, producer notes, timestamps, and optional preview metadata.
- Default local-computer workflow: read files directly by local path using OpenCode file tools plus PDF/DOCX scripts; do not recreate ChatGPT upload indexing unless a task explicitly needs source IDs, chunk IDs, or cross-file semantic retrieval.
- Exact ChatGPT platform services remain out of scope: `file_search` source/chunk UI, `web.run`, `python_user_visible`, hosted artifact previews, and `sandbox:/mnt/data/...` link generation are platform layers, not PDF script files.
- Recommended next implementation, if needed: improve direct local workflows first, then add optional registry-backed download links or source/chunk indexing only when direct file access is insufficient.

## Baseline dependencies

For the local OpenCode + GPT-5.5 plan, keep dependencies small. OpenCode/GPT-5.5 supplies reasoning, research, and multimodal page reading; local tools only need to parse PDFs, extract digital text/layout, render pages, and write outputs. See `docs/local-opencode-gpt55-install.md`.

Python:

```powershell
python -m pip install pypdf pdfplumber reportlab pypdfium2
```

On the current machine, `fitz`/PyMuPDF, Pillow, `openpyxl`, and `numpy` are already available. `pandas` is optional for future table/data workflows; it is not a direct import in the recovered Python scripts.

Optional:

```powershell
python -m pip install playwright
npm install pdf-lib pdfjs-dist
```

Local OCR is not part of the default dependency plan. If offline OCR or searchable-PDF generation is explicitly required, add `ocrmypdf` plus system OCR dependencies separately.

System tools by feature:

- Poppler: optional renderer parity, `pdftotext`, `pdfinfo`, and `pdffonts` diagnostics. `pypdfium2` is enough for the default render-to-image flow.
- LibreOffice: optional DOCX/PPTX/ODT -> PDF conversion
- Pandoc + XeLaTeX: optional Markdown/LaTeX PDF generation
- Tesseract: optional local OCR backend only when not using the multimodal model fallback
- qpdf: repair/optimize/encrypt/decrypt helpers
