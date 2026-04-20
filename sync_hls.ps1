$apiKey = "1378f133-dc9b-45c8-9d72155c0d00-3a70-4874"
$libId = "640806"
$pullHost = "vz-e5546235-a7a.b-cdn.net"
Write-Host "Conectando Bunny Stream..." -ForegroundColor Cyan
$allVideos = @()
$page = 1
do {
    $url = "https://video.bunnycdn.com/library/$libId/videos?page=$page&itemsPerPage=100&orderBy=title"
    $r = Invoke-RestMethod -Uri $url -Headers @{AccessKey=$apiKey; accept="application/json"}
    $allVideos += $r.items
    Write-Host "  Pagina $page : $($r.items.Count) videos | Total: $($allVideos.Count)/$($r.totalItems)"
    $page++
} while ($allVideos.Count -lt $r.totalItems -and $r.items.Count -eq 100)
Write-Host "OK: $($allVideos.Count) videos en Bunny" -ForegroundColor Green
function Norm($s) {
    if (-not $s) { return "" }
    $s = $s.ToLower()
    $s = $s -replace "\(.*?\)|\[.*?\]", ""
    $s = $s -replace "[^a-z0-9 ]", ""
    return ($s -replace "  +", " ").Trim()
}
$bunnyMap = @{}
foreach ($v in $allVideos) {
    $k = Norm $v.title
    if ($k -and -not $bunnyMap.ContainsKey($k)) { $bunnyMap[$k] = $v }
}
function FindMatch($title) {
    $q = Norm $title
    if ($bunnyMap.ContainsKey($q)) { return @{video=$bunnyMap[$q]; type="exact"} }
    foreach ($k in $bunnyMap.Keys) {
        if (($q -like "*$k*" -or $k -like "*$q*") -and ([Math]::Abs($q.Length - $k.Length) -lt 15)) {
            return @{video=$bunnyMap[$k]; type="partial"}
        }
    }
    return $null
}
Write-Host "Cargando catalogo..." -ForegroundColor Cyan
$catalog = Get-Content "micinema_catalog.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$updated = 0; $already = 0; $noMatch = 0; $noMatchList = @()
function ProcessEntry($entry, $label) {
    if (-not $entry.links) { return }
    $cur = $entry.links.default
    if ($cur -like "*playlist.m3u8*") { $script:already++; return }
    $title = if ($entry.title) { $entry.title } else { $entry.name }
    $m = FindMatch $title
    if (-not $m) {
        $script:noMatch++
        $script:noMatchList += "[$label] $title"
        Write-Host "  x $title" -ForegroundColor Yellow
        return
    }
    $hls = "https://$pullHost/$($m.video.guid)/playlist.m3u8"
    $entry.links.default = $hls
    if ($entry.links.language_Spanish -like "http*") { $entry.links.language_Spanish = $hls }
    if ($entry.links.language_English -like "http*") { $entry.links.language_English = $hls }
    $script:updated++
    Write-Host "  OK $title" -ForegroundColor Green
}
Write-Host "Procesando peliculas..." -ForegroundColor Cyan
foreach ($m in $catalog.movies) { ProcessEntry $m "movie" }
Write-Host "Procesando series..." -ForegroundColor Cyan
foreach ($s in $catalog.series) {
    foreach ($ep in $s.episodes) { ProcessEntry $ep $s.title }
    foreach ($season in $s.seasons) {
        foreach ($ep in $season.episodes) { ProcessEntry $ep $s.title }
    }
}
$catalog | ConvertTo-Json -Depth 20 | Set-Content "micinema_catalog_hls.json" -Encoding UTF8
if ($noMatchList.Count -gt 0) { $noMatchList | Set-Content "sync_no_match.txt" -Encoding UTF8 }
Write-Host ""
Write-Host "=== REPORTE ===" -ForegroundColor Cyan
Write-Host "Actualizados : $updated" -ForegroundColor Green
Write-Host "Ya eran HLS  : $already"
Write-Host "Sin match    : $noMatch" -ForegroundColor Yellow
Write-Host "Listo -> micinema_catalog_hls.json" -ForegroundColor Green