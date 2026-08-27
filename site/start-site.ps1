[CmdletBinding()]
param(
    [switch]$NoBrowser,
    [ValidateRange(1, 65535)]
    [int]$Port = 8080
)

$ErrorActionPreference = "Stop"
$siteUrl = "http://127.0.0.1:$Port/"
$healthUrl = "http://127.0.0.1:$Port/health"
$buildScript = Join-Path $PSScriptRoot "scripts\build.mjs"
$previewScript = Join-Path $PSScriptRoot "scripts\serve.mjs"
$runtimeLogsDir = Join-Path $PSScriptRoot ".tmp\logs"
New-Item -ItemType Directory -Path $runtimeLogsDir -Force | Out-Null

function Test-SiteReachable {
    try {
        $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 1
        $payload = $response.Content | ConvertFrom-Json
        return $response.StatusCode -eq 200 -and $payload.service -eq "syzygy-site-preview"
    }
    catch {
        return $false
    }
}

function Open-Site {
    if (-not $NoBrowser) {
        Start-Process $siteUrl
    }
}

if (Test-SiteReachable) {
    Write-Host "SYZYGY site is already running at $siteUrl"
    Open-Site
    exit 0
}

$nodeCommand = Get-Command "node" -ErrorAction SilentlyContinue
if (-not $nodeCommand) {
    throw "Node.js 22 or newer was not found. Install Node.js or run the static files with another local HTTP server."
}

$nodeVersion = (& $nodeCommand.Source --version).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Node.js could not be executed."
}

$stdoutLog = Join-Path $runtimeLogsDir "site-preview.stdout.log"
$stderrLog = Join-Path $runtimeLogsDir "site-preview.stderr.log"
$quotedPreviewScript = '"' + $previewScript + '"'
& $nodeCommand.Source $buildScript
if ($LASTEXITCODE -ne 0) {
    throw "The static site build failed."
}
Write-Host "Starting the dependency-free SYZYGY site with Node.js $nodeVersion"
$process = Start-Process -FilePath $nodeCommand.Source `
    -ArgumentList @($quotedPreviewScript, "--port", "$Port") `
    -WorkingDirectory $PSScriptRoot -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog -WindowStyle Hidden -PassThru

for ($attempt = 0; $attempt -lt 40; $attempt++) {
    if (Test-SiteReachable) {
        Write-Host "SYZYGY site is ready at $siteUrl (PID $($process.Id))"
        Open-Site
        exit 0
    }
    if ($process.HasExited) {
        break
    }
    Start-Sleep -Milliseconds 250
}

throw "Site did not become ready. Review $stdoutLog and $stderrLog."
