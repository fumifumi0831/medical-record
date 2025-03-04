import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app

client = TestClient(app)


@pytest.fixture
def mock_supabase():
    """Supabaseのモックを作成するフィクスチャ"""
    mock = MagicMock()
    return mock


def test_health_check():
    """GET /api/health エンドポイントのテスト"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"


@patch("main.get_supabase")
def test_get_records(mock_get_supabase, mock_supabase):
    """GET /api/records エンドポイントのテスト"""
    # Supabaseのモック設定
    mock_get_supabase.return_value = mock_supabase
    mock_result = MagicMock()
    mock_result.data = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "original_image_url": "http://example.com/image.jpg",
            "uploaded_at": "2025-03-04T12:34:56.789Z",
            "processing_status": "completed"
        }
    ]
    
    # Supabaseクエリメソッドをチェーンでモック
    mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.offset.return_value.execute.return_value = mock_result
    
    # APIリクエスト実行
    response = client.get("/api/records")
    
    # 検証
    assert response.status_code == 200
    assert "records" in response.json()
    assert len(response.json()["records"]) == 1
    assert response.json()["records"][0]["id"] == "550e8400-e29b-41d4-a716-446655440000"


@patch("main.get_supabase")
def test_get_record_by_id(mock_get_supabase, mock_supabase):
    """GET /api/records/{record_id} エンドポイントのテスト"""
    # Supabaseのモック設定
    mock_get_supabase.return_value = mock_supabase
    
    # レコードデータのモック
    mock_record_result = MagicMock()
    mock_record_result.data = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "original_image_url": "http://example.com/image.jpg",
            "uploaded_at": "2025-03-04T12:34:56.789Z",
            "processing_status": "completed"
        }
    ]
    
    # 抽出データのモック
    mock_extracted_result = MagicMock()
    mock_extracted_result.data = [
        {
            "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "record_id": "550e8400-e29b-41d4-a716-446655440000",
            "extracted_text": "Test extracted text",
            "extracted_at": "2025-03-04T12:40:00.000Z"
        }
    ]
    
    # Supabaseクエリメソッドをモック
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
        mock_record_result,
        mock_extracted_result
    ]
    
    # APIリクエスト実行
    response = client.get("/api/records/550e8400-e29b-41d4-a716-446655440000")
    
    # 検証
    assert response.status_code == 200
    assert "record" in response.json()
    assert "extracted_data" in response.json()
    assert response.json()["record"]["id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert response.json()["extracted_data"]["id"] == "6ba7b810-9dad-11d1-80b4-00c04fd430c8"


@patch("main.get_supabase")
@patch("main.asyncio.create_task")
def test_reprocess_record(mock_create_task, mock_get_supabase, mock_supabase):
    """POST /api/process/{record_id} エンドポイントのテスト"""
    # Supabaseのモック設定
    mock_get_supabase.return_value = mock_supabase
    
    # レコードデータのモック
    mock_record_result = MagicMock()
    mock_record_result.data = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "original_image_url": "http://example.com/image.jpg",
            "uploaded_at": "2025-03-04T12:34:56.789Z",
            "processing_status": "error"
        }
    ]
    
    # 更新結果のモック
    mock_update_result = MagicMock()
    
    # クエリメソッドをモック
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_record_result
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_result
    
    # httpxクライアントのモック
    with patch("httpx.AsyncClient") as mock_client:
        mock_client_instance = MagicMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"test image data"
        mock_client_instance.get.return_value = mock_response
        
        # APIリクエスト実行
        response = client.post("/api/process/550e8400-e29b-41d4-a716-446655440000")
        
        # 検証
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "processing"
        assert response.json()["record_id"] == "550e8400-e29b-41d4-a716-446655440000"
        
        # 非同期タスクが作成されたことを確認
        assert mock_create_task.called