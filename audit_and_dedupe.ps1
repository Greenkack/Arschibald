param(
  [string]$Root = ".",
  [int]$MinSimilarityLines = 8,
  [switch]$OpenReports
)

$ErrorActionPreference = "Stop"
$reportDir = Join-Path $Root "reports"
$newline = [Environment]::NewLine
if (!(Test-Path $reportDir)) { New-Item -Type Directory -Path $reportDir | Out-Null }

function Step($a,$b,$c){ Write-Progress -Activity $a -Status $b -PercentComplete $c }

try {
  Step "Umgebung" "Python prüfen / venv anlegen" 5
  if (!(Test-Path (Join-Path $Root ".venv"))) {
    python -m venv (Join-Path $Root ".venv")
  }
  $py = Join-Path $Root ".venv/Scripts/python.exe"
  & $py -m pip install --upgrade pip > $null

  Step "Abhängigkeiten" "Lint/Fix Tools installieren" 10
  & $py -m pip install -q ruff autopep8 pylint vulture > $null

  Step "Auto-Fix" "Ruff: schnelle sichere Fixes" 25
  & $py -m ruff check $Root --fix --exit-zero | Tee-Object (Join-Path $reportDir "ruff.txt") | Out-Null

  Step "Auto-Fix" "Autopep8: konservativ formatieren" 35
  & $py -m autopep8 -r $Root --in-place --aggressive --aggressive --exclude .venv,node_modules,build,dist > $null

  Step "Analyse" "Pylint: Duplikate suchen" 55
  $pylintFile = Join-Path $reportDir "pylint-duplicates.txt"
  & $py -m pylint `
      --enable=duplicate-code `
      --min-similarity-lines=$MinSimilarityLines `
      --recursive=y $Root 1> $pylintFile 2>&1

  Step "Analyse" "Vulture: toter Code" 65
  $vultureFile = Join-Path $reportDir "vulture-deadcode.txt"
  & $py -m vulture $Root --min-confidence 70 1> $vultureFile 2>&1

  Step "Aufbereitung" "Refactor-TODO generieren" 80
  $todo = Join-Path $reportDir "REFactor_TODO.md"
  $dup = Get-Content $pylintFile
  $dead = Get-Content $vultureFile

  $dupBlocks = @()
  $current = @()
  foreach($line in $dup){
    if ($line -match "R0801: Similar lines in"){
      if ($current.Count){ $dupBlocks += ,@($current); $current = @() }
      $current += $line
    } elseif ($line -match "== "){
      $current += $line
    }
  }
  if ($current.Count){ $dupBlocks += ,@($current) }

  $todoLines = @()
  $todoLines += "# Refactor TODO"
  $todoLines += ""
  $todoLines += "## Duplizierter Code (Pylint R0801, min-similarity-lines=$MinSimilarityLines)"
  if ($dupBlocks.Count -eq 0) {
    $todoLines += "- Keine Duplikate gefunden."
  } else {
    $i = 1
    foreach($b in $dupBlocks){
      $todoLines += ""
      $todoLines += "### Block $i"
      foreach($l in $b){ $todoLines += "- $l" }
      $todoLines += "Empfehlung: Gemeinsame Funktion/Utility extrahieren und beide Stellen darauf umstellen."
      $i++
    }
  }
  $todoLines += ""
  $todoLines += "## Toter/ungenutzter Code (Vulture >=70% Vertrauen)"
  if ($dead.Count -eq 0) {
    $todoLines += "- Kein toter Code gefunden."
  } else {
    foreach($l in $dead){ $todoLines += "- $l" }
    $todoLines += "Empfehlung: Unbenutzte Funktionen/Variablen entfernen oder testbar machen."
  }
  $todoLines | Set-Content -Encoding UTF8 $todo

  Step "Fertig" "Berichte geschrieben" 95

  if ($OpenReports) {
    Start-Process $pylintFile
    Start-Process $vultureFile
    Start-Process (Join-Path $reportDir "ruff.txt")
    Start-Process $todo
  }

  Step "Fertig" "OK" 100
  Write-Host "Berichte in: $reportDir"
  Write-Host " - ruff.txt           (Auto-Fixes und Funde)"
  Write-Host " - pylint-duplicates.txt"
  Write-Host " - vulture-deadcode.txt"
  Write-Host " - REFactor_TODO.md    (konkrete Refaktor-Aufgaben)"
}
catch {
  Step "Fehler" $_.Exception.Message 100
  Write-Error $_.Exception.Message
  Write-Host "Logs unter $reportDir prüfen."
  exit 1
}
