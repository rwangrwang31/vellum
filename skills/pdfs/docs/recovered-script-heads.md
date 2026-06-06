# Recovered Script Heads

This file records recovered script source status and earlier script fragments from the known PDF skill package. All paths in the recovered script inventory now have complete local files under `scripts/`.

See `docs/script-inventory.json` for machine-readable script metadata: line counts, byte counts, imports, functions, arguments, and subcommands. Use the metadata for interface reconstruction and sanity checks, not exact parity assertions.

## Status

- `batch_pdf.py`: complete source recovered and implemented locally.
- `box_picker_html.py`: complete source recovered and implemented locally.
- `compare_renders.py`: complete source recovered and implemented locally.
- `create_montage.py`: complete source recovered and implemented locally.
- `edit_smoketest.py`: complete source recovered and implemented locally.
- `forms_smoketest.py`: complete source recovered and implemented locally.
- `html_to_pdf.py`: complete source recovered and implemented locally.
- `latex_to_pdf.py`: complete source recovered and implemented locally.
- `lo_convert_to_pdf.py`: complete source recovered and implemented locally.
- `make_watermark_pdf.py`: complete source recovered and implemented locally.
- `md_to_pdf.py`: complete source recovered and implemented locally.
- `ocr_pdf.py`: complete source recovered and implemented locally.
- `pdf_edit.py`: complete source recovered and implemented locally.
- `pdf_extract.py`: complete source recovered and implemented locally.
- `pdf_inspect.py`: complete source recovered and implemented locally.
- `pdf_preflight.py`: complete source recovered and implemented locally.
- `pdf_redact.py`: complete source recovered and implemented locally.
- `place_text_by_boxes.py`: complete source recovered and implemented locally.
- `redact_smoketest.py`: complete source recovered and implemented locally.
- `render_pdf.py`: complete source recovered and implemented locally.
- `renderer_parity.py`: complete source recovered and implemented locally.

## Complete Recovered Script Path Inventory

The package map names these script paths under `/home/oai/skills/pdfs/scripts/`. They should map locally to `skills/pdfs/scripts/` when implemented.

- `scripts/batch_pdf.py`
- `scripts/box_picker_html.py`
- `scripts/compare_renders.py`
- `scripts/create_montage.py`
- `scripts/edit_smoketest.py`
- `scripts/forms_smoketest.py`
- `scripts/html_to_pdf.py`
- `scripts/latex_to_pdf.py`
- `scripts/lo_convert_to_pdf.py`
- `scripts/make_watermark_pdf.py`
- `scripts/md_to_pdf.py`
- `scripts/ocr_pdf.py`
- `scripts/pdf_edit.py`
- `scripts/pdf_extract.py`
- `scripts/pdf_inspect.py`
- `scripts/pdf_preflight.py`
- `scripts/pdf_redact.py`
- `scripts/place_text_by_boxes.py`
- `scripts/redact_smoketest.py`
- `scripts/render_pdf.py`
- `scripts/renderer_parity.py`

## `render_pdf.py`

Recovered intent:

- Render PDF pages to PNGs for visual inspection.
- Default renderer is Poppler `pdftoppm`.
- Optional renderer is `pypdfium2`.
- Output naming is `<out_dir>/<prefix>-1.png`, `<out_dir>/<prefix>-2.png`, etc.

Recovered examples:

```bash
python render_pdf.py input.pdf --out_dir /mnt/data/_renders/input
python render_pdf.py input.pdf --out_dir /mnt/data/_renders/input --dpi 200 --pages 1-3
```

Recovered imports and helpers:

- `argparse`, `os`, `re`, `shutil`, `subprocess`
- `Path`
- `Iterable`, `List`, `Optional`, `Tuple`
- `_clear_existing(out_dir, prefix, fmt)` removes stale render outputs matching `prefix-N.fmt`.
- `_parse_pages(pages)` parses page ranges like `1-3,5,7-9`.
- `_pdftoppm_render(...)` begins by checking `pdftoppm`, creating `out_dir`, clearing stale outputs, and invoking Poppler once per range.

