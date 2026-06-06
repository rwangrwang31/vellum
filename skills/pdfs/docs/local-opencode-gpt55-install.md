# Local OpenCode GPT-5.5 Install Profile

Use this when all intelligence is provided by OpenCode calling GPT-5.5, and local tools only handle files.

## Scope

Default flow:

```text
local files and scripts
-> OpenCode tool calls
-> GPT-5.5 reasoning, research, and multimodal page reading
-> local outputs and indexes
```

Default exclusions:

- No OCRmyPDF or Tesseract.
- No local LLM runtime.
- No local embedding model.
- No Docling, Marker, or Unstructured heavy parser.
- No Docker, gVisor, Firejail, Jupyter, or Code Interpreter sandbox.

## Current Machine Status

Available commands:

- `python`
- `node`
- `npm`
- `qpdf`

Missing commands:

- `pdftoppm`
- `pdftotext`
- `pdfinfo`
- `pdffonts`
- `soffice`
- `pandoc`
- `xelatex`
- `playwright` command

Available Python imports:

- `fitz` / PyMuPDF
- `PIL` / Pillow

Missing Python imports:

- `playwright`
- `pdfminer` (normally installed through `pdfplumber`)

Missing Node packages in `skills/pdfs/js`:

- `pdf-lib`
- `pdfjs-dist`

## Minimal Install

Install the Python packages needed for the local PDF workbench:

```powershell
python -m pip install PyMuPDF Pillow pypdf pdfplumber reportlab pypdfium2
```

Install JS helper dependencies from `skills/pdfs/js`:

```powershell
npm install
```

Expected extra space:

```text
400MB - 1.2GB
```

## Why These Packages

| Package | Needed for |
| --- | --- |
| `PyMuPDF` | preflight, redaction, image extraction, and repair/optimize helpers through `fitz`. |
| `Pillow` | render comparison, montage creation, and image QA. |
| `pypdf` | inspect, edit, merge/split, forms, attachments, structural reads. |
| `pdfplumber` | text, word, char, and table extraction with page/coordinate metadata. |
| `reportlab` | watermarking, PDF creation, non-fillable form stamping, smoke tests. |
| `pypdfium2` | render PDF pages locally without Poppler; enough for GPT-5.5 multimodal page reading. |
| `pdf-lib` | JS form fill and flatten helper. |
| `pdfjs-dist` | JS text/form inspection helper. |

## Optional Installs

| Tool | Install only when | Skip by default because |
| --- | --- | --- |
| Poppler | Need `pdftoppm`, `pdftotext`, `pdfinfo`, `pdffonts`, or renderer parity. | `pypdfium2` can render pages for GPT-5.5 multimodal reading. |
| Playwright Python + Chromium | Need local HTML -> PDF via `html_to_pdf.py`. | Browser install is large; OpenCode already has browser MCP tools. |
| LibreOffice | Need DOCX/PPTX/ODT -> PDF via `lo_convert_to_pdf.py`. | Large install; not needed for PDF read/edit/search. |
| Pandoc | Need Markdown -> PDF via `md_to_pdf.py`. | Not needed for default PDF workflows. |
| XeLaTeX / TeX Live | Need LaTeX PDF generation. | Very large install. |
| OCRmyPDF / Tesseract | Need searchable PDF text layers or offline deterministic OCR. | Default scanned-page flow uses rendered page images plus GPT-5.5 multimodal reading. |
| `openpyxl` | Need XLSX output from table extraction or XLSX-to-DOCX table conversion. | Not required for the minimal render/read/edit PDF profile. |
| Chroma/Qdrant/FAISS/txtai | Need semantic search over many local documents. | MVP can start with keyword search/SQLite FTS; GPT-5.5 handles reasoning. |
| Docling/Marker/Unstructured | Need advanced layout parsing beyond current scripts and GPT-5.5 vision. | Heavy dependencies/models. |
| Docker/Jupyter/gVisor/Firejail | Need sandboxed execution of untrusted code/files. | Local trusted workflow can use shell Python plus explicit output files. |
| `pandas` | Need larger table/data workflows beyond current scripts. | Current recovered Python scripts do not directly import it. |

## Scanned PDF Flow Without OCR

```text
PDF page
-> render_pdf.py using pypdfium2
-> page PNG/JPEG
-> GPT-5.5 multimodal reading
-> page text/summary saved with source_id/page metadata
-> keyword index
```

This avoids local OCR dependencies while preserving page-level citations.

## Recommended Starting Point

Start with the minimal install only:

```powershell
python -m pip install PyMuPDF Pillow pypdf pdfplumber reportlab pypdfium2
```

Then from `skills/pdfs/js`:

```powershell
npm install
```

Add optional tools only when a real task requires them.

## Post-Install Verification

Run these checks after installing the minimal profile.

### Python imports

```powershell
python -c "import fitz, pypdf, pdfplumber, reportlab, PIL, pypdfium2; print('python pdf deps ok')"
```

Expected:

```text
python pdf deps ok
```

### JS helpers

From `skills/pdfs/js`:

```powershell
npm list --depth=0
node --check .\fill_form.mjs
node --check .\extract_form_fields.mjs
node --check .\extract_text_pdfjs.mjs
```

Expected packages:

```text
pdf-lib
pdfjs-dist
```

### PDF scripts syntax

From `skills/pdfs`:

```powershell
python -c "import ast; from pathlib import Path; files=sorted(Path('scripts').glob('*.py')); [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in files]; print(f'python_scripts_parsed={len(files)}')"
```

Expected:

```text
python_scripts_parsed=22
```

### Render path check

Use this after you have any sample PDF available:

```powershell
python .\scripts\render_pdf.py .\data\sample.pdf --out_dir .\outputs\renders\sample --engine pdfium --dpi 150 --pages 1
```

This verifies the no-Poppler rendering path used before sending scanned/low-text pages to GPT-5.5 multimodal reading.

### Optional command checks

These may stay missing in the minimal profile:

```powershell
python -c "import shutil; cmds=['pdftoppm','pdftotext','pdfinfo','pdffonts','soffice','pandoc','xelatex']; [print(c+'='+(shutil.which(c) or 'MISSING')) for c in cmds]"
```

Missing output is acceptable unless a task explicitly needs that optional feature.
