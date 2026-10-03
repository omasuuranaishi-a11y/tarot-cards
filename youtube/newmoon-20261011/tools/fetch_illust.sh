#!/usr/bin/env bash
# 全編 v4 のイラスト（いらすとや・いらすとん）を取得して illust/ に置く。一覧は tools/illust.tsv（名前・場面・題・ページ・画像のURL）。
#   bash tools/fetch_illust.sh
# いらすとやの規約：商用は1つの制作物につき20点まで（同じイラストの重複は1点）、クレジット不要、素材の再配布は禁止。
# いらすとんの規約：個人・法人・商用・非商用とも無料、クレジット不要、点数の上限なし、素材の二次配布・販売は禁止。
# そのため画像は GitHub に入れない（illust/ は .gitignore 済み）。このスクリプトで取り直す。
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p illust
n=0; m=0
while IFS=$'\t' read -r name scenes title page url || [ -n "$name" ]; do
  [ "$name" = "name" ] && continue
  ext="${url##*.}"; ext="$(echo "$ext" | tr 'A-Z' 'a-z')"   # いらすとやは png、いらすとんは jpg
  [ -s "illust/$name.$ext" ] || curl -fsSL --retry 3 -o "illust/$name.$ext" "$url"
  case "$page" in *irasutoya*) n=$((n+1));; *) m=$((m+1));; esac
  echo "$name（$scenes）: $title"
done < tools/illust.tsv
echo "ok いらすとや $n 点（上限20点）、いらすとん $m 点"
