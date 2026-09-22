# FLUX.2 API 日本語ガイド：モデル ID・1枚単価・実行例

> **1枚あたり $0.024 (1MP)** の従量課金。最低 1 ドルからチャージでき、OpenAI 互換の `https://api.apimart.ai/v1` だけで完結します。

<p align="center"><img src="assets/01-preview.jpg" width="820" alt="FLUX.2 sample output"></p>
**[FLUX.2 のモデルページ](https://apimart.ai/ja/model/flux-2)** · **[最新の料金](https://apimart.ai/ja/pricing)** · **[API キーを取得](https://apimart.ai/ja/keys)**

出力メガピクセル単位の課金で 1MP は1枚 2.4 セント。pro / max / flex を切り替えても API は同じ。

## APIMart 経由で FLUX.2 を呼ぶ理由

- **1 つのキーで全カタログ。** 同じベース URL と認証ヘッダで FLUX.2 を含む 300 以上の画像・動画・言語モデルに到達でき、切り替えは `model` フィールドのみ。
- **最低 1 ドル、従量課金。** サブスクも前払いプランも不要。無料枠を使い切る必要もなく、表の単価がそのまま実単価です。
- **課金額がレスポンスで返る。** 各呼び出しが `cost` / `credits_cost` を返すため、月末に推測する必要がありません。
- **非同期タスク前提の設計。** 送信して `task_id` を受け取り、`GET /v1/tasks/{id}` をポーリング。バッチも再試行も普通のキュー処理です。

## モデル ID とエンドポイント

| フィールド | 値 |
| --- | --- |
| `model` | `flux-2-pro` |
| endpoint | `POST https://api.apimart.ai/v1/images/generations` |
| task | GET /v1/tasks/{id} |


## 実際に生成したサンプル（すべて実コールの結果）

| sample | 費用 | prompt |
| --- | --- | --- |
| <img src="assets/01-preview.jpg" width="260"> | $0.024 | `雨上がりの路地、濡れた石畳に映る看板の灯り、フィルムライクな質感` |
| <img src="assets/02-preview.jpg" width="260"> | $0.024 | `白いスタジオで撮影した陶器のカップ、柔らかな窓光、85mm レンズ` |

## 実測料金

<!-- pricing:model:start -->
| 出力 | 単価 |
| --- | --- |
| `1MP` | $0.024 |
| `2MP` | $0.036 |
| `3MP` | $0.048 |
<!-- pricing:model:end -->

## リクエストパラメータ

| フィールド | 値 |
| --- | --- |
| `model` | `flux-2-pro` |
| `resolution` | `1MP / 2MP / 3MP` |
| `size` | `1:1 / 16:9 / 21:9` |
| `n` | `1-4` |

## 60 秒で開始

```bash
export APIMART_API_KEY="<token>"
curl --request POST \
  --url https://api.apimart.ai/v1/images/generations \
  --header "Authorization: Bearer $APIMART_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{"model":"flux-2-pro", "prompt":"a cozy reading nook by a rainy window, warm lamp light", "n":1}'
```

```python
import os, time, requests

BASE = "https://api.apimart.ai/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['APIMART_API_KEY']}", "Content-Type": "application/json"}

r = requests.post(f"{BASE}/images/generations", headers=HEADERS, timeout=60, json={
    "model": "flux-2-pro",
    "prompt": "a cozy reading nook by a rainy window, warm lamp light",
    "n": 1,
})
r.raise_for_status()
task_id = (r.json().get("data") or {}).get("id")
while True:
    t = requests.get(f"{BASE}/tasks/{task_id}", headers=HEADERS, timeout=60).json().get("data", {})
    if t.get("status") in ("completed", "failed"):
        print(t.get("status"), t.get("cost"))
        break
    time.sleep(5)
```

## まとめて実行した場合の費用

| 利用量 | 費用 |
| --- | --- |
| 1,000 | $24 |
| 10,000 | $240 |

上記の単価で線形計算した概算です（段階割引は考慮していません）。予算化の前に最新料金を確認してください。（snapshot 2026-09-21）

## 初回呼び出しのトラブルシュート

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| `401` / invalid api key | キーが無い、途中で切れている、改行が混入している | コンソールから再コピー。ヘッダは `Authorization: Bearer $APIMART_API_KEY` の形式 |
| 残高不足 / credit エラー | アカウント残高がゼロ | コンソールで最低 1 ドルをチャージ。無料枠はありません |
| `429` | 同一キーの同時実行が多すぎる | バックオフして再試行。再試行時は同じ `Idempotency-Key` を使う |
| `400` / model が見つからない | モデル ID かパラメータが誤り | 上の表の `model` 値をそのまま使用。ティアごとにフィールド名が異なります |
| タスクが `failed` | プロンプトがフィルタされた、参照画像の URL が失効した | 新しい `Idempotency-Key` で再送信し、参照画像は再ホストする |

## よくある質問

**課金単位は？**

画像は1枚、動画は1秒、言語モデルは100万トークン単位です。金額はタスク応答に含まれるため、1件ずつ確認できます。

**利用明細は確認できますか？**

コンソールの請求ページで、呼び出しごとの消費と残高の推移を確認できます。

**どんな言語から呼べますか？**

HTTP が送れる言語なら何でも可。OpenAI 互換なので、Python は openai SDK の base_url を差し替えるだけで動きます。

**結果 URL は失効しますか？**

失効します。タスク完了後すぐに自分のストレージへ保存してください。

## 開示

本リポジトリはサードパーティ中継サービス APIMart の利用ガイドです。モデル提供元とは無関係です。料金とパラメータはリポジトリ内のスナップショット時点のもので、実際の請求はプラットフォームの明細が基準です。

## リポジトリ構成

```
README.md            本文件
data/model.json      模型 ID、价格快照、参数
examples/curl.sh     curl 示例
examples/python.py   Python（提交 + 轮询）
LICENSE, .gitignore
```

## License

MIT
