from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import uuid
import httpx
import json
import base64
import asyncio
import logging
import random
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai

# 環境変数の読み込み
load_dotenv()

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="医療カルテ文字抽出 API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では実際のドメインに制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase接続
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_KEY: {supabase_key[:10]}..." if supabase_key else "SUPABASE_KEY not set")

# Gemini API設定
gemini_api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

# Supabaseクライアント作成
def get_supabase() -> Client:
    if not supabase_url or not supabase_key:
        raise HTTPException(status_code=500, detail="Supabase credentials not configured")
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        logger.error(f"Supabase client creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not connect to database")

@app.get("/api/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), supabase: Client = Depends(get_supabase)):
    """カルテ画像のアップロード処理"""
    try:
        # ファイル拡張子の確認
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in [".jpg", ".jpeg", ".png"]:
            raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed")
        
        # ファイルサイズ確認 (10MB以下)
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # 一意のファイル名を生成
        file_name = f"{uuid.uuid4()}{file_ext}"
        
        # Supabaseのストレージにアップロード
        storage_path = f"medical_records/{file_name}"
        
        # from_メソッドを使用（fromはPythonの予約語なのでfrom_を使用）
        upload_result = supabase.storage.from_("images").upload(
            path=storage_path,
            file=contents,
            file_options={"content-type": file.content_type}
        )
        
        # 画像のURLを取得
        file_url = supabase.storage.from_("images").get_public_url(storage_path)
        
        # DBに新しいレコードを作成
        record = supabase.table("medical_records").insert({
            "original_image_url": file_url,
            "processing_status": "pending"
        }).execute()
        
        if not record.data:
            raise HTTPException(status_code=500, detail="Failed to create record")
        
        record_id = record.data[0]["id"]
        
        # バックグラウンドでの画像処理を開始
        asyncio.create_task(process_image(record_id, file_url, contents))
        
        return {"record_id": record_id, "status": "processing"}
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

async def process_image(record_id: str, image_url: str, image_bytes: bytes, language="ja", max_retries=5, initial_delay=2):
    """画像処理と文字抽出を行う非同期関数（リトライ機能付き）"""
    retries = 0
    
    # Supabaseに再接続（非同期タスク内）
    supabase = create_client(supabase_url, supabase_key)
    
    # 医療カルテの状態を処理中に更新
    try:
        supabase.table("medical_records").update({
            "processing_status": "processing"
        }).eq("id", record_id).execute()
    except Exception as e:
        logger.error(f"処理状態の更新に失敗しました: {str(e)}")
    
    while retries <= max_retries:
        try:
            # プロンプトの設定
            if language == "ja":
                prompt = """
                この医療カルテ画像から、実際に書かれているテキストのみを抽出してください。

                重要な指示：
                - 画像に実際に存在するテキストだけを抽出する
                - 存在しない情報は決して補完や推測しない
                - 書かれていない項目や見出しは追加しない
                - 形式やフォーマットを勝手に追加しない
                - 余分な説明は一切不要

                具体的な抽出方法：
                1. 画像に見えるテキストをそのまま読み取る
                2. 表形式のデータはスペースや記号で区切って表現
                3. 改行や段落は原文のまま保持
                4. 判読不能な部分は「[判読不能]」と表記
                5. レイアウトをなるべく維持

                例えば、画像に「体温 36.5℃」としか書かれていなければ、余分な見出しや区分けせず「体温 36.5℃」とだけ出力してください。
                """
            else:
                prompt = """
                Extract ONLY the text that is actually written in this medical record image.

                Important instructions:
                - Extract ONLY text that actually exists in the image
                - DO NOT add information that is not present
                - DO NOT add headings or sections that aren't in the image
                - DO NOT add formatting or structure that isn't present
                - NO additional explanations needed

                Specific extraction method:
                1. Read the text exactly as it appears
                2. Represent table data with spaces or symbols as appropriate
                3. Maintain original line breaks and paragraphs
                4. Mark illegible text as "[ILLEGIBLE]"
                5. Preserve layout as much as possible

                For example, if the image only shows "Temperature 98.6°F", just output "Temperature 98.6°F" without any additional headings or sections.
                """
            
            # Gemini モデルを設定
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # 画像をmimeタイプとBase64で準備
            image_part = {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode('utf-8')
            }
            
            # 生成設定 - OCRに最適化
            generation_config = {
                "max_output_tokens": 8192,
                "temperature": 0.1,  # 低い温度で創造性を抑え、正確な抽出のみを促進
                "top_p": 0.95,
            }
            
            # モデルにコンテンツを送信（画像とプロンプト）
            response = model.generate_content([prompt, image_part], generation_config=generation_config)
            
            # テキスト抽出結果の取得
            extracted_text = response.text
            
            # DBに抽出データを保存
            supabase.table("extracted_data").insert({
                "record_id": record_id,
                "extracted_text": extracted_text,
            }).execute()
            
            # 医療カルテの状態を更新
            supabase.table("medical_records").update({
                "processing_status": "completed"
            }).eq("id", record_id).execute()
            
            logger.info(f"Processed record {record_id} successfully")
            return
            
        except Exception as e:
            retries += 1
            error_message = str(e)
            
            if retries > max_retries:
                logger.error(f"最大リトライ回数({max_retries})に達しました。処理を中止します。エラー: {error_message}")
                # エラー状態に更新
                try:
                    supabase.table("medical_records").update({
                        "processing_status": "failed"
                    }).eq("id", record_id).execute()
                except Exception as update_error:
                    logger.error(f"エラー状態への更新に失敗しました: {str(update_error)}")
                return
            
            # エラーメッセージを出力
            logger.warning(f"画像処理中にエラー発生: {error_message}。{retries}/{max_retries}回目のリトライ")
            
            # エクスポネンシャルバックオフ（ジッター付き）
            delay = initial_delay * (2 ** (retries - 1)) * (0.5 + random.random())
            logger.info(f"{delay:.2f}秒後にリトライします。")
            await asyncio.sleep(delay)  # asyncioを使用して非同期に待機
            
            # APIキーに関連するエラーの場合は長めに待機
            if any(keyword in error_message.lower() for keyword in ["key", "quota", "permission", "limit", "api"]):
                extra_delay = 60  # 1分追加で待機
                logger.warning(f"APIキー関連のエラーが疑われます。追加で{extra_delay}秒待機します。")
                await asyncio.sleep(extra_delay)  # asyncioを使用して非同期に待機

@app.get("/api/records/{record_id}")
async def get_record(record_id: str, supabase: Client = Depends(get_supabase)):
    """特定のカルテレコードと抽出データを取得"""
    try:
        # 医療カルテレコードを取得
        record = supabase.table("medical_records").select("*").eq("id", record_id).execute()
        
        if not record.data:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # 抽出データを取得
        extracted = supabase.table("extracted_data").select("*").eq("record_id", record_id).execute()
        
        return {
            "record": record.data[0],
            "extracted_data": extracted.data
        }
    
    except Exception as e:
        logger.error(f"Error fetching record: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/records")
async def get_records(limit: int = 10, offset: int = 0, supabase: Client = Depends(get_supabase)):
    """カルテレコードのリストを取得"""
    try:
        records = supabase.table("medical_records") \
            .select("*") \
            .order("uploaded_at", desc=True) \
            .limit(limit) \
            .offset(offset) \
            .execute()
        
        return {"records": records.data}
    
    except Exception as e:
        logger.error(f"Error fetching records: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/{record_id}")
async def reprocess_record(record_id: str, supabase: Client = Depends(get_supabase)):
    """特定のカルテを再処理する"""
    try:
        # レコードの確認
        record = supabase.table("medical_records").select("*").eq("id", record_id).execute()
        
        if not record.data:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # ステータスを処理中に更新
        supabase.table("medical_records").update({
            "processing_status": "pending"
        }).eq("id", record_id).execute()
        
        # 画像URLを取得
        image_url = record.data[0]["original_image_url"]
        
        # 画像をダウンロード
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to download image")
            image_bytes = response.content
        
        # 処理タスクを開始
        asyncio.create_task(process_image(record_id, image_url, image_bytes))
        
        return {"status": "processing", "record_id": record_id}
    
    except Exception as e:
        logger.error(f"Error reprocessing record: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
