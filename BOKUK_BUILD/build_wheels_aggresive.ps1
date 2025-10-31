<#
build_wheels_aggressive.ps1
Aggressive wheel builder (best-effort). Läuft auf einem Build-PC mit Internet.
Benutzen: Set-ExecutionPolicy -Scope Process Bypass
        .\build_wheels_aggressive.ps1 -PythonExe "C:\Path\to\python.exe"

WICHTIG: Verwende die gleiche Python-Version wie das Embeddable-Python, das du später einsetzen willst.
#>

param(
  [Parameter(Mandatory=$true)][string]$PythonExe,
  [string]$ReqFile = ".\app\requirements.txt",
  [string]$WheelDir = ".\wheelhouse",
  [switch]$ForceRebuild,
  [int]$TimeoutSecondsPerBuild = 900
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Log([string]$m){
    $t = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$t  $m" | Tee-Object -FilePath ".\build_wheels_aggressive.log" -Append
}

function Run-ProcessCapture($exe, $args, $workdir=$PWD, [int]$timeoutSec = 0) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $exe
    $psi.Arguments = $args
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.WorkingDirectory = $workdir
    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    $proc.Start() | Out-Null

    $stdout = $proc.StandardOutput
    $stderr = $proc.StandardError

    $outBuilder = New-Object System.Text.StringBuilder
    $errBuilder = New-Object System.Text.StringBuilder

    # read asynchronously
    while (-not $proc.HasExited) {
        Start-Sleep -Milliseconds 200
        while (-not $stdout.EndOfStream) { $line = $stdout.ReadLine(); $outBuilder.AppendLine($line) | Out-Null; Log("OUT: $line") }
        while (-not $stderr.EndOfStream) { $line = $stderr.ReadLine(); $errBuilder.AppendLine($line) | Out-Null; Log("ERR: $line") }
        if ($timeoutSec -gt 0) {
            $timeoutSec -= 0.2
            if ($timeoutSec -le 0) {
                try { $proc.Kill() } catch {}
                throw "Timeout"
            }
        }
    }
    # drain any remaining
    while (-not $stdout.EndOfStream) { $line = $stdout.ReadLine(); $outBuilder.AppendLine($line) | Out-Null; Log("OUT: $line") }
    while (-not $stderr.EndOfStream) { $line = $stderr.ReadLine(); $errBuilder.AppendLine($line) | Out-Null; Log("ERR: $line") }

    return @{ ExitCode = $proc.ExitCode; Stdout = $outBuilder.ToString(); Stderr = $errBuilder.ToString() }
}

# --- Start ---
Log "=== aggressive build start ($(Get-Date)) ==="

if (-not (Test-Path $PythonExe)) { throw "PythonExe nicht gefunden: $PythonExe" }
if (-not (Test-Path $ReqFile)) { throw "requirements.txt nicht gefunden: $ReqFile" }
if (Test-Path $WheelDir -and $ForceRebuild) { Remove-Item -LiteralPath $WheelDir -Recurse -Force -ErrorAction SilentlyContinue }
if (-not (Test-Path $WheelDir)) { New-Item -ItemType Directory -Path $WheelDir | Out-Null }

# create isolated venv
$venv = Join-Path $PSScriptRoot "venv_build"
if (Test-Path $venv -and $ForceRebuild) { Remove-Item -LiteralPath $venv -Recurse -Force -ErrorAction SilentlyContinue }
if (-not (Test-Path $venv)) {
    Log "Create venv $venv using $PythonExe"
    & $PythonExe -m venv $venv
}

$py = Join-Path $venv "Scripts\python.exe"
$pip = Join-Path $venv "Scripts\pip.exe"

Log "Upgrade pip/setuptools/wheel/build tooling in venv"
& $py -m pip install -U pip setuptools wheel build packaging pyproject_hooks pip-tools 2>&1 | ForEach-Object { Log $_ }

# 1) Try pip wheel for everything (binary wheels)
Log "Phase 1: pip wheel -r $ReqFile -w $WheelDir"
$res = Run-ProcessCapture $py "-m pip wheel -r `"$ReqFile`" -w `"$WheelDir`"" $PSScriptRoot $TimeoutSecondsPerBuild
if ($res.ExitCode -ne 0) { Log "pip wheel returned $($res.ExitCode). Continuing to aggressive sdists processing." } else { Log "pip wheel finished OK." }

