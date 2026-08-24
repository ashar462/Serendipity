$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProgressPreference = 'SilentlyContinue'

$t = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('ZmlnZF8wY01BU3YzLWV2QllyN1EyVk9GYTRHM0VSQzZadlRVQXhmd2plQ3A3'))
$h = @{ 'X-Figma-Token' = $t }
$k = 'BO6GAA0KF1Q0W9SzpfcZym'
$dir = Join-Path (Get-Location) 'figma-export-data'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
(New-Item -ItemType Directory -Force -Path (Join-Path $dir 'renders')) | Out-Null

Write-Host 'Serendipity export — Figma rate limit ka intezar ho sakta hai (max 40 min)'
Write-Host ''

# 1) wait until the token is usable (poll /me — free, small)
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
  try { Invoke-RestMethod -Uri 'https://api.figma.com/v1/me' -Headers $h | Out-Null; $ready = $true; break }
  catch {
    Write-Host "Figma rate limit active hai — 2 minute wait karke dobara check (try $($i+1)/20)..."
    Start-Sleep -Seconds 120
  }
}
if (-not $ready) { Write-Host 'LIMIT ABHI BHI HAI — thori der baad script dobara chala dein.' -ForegroundColor Red; Read-Host 'Press Enter to close'; exit }

function Get-It($url, $name, $tries) {
  for ($i = 1; $i -le $tries; $i++) {
    try {
      Write-Host "downloading: $name"
      Invoke-WebRequest -Uri $url -Headers $h -OutFile (Join-Path $dir $name) -UseBasicParsing
      return
    } catch {
      Write-Host "error (try $i/$tries) — 90s wait..."; Start-Sleep -Seconds 90
    }
  }
  Write-Host "SKIP: $name" -ForegroundColor Yellow
}

function Save-Render($url, $name) {
  Write-Host "render: $name"
  Invoke-WebRequest -Uri $url -OutFile (Join-Path $dir "renders\$name") -UseBasicParsing
}

function Get-Renders($ids, $scale) {
  for ($try = 1; $try -le 4; $try++) {
    try {
      $r = Invoke-RestMethod -Uri "https://api.figma.com/v1/images/$k`?ids=$ids&scale=$scale&format=png" -Headers $h
      return $r.images
    } catch {
      Write-Host "rate limited / error (try $try/4) — 60s wait..."; Start-Sleep -Seconds 60
    }
  }
  return $null
}

# 2) the critical JSON first
Get-It "https://api.figma.com/v1/files/$k" 'file.json' 4
Get-It "https://api.figma.com/v1/files/$k/images" 'image-refs.json' 2

# 3) renders (QA references)
$fullIds = '247:1092,736:1531,740:4330,767:5221'
$m = Get-Renders $fullIds 1
if ($m) { foreach ($p in $m.PSObject.Properties) { if ($p.Value) { try { Save-Render $p.Value ("page-" + $p.Name.Replace(':','-') + ".png") } catch {} } } }

Start-Sleep -Seconds 8
$secIds = '247:1093,247:1094,951:5910,247:1095,247:1098,247:1101,1432:3336,1432:3338,247:1110,247:1111,247:1112,247:1125,247:1126,2165:5616,247:1137,1414:3313,259:691,2165:5650,259:1073,247:1181,259:511,259:445,259:735,259:410,259:792,247:1248,255:1937,247:1250,247:1251,247:1252,2161:3062'
$m2 = Get-Renders $secIds 1
if ($m2) { foreach ($p in $m2.PSObject.Properties) { if ($p.Value) { try { Save-Render $p.Value ("home-" + $p.Name.Replace(':','-') + ".png") } catch {} } } }

Write-Host ''
Write-Host '=====================================================' -ForegroundColor Green
Write-Host ' DONE! Ab "figma-export-data" folder ki SAARI files is' -ForegroundColor Green
Write-Host ' link par drag-drop kar ke Commit karein:' -ForegroundColor Green
Write-Host ' https://github.com/ashar462/Serendipity/upload/arena/01a02942-serendipity/figma-export-data' -ForegroundColor Yellow
Write-Host '=====================================================' -ForegroundColor Green
Read-Host 'Press Enter to close'
