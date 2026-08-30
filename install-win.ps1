$ErrorActionPreference = "Stop"

$Repo = "SmileLulz/smytm"
$ApiUrl = "https://api.github.com/repos/$Repo/releases/latest"

function Write-ErrorMessage {
    param([string]$Message)

    Write-Host "Error: $Message" -ForegroundColor Red
}

function Write-Success {
    param([string]$Message)

    Write-Host $Message -ForegroundColor Green
}

function Write-WarningMessage {
    param([string]$Message)

    Write-Host $Message -ForegroundColor Yellow
}

function Install-WingetPackage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Id
    )

    Write-Host "Checking $Id..."

    winget list `
        --id $Id `
        -e `
        --accept-source-agreements *> $null

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Already installed: $Id"
        return
    }

    Write-Host "Installing $Id..."

    winget install `
        --id $Id `
        -e `
        --accept-source-agreements `
        --accept-package-agreements

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install $Id with winget."
    }

    Write-Success "Installed: $Id"
}

Write-Host "smytm installer" -ForegroundColor Cyan
Write-Host


# Requirements

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-ErrorMessage "winget is required but was not found."
    exit 1
}

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-ErrorMessage "Python launcher 'py' is required but was not found."
    Write-Host
    Write-Host "Install Python from:"
    Write-Host "https://www.python.org/downloads/windows/"
    exit 1
}


# Install xternal dependencies

Write-Host "Installing/checking required command-line tools with winget..."
Write-Host

Install-WingetPackage "BtbN.FFmpeg.GPL"
Install-WingetPackage "hpjansson.Chafa"
Install-WingetPackage "wez.atomicparsley"

Write-Host


# Fetch latest release

Write-WarningMessage "Fetching latest smytm release information..."

$Headers = @{
    "Accept" = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2026-03-10"
}

$Release = Invoke-RestMethod `
    -Uri $ApiUrl `
    -Headers $Headers

$ReleaseTag = $Release.tag_name
$ReleaseName = $Release.name

if ([string]::IsNullOrWhiteSpace($ReleaseTag)) {
    throw "GitHub release did not contain a tag name."
}

Write-Host "Release: $ReleaseName"
Write-Host "Tag:     $ReleaseTag"
Write-Host


# Find wheel

$Wheels = @(
    $Release.assets | Where-Object {
        $_.name -match '^smytm-.+\.whl$'
    }
)

if ($Wheels.Count -eq 0) {
    throw "No smytm wheel was found in the latest GitHub release."
}

if ($Wheels.Count -gt 1) {
    $Names = ($Wheels | ForEach-Object { $_.name }) -join ", "
    throw "Multiple smytm wheels were found: $Names"
}

$Wheel = $Wheels[0]

$AssetName = $Wheel.name
$DownloadUrl = $Wheel.browser_download_url
$Digest = $Wheel.digest

Write-Host "Package: $AssetName"
Write-Host

if ([string]::IsNullOrWhiteSpace($Digest) -or
    -not $Digest.StartsWith("sha256:")) {
    throw "GitHub did not provide a SHA-256 digest for the selected wheel."
}

$ExpectedSha = $Digest.Substring(7)


# Download and verify wheel

$TempDir = Join-Path $env:TEMP ("smytm-" + [guid]::NewGuid().ToString())

New-Item `
    -ItemType Directory `
    -Path $TempDir `
    -Force `
    | Out-Null

try {
    $WheelPath = Join-Path $TempDir $AssetName

    Write-WarningMessage "Downloading package..."

    Invoke-WebRequest `
        -Uri $DownloadUrl `
        -OutFile $WheelPath

    $ActualSha = (
        Get-FileHash `
            -Path $WheelPath `
            -Algorithm SHA256
    ).Hash.ToLowerInvariant()

    if ($ActualSha -ne $ExpectedSha.ToLowerInvariant()) {
        Write-ErrorMessage "SHA-256 verification failed."
        Write-Host "Expected: $ExpectedSha"
        Write-Host "Actual:   $ActualSha"
        exit 1
    }

    Write-Success "SHA-256 verified."
    Write-Host

    # Install wheel

    Write-WarningMessage "Installing smytm..."

    & py -3 -m pip install `
        --upgrade `
        $WheelPath

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install smytm with pip."
    }

    Write-Host
    Write-Success "smytm $ReleaseTag installed successfully."
    Write-Host

    Write-Host "Run it with:"
    Write-Host "  smytm"

    Write-Host
    Write-WarningMessage "rsgain is not installed automatically."
    Write-Host
    Write-Host "rsgain is required for ReplayGain processing."
    Write-Host "Install it separately and make sure rsgain.exe is available on PATH."
    Write-Host
    Write-Host "See:"
    Write-Host "https://github.com/complexlogic/rsgain"
}
finally {
    if (Test-Path $TempDir) {
        Remove-Item `
            -Path $TempDir `
            -Recurse `
            -Force `
            -ErrorAction SilentlyContinue
    }
}
