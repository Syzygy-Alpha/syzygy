[CmdletBinding()]
param(
    [switch]$NoBrowser,
    [ValidateRange(1, 65535)]
    [int]$Port = 8040
)

$ErrorActionPreference = "Stop"

$nervRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$workspaceRoot = (Resolve-Path (Join-Path $nervRoot "..")).Path
$dashboardUrl = "http://127.0.0.1:$Port/"
$healthUrl = "http://127.0.0.1:$Port/health"

function Test-NervReachable {
    try {
        $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 1
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function Open-NervDashboard {
    if (-not $NoBrowser) {
        Start-Process $dashboardUrl
    }
}

if (Test-NervReachable) {
    Write-Host "NERV is already running at $dashboardUrl"
    Open-NervDashboard
    exit 0
}

$venvPython = Join-Path $workspaceRoot ".venv\Scripts\python.exe"
if ($env:SYZYGY_NERV_PYTHON_EXECUTABLE) {
    $pythonExecutable = $env:SYZYGY_NERV_PYTHON_EXECUTABLE
}
elseif (Test-Path -LiteralPath $venvPython) {
    $pythonExecutable = $venvPython
}
else {
    $pythonExecutable = "python"
}

$runtimeLogsDir = Join-Path $nervRoot "data\runtime-logs"
New-Item -ItemType Directory -Path $runtimeLogsDir -Force | Out-Null
$stdoutLog = Join-Path $runtimeLogsDir "nerv-launcher.stdout.log"
$stderrLog = Join-Path $runtimeLogsDir "nerv-launcher.stderr.log"

Write-Host "Starting NERV with $pythonExecutable"
$startProcessArgs = @{
    FilePath               = $pythonExecutable
    ArgumentList           = @(
        "-m",
        "uvicorn",
        "syzygy_nerv.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "$Port"
    )
    WorkingDirectory       = $nervRoot
    RedirectStandardOutput = $stdoutLog
    RedirectStandardError  = $stderrLog
    WindowStyle            = "Hidden"
    PassThru               = $true
}
$process = Start-Process @startProcessArgs

for ($attempt = 0; $attempt -lt 60; $attempt++) {
    if (Test-NervReachable) {
        Write-Host "NERV is ready at $dashboardUrl (PID $($process.Id))"
        Open-NervDashboard
        exit 0
    }
    if ($process.HasExited) {
        break
    }
    Start-Sleep -Milliseconds 250
}

throw "NERV did not become ready. Review $stdoutLog and $stderrLog."
