# Platform Local Replacements

This document maps the ChatGPT/GPT-5.5 Thinking platform tools referenced by the recovered prompt to local OpenCode capabilities available in this workspace.

The goal is practical local-computer PDF work, not exact reproduction of OpenAI internal services. The default local workflow is direct file-path access: read, extract, render, and register files already on this machine.

## Scope

- Included: local tool equivalents, recommended usage, and gaps that matter for PDF workflows.
- Excluded: OpenAI internal source code, private service contracts, model weights, exact UI behavior, and hosted citation/link infrastructure.
- Safety note: the active OpenCode profile has provider credentials in its config. Do not copy config values into docs or logs.

## Current OpenCode Capabilities

These capability groups are exposed in the current session or configured in the active Trellis profile.

- Filesystem and code search: `glob`, `grep`, `read`, `fast-context`, YCE search.
- Local execution: `bash`, PowerShell, Python subprocesses, Node subprocesses, `apply_patch` for edits.
- Web search and fetch: `grok-search`, `tavily-hikari`, `smart-search`, `webfetch`.
- Browser automation and screenshots: `chrome-devtools`, `cloakbrowser`.
- Repository documentation lookup: `deepwiki`.
- PDF-specific local tools: scripts under `skills/pdfs/scripts/` and JS helpers under `skills/pdfs/js/`.

## Tool Mapping

| ChatGPT platform tool | Local replacement | Status | Notes |
| --- | --- | --- | --- |
| `/home/oai/skills/pdfs` | `./skills/pdfs` | Implemented | Local package root for docs, scripts, examples, and helpers. |
| `/mnt/data` | `./outputs` or `./data` | Manual convention | Use `outputs/` for generated deliverables and `data/` for inputs. Create these folders per project when needed. |
| `sandbox:/mnt/data/<file>` | Local file path or future registry-backed download link | Partial | OpenCode can write/read files, and registered outputs now have stable artifact IDs. There is still no built-in ChatGPT-style sandbox URL renderer in this package. |
| `file_search.msearch/mclick` | Direct local file access with `glob`, `grep`, `read`, `fast-context`, YCE, and PDF/DOCX scripts | Available for local files | For this local computer setup, read files directly by path. Add a separate upload/source index only if ChatGPT-style source IDs, chunks, or cross-file semantic retrieval are explicitly needed. |
| ChatGPT upload indexing | Optional source/chunk indexing layer | Optional future enhancement | Not required for normal local use. Prefer direct file paths, `pdf_extract.py`, `render_pdf.py`, and model reading of rendered pages. |
| `web.run.search_query` | `grok-search_web_search`, `tavily_search`, `smart_search_search` | Available | Use for current or external web research. Results and citation behavior are not identical to ChatGPT UI citations. |
| `web.run.open` / fetch | `webfetch`, `grok-search_web_fetch`, `smart_search_fetch`, Tavily extract | Available | Use fetch tools for static pages; use browser tools for JS-heavy pages. |
| `web.run.screenshot` | `chrome-devtools_take_screenshot`, `cloakbrowser_screenshot`, `render_pdf.py` | Available | For web pages use browser screenshots. For PDFs use `render_pdf.py` or browser PDF rendering. |
| `python_user_visible` | `bash` running Python scripts | Partial | Local execution can generate artifacts, but it is not an isolated, UI-backed Code Interpreter notebook. |
| `artifact_tool` | `artifact_registry.py` over `outputs/artifacts/registry.jsonl` | Implemented local registry with gaps | Register existing files under `outputs/` with stable IDs, repo-relative paths, hashes, size, producer notes, timestamps, and optional preview metadata. Hosted preview UI, download links, and `sandbox:/mnt/data/...` URLs remain future adapters. |
| Spreadsheet helper environment | Python packages such as `openpyxl` if installed | Partial | `implementation-plan.md` lists baseline package install commands. Do not assume optional packages exist until verified. |

## PDF Workflow Replacements

### Reading and Reviewing PDFs

Use the PDF skill's render-first loop:

```powershell
python .\skills\pdfs\scripts\render_pdf.py .\data\input.pdf --out_dir .\outputs\renders\input --dpi 200
python .\skills\pdfs\scripts\pdf_inspect.py .\data\input.pdf --json .\outputs\input.inspect.json
```

If the PDF was provided as an upload outside the workspace, first copy or stage it under `data/uploads/`.

