# テストガイド

## 概要

このドキュメントでは、医療カルテ文字抽出アプリケーションのテスト手順とアプローチについて説明します。

## テスト環境の設定

1. 開発環境をセットアップします（`setup.md`を参照）。

2. テスト用の環境変数を設定します（本番とは別のSupabaseプロジェクトを使用することを推奨）。

## テスト種別

### 1. ユニットテスト

バックエンドの各関数とAPIエンドポイントの動作を個別にテストします。

```bash
cd backend
python -m pytest tests/unit/
```

### 2. 統合テスト

バックエンドとフロントエンドの統合をテストします。

```bash
cd backend
python -m pytest tests/integration/
```

### 3. マニュアルテスト

以下のシナリオを手動でテストします：

1. **画像アップロードテスト**
   - サンプルカルテ画像をアップロードします
   - 処理状況が正しく表示されることを確認します
   - 処理完了後、抽出結果が表示されることを確認します

2. **履歴表示テスト**
   - ホームページから履歴ページに遷移します
   - アップロードしたカルテが履歴に表示されることを確認します
   - 各カルテの詳細ページに移動し、内容が正しく表示されることを確認します

3. **エラーハンドリングテスト**
   - 無効なファイル形式（例: .txtファイル）をアップロードして、エラーメッセージが表示されることを確認します
   - 大きすぎるファイル（10MB以上）をアップロードして、エラーメッセージが表示されることを確認します

4. **再処理機能テスト**
   - エラー状態のカルテに対して再処理を行い、正しく処理されることを確認します

### 4. パフォーマンステスト

アプリケーションのパフォーマンスを評価します。

1. **レスポンスタイムテスト**
   - 画像アップロードから処理完了までの時間を計測します
   - データ取得のレスポンスタイムを計測します

2. **負荷テスト**
   - 複数の画像を連続でアップロードし、システムの動作を確認します

## テストデータ

テストに使用するサンプル画像は `docs/sample_images/` ディレクトリに用意されています。テストデータについての詳細は `sample_data.md` を参照してください。

## バグ報告とトラッキング

テスト中に発見された問題はプロジェクトのGitHub Issuesに報告してください。報告時には以下の情報を含めてください：

- 問題のタイトルと簡単な説明
- 発生時の手順と環境
- 期待される動作と実際の動作
- スクリーンショットやエラーメッセージなどの補足情報
