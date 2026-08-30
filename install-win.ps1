$ErrorActionPreference = "Stop"

$Repo = "SmileLulz/smytm"
$ApiUrl = "https://api.github.com/repos/$Repo/releases/latest"

function Write-Info([string]$Message) {
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Success([string]$Message) {
    Write-Host $Message -ForegroundColor Green
}

function Write-WarningMessage([string]$Message) {
    Write-Host $Message -ForegroundColor Yellow
}

function Fail([string]$Message) {
    Write-Host "Error: $Message" -ForegroundColor Red
    exit 1
}

function Require-Command([string]$Command) {
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        Fail "Required command not found: $Command"
    }
}

Write-Host "smytm installer" -ForegroundColor Cyan
Write-Host ""

Require-Command "winget"
Require-Command "py"

Write-Info "Installing/updating required command-line tools with winget..."

$WingetPackages = @(
    "BtbN.FFmpeg.GPL",
    "hpjansson.Chafa",
    "wez.atomicparsley"
)

foreach ($Package in $WingetPackages) {
    Write-Host "Installing $Package..."
    winget install --id $Package --exact --source winget `
        --accept-source-agreements `
        --accept-package-agreements

    if ($LASTEXITCODE -ne 0) {
        Fail "Failed to install $Package with winget."
    }
}

Write-Success "✓ Required Windows tools installed."
Write-Host ""

Write-Info "Updating pip..."
py -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Fail "Failed to update pip."
}

Write-Info "Fetching latest smytm release..."

$Headers = @{
    "Accept" = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2026-03-10"
}

try {
    $Release = Invoke-RestMethod -Uri $ApiUrl -Headers $Headers
} catch {
    Fail "Unable to fetch the latest GitHub release: $($_.Exception.Message)"
}

$WheelAssets = @(
    $Release.assets | Where-Object {
        $_.name -match '^smytm-.+-py3-none-any\.whl$'
    }
)

if ($WheelAssets.Count -eq 0) {
    Fail "No py3-none-any wheel was found in release $($Release.tag_name)."
}

if ($WheelAssets.Count -gt 1) {
    Fail "Multiple matching wheels were found in release $($Release.tag_name)."
}

$Wheel = $WheelAssets[0]
$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("smytm-" + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $TempDir | Out-Null

try {
    $WheelPath = Join-Path $TempDir $Wheel.name

    Write-Info "Downloading $($Wheel.name)..."
    Invoke-WebRequest -Uri $Wheel.browser_download_url -OutFile $WheelPath

    if (-not $Wheel.digest -or -not $Wheel.digest.StartsWith("sha256:")) {
        Fail "GitHub did not provide a SHA-256 digest for the selected wheel."
    }

    $ExpectedHash = $Wheel.digest.Substring(7).ToLowerInvariant()
    $ActualHash = (Get-FileHash -Algorithm SHA256 -Path $WheelPath).Hash.ToLowerInvariant()

    if ($ActualHash -ne $ExpectedHash) {
        Fail "SHA-256 verification failed.`nExpected: $ExpectedHash`nActual:   $ActualHash"
    }

    Write-Success "✓ SHA-256 verified"
    Write-Host ""

    Write-Info "Installing smytm from the verified wheel..."
    py -m pip install $WheelPath

    if ($LASTEXITCODE -ne 0) {
        Fail "Failed to install smytm."
    }

    Write-Host ""
    Write-Success "✓ smytm $($Release.tag_name) installed successfully."
    Write-Host ""
    Write-Host "Restart your terminal before using the newly installed commands."
    Write-Host ""
    Write-WarningMessage "rsgain is optional and is required only for ReplayGain 2.0 tagging."
    Write-WarningMessage "    Install it manually from:"
    Write-WarningMessage "    https://github.com/complexlogic/rsgain/releases"
    Write-WarningMessage "    Extract rsgain.exe and add its directory to PATH."
    Write-Host ""
    Write-Host "Run it with:"
    Write-Host "  smytm"
}
finally {
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
}
