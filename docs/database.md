# 医療カルテアプリのデータベース構築と解説

このドキュメントでは、医療カルテ文字抽出アプリケーションで使用されているSupabaseデータベースの構造と、SQL移行ファイルの詳細な解説を提供します。

## データベース概要

このアプリケーションは、Supabase（PostgreSQL）を使用して、手書き医療カルテの画像とそこから抽出されたテキストデータを管理します。データベースは主に以下の構成要素からなります：

1. ストレージバケット：カルテ画像の保存場所
2. テーブル構造：カルテ情報と抽出データの保存
3. セキュリティポリシー：データアクセス制御

## SQL移行ファイルの詳細解説

### ストレージバケットの作成

```sql
-- Create storage bucket for medical record images
INSERT INTO storage.buckets (id, name) VALUES ('images', 'images')
ON CONFLICT DO NOTHING;

-- Set up public access policy for the images bucket
CREATE POLICY "Public Access" ON storage.objects FOR SELECT USING (bucket_id = 'images');
```

**解説：**
- `storage.buckets`テーブルに`images`という名前のバケットを作成します
- 既に存在する場合は何もしない（`ON CONFLICT DO NOTHING`）
- `Public Access`ポリシーを作成し、`images`バケット内のオブジェクトに対して読み取り（SELECT）権限を付与しています
- このポリシーにより、認証なしでもアップロードされた画像を表示できます

### メインテーブルの作成

```sql
-- Create medical_records table
CREATE TABLE IF NOT EXISTS public.medical_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  original_image_url TEXT NOT NULL,
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processing_status TEXT DEFAULT 'pending'
);
```

**解説：**
- `medical_records`テーブルは、アップロードされた医療カルテの基本情報を格納します
- 各レコードには以下のフィールドがあります：
  - `id`: 一意の識別子（UUID型で自動生成）
  - `original_image_url`: アップロードされた画像のURL（必須）
  - `uploaded_at`: アップロード日時（デフォルトは現在時刻）
  - `processing_status`: 処理状態（デフォルトは'pending'）
- 処理状態は以下の値を取ります：
  - `pending`: 処理待ち
  - `processing`: 処理中
  - `completed`: 処理完了
  - `failed`: 処理失敗

### 抽出データテーブルの作成

