import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

type UploadFormProps = {
  onUploadStart: () => void;
  onUploadSuccess: (recordId: string) => void;
};

export default function UploadForm({ onUploadStart, onUploadSuccess }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxFiles: 1,
    multiple: false
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('ファイルを選択してください');
      return;
    }

    setUploading(true);
    setError(null);
    onUploadStart();

    // FormDataの作成
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('アップロードに失敗しました');
      }

      const data = await response.json();
      onUploadSuccess(data.record_id);
    } catch (err) {
      console.error('Error uploading:', err);
      setError('アップロード中にエラーが発生しました。再度お試しください。');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full">
      <h2 className="text-xl font-semibold mb-4">カルテ画像をアップロード</h2>
      
      <form onSubmit={handleSubmit}>
        <div 
          {...getRootProps()} 
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
            ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}
            ${error ? 'border-red-300' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          {file ? (
            <div className="py-4">
              <p className="text-green-600 font-medium">ファイルが選択されました:</p>
              <p className="text-gray-700">{file.name}</p>
              <p className="text-gray-500 text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          ) : (
            <div className="py-8">
              <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4h-12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              
              <p className="mt-2 text-sm font-medium text-gray-900">
                {isDragActive ? 'ファイルをここにドロップ' : 'クリックまたはドラッグ＆ドロップでファイルを選択'}
              </p>
              <p className="mt-1 text-xs text-gray-500">
                PNG, JPG (最大10MB)
              </p>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-2 text-sm text-red-600">
            {error}
          </div>
        )}

        <div className="mt-4">
          <button
            type="submit"
            disabled={!file || uploading}
            className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
              ${(!file || uploading) ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {uploading ? '処理中...' : '画像をアップロード'}
          </button>
        </div>
      </form>
    </div>
  );
}
