import { useState, useEffect } from 'react';
import Link from 'next/link';

type ResultDisplayProps = {
  recordId: string;
};

type ExtractedData = {
  id: string;
  record_id: string;
  extracted_text: string;
  extracted_at: string;
};

type RecordData = {
  record: {
    id: string;
    original_image_url: string;
    processing_status: string;
  };
  extracted_data: ExtractedData[];
};

export default function ResultDisplay({ recordId }: ResultDisplayProps) {
  const [data, setData] = useState<RecordData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [pollingCount, setPollingCount] = useState<number>(0);

  useEffect(() => {
    let isMounted = true;
    const maxPollingAttempts = 20; // 最大ポーリング試行回数
    
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/records/${recordId}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch result');
        }
        
        const resultData = await response.json();
        
        if (isMounted) {
          setData(resultData);
          
          // 処理ステータスに基づいてポーリングを管理
          if (resultData.record.processing_status === 'completed' || 
              resultData.record.processing_status === 'failed' ||
              pollingCount >= maxPollingAttempts) {
            // 処理完了またはエラー時、またはポーリング上限に達した場合はポーリングを停止
            setLoading(false);
            return true; // ポーリング停止を示す
          }
          
          // ポーリングが継続中でもUIのローディング状態は更新
          if (resultData.record.processing_status === 'processing') {
            setLoading(true);
          }
        }
        return false; // ポーリング継続を示す
      } catch (err) {
        console.error('Error fetching result:', err);
        if (isMounted) {
          setError('結果の取得中にエラーが発生しました');
          setLoading(false);
        }
        return true; // エラー時はポーリングを停止
      }
    };

    // 初回データ取得
    fetchData();
    
    // 動的なポーリング間隔を設定
    const getPollingInterval = (count: number) => {
      // 最初は短い間隔で、その後徐々に長くする
      if (count < 5) return 3000; // 最初の5回は3秒
      if (count < 10) return 5000; // 次の5回は5秒
      return 10000; // それ以降は10秒
    };
    
    // ポーリングを実行
    const intervalId = setInterval(async () => {
      const shouldStop = await fetchData();
      
      if (shouldStop) {
        clearInterval(intervalId);
      } else {
        setPollingCount(prev => prev + 1);
      }
    }, getPollingInterval(pollingCount));

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [recordId, pollingCount]);

  // 文字列をJSONとしてパースして表示する試み
  const renderExtractedText = (text: string) => {
    try {
      // JSONパースを試みる
      const jsonData = JSON.parse(text);
      return (
        <pre className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-80">
          {JSON.stringify(jsonData, null, 2)}
        </pre>
      );
    } catch (e) {
      // 通常テキストとして表示
      return (
        <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap overflow-auto max-h-80">
          {text}
        </div>
      );
    }
  };

  // エラーの詳細表示
  const showErrorDetails = () => {
    if (!data) return null;
    
    // エラーステータスの場合の詳細情報
    if (data.record.processing_status === 'failed') {
      return (
        <div className="mt-2">
          <button 
            onClick={() => alert('管理者に問い合わせてください')}
            className="text-xs text-blue-600 hover:text-blue-800 underline"
          >
            詳細を表示
          </button>
        </div>
      );
    }
    return null;
  };

  // ローディング表示の改良
  if (loading && (!data || data.record.processing_status === 'pending' || data.record.processing_status === 'processing')) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">
          {data?.record.processing_status === 'processing' 
            ? "テキスト抽出中です。しばらくお待ちください..." 
            : "処理の準備中です..."}
        </p>
        <p className="mt-2 text-xs text-gray-500">
          {pollingCount > 10 
            ? "処理に時間がかかっています。大きな画像や複雑なカルテの場合は数分かかることがあります。" 
            : ""}
        </p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4">
        <p>{error || 'データを取得できませんでした'}</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-2 text-sm underline"
        >
          再試行する
        </button>
      </div>
    );
  }

  return (
    <div className="w-full">
      <h2 className="text-xl font-semibold mb-4">処理結果</h2>
      
      <div className="flex flex-col md:flex-row gap-6">
        {/* 元の画像 */}
        <div className="md:w-1/3">
          <h3 className="text-lg font-medium mb-2">元画像</h3>
          <div className="border rounded-md overflow-hidden">
            <img
              src={data?.record?.original_image_url}
              onError={(e) => console.error("Image failed to load:", data?.record?.original_image_url, e)}
              onLoad={() => console.log("Image loaded successfully:", data?.record?.original_image_url)}
              alt="カルテ画像"
              className="w-full object-contain"
            />
          </div>
        </div>
        
        {/* 抽出結果 */}
        <div className="md:w-2/3">
          <h3 className="text-lg font-medium mb-2">抽出テキスト</h3>
          
          {data.record.processing_status === 'pending' ? (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">処理中です。しばらくお待ちください。</p>
                </div>
              </div>
            </div>
          ) : data.record.processing_status === 'failed' ? (
            <div className="bg-red-50 border-l-4 border-red-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">エラーが発生しました。もう一度試してください。</p>
                  {showErrorDetails()}
                </div>
              </div>
            </div>
          ) : data.extracted_data && data.extracted_data.length > 0 ? (
            renderExtractedText(data.extracted_data[0].extracted_text)
          ) : (
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-500">抽出結果がありません。</p>
            </div>
          )}
          
          <div className="mt-4 text-right">
            <button
              onClick={() => window.location.reload()}
              className="mr-4 text-gray-600 hover:text-gray-800"
            >
              更新
            </button>
            <Link href={`/record/${recordId}`} className="text-blue-600 hover:text-blue-800">
              詳細を表示 →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
