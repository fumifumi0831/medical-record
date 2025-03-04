# APIドキュメント

## 概要

バックエンドAPIは、FastAPIを使用して実装されています。このドキュメントでは、利用可能なすべてのAPIエンドポイントと、その使用方法について説明します。

## ベースURL

- 開発環境: `http://localhost:8000`
- 本番環境: `https://your-app-url.vercel.app`

## エンドポイント

### ヘルスチェック

```
GET /api/health
```

サーバーのステータスを確認します。

**レスポンス例**:

```json
{
  "status": "ok",
  "timestamp": "2025-03-04T12:34:56.789Z"
}
```

### カルテ画像のアップロード

```
POST /api/upload
```

手書き医療カルテの画像をアップロードし、処理を開始します。

**リクエスト**:

`multipart/form-data` 形式で、ファイルを `file` パラメータで送信します。

**レスポンス例**:

```json
{
  "record_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing"
}
```

### カルテ詳細の取得

```
GET /api/records/{record_id}
```

特定のカルテレコードとその抽出データを取得します。

**パスパラメータ**:

- `record_id`: カルテレコードのUUID

**レスポンス例**:

```json
{
  "record": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "original_image_url": "https://example.com/images/medical_records/12345.jpg",
    "uploaded_at": "2025-03-04T12:34:56.789Z",
    "processing_status": "completed"
  },
  "extracted_data": {
    "id": "987e6543-e21b-12d3-a456-426614174000",
    "record_id": "123e4567-e89b-12d3-a456-426614174000",
    "extracted_text": "\u60a3\u8005\u540d: \u5c71\u7530\u592a\u90ce\n\u751f\u5e74\u6708\u65e5: 1980\u5e744\u67081\u65e5\n\u8a3a\u65ad: \u9ad8\u8840\u5727\n\u51e6\u65b9: \u964d\u5727\u5264 \u671d1\u932b\n\u6240\u898b: \u8840\u5727145/95",
    "extracted_at": "2025-03-04T12:40:00.000Z"
  }
}
```

### カルテリストの取得

```
GET /api/records
```

すべてのカルテレコードの一覧を取得します。

**クエリパラメータ**:

- `limit`: 取得するレコード数の上限 (デフォルト: 10)
- `offset`: ページネーションのオフセット (デフォルト: 0)

**レスポンス例**:

```json
{
  "records": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "original_image_url": "https://example.com/images/medical_records/12345.jpg",
      "uploaded_at": "2025-03-04T12:34:56.789Z",
      "processing_status": "completed"
    },
    {
      "id": "223e4567-e89b-12d3-a456-426614174001",
      "original_image_url": "https://example.com/images/medical_records/12346.jpg",
      "uploaded_at": "2025-03-04T13:34:56.789Z",
      "processing_status": "pending"
    }
  ]
}
```

### カルテの再処理

```
POST /api/process/{record_id}
```

特定のカルテを再処理します。エラーが発生した場合などに使用します。

**パスパラメータ**:

- `record_id`: カルテレコードのUUID

**レスポンス例**:

```json
{
  "status": "processing",
  "record_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

## エラーレスポンス

エラーが発生した場合、以下のようなレスポンスが返されます。

```json
{
  "detail": "Error message here"
}
```

一般的なエラーステータスコード:

- `400`: リクエストが不正
- `404`: リソースが見つからない
- `500`: サーバー内部エラー