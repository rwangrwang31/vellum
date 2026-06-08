# PDF Production Workflow

This is the repo-level entrypoint for the local OpenCode/GPT-5.5 non-OCR PDF production workflow.

Use this when a future OpenCode session needs to discover how to generate production PDFs from local PDFs, page images, DOCX files, Markdown, HTML, or LaTeX.

For a clone-to-first-check path, start with `QUICKSTART.md`, then return here for the full workflow and command reference.

## Hard Agent Entry Rule

For agent-driven work, this file and `QUICKSTART.md` are the required entry
documents. Do not begin a PDF, LaTeX, XeLaTeX, TikZ, PDF QA,
`pdf-production-stack`, `render_pdf`, focused crop, artifact-registration, or
diagram/formula-heavy task by scanning directories, enumerating `skills/`,
searching for `.tex` files, running broad searches such as `rg latex`, or
jumping directly into `skills/pdfs/`.

Read the entry docs first, then activate the repository workflow and run the
doctor. Run the smoke test before debugging or changing workflow entrypoints.
Only after that should you inspect implementation files or use targeted search.

## Activation

Activate the repository workflow before running PDF production commands:

```powershell
. .\scripts\activate.ps1 -StackRoot <external-stack-root>
```

The repository is the workflow source of truth. `scripts/activate.ps1` resolves the current clone as `VELLUM_REPO_ROOT`, then dot-sources the external stack activation script only to expose third-party tools and runtime paths for the current PowerShell session.

Set `PDF_PRODUCTION_STACK` for the current shell or pass `-StackRoot` explicitly.
The external stack root is machine-local runtime state and should not be
committed as a concrete absolute path:

```text
<external-stack-root>
```

Explicit activation example:

```powershell
. .\scripts\activate.ps1 -StackRoot <external-stack-root>
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

The external stack location is local machine state:

```text
<external-stack-root>
```

Operational notes and uninstall instructions, if present at your stack root:

```text
<external-stack-root>\install-notes.md
```

If a dependency such as `qpdf` is installed outside the external stack, expose it
through the shell `PATH` or the external stack activation script rather than
recording a machine-specific absolute path in repository docs:

```text
<qpdf-bin>\qpdf.exe
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
- The source uses relative paths, not machine-specific absolute paths or tool
  temporary directories.
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

For layout-sensitive pages, create focused crops from the final rendered pages.
Prefer a structured crop spec so the crop boxes and the visual claim being
verified are repeatable. Keep crop outputs in a separate directory from
whole-page renders so the contact sheet cannot accidentally include old crop
PNGs:

```powershell
@'
{
  "task": "task",
  "crops": [
    {
      "name": "figure-2-2",
      "source": "outputs/task/qa-pages/report-page-2.png",
      "box": [120, 180, 980, 720],
      "output": "outputs/task/qa-crops/figure-2-2-crop.png",
      "verifies": "caption, labels, and plotted geometry do not overlap",
      "checks": [
        "caption is fully visible and separated from the frame",
        "labels do not touch plotted lines, markers, arrows, axes, or formulas",
        "plotted geometry satisfies the stated invariant"
      ],
      "reject_if": [
        "any label touches or crosses a diagram element",
        "any formula or label is clipped by the crop or page frame",
        "the crop omits a high-risk edge needed to prove clearance"
      ]
    }
  ]
}
'@ | Set-Content -Encoding UTF8 .\outputs\task\focused-crops.json

python .\skills\pdfs\scripts\crop_rendered_pages.py .\outputs\task\focused-crops.json --base_dir . --strict --json
```

One-off PIL crop commands are still acceptable for exploration, but final QA
evidence for diagram-heavy or formula-heavy PDFs should use a saved crop spec.

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
   PNGs from an earlier PDF cannot pollute the evidence. Keep that directory
   limited to whole-page renders.
2. Confirm `pdfinfo` page count, rendered PNG count, and expected page count
   match.
3. Generate a contact sheet from the final page PNGs and inspect it for page
   order, blank pages, missing images, bad pagination, clipped text, and major
   overlaps.
4. Identify high-risk elements and create focused crop evidence for each one
   that could fail locally while looking acceptable in a contact sheet.
   Save focused crop output under a separate directory such as
   `outputs/<task>/qa-crops/`, not inside the whole-page render directory.
5. For each focused crop, record concrete `checks` and `reject_if` conditions.
   The `verifies` sentence alone is not enough for final QA; it must be backed
   by itemized visual assertions such as label clearance, crop edge clearance,
   point-on-curve alignment, and formula/frame separation.
6. For generated math or physics diagrams, inspect and record geometry-specific
   invariants, not just whether the page looks generally tidy.
7. Record the evidence in `qa-manifest.json` or an equivalent task note before
   registering the PDF as final.

High-risk elements include:

- TikZ, circuitikz, PGFPlots, and other generated diagrams.
- Dense formulas, derivations, matrices, and aligned equations.
- Complex tables, long labels, narrow columns, captions, footnotes, and callouts.
- Inserted raster images, generated covers, and pages with exact size claims.
- Any page changed during the final fix iteration.

For math, physics, engineering, and other generated diagrams, preserve geometry
invariants in source where practical:

