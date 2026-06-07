param(
    [string]$StackRoot = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Failures = New-Object System.Collections.Generic.List[string]
$ActivateScript = Join-Path $PSScriptRoot "activate.ps1"

if ([string]::IsNullOrWhiteSpace($StackRoot)) {
    . $ActivateScript -Quiet
}
else {
    . $ActivateScript -StackRoot $StackRoot -Quiet
}

$RepoRoot = $env:VELLUM_REPO_ROOT
$Python = $env:VELLUM_PYTHON

function Add-Pass {
    param(
        [string]$Name,
        [string]$Detail
    )
    if ([string]::IsNullOrWhiteSpace($Detail)) {
        $Detail = "ok"
    }
    Write-Output "[PASS] $Name - $Detail"
}

function Add-Fail {
    param(
        [string]$Name,
        [string]$Detail
    )
    if ([string]::IsNullOrWhiteSpace($Detail)) {
        $Detail = "failed"
    }
    Write-Output "[FAIL] $Name - $Detail"
    $script:Failures.Add($Name) | Out-Null
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [string]$WorkingDirectory = ""
    )

    if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
        Push-Location -LiteralPath $WorkingDirectory
    }

    try {
        $Output = & $FilePath @Arguments 2>&1
        $ExitCode = $LASTEXITCODE
        if ($ExitCode -ne 0) {
            throw "Command failed with exit code ${ExitCode}: $FilePath $($Arguments -join ' ') $($Output -join ' ')"
        }
        return (($Output | ForEach-Object { $_.ToString() }) -join " ").Trim()
    }
    finally {
        if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
            Pop-Location
        }
    }
}

function Invoke-Check {
    param(
        [string]$Name,
        [scriptblock]$Script
    )

    try {
        $Result = & $Script
        $Detail = (($Result | Where-Object { -not [string]::IsNullOrWhiteSpace($_.ToString()) } | Select-Object -First 1) -join " ").Trim()
        Add-Pass -Name $Name -Detail $Detail
    }
    catch {
        Add-Fail -Name $Name -Detail $_.Exception.Message
    }
}

Invoke-Check "repository root" {
    if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
        throw "not found: $RepoRoot"
    }
    $RepoRoot
}

Invoke-Check "selected Python" {
    if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
        throw "not found: $Python"
    }
    "$Python ($env:VELLUM_PYTHON_SOURCE)"
}

$RequiredRepoFiles = @(
    "requirements.txt",
    "skills\pdfs\scripts\html_to_pdf.py",
    "skills\pdfs\scripts\render_pdf.py",
    "skills\pdfs\scripts\create_montage.py",
    "skills\pdfs\scripts\artifact_registry.py",
    "skills\pdfs\js\package.json",
    "skills\pdfs\js\package-lock.json"
)

foreach ($RelativePath in $RequiredRepoFiles) {
    Invoke-Check "repo file $RelativePath" {
        $Path = Join-Path $RepoRoot $RelativePath
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            throw "missing: $Path"
        }
        $Path
    }
}

$RequiredCommands = @(
    "xelatex",
    "latexmk",
    "pandoc",
    "pdfinfo",
    "pdftoppm",
    "gswin64c",
    "soffice",
    "qpdf",
    "node",
    "npm"
)

foreach ($CommandName in $RequiredCommands) {
    Invoke-Check "command $CommandName" {
        (Get-Command $CommandName -ErrorAction Stop).Source
    }
}

Invoke-Check "Playwright browser cache" {
    $BrowserPath = [Environment]::GetEnvironmentVariable("PLAYWRIGHT_BROWSERS_PATH")
    if ([string]::IsNullOrWhiteSpace($BrowserPath)) {
        throw "PLAYWRIGHT_BROWSERS_PATH is not set"
    }
    if (-not (Test-Path -LiteralPath $BrowserPath -PathType Container)) {
        throw "not found: $BrowserPath"
    }
    $BrowserPath
}

$ImportMap = @{
    "PyMuPDF" = "fitz"
    "Pillow" = "PIL"
    "beautifulsoup4" = "bs4"
    "Jinja2" = "jinja2"
    "lxml" = "lxml"
    "markdown" = "markdown"
    "openpyxl" = "openpyxl"
    "pdf2image" = "pdf2image"
    "pdfplumber" = "pdfplumber"
    "playwright" = "playwright"
    "pypdf" = "pypdf"
    "pypdfium2" = "pypdfium2"
    "python-docx" = "docx"
    "reportlab" = "reportlab"
}

$RequirementPath = Join-Path $RepoRoot "requirements.txt"
$Requirements = Get-Content -LiteralPath $RequirementPath |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") }

foreach ($Requirement in $Requirements) {
    $RequirementName = ($Requirement -split "[<>=!~ ]", 2)[0]
    $ModuleName = $ImportMap[$RequirementName]
    if ([string]::IsNullOrWhiteSpace($ModuleName)) {
        $ModuleName = $RequirementName.Replace("-", "_")
    }

    Invoke-Check "python package $RequirementName" {
        $Code = "import importlib; importlib.import_module('$ModuleName'); print('$ModuleName')"
        Invoke-Native -FilePath $Python -Arguments @("-c", $Code)
    }
}

$ParseCode = 'import ast, os; from pathlib import Path; root=Path(os.environ["VELLUM_REPO_ROOT"]); files=sorted((root/"skills"/"pdfs"/"scripts").glob("*.py")); [ast.parse(p.read_text(encoding="utf-8"), filename=str(p)) for p in files]; print(f"parsed={len(files)}")'
Invoke-Check "PDF script syntax" {
    Invoke-Native -FilePath $Python -Arguments @("-c", $ParseCode)
}

$JsDir = Join-Path $RepoRoot "skills\pdfs\js"
Invoke-Check "JS dependency tree" {
    Invoke-Native -FilePath "npm" -Arguments @("list", "--depth=0") -WorkingDirectory $JsDir
}

foreach ($ScriptName in @("fill_form.mjs", "extract_form_fields.mjs", "extract_text_pdfjs.mjs")) {
    Invoke-Check "JS syntax $ScriptName" {
        Invoke-Native -FilePath "node" -Arguments @("--check", (Join-Path $JsDir $ScriptName))
    }
}

if ($Failures.Count -gt 0) {
    Write-Output ""
    Write-Output "FAIL: Vellum repository PDF workflow doctor found $($Failures.Count) issue(s)."
    exit 1
}

Write-Output ""
Write-Output "PASS: external stack satisfies the Vellum repository PDF workflow contract."
