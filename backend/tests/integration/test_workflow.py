import pytest
import os
import time
from pathlib import Path
from fastapi.testclient import TestClient
from supabase import create_client

from main import app

# 統合テストでは実際のSupabase環境と通信する（テスト環境用）
client = TestClient(app)


@pytest.fixture
def supabase_client():
    """Supabaseクライアントを作成するフィクスチャ"""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        pytest.skip("Supabase credentials not set in environment variables")
    
    return create_client(supabase_url, supabase_key)


@pytest.fixture
def sample_image():
    """テスト用のサンプル画像パス"""
    # プロジェクトルートからの相対パスでサンプル画像を取得
    sample_path = Path(__file__).parents[3] / "docs" / "sample_images" / "sample_medical_record.jpg"
    
    if not sample_path.exists():
        pytest.skip(f"Sample image not found at {sample_path}")
    
    return sample_path


@pytest.mark.skipif(not os.environ.get("RUN_INTEGRATION_TESTS"), reason="Integration tests disabled")
def test_upload_and_process_workflow(supabase_client, sample_image):
    """アップロードと処理のワークフローテスト"""
    # ファイルをアップロード
    with open(sample_image, "rb") as f:
        files = {"file": ("sample_medical_record.jpg", f, "image/jpeg")}
        response = client.post("/api/upload", files=files)
    
    # レスポンスを確認
    assert response.status_code == 200
    data = response.json()
    assert "record_id" in data
    assert "status" in data
    assert data["status"] == "processing"
    
    record_id = data["record_id"]
    
    # 処理が完了するまで待機（最大30秒）
    max_wait_time = 30
    wait_interval = 2
    elapsed_time = 0
    
    while elapsed_time < max_wait_time:
        # レコードの状態を確認
        response = client.get(f"/api/records/{record_id}")
        assert response.status_code == 200
        
        record_data = response.json()
        assert "record" in record_data
        
        # 処理が完了したか確認
        if record_data["record"]["processing_status"] == "completed":
            break
        elif record_data["record"]["processing_status"] == "error":
            pytest.fail("Processing ended with error status")
        
        # 待機して再確認
        time.sleep(wait_interval)
        elapsed_time += wait_interval
    
    # タイムアウトした場合
    if elapsed_time >= max_wait_time:
        pytest.fail("Processing timed out")
    
    # 処理結果を確認
    response = client.get(f"/api/records/{record_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert "record" in data
    assert "extracted_data" in data
    assert data["extracted_data"] is not None
    assert "extracted_text" in data["extracted_data"]
    
    # 抽出テキストが空でないことを確認
    assert data["extracted_data"]["extracted_text"]
    
    # 後始末: 作成したレコードを削除
    # Note: この実装は、Supabaseの設定によっては変更が必要
    supabase_client.table("medical_records").delete().eq("id", record_id).execute()


@pytest.mark.skipif(not os.environ.get("RUN_INTEGRATION_TESTS"), reason="Integration tests disabled")
def test_get_records(supabase_client):
    """レコード一覧取得のテスト"""
    # レコード一覧を取得
    response = client.get("/api/records")
    
    # レスポンスを確認
    assert response.status_code == 200
    data = response.json()
    assert "records" in data
    assert isinstance(data["records"], list)


@pytest.mark.skipif(not os.environ.get("RUN_INTEGRATION_TESTS"), reason="Integration tests disabled")
def test_error_handling_invalid_file():
    """無効なファイル形式のエラーハンドリングテスト"""
    # テキストファイルをアップロード（サポートされていない形式）
    files = {"file": ("invalid.txt", b"This is a text file", "text/plain")}
    response = client.post("/api/upload", files=files)
    
    # 400エラーが返ることを確認
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "Only JPG and PNG files are allowed" in response.json()["detail"]


@pytest.mark.skipif(not os.environ.get("RUN_INTEGRATION_TESTS"), reason="Integration tests disabled")
def test_error_handling_invalid_record_id():
    """存在しないレコードIDのエラーハンドリングテスト"""
    # 存在しないレコードIDにリクエスト
    invalid_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/records/{invalid_id}")
    
    # 404エラーが返ることを確認
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "Record not found" in response.json()["detail"]