```sql
-- Create extracted_data table
CREATE TABLE IF NOT EXISTS public.extracted_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  record_id UUID NOT NULL REFERENCES public.medical_records(id) ON DELETE CASCADE,
  extracted_text TEXT,
  extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**解説：**
- `extracted_data`テーブルは、AI（Gemini 2.0）によって抽出されたテキストデータを格納します
- 各レコードには以下のフィールドがあります：
  - `id`: 一意の識別子（UUID型で自動生成）
  - `record_id`: 関連する`medical_records`テーブルのID（外部キー）
  - `extracted_text`: 抽出されたテキスト内容
  - `extracted_at`: テキスト抽出が完了した日時
- `ON DELETE CASCADE`制約により、元のカルテレコードが削除された場合、関連する抽出データも自動的に削除されます

### インデックスの作成

```sql
-- Create indexes
CREATE INDEX IF NOT EXISTS idx_medical_records_uploaded_at ON public.medical_records(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_extracted_data_record_id ON public.extracted_data(record_id);
```

**解説：**
- パフォーマンス向上のため、2つのインデックスを作成しています
- `idx_medical_records_uploaded_at`: アップロード日時によるソートやフィルタリングを高速化
- `idx_extracted_data_record_id`: レコードIDによる関連抽出データの検索を高速化

### 行レベルセキュリティの有効化

```sql
-- Enable RLS (Row Level Security)
ALTER TABLE public.medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.extracted_data ENABLE ROW LEVEL SECURITY;
```

**解説：**
- 両方のテーブルで行レベルセキュリティ（RLS）を有効にしています
- RLSは、行ごとにアクセス制御を行うためのPostgreSQLの機能です
- デフォルトでは、RLSを有効にすると全てのアクセスが拒否されます
- 特定のアクセスを許可するためには、追加のポリシーが必要です

### アクセスポリシーの作成

```sql
-- Create policies for anonymous access (since we don't need authentication for this app)
CREATE POLICY "Anonymous select medical_records" ON public.medical_records
  FOR SELECT USING (true);

CREATE POLICY "Anonymous insert medical_records" ON public.medical_records
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Anonymous update medical_records" ON public.medical_records
  FOR UPDATE USING (true);

CREATE POLICY "Anonymous select extracted_data" ON public.extracted_data
  FOR SELECT USING (true);

CREATE POLICY "Anonymous insert extracted_data" ON public.extracted_data
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Anonymous update extracted_data" ON public.extracted_data
  FOR UPDATE USING (true);
```

**解説：**
- このアプリケーションでは認証を必要としないため、匿名アクセスを許可するポリシーを設定しています
- 各テーブルに対して、以下の操作を許可するポリシーを作成：
  - SELECT: データの読み取り
  - INSERT: 新しいデータの挿入
  - UPDATE: 既存データの更新
- 各ポリシーの条件は`true`となっており、全てのレコードに対して操作を許可しています
- 削除（DELETE）操作に対するポリシーは定義されていないため、データの削除はデフォルトで禁止されています

## データベース構築手順

以下の手順で、このアプリケーション用のデータベースを構築できます：

### 1. Supabaseプロジェクトのセットアップ

1. [Supabase](https://supabase.com/)にアクセスし、アカウントを作成（または既存のアカウントでログイン）
2. 新しいプロジェクトを作成
3. プロジェクト名を設定し、リージョンを選択（データの場所として最適な地域）
4. データベースのパスワードを設定
5. 「Create new project」をクリックして作成を開始

### 2. マイグレーションの実行

#### 自動マイグレーション（推奨）

Supabase CLIを使用して自動的にマイグレーションを適用する方法：

1. Supabase CLIのインストール
   ```bash
   npm install -g supabase
   ```

2. Supabaseにログイン
   ```bash
   supabase login
   ```
   - ブラウザが開き、Supabaseアカウントでの認証を求められます
   - 認証が成功すると、CLIにアクセストークンが保存されます

3. プロジェクトのリンク
   ```bash
   supabase link --project-ref <your-project-ref>
   ```
   
   **project-refの確認方法**:
   1. [Supabaseダッシュボード](https://app.supabase.com)にログイン
   2. 対象のプロジェクトを選択
   3. 左側のサイドバーから「Project Settings」（プロジェクト設定）をクリック
   4. 「General」タブ内の「Reference ID」の値をコピー
   
   例えば、Reference IDが `abcdefghijklmnopqrst` の場合:
   ```bash
   supabase link --project-ref abcdefghijklmnopqrst
   ```

4. マイグレーションの適用
   ```bash
   supabase db push
   ```
   - このコマンドは、`supabase/migrations`ディレクトリ内のすべてのSQLファイルを適用します

#### 手動マイグレーション

Supabase管理パネルからSQLエディタを使用して手動でスクリプトを実行：

1. Supabaseダッシュボードにログイン
2. プロジェクトを選択
3. 左側のメニューから「SQL Editor」を選択
4. 「New query」をクリックして新しいクエリを作成
5. リポジトリの`supabase/migrations/20240304134212_initial.sql`ファイルの内容をコピーして貼り付け
6. 「Run」をクリックしてSQLを実行

### 3. 環境変数の設定

アプリケーションが正しくSupabaseに接続できるよう、以下の環境変数を設定します：

1. Supabaseダッシュボードの「Settings」→「API」から必要な情報を取得:
   - 「Project URL」: プロジェクトのURL
   - 「anon public」: 匿名（公開）キー
   
2. `.env.local`（フロントエンド）と`.env`（バックエンド）ファイルを作成し、以下の変数を設定：

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

## データフロー

このデータベース設計におけるデータフローは以下のとおりです：

1. ユーザーが手書き医療カルテの画像をアップロード
2. 画像はSupabaseのストレージ（`images`バケット）に保存
3. 画像のURLと初期状態を`medical_records`テーブルに記録
4. バックエンドがGemini 2.0 APIを使用してテキスト抽出を実行
5. 抽出されたテキストが`extracted_data`テーブルに保存
6. `medical_records`テーブルの`processing_status`が更新される
7. フロントエンドがデータを取得して表示

## 注意点と拡張可能性

- このデータベース構造は、認証なしでの公開アクセスを前提としています。実際の医療データを扱う場合は、適切な認証と承認の仕組みを追加することを強く推奨します。
- 将来的に患者情報や医師情報などを追加する場合は、関連するテーブルと関係を設計する必要があります。
- 本番環境では、抽出されたテキスト内の機密情報（個人情報など）を適切に管理するためのポリシーを検討してください。