### Local File Reading and Search

For files already on this computer, do not simulate ChatGPT uploads by default. Use the local path directly:

1. Keep source files where they are, or copy them under `data/` when a task needs a stable project-local input path.
2. Use `read`, `grep`, `glob`, YCE, or `fast-context` for text/code files.
3. For digital PDFs, extract text or layout with `pdf_extract.py` and inspect metadata with `pdf_inspect.py`.
4. For scanned or low-text PDFs, render pages with `render_pdf.py` and ask the multimodal model to read or summarize the page image. Local OCR dependencies are not required by default.
5. Write generated deliverables under `outputs/` and register final artifacts with `artifact_registry.py` when durable metadata is useful.

A separate `data/uploads/` source registry or chunk index is optional. Add it only if a future task needs ChatGPT-style `source_id`, `chunk_id`, cross-file semantic retrieval, or citation rendering over many local documents.

### Web Screenshots and PDF Renders

Use browser MCP screenshots for web content and PDF render scripts for PDFs:

```powershell
python .\skills\pdfs\scripts\render_pdf.py .\data\input.pdf --out_dir .\outputs\renders\input --dpi 200
```

For web pages, prefer `chrome-devtools` when a normal browser is sufficient and `cloakbrowser` only when a site requires stealth browser behavior.

### Visible Python Outputs

Use local Python commands and explicit output paths:

```powershell
python .\skills\pdfs\scripts\pdf_extract.py text .\data\input.pdf --out .\outputs\input.txt
```

Then refer to `outputs/input.txt` instead of a `sandbox:/mnt/data/...` URL.

### Artifact Registry for Generated Outputs

Use `artifact_registry.py` to record generated deliverables under `outputs/` without moving or copying them:

```powershell
python .\skills\pdfs\scripts\artifact_registry.py register .\outputs\final.pdf --type application/pdf --description "Final PDF" --producer "pdf_edit.py merge"
python .\skills\pdfs\scripts\artifact_registry.py list
python .\skills\pdfs\scripts\artifact_registry.py show <artifact_id>
```

The registry stores JSONL rows at `outputs/artifacts/registry.jsonl`. Each row records a stable artifact ID, repo-relative path, type, description, SHA-256 hash, size, producer note, UTC timestamp, and optional preview path or note. It accepts only existing files under `outputs/`, and paths are stored as repo-relative POSIX-style paths so local machine-specific absolute paths are not written into metadata.

Default IDs are deterministic: sanitized file stem plus the first 12 characters of the file SHA-256. Re-registering the same path, content, and metadata returns the existing row instead of appending a duplicate. Reusing an artifact ID or the same path/content with different metadata is rejected because update/alias behavior is not part of the first version.

This is a local registry, not a download service. A future `sandbox:/mnt/data/...` adapter can map registry IDs to links if the host UI needs clickable downloads.

## Recommended Platform-Layer Additions

If this package needs to behave more like ChatGPT, implement these separately from the PDF scripts:

- Artifact registry: implemented as `skills/pdfs/scripts/artifact_registry.py`, mapping logical artifact IDs to files under `outputs/`.
- Direct local file workflow: default path for this OpenCode setup; use existing filesystem/search tools and PDF/DOCX scripts instead of recreating upload semantics.
- Download server or `sandbox:/mnt/data/...` adapter: expose selected registered `outputs/` files through local links if the host UI needs links.
- Optional source/chunk index: only if direct file access is not enough and ChatGPT-style uploaded-document retrieval is explicitly required.
- Optional citation renderer: format local source references consistently, for example `data/example.pdf#page=3`, if citation UI becomes a goal.
- Isolated Python runtime: run PDF scripts in a venv, container, or sandbox if untrusted PDFs are expected.

## Practical Rule

For PDF work in OpenCode, treat ChatGPT platform services as adapters around the local PDF workbench:

- The PDF scripts do rendering, extraction, editing, optional local OCR, redaction, conversion, and verification. Default scanned-page handling can use rendered images plus the multimodal model instead of installing OCR engines.
- OpenCode tools do direct local file access, command execution, web research, and browser screenshots.
- Missing platform adapters are optional for normal local use. They mainly matter only if you want ChatGPT-style upload source IDs, `sandbox:/mnt/data/...` download links, or citation UI behavior. The local artifact registry covers durable metadata for generated `outputs/` files.
