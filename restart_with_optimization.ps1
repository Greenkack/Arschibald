# restart_with_optimization.ps1
# Automatischer Neustart von Streamlit mit Optimierungen

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "🚀 STREAMLIT NEUSTART MIT OPTIMIERUNGEN" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

# Schritt 1: Python Cache löschen
Write-Host "`n[1/4] 🧹 Lösche Python Cache..." -ForegroundColor Cyan
try {
    Get-ChildItem -Path . -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
    Write-Host "      ✅ Cache gelöscht" -ForegroundColor Green
} catch {
    Write-Host "      ⚠️  Cache konnte nicht vollständig gelöscht werden" -ForegroundColor Yellow
}

# Schritt 2: Import-Test
Write-Host "`n[2/4] 🔍 Teste optimierte Module..." -ForegroundColor Cyan
$importTest = python test_optimized_import.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "      ✅ Module erfolgreich importiert" -ForegroundColor Green
    
    # Prüfe ob optimierte Version geladen wird
    if ($importTest -match "admin_panel.py würde OPTIMIERTE Version laden") {
        Write-Host "      ✅ Optimierte Version wird verwendet" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  Warnung: Alte Version könnte geladen werden" -ForegroundColor Yellow
    }
} else {
    Write-Host "      ❌ Import-Test fehlgeschlagen!" -ForegroundColor Red
    Write-Host $importTest
    Read-Host "`nDrücke Enter zum Beenden"
    exit 1
}

# Schritt 3: Streamlit-Prozesse beenden
Write-Host "`n[3/4] 🛑 Beende laufende Streamlit-Prozesse..." -ForegroundColor Cyan
$streamlitProcesses = Get-Process -Name "streamlit" -ErrorAction SilentlyContinue
if ($streamlitProcesses) {
    $streamlitProcesses | Stop-Process -Force
    Write-Host "      ✅ $($streamlitProcesses.Count) Prozess(e) beendet" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "      ℹ️  Keine laufenden Streamlit-Prozesse gefunden" -ForegroundColor Gray
}

# Schritt 4: Streamlit starten
Write-Host "`n[4/4] 🚀 Starte Streamlit mit Optimierungen..." -ForegroundColor Cyan
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host ("=" * 59) -ForegroundColor Green
Write-Host "✅ NEUSTART ABGESCHLOSSEN - STREAMLIT STARTET JETZT" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host ("=" * 59) -ForegroundColor Green
Write-Host ""
Write-Host "📌 WICHTIG: Achte auf diese Meldung im Terminal:" -ForegroundColor Yellow
Write-Host "   '✅ admin_product_database_ui_optimized.py IMPORTIERT'" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 Weitere Infos: SCHNELLSTART_OPTIMIERUNG.md" -ForegroundColor Gray
Write-Host ""

# Streamlit starten
streamlit run gui.py
