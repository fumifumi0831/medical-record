# サンプルデータ

## サンプルデータの使い方

このドキュメントには、テスト用のサンプルデータが含まれています。実際の医療カルテ画像を使用する前に、このサンプルデータを用いてアプリケーションをテストすることができます。

## サンプルデータ

### テスト用カルテレコード

```json
{
  "record": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "original_image_url": "https://example.com/images/sample_medical_record.jpg",
    "uploaded_at": "2025-03-04T12:34:56.789Z",
    "processing_status": "completed"
  },
  "extracted_data": {
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "record_id": "550e8400-e29b-41d4-a716-446655440000",
    "extracted_text": "{
      \"patient_info\": {
        \"name\": \"\u5c71\u7530 \u592a\u90ce\",
        \"dob\": \"1980-04-01\",
        \"gender\": \"\u7537\u6027\",
        \"id\": \"P12345\"
      },
      \"diagnosis\": {
        \"primary\": \"\u9ad8\u8840\u5727\",
        \"secondary\": \"\u7cd6\u5c3f\u75c5\u4e88\u5099\u7fa4\"
      },
      \"measurements\": {
        \"blood_pressure\": \"145/95 mmHg\",
        \"pulse\": \"78 bpm\",
        \"weight\": \"75.5 kg\",
        \"height\": \"172 cm\",
        \"bmi\": \"25.5\"
      },
      \"medications\": [
        {
          \"name\": \"\u30a2\u30e0\u30ed\u30b8\u30d4\u30f3\",
          \"dosage\": \"5mg\",
          \"frequency\": \"\u671d1\u56de\"
        }
      ],
      \"doctor_notes\": \"\u8840\u5727\u4f4e\u4e0b\u306b\u52b9\u679c\u304c\u898b\u3089\u308c\u308b\u304c\u3001\u751f\u6d3b\u7fd2\u6163\u306e\u6539\u5584\u304c\u5fc5\u8981\u3002\u904b\u52d5\u3068\u9699\u9593\u98df\u3092\u6e1b\u3089\u3059\u3088\u3046\u6307\u5c0e\u3002\"
    }",
    "extracted_at": "2025-03-04T12:40:00.000Z"
  }
}
```

### テスト用レコードリスト

```json
{
  "records": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "original_image_url": "https://example.com/images/sample_medical_record.jpg",
      "uploaded_at": "2025-03-04T12:34:56.789Z",
      "processing_status": "completed"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "original_image_url": "https://example.com/images/sample_medical_record2.jpg",
      "uploaded_at": "2025-03-04T13:34:56.789Z",
      "processing_status": "pending"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "original_image_url": "https://example.com/images/sample_medical_record3.jpg",
      "uploaded_at": "2025-03-04T14:34:56.789Z",
      "processing_status": "error"
    }
  ]
}
```

## テストアプローチ

1. データベースの初期化
   - Supabaseのデータベーススキーマをセットアップする

2. サンプルデータを使ったテスト
   - 上記のサンプルデータを使用して、アプリケーションの機能をテストする

3. テスト手順
   - バックエンドAPIの動作確認テスト
   - フロントエンドUIの機能確認テスト
   - Gemini API連携のテスト
   - 統合テスト

## サンプル画像

実際のテストに使用できるサンプル画像は、`/docs/sample_images/`ディレクトリに用意されています。これらは模擬的な二次制作データであり、実際の医療情報は含まれていません。
