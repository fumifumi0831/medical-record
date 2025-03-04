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
  extracted_data: ExtractedData | null;
};

export default function ResultDisplay({ recordId }: ResultDisplayProps) {
  const [data, setData] = useState<RecordData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/records/${recordId}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch result');
        }
        
        const resultData = await response.json();
        setData(resultData);
      } catch (err) {
        console.error('Error fetching result:', err);
        setError('結果の取得中にエラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    const interval = setInterval(fetchData, 3000); // 3秒ごとに状態を確認
    fetchData(); // 初回実行

    return () => clearInterval(interval);
  }, [recordId]);

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

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">処理中です。しばらくお待ちください...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4">
        <p>{error || 'データを取得できませんでした'}</p>
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
              src={data.record.original_image_url} 
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
          ) : data.record.processing_status === 'error' ? (
            <div className="bg-red-50 border-l-4 border-red-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">エラーが発生しました。もう一度試してください。</p>
                </div>
              </div>
            </div>
          ) : data.extracted_data ? (
            renderExtractedText(data.extracted_data.extracted_text)
          ) : (
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-500">抽出結果がありません。</p>
            </div>
          )}
          
          <div className="mt-4 text-right">
            <Link href={`/record/${recordId}`} className="text-blue-600 hover:text-blue-800">
              詳細を表示 →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
