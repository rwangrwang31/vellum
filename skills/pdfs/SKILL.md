---
name: pdfs
description: "Reliable, workflow-driven PDF processing: render, verify, operate, then re-render/verify, covering reading, inspection, extraction, editing, forms, OCR, redaction, conversion, and diffing. Prefer authoring in DOCX or PPTX then converting to PDF for text-heavy docs or slide-like layouts; use ReportLab here for programmatic PDF generation."
---

# PDF Skill (Read, Inspect, Extract, Edit, Render, Forms, OCR, Redact, Convert, Diff)

This skill is designed for reliable, workflow-driven PDF work: render -> verify -> operate -> re-render verify.

## Repository entry guard

When using this package inside the Vellum repository, do not treat this file as
the first workflow entrypoint. If you reached it by scanning directories,
searching for `.tex` files, running `rg latex`, or jumping directly into
`skills/pdfs/`, stop and return to the repository root.

Read `PDF_PRODUCTION_WORKFLOW.md` and `QUICKSTART.md` first. Activate the
repository workflow, run `scripts/doctor.ps1`, and run `scripts/smoke.ps1`
before debugging or changing workflow entrypoints. The repository is the source
of truth; `<external-stack-root>` is only a provider of external tools.

## Before you touch PDFs: should this be DOCX/PPTX instead?

Even if the user asks for a PDF deliverable, the best workflow is often:

- Text-heavy, business-doc layout (headings, TOC, long tables, rich lists) -> use the DOCX skill to author, then convert to PDF with `lo_convert_to_pdf.py`.
- Slide-like visual layout (charts, callouts, fixed positioning, figure captions) -> use the Slides skill (PPTX) to author, then export to PDF.
- Programmatic generation -> ReportLab (this skill) is fine.

If you find yourself hand-tuning line breaks or typography in ReportLab, you probably picked the wrong authoring format.

## Generated raster assets

When creating a PDF with original visuals, coordinate with the image generation
workflow explicitly:

- If the user asks for generated images, covers, hero artwork, illustrations, or
  visual assets, use the available image-gen MCP/tool instead of substituting a
  hand-coded placeholder.
- Store generated source images and final prepared image assets in the same
  task output folder as the PDF source.
- Reference only workspace-local prepared assets from the PDF source.
- Validate required image dimensions before generation and inspect the rendered
  PDF page PNGs to confirm the assets are visible, undistorted, and not clipped.
- For explicit size claims such as 4K, verify the saved file's actual pixel
  dimensions; do not rely only on the generator's returned size label.

For insertion:

- HTML: use relative `<img src="asset.png" alt="...">` paths next to the HTML
  file.
- Markdown: use relative image paths to prepared assets in the task output
  directory, and pass that directory as the resource path when needed.
- LaTeX: keep images beside the `.tex` file and use `\includegraphics`.
- DOCX: prefer inline images; floating anchors are high-risk during
  LibreOffice-to-PDF conversion.
- PPTX: place images on slides, then render the exported PDF to PNGs for visual
  QA.

---

## Core loop (always)

1. Render to images

```bash
python ./skills/pdfs/scripts/render_pdf.py ./data/input.pdf --out_dir ./outputs/_renders/in --dpi 200
```

2. Inspect PNGs. Tables, figures, and layout are authoritative. For long
   documents, create a contact sheet for triage, then inspect focused crops of
   high-risk local regions such as dense diagrams, formulas, tables, captions,
   generated images, or pages changed during the final iteration. Keep focused
   crop outputs in a separate directory from whole-page renders so contact
   sheets cannot include crop PNGs.

3. Perform the edit, extract, or create operation.

4. Re-render and compare.

```bash
python ./skills/pdfs/scripts/compare_renders.py ./outputs/task/before.pdf ./outputs/task/after.pdf --out_dir ./outputs/_diff --dpi 200
```

---

## Task index (progressive)

Start with the smallest task that answers the user.

### Read / review

- `tasks/read_review.md`

### Extract (text/layout/tables/images/attachments/forms)

- `tasks/extract.md`
- `tasks/coords.md` (coordinate sanity)

### Edit (merge/split/rotate/crop/watermark/paginate/encrypt/repair)

- `tasks/edit.md`
- `tasks/compare.md` (visual regression)

### Forms

- Fillable forms: `tasks/forms_annotations.md`
- Debugging/introspection: `tasks/forms_debugging.md`
- Non-fillable / stamping workflow: `tasks/forms_nonfillable.md`

### OCR

- `tasks/ocr.md`

### Preflight / normalize

- `tasks/preflight.md`

### Redaction

- `tasks/redact.md`

### Renderer parity

- `tasks/parity.md`

### Batch processing

- `tasks/batch.md`

### Create / convert

- `tasks/create.md`
- `tasks/convert.md`
- `tasks/js_tools.md` (pdf-lib, pdfjs)

---

## Package map (where things live)

