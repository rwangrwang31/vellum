# PDF Production Workflow

This is the repo-level entrypoint for the local OpenCode/GPT-5.5 non-OCR PDF production workflow.

Use this when a future OpenCode session needs to discover how to generate production PDFs from local PDFs, page images, DOCX files, Markdown, HTML, or LaTeX.

For a clone-to-first-check path, start with `QUICKSTART.md`, then return here for the full workflow and command reference.

## Activation

Activate the repository workflow before running PDF production commands:

```powershell
. .\scripts\activate.ps1
```

The repository is the workflow source of truth. `scripts/activate.ps1` resolves the current clone as `VELLUM_REPO_ROOT`, then dot-sources the external stack activation script only to expose third-party tools and runtime paths for the current PowerShell session.

On this machine the default external stack is:

```text
D:\pdf-production-stack
```

Use `-StackRoot` only when the external tools live elsewhere:

```powershell
. .\scripts\activate.ps1 -StackRoot D:\pdf-production-stack
```

The external stack provides:

```text
MiKTeX / XeLaTeX / latexmk
Pandoc
Poppler: pdfinfo, pdftoppm
Ghostscript: gswin64c
LibreOffice: soffice
qpdf
Production Python venv
Playwright Chromium cache
```

The activation script prefers a repository-local `.venv` when present. If `.venv` is not present, it uses the external stack Python venv. It does not require a persistent system PATH change.

Validate the activated repository workflow with:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\doctor.ps1
```

Run an end-to-end smoke test with:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\smoke.ps1
```

## Stack Location

Installed stack root on this machine:

```text
D:\pdf-production-stack
```

Operational notes and uninstall instructions, if present at your stack root:

```text
D:\pdf-production-stack\install-notes.md
```

Pre-existing qpdf dependency reused by this machine's stack:

```text
D:\qpdf 12.3.2\bin\qpdf.exe
```

## Non-OCR Rule

Do not install or require local OCR engines for the default workflow.

The intended replacement is:

```text
render PDF/page to high-resolution image
-> GPT-5.5 multimodal reading
-> structured text / formulas / figures
-> Markdown, HTML, or LaTeX
-> production PDF
```

Excluded by default:

```text
tesseract
pytesseract
PaddleOCR
Surya OCR
EasyOCR
OCRmyPDF OCR backend setup
```

## Main Workflow

```text
local input PDF/image/DOCX
-> direct local file access
-> PDF/DOCX scripts under skills/pdfs and skills/docx
-> GPT-5.5 multimodal reading for scanned or low-text pages
-> image-gen MCP for requested or visually important raster assets
-> outputs/<task>/ source files and generated files
-> XeLaTeX / Pandoc / Playwright / LibreOffice PDF generation
-> final-PDF render QA with contact sheet and focused crops
-> artifact_registry.py registration
```

## Image Generation Coordination

When a PDF task explicitly asks for generated imagery, or when the PDF is a
visual onboarding, marketing, report-cover, diagram-heavy, or slide-like
artifact that needs original raster visuals, treat image generation as part of
the production workflow rather than as an optional decoration.

Required coordination steps:

1. Call the available image-gen MCP/tool before final PDF generation.
2. Save generated source images under the task output directory, for example:

```text
outputs/<task>/imagegen-<asset-name>-source.png
```

3. Prepare PDF-ready assets under the same output directory with stable names,
   dimensions, and format, for example:

```text
outputs/<task>/hero.png
outputs/<task>/diagram-background.png
```

4. Reference the prepared assets from the HTML, Markdown, LaTeX, DOCX, or PPTX
   source. Do not leave a PDF-referenced image only in a tool-default temporary
   or global image output folder.
5. Record enough provenance in the task output or task notes to identify which
   generated source image became the final PDF asset.
6. During QA, verify that generated images are present, not stretched in a
   visibly bad way, not clipped unexpectedly, and rendered in the final PDF
   page PNGs.

For explicit size requirements such as a 4K hero image, validate the prepared
asset dimensions before PDF generation and again in the final QA evidence.
Do not trust a generator response alone for pixel-size claims; inspect the
saved image file with a standard image inspector or a short Pillow check.

Dimension check example:

