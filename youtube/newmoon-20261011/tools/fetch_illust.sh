#!/usr/bin/env bash
# 全編 v4 のイラスト（いらすとや）を取得して illust/ に置く。一覧は tools/illust.tsv（名前・場面・題・ページ・画像のURL）。
#   bash tools/fetch_illust.sh
# いらすとやの規約：商用は1つの制作物につき20点まで（同じイラストの重複は1点）、クレジット不要、素材の再配布は禁止。
# そのため画像は GitHub に入れない（illust/ は .gitignore 済み）。このスクリプトで取り直す。
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p illust
n=0
while IFS=$'\t' read -r name scenes title page url; do
  [ "$name" = "name" ] && continue
  [ -s "illust/$name.png" ] || curl -fsSL --retry 3 -o "illust/$name.png" "$url"
  n=$((n+1)); echo "$name（$scenes）: $title"
done < tools/illust.tsv
echo "ok $n 点（上限20点）"