This pack includes a `manifest.txt` that is a pure list of relative file paths used by download tooling.

Quick map:

- `tasks/` (what to do)
- `docs/` (local setup, platform mapping, recovery notes)
- `scripts/` (run these)
- `js/` (Node helpers)
- `examples/`
- `troubleshooting/`

### tasks/

- `read_review.md` - render-first reading/review
- `extract.md` - extract text/layout/tables/images/attachments/forms
- `coords.md` - coordinate system cheatsheet (PDF pt vs image px)
- `edit.md` - merge/split/select/rotate/crop/watermark/paginate/encrypt/repair
- `compare.md` - visual diff workflow
- `forms_annotations.md` - fillable forms + appearance pitfalls + correctness checklist
- `forms_debugging.md` - widget-level introspection + acceptable values
- `forms_nonfillable.md` - stamp-by-boxes workflow for non-fillable forms
- `ocr.md` - optional local OCR; default scanned-page flow can use rendered images + multimodal model
- `preflight.md` - quick triage + normalization guidance
- `redact.md` - true redaction workflows
- `parity.md` - render parity across engines
- `batch.md` - batch helpers for corpora
- `create.md` - choose reportlab/latex/html/docx/pptx pipeline
- `convert.md` - docx/pptx/html/markdown/latex to PDF conversion
- `js_tools.md` - pdf-lib/pdfjs helper CLIs

### docs/

- `local-opencode-gpt55-install.md` - minimal local install profile when OpenCode calls GPT-5.5 for reasoning, research, and multimodal page reading
- `platform-local-replacements.md` - local OpenCode equivalents for ChatGPT platform tools such as `file_search`, `web.run`, `python_user_visible`, `artifact_tool`, and `sandbox:/mnt/data/...`; includes the local artifact registry contract
- `implementation-plan.md` - recovered implementation status and dependency notes
- `missing.md` - package gaps vs platform-layer gaps
- `recovered-script-heads.md` - recovered script notes
- `script-inventory.json` - machine-readable script metadata

### scripts/

- `render_pdf.py` - render to PNGs (pdfium or poppler)
- `compare_renders.py` - render-and-diff two PDFs (pixel diff)
- `pdf_inspect.py` - metadata/structure overview
- `pdf_extract.py` - text/words/chars/tables/images/attachments/annots/forms
- `pdf_edit.py` - editing toolkit (merge/split/select/rotate/crop/watermark/paginate/encrypt/repair/optimize)
- `pdf_preflight.py` - preflight/triage warnings
- `pdf_redact.py` - true redaction (remove underlying content)
- `renderer_parity.py` - diff pdftoppm vs pdfium renders
- `batch_pdf.py` - batch runner for common ops
- `artifact_registry.py` - register generated files under `outputs/` with stable IDs, hashes, metadata, and optional preview notes
- `box_picker_html.py` - generate interactive HTML to pick rectangles -> JSON in PDF coords
- `place_text_by_boxes.py` - stamp text/checkmarks into rectangles (non-fillable forms)
- `ocr_pdf.py` - OCR wrapper
- `html_to_pdf.py`, `md_to_pdf.py`, `latex_to_pdf.py`, `lo_convert_to_pdf.py` - conversion helpers

### js/

- `install_deps.sh` - installs pdf-lib + pdfjs-dist
- `fill_form.mjs` - fill + optional flatten (supports flags and positional args)
- `extract_form_fields.mjs` - list AcroForm fields
- `extract_text_pdfjs.mjs` - extract text via pdfjs-dist

### examples/

- `smoke_test.md` - runnable smoke flows

### troubleshooting/

- `common.md` - common pitfalls and fixes

---

## Final deliverable expectations

- No clipped text, overlaps, black squares, or broken glyphs in rendered PNGs.
- Contact sheets are triage only; diagram-heavy, formula-heavy, or
  layout-sensitive PDFs also need focused crop evidence from the final rendered
  pages, with crop PNGs kept outside the whole-page render directory.
- After any layout-sensitive fix, re-render the final PDF, regenerate the
  contact sheet and focused crops, and update the QA manifest or task notes
  before reporting completion.
- For textbook-style analog electronics circuits, prefer task-local `schemdraw`
  generators for new or substantially revised standard schematics. Legacy
  `circuitikz` components should be horizontal or vertical unless a real
  schematic convention requires a diagonal component.
- Circuit-heavy PDF crops should explicitly reject slanted or distorted
  components, label overlap, same-endpoint voltage polarity marks, ambiguous
  `U_C` versus `U_{CEQ}` measurements, unclear BJT small-signal ports, and
  inconsistent `\beta i_b` controlled-source direction.
- Verify in at least one renderer (`pdfium` or `pdftoppm`). For tricky forms, verify in two.
- Remove intermediate artifacts from the deliverable folder (keep only final PDFs).
- Avoid Unicode dashes that some renderers mishandle; prefer ASCII `-`.
