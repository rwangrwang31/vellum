param(
    [string]$StackRoot = "",
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($StackRoot)) {
    if (-not [string]::IsNullOrWhiteSpace($env:PDF_PRODUCTION_STACK)) {
        $StackRoot = $env:PDF_PRODUCTION_STACK
    }
    else {
        $StackRoot = "D:\pdf-production-stack"
    }
}

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
if (-not (Test-Path -LiteralPath $StackRoot -PathType Container)) {
    throw "External PDF stack root not found: $StackRoot"
}

$ResolvedStackRoot = (Resolve-Path -LiteralPath $StackRoot).Path
$StackActivate = Join-Path $ResolvedStackRoot "activate.ps1"
if (-not (Test-Path -LiteralPath $StackActivate -PathType Leaf)) {
    throw "External PDF stack activation script not found: $StackActivate"
}

if ($Quiet) {
    . $StackActivate *> $null
}
else {
    . $StackActivate
}

$RepoPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$StackPython = Join-Path $ResolvedStackRoot "python-venv\Scripts\python.exe"

if (Test-Path -LiteralPath $RepoPython -PathType Leaf) {
    $SelectedPython = (Resolve-Path -LiteralPath $RepoPython).Path
    $PythonSource = "repository .venv"
}
elseif (Test-Path -LiteralPath $StackPython -PathType Leaf) {
    $SelectedPython = (Resolve-Path -LiteralPath $StackPython).Path
    $PythonSource = "external stack python-venv"
}
else {
    $PythonCommand = Get-Command python -ErrorAction Stop
    $SelectedPython = $PythonCommand.Source
    $PythonSource = "PATH"
}

$PythonScriptsDir = Split-Path -Parent $SelectedPython
if (-not [string]::IsNullOrWhiteSpace($PythonScriptsDir)) {
    $env:Path = "$PythonScriptsDir;$env:Path"
}

$PipCandidate = Join-Path $PythonScriptsDir "pip.exe"
Set-Alias -Name python-vellum -Value $SelectedPython -Scope Global
if (Test-Path -LiteralPath $PipCandidate -PathType Leaf) {
    Set-Alias -Name pip-vellum -Value $PipCandidate -Scope Global
}

$env:VELLUM_REPO_ROOT = $RepoRoot
$env:VELLUM_EXTERNAL_STACK_ROOT = $ResolvedStackRoot
$env:VELLUM_PYTHON = $SelectedPython
$env:VELLUM_PYTHON_SOURCE = $PythonSource
$env:VELLUM_PDF_WORKFLOW_ACTIVE = "1"

if (-not $Quiet) {
    Write-Output "Vellum repository PDF workflow activated."
    Write-Output "VELLUM_REPO_ROOT=$env:VELLUM_REPO_ROOT"
    Write-Output "VELLUM_EXTERNAL_STACK_ROOT=$env:VELLUM_EXTERNAL_STACK_ROOT"
    Write-Output "VELLUM_PYTHON=$env:VELLUM_PYTHON"
    Write-Output "VELLUM_PYTHON_SOURCE=$env:VELLUM_PYTHON_SOURCE"
    Write-Output "outputs=$(Join-Path $RepoRoot 'outputs')"
}
