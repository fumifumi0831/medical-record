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
└── docs/              # プロジェクトドキュメント
```

## セットアップ方法

### 前提条件

- Node.js 18以上
- Python 3.8以上
- Supabaseアカウント
- Google AI Studio API キー

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