```powershell
python -c "from PIL import Image; im=Image.open(r'.\outputs\task\hero.png'); print(im.size)"
```

Observed local MCP behavior on 2026-06-05:

- A `3840x2160` request was accepted, but the saved PNG inspected as
  `1672x941`.
- `3840x2160` with higher quality settings timed out in the active MCP path.
- Therefore, treat 4K as a requested target that must pass file-level
  dimension verification before it can be claimed as delivered.

## Insert Images Into PDF Sources

Keep image assets next to the source file that references them. Use relative
paths so the source can be re-rendered from the task output directory without
machine-specific absolute paths.

Recommended insertion patterns:

```html
<img src="hero.png" alt="Descriptive text" />
```

```markdown
![Descriptive text](hero.png)
```

```latex
\includegraphics[width=\linewidth]{hero.png}
```

For DOCX sources, prefer inline images and keep captions in the following
paragraph; floating images are high-risk during LibreOffice PDF export. For
PPTX sources, use slide-local image placement and render slides/PDF pages for
visual QA.

Image insertion checks:

- The referenced file exists before PDF generation.
- The source uses relative paths, not `C:\...`, `D:\...`, or tool temporary
  directories.
- The final PDF render shows the image on the intended page.
- The image keeps its intended aspect ratio unless the task explicitly asks for
  a crop.
- Captions or nearby labels remain visually attached to the image.

## Production-Validated Illustrated PDF

A production dry run was completed from a fresh remote clone of the public
repository, using only the user request:

```text
研究报告：GPT-5.5 vs Claude Opus 4.8
```

Validation summary:

1. Clone `https://github.com/rwangrwang31/gpt-pdf-web.git`.
2. Generate two report illustrations with the image-gen MCP.
3. Save generated sources and stable PDF-ready assets in
   `outputs/research-gpt55-vs-claude-opus48/`.
4. Author `report.html` with relative image paths.
5. Generate PDF with `skills/pdfs/scripts/html_to_pdf.py`.
6. Render the final PDF with `skills/pdfs/scripts/render_pdf.py`.
7. Extract embedded images with `skills/pdfs/scripts/pdf_extract.py images`.
8. Register the final PDF with `skills/pdfs/scripts/artifact_registry.py`.

The run produced a 3-page A4 PDF, rendered 3 QA PNGs, extracted 2 embedded
images from the PDF, and confirmed text extraction for the title, model names,
figure caption, sources, and image-generation note.

## Common Commands

Run from the repo root:

```powershell
. .\scripts\activate.ps1
```

HTML to PDF:

```powershell
python .\skills\pdfs\scripts\html_to_pdf.py .\outputs\task\report.html --output .\outputs\task\report.pdf --format A4
```

Markdown to PDF through Pandoc and XeLaTeX:

```powershell
python .\skills\pdfs\scripts\md_to_pdf.py .\outputs\task\report.md --output .\outputs\task\report.pdf --pdf_engine xelatex --resource_path .\outputs\task
```

LaTeX to PDF through latexmk and XeLaTeX:

```powershell
python .\skills\pdfs\scripts\latex_to_pdf.py .\outputs\task\report.tex --output .\outputs\task\report.pdf --engine xelatex
```

Render final PDF pages for QA. Prefer the local render script so reruns clear
stale files for the selected prefix:

```powershell
python .\skills\pdfs\scripts\render_pdf.py .\outputs\task\report.pdf --out_dir .\outputs\task\qa-pages --prefix report-page --engine pdftoppm --dpi 150
```

Create a contact sheet for whole-document triage:

```powershell
python .\skills\pdfs\scripts\create_montage.py .\outputs\task\qa-pages --out .\outputs\task\qa-contact-sheet.png --cols 4 --tile_max_w 320
```

For a layout-sensitive page, create a focused crop from the final rendered
page. Adjust the box to the figure, table, formula block, caption, or changed
region being checked:

```powershell
python -c "from PIL import Image; im=Image.open(r'.\outputs\task\qa-pages\report-page-2.png'); im.crop((120,180,980,720)).save(r'.\outputs\task\qa-pages\figure-2-2-crop.png')"
```

Register final PDF:

