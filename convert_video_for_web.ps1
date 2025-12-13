# Video-Konvertierung für Web-Optimierung
# Konvertiert große MP4-Videos in WebM mit optimaler Größe/Qualität

param(
    [string]$InputFile = "static\intro_videos\intro_video.mp4",
    [string]$Quality = "high"  # "low", "medium", "high"
)

$OutputWebM = $InputFile -replace '\.mp4$', '.webm'
$OutputMP4 = $InputFile -replace '\.mp4$', '_optimized.mp4'

Write-Host "`n=== VIDEO-KONVERTIERUNG FÜR WEB ===" -ForegroundColor Cyan
Write-Host "Input: $InputFile" -ForegroundColor Yellow

# Prüfe ob Datei existiert
if (!(Test-Path $InputFile)) {
    Write-Host "FEHLER: Datei nicht gefunden: $InputFile" -ForegroundColor Red
    exit 1
}

# Zeige Original-Größe
$originalSize = (Get-Item $InputFile).Length / 1MB
Write-Host "Original-Größe: $([math]::Round($originalSize, 2)) MB" -ForegroundColor Yellow

# Qualitäts-Einstellungen
$settings = @{
    "low" = @{
        resolution = "854:480"
        videoBitrate = "800k"
        audioBitrate = "96k"
        targetSize = "5-8 MB"
    }
    "medium" = @{
        resolution = "1280:720"
        videoBitrate = "1500k"
        audioBitrate = "128k"
        targetSize = "10-15 MB"
    }
    "high" = @{
        resolution = "1920:1080"
        videoBitrate = "2500k"
        audioBitrate = "192k"
        targetSize = "15-25 MB"
    }
}

$config = $settings[$Quality]
Write-Host "`nQualität: $Quality" -ForegroundColor Cyan
Write-Host "Auflösung: $($config.resolution)" -ForegroundColor Gray
Write-Host "Video-Bitrate: $($config.videoBitrate)" -ForegroundColor Gray
Write-Host "Zielgröße: $($config.targetSize)" -ForegroundColor Gray

# Konvertierung 1: WebM (beste Kompression)
Write-Host "`n[1/2] Konvertiere zu WebM (empfohlen für Web)..." -ForegroundColor Green
ffmpeg -i $InputFile `
    -c:v libvpx-vp9 `
    -b:v $($config.videoBitrate) `
    -vf "scale=$($config.resolution):force_original_aspect_ratio=decrease,pad=$($config.resolution):(ow-iw)/2:(oh-ih)/2" `
    -c:a libopus `
    -b:a $($config.audioBitrate) `
    -movflags +faststart `
    -deadline good `
    -cpu-used 2 `
    -y `
    $OutputWebM 2>&1 | Out-Null

if (Test-Path $OutputWebM) {
    $webmSize = (Get-Item $OutputWebM).Length / 1MB
    Write-Host "  WebM erstellt: $([math]::Round($webmSize, 2)) MB" -ForegroundColor Green
}

# Konvertierung 2: Optimiertes MP4 (Fallback)
Write-Host "`n[2/2] Konvertiere zu optimiertem MP4 (Fallback)..." -ForegroundColor Green
ffmpeg -i $InputFile `
    -c:v libx264 `
    -preset slow `
    -crf 28 `
    -b:v $($config.videoBitrate) `
    -vf "scale=$($config.resolution):force_original_aspect_ratio=decrease,pad=$($config.resolution):(ow-iw)/2:(oh-ih)/2" `
    -c:a aac `
    -b:a $($config.audioBitrate) `
    -movflags +faststart `
    -y `
    $OutputMP4 2>&1 | Out-Null

if (Test-Path $OutputMP4) {
    $mp4Size = (Get-Item $OutputMP4).Length / 1MB
    Write-Host "  MP4 erstellt: $([math]::Round($mp4Size, 2)) MB" -ForegroundColor Green
}

# Zusammenfassung
Write-Host "`n=== ZUSAMMENFASSUNG ===" -ForegroundColor Cyan
Write-Host "Original:          $([math]::Round($originalSize, 2)) MB" -ForegroundColor Yellow
if (Test-Path $OutputWebM) {
    Write-Host "WebM (empfohlen):  $([math]::Round($webmSize, 2)) MB (-$([math]::Round((1 - $webmSize/$originalSize)*100, 1))%)" -ForegroundColor Green
}
if (Test-Path $OutputMP4) {
    Write-Host "MP4 (Fallback):    $([math]::Round($mp4Size, 2)) MB (-$([math]::Round((1 - $mp4Size/$originalSize)*100, 1))%)" -ForegroundColor Green
}

Write-Host "`n=== NÄCHSTE SCHRITTE ===" -ForegroundColor Cyan
Write-Host "1. Benenne die optimierte Datei um:" -ForegroundColor White
Write-Host "   Rename-Item '$OutputWebM' 'intro_video.webm'" -ForegroundColor Gray
Write-Host "   ODER" -ForegroundColor Yellow
Write-Host "   Rename-Item '$OutputMP4' 'intro_video.mp4'" -ForegroundColor Gray
Write-Host "`n2. Starte die App neu:" -ForegroundColor White
Write-Host "   streamlit run gui.py" -ForegroundColor Gray
Write-Host "`nTipp: WebM hat kleinere Dateigröße und besseren Browser-Support!" -ForegroundColor Cyan
