# Emoji-Entferner für einzelne Datei
Get - Content "analysis.py" | ForEach - Object {
    $_ -replace " ", "" - replace " ", "" - replace "", "" - replace "", ""
    - replace " ", "" - replace " ", "" - replace "", "" - replace " ", ""
    - replace "", "" - replace "", "" - replace " ", "" - replace "", ""
    - replace "", "" - replace "", "" - replace "", "" - replace "", ""
    - replace "", "" - replace "", "" - replace " ", "" - replace " ", ""
    - replace "", "" - replace " ", "" - replace " ", "" - replace " ", ""
    - replace " ", "" - replace "", "" - replace " ", "" - replace " ", ""
    - replace " ", "" - replace " ", "" - replace " ", "" - replace " ", ""
    - replace " ", ""
} | Set - Content "analysis_clean.py"

# Alle Python-Dateien in einem Ordner bereinigen
Get - ChildItem "*.py" | ForEach - Object {
    $content = Get - Content $_.FullName | ForEach - Object {
        $_ -replace "[\u{1F300}-\u{1F9FF}]", ""
    }
    Set - Content $_.FullName $content
    Write - Host "$($_.Name) bereinigt"
}
