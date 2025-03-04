# 医療カルテ文字抽出アプリ

手書き医療カルテの画像をアップロードし、Gemini 2.0 Flash AIを使用して文字を抽出するWebアプリケーションです。

## 技術スタック

- **フロントエンド**: Next.js
- **バックエンド**: FastAPI
- **データベース**: Supabase (PostgreSQL)
- **AI処理**: Google Gemini 2.0 Flash API
- **デプロイ**: Vercel

## 機能

- 手書き医療カルテの画像アップロード
- AIによる画像からのテキスト抽出
- 抽出結果の表示と保存
- 過去の処理履歴の閲覧

## プロジェクト構造

```
/
├── frontend/          # Next.jsフロントエンド
├── backend/           # FastAPIバックエンド
├── supabase/          # Supabaseのマイグレーションスクリプト
│   └── migrations/    # データベースのマイグレーションファイル
└── docs/              # プロジェクトドキュメント
    └── database.md    # データベース構造の詳細な解説
```

## データベース構造

このプロジェクトはSupabase（PostgreSQL）を使用してデータを管理しています。データベースには以下のテーブルが含まれています：

- **medical_records**: 医療カルテの画像情報と処理状態を管理
- **extracted_data**: AIによって抽出されたテキストデータを管理

詳細なデータベースの構造と設定方法については[データベースドキュメント](docs/database.md)を参照してください。

## セットアップ方法

### 前提条件

- Node.js 18以上
- Python 3.8以上
- Supabaseアカウント
- Google AI Studio API キー

### Supabaseのセットアップ

1. [Supabase](https://supabase.com/)でアカウントを作成し、新しいプロジェクトを作成
2. データベーススキーマの設定（詳細は[データベースドキュメント](docs/database.md)を参照）
3. プロジェクトのURLと匿名キーをメモ

### 環境変数

`.env.local`ファイル（フロントエンド）と`.env`ファイル（バックエンド）を作成し、以下の環境変数を設定してください：

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
GEMINI_API_KEY=your-gemini-api-key
```

### インストールと実行

```bash
# フロントエンドのセットアップ
cd frontend
npm install
npm run dev

# バックエンドのセットアップ
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## デプロイ

Vercelを使用して簡単にデプロイできます。

```bash
vercel
```

## ライセンス

MIT
