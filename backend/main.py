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

# Gemini API設定
gemini_api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

# Supabaseクライアント作成
def get_supabase() -> Client:
    if not supabase_url or not supabase_key:
        raise HTTPException(status_code=500, detail="Supabase credentials not configured")
    return create_client(supabase_url, supabase_key)

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
        upload_result = supabase.storage.from("images").upload(
            path=storage_path,
            file=contents,
            file_options={"content-type": file.content_type}
        )
        
        # 画像のURLを取得
        file_url = supabase.storage.from("images").get_public_url(storage_path)
        
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

async def process_image(record_id: str, image_url: str, image_bytes: bytes):
    """画像処理と文字抽出を行う非同期関数"""
    try:
        # Supabaseに再接続（非同期タスク内）
        supabase = create_client(supabase_url, supabase_key)
        
        # Base64エンコード
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Gemini モデルを設定
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # 画像をmimeタイプとBase64で準備
        image_parts = [{
            "mime_type": "image/jpeg",
            "data": encoded_image
        }]
        
        # Gemini APIリクエスト送信
        prompt = "この医療カルテから画像と文字情報を抽出してください。できるだけ構造化されたデータとして抽出し、患者名、診断情報、処方薬、医師のコメントなどの重要情報を特定してください。結果はJSON形式で返してください。"
        
        response = model.generate_content([prompt, image_parts[0]])
        
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
    
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        # エラー時の処理
        try:
            supabase.table("medical_records").update({
                "processing_status": "error"
            }).eq("id", record_id).execute()
        except Exception as update_error:
            logger.error(f"Failed to update record status: {str(update_error)}")

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
            "extracted_data": extracted.data[0] if extracted.data else None
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
