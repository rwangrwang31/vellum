# Quick Start

Use this guide to verify the local PDF/DOCX workbench after cloning the repository. It covers the committed workflow files only. Runtime outputs and the D-drive production stack are local-machine state.

## 1. Activate The Repository Workflow

From the repository root:

```powershell
. .\scripts\activate.ps1
```

`vellum` is the workflow source of truth. The repository activation script resolves this clone as `VELLUM_REPO_ROOT`, then uses the external PDF stack only as a provider for MiKTeX/XeLaTeX, Pandoc, Poppler, Ghostscript, LibreOffice, qpdf, Python fallback, and Playwright Chromium.

On this machine the default external stack is:

```text
D:\pdf-production-stack
```

Use `-StackRoot` only when the external tools live somewhere else:

```powershell
. .\scripts\activate.ps1 -StackRoot D:\pdf-production-stack
```

The script prefers a repository-local `.venv` when present. If `.venv` is not present, it uses the external stack Python venv. If the external stack activation script is missing, use `skills/pdfs/docs/local-opencode-gpt55-install.md` for the minimal Python/JS setup and add optional system tools only when a task needs them.

## 2. Run The Repository Doctor

Run the committed workflow contract check from the repository root:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\doctor.ps1
```

Expected result on a ready machine:

```text
PASS: external stack satisfies the Vellum repository PDF workflow contract.
```

The doctor checks the repository `requirements.txt`, PDF script syntax, JS helper dependencies in `skills/pdfs/js`, expected external commands, Playwright browser cache, and the selected Python interpreter.

## 3. Run The Repository Smoke Test

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\smoke.ps1
```

The smoke test generates a PDF, renders the first QA page, creates a contact sheet, and writes a local registry row under:

```text
outputs/repo-workflow-smoke/
```

That output directory is ignored runtime state.

## 4. Verify Python Dependencies Manually

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

## 5. Verify JavaScript Helpers

From `skills/pdfs/js`:

```powershell
npm install
npm list --depth=0
node --check .\fill_form.mjs
node --check .\extract_form_fields.mjs
node --check .\extract_text_pdfjs.mjs
```

The expected direct dependencies are `pdf-lib` and `pdfjs-dist`.

## 6. Verify PDF Script Syntax

From `skills/pdfs`:

```powershell
python -c "import ast; from pathlib import Path; files=sorted(Path('scripts').glob('*.py')); [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in files]; print(f'python_scripts_parsed={len(files)}')"
```

Expected result for the local package is `python_scripts_parsed=22`, including `artifact_registry.py`.

## 7. Create Runtime Folders

The repository intentionally ignores generated inputs and outputs. Create them when needed:

```powershell
New-Item -ItemType Directory -Force -Path .\data, .\outputs, .\outputs\artifacts
```

Use `data/` for stable input files and `outputs/` for generated deliverables, QA renders, and local registry rows.

## 8. Render A Sample PDF

After placing any sample PDF at `data/sample.pdf`:

```powershell
python .\skills\pdfs\scripts\render_pdf.py .\data\sample.pdf --out_dir .\outputs\renders\sample --engine pdfium --dpi 150 --pages 1
```

This verifies the no-Poppler render path used before GPT-5.5 multimodal reading of scanned or low-text pages.

## 9. Generate And QA A PDF

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
rendered pages. Prefer a saved crop spec so the checked region and visual claim
are repeatable:

```powershell
python .\skills\pdfs\scripts\crop_rendered_pages.py .\outputs\task\focused-crops.json --base_dir . --strict --json
```

Inspect the rendered PNGs, contact sheet, and focused crops before treating the
PDF as complete. Record the final PDF hash, page count, rendered PNG count,
contact sheet path, focused crop spec path, focused crop paths, and manual
inspection result in `qa-manifest.json` or an equivalent task note. For
math/physics diagrams, record the geometry invariant checked by the crop, such
as point-on-curve alignment, tangent/normal direction, and label clearance.
In final QA, each focused crop spec should include itemized `checks` and
`reject_if` conditions so the crop cannot pass on a vague "looks fine" judgment.

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

## 10. Optional System Tool Checks

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

## 11. Committed Tree Review

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