Implementation note:

- The default output prefix should be `page` to match `compare_renders.py`, smoke tests, and task docs.

## `compare_renders.py`

Recovered intent:

- Render two PDFs and compute pixel diffs.
- Catch visual regressions such as clipping, missing glyphs, and incorrect form marks.

Recovered golden path:

```bash
python compare_renders.py a.pdf b.pdf --out_dir /mnt/data/_diff --dpi 200
```

Recovered outputs:

- `summary.json`
- `diff/page-<N>.png` for changed pages
- `render_a/...`
- `render_b/...`

Recovered behavior:

- Calls sibling `render_pdf.py` via `subprocess.check_call`.
- Looks for rendered pages as `page-*.png`.
- Uses `PIL.Image` and `PIL.ImageChops`.
- Pads images to the larger canvas when page render sizes differ.
- Uses `ImageChops.difference`, `getbbox()`, grayscale histogram, percent changed, and max-channel diff metadata.

## `make_watermark_pdf.py`

Recovered intent:

- Generate a single-page watermark PDF with ReportLab.

Recovered behavior:

- Validates `--opacity` is in `[0,1]`.
- Supports `--pagesize letter` and A4 fallback.
- Creates output parent directories.
- Uses `canvas.Canvas`.
- Uses `setFillAlpha(opacity)` when ReportLab supports it.
- Draws centered text at either explicit `center_x`/`center_y` or page center.
- Applies translation and rotation before `drawCentredString`.

## `create_montage.py`

Recovered intent:

- Create a contact-sheet montage from render PNG/JPEG files.
- Useful for quickly skimming multi-page renders.

Recovered examples:

```bash
python create_montage.py /mnt/data/_renders/input --out /mnt/data/montage.png
python create_montage.py /mnt/data/_renders/input/page-*.png --out /mnt/data/montage.png --cols 4
```

Recovered behavior:

- Accepts directories, glob patterns, and explicit image paths.
- Keeps `.png`, `.jpg`, and `.jpeg` files.
- De-duplicates paths while preserving order.
- Uses `PIL.Image`.
- Resizes tiles to `tile_max_w` while preserving aspect ratio.
- Builds a white RGB canvas with margins.
- Places images in sorted reading order by row/column.

## `edit_smoketest.py`

Recovered intent:

- Smoke-test common edit operations with focus on `pdf_edit.py paginate`.
- Guard against API mismatches across `pypdf` versions.

Recovered run command:

```bash
python edit_smoketest.py --workdir /mnt/data/_pdf_edit_smoke
```

Recovered behavior:

- Generates a two-page ReportLab PDF.
- Calls sibling `pdf_edit.py paginate` with `--start 1 --position br`.
- Renders page 1 with sibling `render_pdf.py`.
- Expects `render/page-1.png` to exist.
- Prints `[OK] edit smoke test passed` on success.

## `forms_smoketest.py`

Recovered intent:

- End-to-end smoke test for form filling correctness.

Recovered behavior:

- Generates a tiny AcroForm PDF with ReportLab.
- Includes a text field named `name`.
- Includes a checkbox named `agree`.
- Writes `values.json` containing `name: Ada Lovelace` and `agree: true`.
- Runs `js/install_deps.sh`.
- Fills and flattens via `js/fill_form.mjs`.
- Renders before/after and compares renders.

## `redact_smoketest.py`

Recovered intent:

- Smoke-test true redaction using PyMuPDF workflow.

Recovered behavior:

- Creates a small ReportLab PDF containing `TOP SECRET: project-aurora`.
- Renders before.
- Calls sibling `pdf_redact.py text` with `--text "TOP SECRET" --ignore_case --whole_word`.
- Renders after.
- Runs `pdftotext` and fails if the phrase remains extractable.
- Uses `PIL.ImageChops` to verify rendered pixels changed.
