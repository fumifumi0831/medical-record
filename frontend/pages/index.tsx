import { useState } from 'react';
import Head from 'next/head';
import UploadForm from '@/components/UploadForm';
import ResultDisplay from '@/components/ResultDisplay';
import { Layout } from '@/components/Layout';

export default function Home() {
  const [recordId, setRecordId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleUploadSuccess = (id: string) => {
    setRecordId(id);
    setLoading(false);
  };

  return (
    <Layout>
      <Head>
        <title>医療カルテ文字抽出アプリ</title>
        <meta name="description" content="手書き医療カルテから文字を抽出するAIアプリ" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8 text-center">医療カルテ文字抽出アプリ</h1>
        
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6 mb-8">
          <UploadForm 
            onUploadStart={() => setLoading(true)} 
            onUploadSuccess={handleUploadSuccess} 
          />
        </div>

        {recordId && (
          <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
            <ResultDisplay recordId={recordId} />
          </div>
        )}
      </main>
    </Layout>
  );
}