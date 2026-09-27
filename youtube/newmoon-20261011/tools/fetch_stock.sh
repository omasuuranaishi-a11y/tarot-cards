#!/usr/bin/env bash
# 全編 v3 の実写素材（Mixkit）を取得し、30fps の JPEG 連番（1920x1080）と stock/manifest.js を作り直す。
#   bash tools/fetch_stock.sh
# 素材の一覧は tools/stock.tsv（場面・題・ページ・切り出し）。取得したものは stock/ に置き、GitHub には入れない（.gitignore 済み）。
#   ss/dur：素材の何秒目から何秒を使うか／speed：再生の速さ（0.6 なら 0.6 倍のゆっくり再生）
#   flip：1 なら左右反転（文字と重ならないよう、明るい所を右へ）／scale・x・y：1920x1080 に合わせた後、さらに拡大して切り抜く位置
#   （x が負のときは、左に黒い余白を -x ピクセル足して、写っているものを右へずらす。夜空など背景が黒い素材だけに使う）
# 色は彩度を少し下げるだけ。暗い紫の重ね・周辺減光・ゆっくり寄る動きはページ側（lib/footage.js）で付ける。
# 環境変数 FFMPEG で ffmpeg の実行ファイルを指定できる（既定 ffmpeg）。
set -euo pipefail
cd "$(dirname "$0")/.."
FF="${FFMPEG:-ffmpeg}"
mkdir -p stock/src stock/frames
manifest="window.STOCK = {"
while IFS=$'\t' read -r name id scenes title page ss dur speed flip scale x y; do
  [ "$name" = "name" ] && continue
  src="stock/src/$id.mp4"
  if [ ! -s "$src" ]; then
    echo "取得: $page"
    curl -fsS --retry 3 -o "$src.part" "https://assets.mixkit.co/videos/$id/$id-1080.mp4"
    mv "$src.part" "$src"
  fi
  out="stock/frames/$name"
  rm -rf "$out"; mkdir -p "$out"
  vf="setpts=(PTS-STARTPTS)/$speed,fps=30"
  [ "$flip" = "1" ] && vf="$vf,hflip"
  vf="$vf,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
  if [ "$scale" != "1" ] || [ "$x" != "0" ] || [ "$y" != "0" ]; then
    vf="$vf,scale=iw*$scale:ih*$scale"
    if [ "${x#-}" != "$x" ]; then vf="$vf,pad=iw+${x#-}:ih:${x#-}:0:black,crop=1920:1080:0:$y"; else vf="$vf,crop=1920:1080:$x:$y"; fi
  fi
  vf="$vf,eq=saturation=0.8"
  "$FF" -nostdin -loglevel error -y -ss "$ss" -t "$dur" -i "$src" -an -vf "$vf" -q:v 3 -start_number 0 "$out/%05d.jpg"
  n=$(ls "$out" | wc -l)
  echo "$name（$scenes）: $n コマ"
  manifest="$manifest
  $name: { n: $n, id: $id, title: \"$title\", page: \"$page\" },"
done < tools/stock.tsv
printf '%s\n};\n' "$manifest" > stock/manifest.js
echo "ok stock/manifest.js"