- Points that should lie on curves must be derived from the same function,
  named path coordinate, or shared calculation as the curve.
- Vectors that represent tangents, normals, radii, or forces should be anchored
  to named coordinates and calculated directions instead of visual guesses.
- Labels should be offset from the diagram element they describe and then
  checked in a focused crop for line, arrow, marker, and frame overlap.
- QA notes should state the invariant being verified, for example "particle
  point lies on the plotted curve" or "normal vector is separated from the
  velocity arrow and labels".

The QA manifest should record at least:

- final PDF path and SHA-256;
- `pdfinfo` page count and rendered PNG count;
- render directory and render command;
- contact sheet path;
- focused crop spec path when structured crops were used;
- focused crop paths with page numbers, what each crop verifies, the itemized
  checks performed, and the reject conditions that would have failed the crop;
- manual inspection result for clipping, overlaps, missing glyphs, broken
  images, and bad pagination.

Do not use compile success, a PDF viewer glance, or a contact sheet alone as
completion evidence for diagram-heavy or formula-heavy PDFs. If a layout bug is
found after delivery, the next fix must re-render the final PDF, regenerate the
contact sheet and focused crops, update `qa-manifest.json`, and only then
register the replacement artifact.

## Analog Electronics And Circuit Schematic QA

For standard textbook-style circuit diagrams, especially analog electronics
amplifier circuits and AC/DC equivalent circuits, treat schematic standardness
as a required QA invariant.

For new or substantially revised textbook circuit bodies, prefer task-local
`schemdraw` generators over hand-authored `circuitikz`. The committed
`requirements.txt` includes `schemdraw` and `matplotlib`; `doctor.ps1` checks
those dependencies. Generate source-controlled-by-code assets under the task
output directory, normally:

```text
outputs/<task>/generate_circuit_assets.py
outputs/<task>/circuits/<asset>.pdf
```

Reference generated PDF circuit assets from LaTeX with relative paths:

```latex
\includegraphics[width=.82\linewidth]{circuits/common-emitter-full.pdf}
```

For legacy `circuitikz` figures that remain in LaTeX source, draw resistors,
capacitors, independent sources, controlled sources, and related components on
horizontal or vertical `to[...]` paths unless the schematic convention
explicitly requires a diagonal component. If two nodes differ in both x and y,
route with ordinary wire segments first, then place the component on an
orthogonal segment.

Circuit contracts for analog amplifier and equivalent-circuit figures:

- Output coupling branches in common-emitter and common-collector diagrams must
  use a horizontal `C_2` followed by a vertical `R_L` to the reference rail.
- Emitter bypass branches must draw `C_E` vertically on an emitter-side branch
  separated from `R_L`, `C_2`, output voltage labels, and load labels.
- Parallel AC load equivalents must show parallel load branches as vertical
  elements connected by horizontal top and bottom rails.
- Collector voltage test leads such as `U_C` must be horizontal from the
  collector node unless a real schematic convention requires otherwise.
- Do not mix collector-to-reference and collector-emitter voltage semantics in
  one ambiguous annotation. `U_C` is collector-to-reference; `U_{CEQ}` is
  collector-emitter quiescent measurement.
- Voltage polarity helpers must use explicit distinct `plus` and `minus` node
  coordinates and fail fast when the coordinates are identical. Do not place
  `+` and `-` as unrelated labels around one terminal.
- Small-signal BJT model figures must show distinct `b`, `c`, and `e` ports,
  `u_{be}` and `u_{ce}` on clear endpoint pairs, a separated `r_{be}` branch,
  an `i_b` arrow on its own lane, and a controlled current source labeled
  `\beta i_b` on a separate collector-emitter branch.
- Controlled-source direction must be consistent across related small-signal
  figures in one PDF unless the figure explicitly documents a different
  convention.
- Full common-emitter schematics with a signal source must reserve separate
  horizontal space for `u_s`, `R_s`, `u_i`, and `C_1`; avoid stacking source
  resistance vertically above the source when it crowds input labels.
- When matching a user-provided textbook reference, match semantic terminal
  styling as well as geometry, including supply endpoint style and labels such
  as `+V_{CC}` with `(+12V)` when the reference shows both.

Circuit-specific failure conditions:

- A `to[C]` or `to[R]` path connects coordinates with both x and y changed.
- `R_L`, `C_2`, `C_E`, `U_C`, `u_o`, or polarity labels overlap or crowd.
- A voltage marker places `+` and `-` on the same open dot, same endpoint, or
  visually indistinguishable terminals.
- One figure labels the same visual endpoint pair as both `U_C` and `U_{CEQ}`.
- Related small-signal figures reverse `\beta i_b` direction without an
  explicit convention note.
- A converted circuit asset is registered without focused crops proving
  orthogonal components, label clearance, voltage polarity endpoints, and
  controlled-source direction.

For circuit-heavy PDFs, `qa-manifest.json` must record the dependency decision,
generated circuit asset list, build command, final render evidence, focused crop
evidence, and manual inspection result. Focused crop specs must include concrete
`checks` and `reject_if` items that reject slanted, stretched, rotated, or
distorted component bodies; label collisions; same-endpoint voltage polarity;
unclear port labels; and inconsistent controlled-source direction.

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
