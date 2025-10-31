# Paketmanager-Migrations-Skript
Write-Host "Migration zu pnpm beginnt..." -ForegroundColor Green

# Aktuelle Node-Prozesse anzeigen
Write-Host "Laufende Node-Prozesse:" -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Format-Table Id, ProcessName, Path

# Bestätigungsabfrage
Write-Host "WARNUNG: Dieses Skript wird alle node_modules-Ordner löschen und die Abhängigkeiten neu installieren." -ForegroundColor Red
$confirmation = Read-Host "Möchten Sie fortfahren? (j/n)"
if ($confirmation -ne 'j') {
    Write-Host "Operation abgebrochen." -ForegroundColor Red
    exit
}

# Lock-Dateien entfernen
Write-Host "Entferne Lock-Dateien..." -ForegroundColor Yellow
Remove-Item -Path "package-lock.json" -ErrorAction SilentlyContinue
Remove-Item -Path "yarn.lock" -ErrorAction SilentlyContinue

# Node-Module entfernen (mit Wartezeit für mögliche Prozessbeendigung)
Write-Host "Warte 2 Sekunden..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host "Versuche node_modules zu entfernen..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    try {
        Remove-Item -Path "node_modules" -Recurse -Force -ErrorAction Stop
        Write-Host "node_modules erfolgreich gelöscht." -ForegroundColor Green
    } catch {
        Write-Host "Konnte node_modules nicht löschen: $_" -ForegroundColor Red
        Write-Host "Versuche Alternative..." -ForegroundColor Yellow
        
        # Alternativer Ansatz - umbenennen und später löschen
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupName = "node_modules_old_$timestamp"
        try {
            Rename-Item -Path "node_modules" -NewName $backupName -ErrorAction Stop
            Write-Host "node_modules zu $backupName umbenannt." -ForegroundColor Green
        } catch {
            Write-Host "Konnte node_modules nicht umbenennen: $_" -ForegroundColor Red
            Write-Host "Fahre fort ohne node_modules zu entfernen." -ForegroundColor Yellow
        }
    }
}

# Auch in Unterordnern prüfen
$subfolderModules = Get-ChildItem -Path . -Filter "node_modules" -Directory -Recurse
foreach ($folder in $subfolderModules) {
    Write-Host "Versuche zu löschen: $($folder.FullName)" -ForegroundColor Yellow
    try {
        Remove-Item -Path $folder.FullName -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Host "Konnte $($folder.FullName) nicht löschen. Wird übersprungen." -ForegroundColor Red
    }
}

# pnpm installieren und konfigurieren
Write-Host "Installiere pnpm..." -ForegroundColor Yellow
& pnpm setup

# Neue Installation mit pnpm
Write-Host "Installiere Abhängigkeiten mit pnpm..." -ForegroundColor Yellow
& pnpm install

Write-Host "Migration abgeschlossen!" -ForegroundColor Green
Write-Host "Falls Probleme aufgetreten sind, versuchen Sie VS Code zu schließen und das Skript erneut auszuführen." -ForegroundColor Yellow
