#!/bin/bash
# Serendipity — Figma data export (macOS)
# Double-click (ya right-click -> Open). Output: figma-export-data/
cd "$(dirname "$0")"
T=$(printf 'ZmlnZF8wY01BU3YzLWV2QllyN1EyVk9GYTRHM0VSQzZadlRVQXhmd2plQ3A3' | base64 -d)
K='BO6GAA0KF1Q0W9SzpfcZym'
D='figma-export-data'
mkdir -p "$D/renders"

dl() { echo "downloading: $2"; curl -sS -H "X-Figma-Token: $T" -o "$D/$2" "$1"; }

dl "https://api.figma.com/v1/files/$K" 'file.json'
dl "https://api.figma.com/v1/files/$K?depth=3" 'file-depth3.json'
dl "https://api.figma.com/v1/files/$K/images" 'image-refs.json'

render() { # ids scale prefix
  for try in 1 2 3 4; do
    JSON=$(curl -sS -H "X-Figma-Token: $T" "https://api.figma.com/v1/images/$K?ids=$1&scale=$2&format=png")
    echo "$JSON" | grep -q '"err"' || break
    echo "rate limited (try $try/4) — 60s wait..."; sleep 60
  done
  echo "$JSON" | python3 -c "import json,sys; d=json.load(sys.stdin).get('images',{}); [print(k.replace(':','-'),v) for k,v in d.items() if v]" | while read -r id url; do
    echo "render: $3-$id.png"; curl -sS -o "$D/renders/$3-$id.png" "$url"
  done
}

render '247:1092,736:1531,740:4330,767:5221' 1 'page'
sleep 8
render '247:1093,247:1094,951:5910,247:1095,247:1098,247:1101,1432:3336,1432:3338,247:1110,247:1111,247:1112,247:1125,247:1126,2165:5616,247:1137,1414:3313,259:691,2165:5650,259:1073,247:1181,259:511,259:445,259:735,259:410,259:792,247:1248,255:1937,247:1250,247:1251,247:1252,2161:3062' 1 'home'

echo ""
echo "====================================================="
echo " DONE! Ab figma-export-data folder ki SAARI files is"
echo " link par drag-drop kar ke Commit karein:"
echo " https://github.com/ashar462/Serendipity/upload/arena/01a02942-serendipity/figma-export-data"
echo "====================================================="
read -r -p "Press Enter to close..."