```powershell
python .\skills\pdfs\scripts\artifact_registry.py register .\outputs\task\report.pdf --type application/pdf --description "Final production PDF" --producer "OpenCode GPT-5.5 multimodal plus XeLaTeX/Pandoc/Playwright stack" --json
```

List registered outputs:

```powershell
python .\skills\pdfs\scripts\artifact_registry.py list --json
```

## Final PDF QA Evidence Gate

Compile or converter success is not enough to claim a PDF is visually correct.
Whole-page renders are required, but they are only the first pass. Contact
sheets are useful triage evidence; they are not final proof for dense local
layout.

Before reporting a generated PDF complete:

1. Render the final PDF after the last edit. Use a fresh task-specific QA
   directory or the local `render_pdf.py` script with a stable prefix so stale
   PNGs from an earlier PDF cannot pollute the evidence.
2. Confirm `pdfinfo` page count, rendered PNG count, and expected page count
   match.
3. Generate a contact sheet from the final page PNGs and inspect it for page
   order, blank pages, missing images, bad pagination, clipped text, and major
   overlaps.
4. Identify high-risk elements and create focused crop evidence for each one
   that could fail locally while looking acceptable in a contact sheet.
5. Record the evidence in `qa-manifest.json` or an equivalent task note before
   registering the PDF as final.

High-risk elements include:

- TikZ, circuitikz, PGFPlots, and other generated diagrams.
- Dense formulas, derivations, matrices, and aligned equations.
- Complex tables, long labels, narrow columns, captions, footnotes, and callouts.
- Inserted raster images, generated covers, and pages with exact size claims.
- Any page changed during the final fix iteration.

The QA manifest should record at least:

- final PDF path and SHA-256;
- `pdfinfo` page count and rendered PNG count;
- render directory and render command;
- contact sheet path;
- focused crop paths with page numbers and what each crop verifies;
- manual inspection result for clipping, overlaps, missing glyphs, broken
  images, and bad pagination.

Do not use compile success, a PDF viewer glance, or a contact sheet alone as
completion evidence for diagram-heavy or formula-heavy PDFs. If a layout bug is
found after delivery, the next fix must re-render the final PDF, regenerate the
contact sheet and focused crops, update `qa-manifest.json`, and only then
register the replacement artifact.

## Current Verified Artifacts

The following artifacts prove the workflow is discoverable and runnable on this machine when the local runtime outputs are present:

```text
subscription-report-e99e3dccd9c9
outputs/generated-pdf/subscription-report.pdf
```

Additional smoke artifact:

```text
sample-tex-4bb6af2930a4
outputs/full-stack-smoke/sample-tex.pdf
```

Use the registry to inspect them:

```powershell
python .\skills\pdfs\scripts\artifact_registry.py show subscription-report-e99e3dccd9c9 --json
```

These generated PDFs, QA renders, and the live registry are runtime state and are intentionally not committed because `outputs/` is ignored. The committed registry shape example is:

```text
outputs/artifacts/registry.example.jsonl
```

Recreate live artifacts by running the commands in this workflow or `QUICKSTART.md`, then registering final deliverables with `artifact_registry.py`.

## Validation

Run the repository doctor first:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\doctor.ps1
```

Run the repository smoke test before debugging or tuning workflow changes:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\smoke.ps1
```

The smoke test writes generated PDF, QA render, contact sheet, and local registry output under:

```text
outputs/repo-workflow-smoke/
```

For focused manual checks after activation, these commands are useful:

```powershell
python -c "import fitz, PIL, playwright, pypdf, docx, markdown, bs4, lxml, jinja2, reportlab; print('production python imports ok')"
xelatex --version
latexmk -version
pandoc --version
pdfinfo -v
pdftoppm -v
gswin64c --version
soffice --version
qpdf --version
```

Known harmless warning:

```text
MiKTeX may print: major issue: So far, you have not checked for MiKTeX updates.
```

This is an update-check warning, not a PDF generation failure.

## Related Docs

```text
skills/pdfs/docs/platform-local-replacements.md
skills/pdfs/docs/implementation-plan.md
skills/pdfs/docs/local-opencode-gpt55-install.md
local production stack install notes, if present at your chosen stack root
```
