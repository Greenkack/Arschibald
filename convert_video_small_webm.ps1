# Erstelle SEHR KLEINES WebM für Base64-Einbettung (Ziel: unter 5 MB)

$InputFile = "static\intro_videos\intro_video.mp4"
$OutputFile = "static\intro_videos\intro_video_small.webm"

Write-Host "`n=== KLEINE WebM-DATEI ERSTELLEN ===" -ForegroundColor Cyan
Write-Host "Ziel: Unter 5 MB für Base64-Einbettung" -ForegroundColor Yellow

# Originalgrößen
$originalSize = (Get-Item $InputFile).Length / 1MB
Write-Host "Original: $([math]::Round($originalSize, 2)) MB" -ForegroundColor Yellow

# SEHR aggressive Kompression
Write-Host "`nKonvertiere mit maximaler Kompression..." -ForegroundColor Green
ffmpeg -i $InputFile `
    -c:v libvpx-vp9 `
    -b:v 400k `
    -vf "scale=640:360:force_original_aspect_ratio=decrease" `
    -c:a libopus `
    -b:a 64k `
    -deadline good `
    -cpu-used 4 `
    -y `
    $OutputFile 2>&1 | Out-Null

if (Test-Path $OutputFile) {
    $newSize = (Get-Item $OutputFile).Length / 1MB
    Write-Host "`n=== ERFOLG ===" -ForegroundColor Green
    Write-Host "Neue Größe: $([math]::Round($newSize, 2)) MB" -ForegroundColor Green
    Write-Host "Kompression: $([math]::Round((1 - $newSize/$originalSize)*100, 1))% kleiner" -ForegroundColor Green
    
    if ($newSize -lt 5) {
        Write-Host "`nPERFEKT! Datei ist unter 5 MB - Base64 wird funktionieren!" -ForegroundColor Green
    } else {
        Write-Host "`nWARNUNG: Datei ist noch über 5 MB. Versuche nochmal mit niedrigerer Auflösung..." -ForegroundColor Yellow
        
        # Noch aggressiver
        ffmpeg -i $InputFile `
            -c:v libvpx-vp9 `
            -b:v 250k `
            -vf "scale=480:270:force_original_aspect_ratio=decrease" `
            -c:a libopus `
            -b:a 48k `
            -deadline good `
            -cpu-used 5 `
            -y `
            $OutputFile 2>&1 | Out-Null
        
        $newSize = (Get-Item $OutputFile).Length / 1MB
        Write-Host "Neue Größe nach 2. Versuch: $([math]::Round($newSize, 2)) MB" -ForegroundColor Green
    }
} else {
    Write-Host "FEHLER: Konvertierung fehlgeschlagen!" -ForegroundColor Red
}
