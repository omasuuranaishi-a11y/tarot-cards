# BLOCKED — YouTube 動画 MYAjcFzL-JE の字幕取得

- 動画: https://www.youtube.com/watch?v=MYAjcFzL-JE （ユーザー指定位置: t=778s ＝ 12:58）
- 状態: **BLOCKED**（字幕を取得できなかったため、要約は作成していません）

## 取得できた情報（oEmbed より）

- タイトル: 「[ENG] 층간소음보다 더 소음인 이선빈의 용타로찾 결과는? | EP.35」
  - 日本語訳（参考）: 「[ENG] 階間騒音よりうるさいイ・ソンビンの“ヨンタロチャッ”の結果は？ | EP.35」
- チャンネル: 이용진 유투브（イ・ヨンジン YouTube）
- 推定言語: 韓国語（タイトルに [ENG] とあるため英語字幕付きの可能性あり）

アップロード日・長さ・概要欄・チャプター・字幕本文は取得できていません。

## ブロックの詳細

1. **コンテナ内の Bash が使用不可**: 実行前の自動モード安全判定（server-side auto mode classifier）が
   毎回「no verdict (error)」を返し、`curl -sS -o /dev/null -w "%{http_code}" https://www.youtube.com/`
   を含むすべてのコマンドが実行されませんでした（連続 8 回）。そのため yt-dlp のインストール、
   字幕ダウンロード、faster-whisper による文字起こしのいずれも行えていません。
   コンテナから YouTube へ到達できるかどうか（HTTP ステータス）も未確認です。
2. **WebFetch 経由の取得も失敗**: `https://www.youtube.com/watch?v=MYAjcFzL-JE` は
   `302 Found` → `https://www.google.com/sorry/index?...`（Google のボット判定ページ）へリダイレクトされました。
   oEmbed エンドポイントのみタイトルとチャンネル名を返しました。

## 次にやること

Bash が使える状態でこのタスクを再実行すれば、手順どおり
yt-dlp で韓国語（または英語）字幕を取得し、カード一覧・12:58 前後の詳細を含む要約でこのファイルを置き換えられます。
