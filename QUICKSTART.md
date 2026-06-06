# Quick Start

Use this guide to verify the local PDF/DOCX workbench after cloning the repository. It covers the committed workflow files only. Runtime outputs and the D-drive production stack are local-machine state.

## 1. Activate the PDF Stack

From the repository root:

```powershell
. D:\pdf-production-stack\activate.ps1
```

This example path is machine-local. Replace it with your own equivalent activation script when cloning elsewhere. It exposes the local MiKTeX/XeLaTeX, Pandoc, Poppler, Ghostscript, LibreOffice, qpdf, production Python venv, and Playwright Chromium paths for the current PowerShell session.

If this file is missing, use `skills/pdfs/docs/local-opencode-gpt55-install.md` for the minimal Python/JS setup and add optional system tools only when a task needs them.

## 2. Verify Python Dependencies

Install the committed Python dependency set first:

```powershell
python -m pip install -r requirements.txt
```

```powershell
python -c "import fitz, PIL, playwright, pypdf, docx, markdown, bs4, lxml, jinja2, reportlab; print('production python imports ok')"
```

For the minimal non-OCR profile, this lighter check is enough:

```powershell
python -c "import fitz, pypdf, pdfplumber, reportlab, PIL, pypdfium2; print('python pdf deps ok')"
```

`openpyxl` is used only for XLSX/table export workflows, and `playwright`
requires a browser install before `html_to_pdf.py` can render HTML to PDF.
Those are part of the committed dependency set, but they are not required for
the minimal PDF rendering and non-OCR review profile.

## 3. Verify JavaScript Helpers

From `skills/pdfs/js`:

```powershell
npm install
npm list --depth=0
node --check .\fill_form.mjs
node --check .\extract_form_fields.mjs
node --check .\extract_text_pdfjs.mjs
```

The expected direct dependencies are `pdf-lib` and `pdfjs-dist`.

## 4. Verify PDF Script Syntax

From `skills/pdfs`:

```powershell
python -c "import ast; from pathlib import Path; files=sorted(Path('scripts').glob('*.py')); [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in files]; print(f'python_scripts_parsed={len(files)}')"
```

Expected result for the local package is `python_scripts_parsed=22`, including `artifact_registry.py`.

## 5. Create Runtime Folders

The repository intentionally ignores generated inputs and outputs. Create them when needed:

```powershell
New-Item -ItemType Directory -Force -Path .\data, .\outputs, .\outputs\artifacts
```

Use `data/` for stable input files and `outputs/` for generated deliverables, QA renders, and local registry rows.

## 6. Render A Sample PDF

After placing any sample PDF at `data/sample.pdf`:

```powershell
python .\skills\pdfs\scripts\render_pdf.py .\data\sample.pdf --out_dir .\outputs\renders\sample --engine pdfium --dpi 150 --pages 1
```

This verifies the no-Poppler render path used before GPT-5.5 multimodal reading of scanned or low-text pages.

## 7. Generate And QA A PDF

HTML to PDF:

```powershell
python .\skills\pdfs\scripts\html_to_pdf.py .\outputs\task\report.html --output .\outputs\task\report.pdf --format A4
```

Markdown to PDF:

```powershell
python .\skills\pdfs\scripts\md_to_pdf.py .\outputs\task\report.md --output .\outputs\task\report.pdf --pdf_engine xelatex --resource_path .\outputs\task
```

LaTeX to PDF:

```powershell
python .\skills\pdfs\scripts\latex_to_pdf.py .\outputs\task\report.tex --output .\outputs\task\report.pdf --engine xelatex
```

Render final pages for QA:

```powershell
python .\skills\pdfs\scripts\render_pdf.py .\outputs\task\report.pdf --out_dir .\outputs\task\qa-pages --prefix report-page --engine pdftoppm --dpi 150
```

Generate a contact sheet for the final page renders:

```powershell
python .\skills\pdfs\scripts\create_montage.py .\outputs\task\qa-pages --out .\outputs\task\qa-contact-sheet.png --cols 4 --tile_max_w 320
```

For dense diagrams, formulas, tables, captions, generated images, or pages
changed late in the iteration, also save focused crop evidence from the final
rendered page:

```powershell
python -c "from PIL import Image; im=Image.open(r'.\outputs\task\qa-pages\report-page-2.png'); im.crop((120,180,980,720)).save(r'.\outputs\task\qa-pages\figure-2-2-crop.png')"
```

Inspect the rendered PNGs, contact sheet, and focused crops before treating the
PDF as complete. Record the final PDF hash, page count, rendered PNG count,
contact sheet path, focused crop paths, and manual inspection result in
`qa-manifest.json` or an equivalent task note.

## 8. Register A Final Artifact

```powershell
python .\skills\pdfs\scripts\artifact_registry.py register .\outputs\task\report.pdf --type application/pdf --description "Final production PDF" --producer "OpenCode GPT-5.5 multimodal plus local PDF stack" --json
```

List and inspect registered outputs:

```powershell
python .\skills\pdfs\scripts\artifact_registry.py list --json
python .\skills\pdfs\scripts\artifact_registry.py show <artifact_id> --json
```

Committed example metadata lives at `outputs/artifacts/registry.example.jsonl`. The live registry path is `outputs/artifacts/registry.jsonl` and remains local runtime state.

For generated-image PDFs with exact pixel-size requirements, inspect the saved
image file itself before accepting the output. Do not rely only on a generation
tool response that repeats the requested size.

## 9. Optional System Tool Checks

These commands are only required for workflows that use the corresponding tools:

```powershell
xelatex --version
latexmk -version
pandoc --version
pdfinfo -v
pdftoppm -v
gswin64c --version
soffice --version
qpdf --version
```

MiKTeX may print an update-check warning. That is not a PDF generation failure.

## 10. Committed Tree Review

Review the committed tree instead of the live working tree:

```powershell
git status --short
git archive --format=tar HEAD | tar -tf -
```

The review should prove committed files, not local session outputs, installed
dependencies, or uncommitted edits.

## Runtime State Not Committed

These paths are intentionally local and are not part of the committed workbench:

```text
data/
outputs/artifacts/registry.jsonl
outputs/generated-pdf/
outputs/full-stack-smoke/
outputs/prod-ocr-workflow/
D:\pdf-production-stack
```

The repository contains the workflow, scripts, docs, and a registry example. It does not contain generated PDFs, QA renders, private input files, or the external D-drive tool stack.