# 2) download all sdists (no-binary)
$sdistsDir = Join-Path $PSScriptRoot "_sdists"
if (Test-Path $sdistsDir -and $ForceRebuild) { Remove-Item -LiteralPath $sdistsDir -Recurse -Force -ErrorAction SilentlyContinue }
if (-not (Test-Path $sdistsDir)) { New-Item -ItemType Directory -Path $sdistsDir | Out-Null }

Log "Phase 2: pip download --no-binary=:all:"
Run-ProcessCapture $py "-m pip download -r `"$ReqFile`" --no-binary=:all: -d `"$sdistsDir`"" $PSScriptRoot 1800

# 3) For each sdist try several strategies
$failed = Join-Path $PSScriptRoot "_failed_sdists"
if (Test-Path $failed -and $ForceRebuild) { Remove-Item -LiteralPath $failed -Recurse -Force -ErrorAction SilentlyContinue }
if (-not (Test-Path $failed)) { New-Item -ItemType Directory -Path $failed | Out-Null }

$sdists = Get-ChildItem -Path $sdistsDir -File -Include *.tar.gz,*.zip -ErrorAction SilentlyContinue
Log ("Found {0} sdists" -f $sdists.Count)

foreach ($s in $sdists) {
    $name = $s.Name
    Log "=== PROCESS SDIST: $name ==="

    # create tmp dir
    $tmp = Join-Path $PSScriptRoot ("_build_tmp\" + [IO.Path]::GetFileNameWithoutExtension($name))
    if (Test-Path $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Path $tmp | Out-Null

    # extract sdist (zip or tar.gz)
    try {
        if ($s.Extension -eq ".zip") {
            Expand-Archive -LiteralPath $s.FullName -DestinationPath $tmp -Force
        } else {
            # tar.gz -> use tar
            try {
                & tar -xzf $s.FullName -C $tmp 2>&1 | ForEach-Object { Log $_ }
            } catch {
                # fallback to Expand-Archive if available (rare)
                Expand-Archive -LiteralPath $s.FullName -DestinationPath $tmp -Force
            }
        }
    } catch {
        Log "ERROR extracting $name : $($_.Exception.Message)"
    }

    # find top-level project dir (where setup.py or pyproject.toml likely is)
    $projDirs = Get-ChildItem -Path $tmp -Directory | Select-Object -First 1
    if ($projDirs) { $projRoot = $projDirs.FullName } else { $projRoot = $tmp }

    $built = $false

    # Strategy A: python -m build (PEP517) normal
    try {
        Log "Strategy A: python -m build --wheel"
        Push-Location $projRoot
        $r = Run-ProcessCapture $py "-m build --wheel --outdir `"$WheelDir`"" $projRoot $TimeoutSecondsPerBuild
        Pop-Location
        if ($r.ExitCode -eq 0) { Log "Built wheel via build: $name"; $built = $true }
    } catch {
        Log "Strategy A failed: $($_.Exception.Message)"
        Pop-Location -ErrorAction SilentlyContinue
    }
    if ($built) { continue }

    # Strategy B: try build with no isolation (use installed build tools from venv)
    try {
        Log "Strategy B: python -m build --no-isolation"
        Push-Location $projRoot
        $r = Run-ProcessCapture $py "-m build --wheel --no-isolation --outdir `"$WheelDir`"" $projRoot $TimeoutSecondsPerBuild
        Pop-Location
        if ($r.ExitCode -eq 0) { Log "Built wheel via build --no-isolation: $name"; $built = $true }
    } catch {
        Log "Strategy B failed: $($_.Exception.Message)"
        Pop-Location -ErrorAction SilentlyContinue
    }
    if ($built) { continue }

    # Strategy C: legacy setup.py bdist_wheel if setup.py exists
    $setupPath = Join-Path $projRoot "setup.py"
    if (Test-Path $setupPath) {
        try {
            Log "Strategy C: python setup.py bdist_wheel (legacy)"
            Push-Location $projRoot
            $r = Run-ProcessCapture $py "`"$setupPath`" bdist_wheel --dist-dir `"$WheelDir`"" $projRoot $TimeoutSecondsPerBuild
            Pop-Location
            if ($r.ExitCode -eq 0) { Log "Built wheel via setup.py bdist_wheel: $name"; $built = $true }
        } catch {
            Log "Strategy C failed: $($_.Exception.Message)"
            Pop-Location -ErrorAction SilentlyContinue
        }
    } else {
        Log "No setup.py found for legacy build."
    }
    if ($built) { continue }

    # Strategy D: use pip wheel on the sdist file directly (in a temp venv)
    try {
        Log "Strategy D: pip wheel on sdist path (temp venv)"
        $tmpvenv = Join-Path $PSScriptRoot ("venv_tmp_" + [IO.Path]::GetFileNameWithoutExtension($name))
        if (Test-Path $tmpvenv) { Remove-Item -LiteralPath $tmpvenv -Recurse -Force -ErrorAction SilentlyContinue }
        & $PythonExe -m venv $tmpvenv
        $tmpPy = Join-Path $tmpvenv "Scripts\python.exe"
        & $tmpPy -m pip install -U pip setuptools wheel build 2>&1 | ForEach-Object { Log $_ }
        $r = Run-ProcessCapture $tmpPy "-m pip wheel `"$($s.FullName)`" -w `"$WheelDir`"" $PSScriptRoot $TimeoutSecondsPerBuild
        if ($r.ExitCode -eq 0) { Log "Built wheel via pip wheel on sdist: $name"; $built = $true }
        Remove-Item -LiteralPath $tmpvenv -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        Log "Strategy D failed: $($_.Exception.Message)"
        Remove-Item -LiteralPath $tmpvenv -Recurse -Force -ErrorAction SilentlyContinue
    }
    if ($built) { continue }

    # Strategy E: attempt to pip install (maybe binary wheel gets cached) then pip wheel from cache
    try {
        Log "Strategy E: pip install sdist into venv (best-effort)"
        $tmpvenv2 = Join-Path $PSScriptRoot ("venv_tmp2_" + [IO.Path]::GetFileNameWithoutExtension($name))
        if (Test-Path $tmpvenv2) { Remove-Item -LiteralPath $tmpvenv2 -Recurse -Force -ErrorAction SilentlyContinue }
        & $PythonExe -m venv $tmpvenv2
        $tmpPy2 = Join-Path $tmpvenv2 "Scripts\python.exe"
        & $tmpPy2 -m pip install -U pip setuptools wheel 2>&1 | ForEach-Object { Log $_ }
        $r1 = Run-ProcessCapture $tmpPy2 "-m pip install `"$($s.FullName)`"" $PSScriptRoot 300
        Log "pip install output: exit=$($r1.ExitCode)"
        # Now try to wheel the package (maybe cached or buildable)
        $r2 = Run-ProcessCapture $tmpPy2 "-m pip wheel `"$($s.FullName)`" -w `"$WheelDir`"" $PSScriptRoot $TimeoutSecondsPerBuild
        if ($r2.ExitCode -eq 0) { Log "Built wheel via pip install+wheel: $name"; $built = $true }
        Remove-Item -LiteralPath $tmpvenv2 -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        Log "Strategy E failed: $($_.Exception.Message)"
        Remove-Item -LiteralPath $tmpvenv2 -Recurse -Force -ErrorAction SilentlyContinue
    }
    if ($built) { continue }

    # All strategies failed -> mark as failed
    Log "ALL STRATEGIES FAILED for $name -> move to _failed_sdists"
    Move-Item -LiteralPath $s.FullName -Destination $failed -Force
}

# Final: list wheelhouse content
$wcount = (Get-ChildItem -Path $WheelDir -Filter *.whl -File -Recurse -ErrorAction SilentlyContinue).Count
Log "Finished. wheelhouse contains $wcount wheels."
Log "See build_wheels_aggressive.log for details. Failed sdists (if any) in _failed_sdists."
Log "=== aggressive build end ($(Get-Date)) ==="
