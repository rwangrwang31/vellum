# Agent Instructions

This repository is the workflow source of truth for local Vellum PDF/DOCX work.

## Hard Entry Rule

For any work involving PDFs, LaTeX, XeLaTeX, TikZ, PDF generation, PDF QA,
`pdf-production-stack`, `render_pdf`, focused crops, artifact registration, or
diagram/formula-heavy output, do not start by scanning directories, enumerating
`skills/`, searching for `.tex` files, or running broad searches such as
`rg latex`.

Start from the repository root and read these files first:

```text
PDF_PRODUCTION_WORKFLOW.md
QUICKSTART.md
```

Only after reading those entry docs should you inspect implementation files,
use targeted search, or choose scripts under `skills/pdfs/`.

## Required Operating Order

From the repository root:

```powershell
. .\scripts\activate.ps1
pwsh -ExecutionPolicy Bypass -File .\scripts\doctor.ps1
```

Run the smoke test before debugging or changing workflow entrypoints:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\smoke.ps1
```

## Source Boundary

The Vellum repository owns the workflow. The external stack is only a tool
provider:

```text
<external-stack-root>
```

Do not debug or tune workflow behavior from the external stack unless the
repository workflow explicitly points there for tool availability.

## Final PDF Gate

Compile or conversion success is not enough. Final PDFs must be rendered back
to pages, inspected with a contact sheet, and checked with focused crops when
the document has dense diagrams, formulas, tables, generated images, or
late-changed layout-sensitive pages. Register final artifacts only after QA
evidence exists under `outputs/<task>/`.
