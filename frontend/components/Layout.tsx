import React, { ReactNode } from 'react';
import Link from 'next/link';
import Head from 'next/head';

type LayoutProps = {
  children: ReactNode;
  title?: string;
};

const Layout = ({ children, title = '医療カルテ文字抽出アプリ' }: LayoutProps) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Head>
        <title>{title}</title>
        <meta charSet="utf-8" />
        <meta name="viewport" content="initial-scale=1.0, width=device-width" />
      </Head>
      
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              <Link href="/" className="hover:text-blue-600 transition duration-300">
                医療カルテ文字抽出アプリ
              </Link>
            </h1>
            <nav>
              <ul className="flex space-x-6">
                <li>
                  <Link 
                    href="/" 
                    className="text-gray-600 hover:text-blue-600 transition duration-300"
                  >
                    ホーム
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/history" 
                    className="text-gray-600 hover:text-blue-600 transition duration-300"
                  >
                    履歴
                  </Link>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </header>
      
      <main className="flex-grow">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>
      
      <footer className="bg-gray-50 border-t">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            © {new Date().getFullYear()} 医療カルテ文字抽出アプリ
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
